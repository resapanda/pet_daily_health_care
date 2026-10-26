// ########################################
// ########## SETUP

// Database
const db = require('./database/db-connector');

// Express
const express = require('express');
const axios = require('axios');
const app = express();
const http = require('http');
const { Server } = require("socket.io");
const server = http.createServer(app);

const io = new Server(server, {
    cors: {
        origin: "*", // Allow React to connect
        methods: ["GET", "POST"]
    }
});

// Middleware
const cors = require('cors');
app.use(cors({ credentials: true, origin: "*" }));
app.use(express.json()); // this is needed for post requests

const asyncHandler = (fn) => (req, res, next) => {
    Promise.resolve(fn(req, res, next)).catch(next);
};


const PORT = 5123;
const path = require('path');
const bcrypt = require('bcryptjs');

// microservices url
const UNIT_SERVICE_URL = 'http://127.0.0.1:6901';
const NOTIFICATION_SERVICE_URL = 'http://127.0.0.1:6907';
const DIET_CALCULATION_URL = 'http://127.0.0.1:6906';
const FILE_SERVICE_URL = 'http://127.0.0.1:6905';

// ########################################
// ########## ROUTE HANDLERS

// WEBHOOK ROUTE
app.post('/webhook', (req, res) => {
    const { user_id, title, message } = req.body;

    console.log(`>>> WEBHOOK HIT AT ${new Date().toLocaleTimeString()}! Data:`, req.body);

    console.log(`\n Notification for User ${user_id}: ${message}`);

    io.emit("new_notification", {
        userId: user_id,
        title: title,
        message: message
    });

    res.status(200).send("OK");
});

// MICROSERVICE
app.post('/api/convert', asyncHandler(async (req, res) => {
    console.log("Calling Unit Conversion Service : ", req.body)
    const response = await axios.post(`${UNIT_SERVICE_URL}/convert-unit`, req.body);
    res.json(response.data);
}));

app.get('/api/daily-goal/:profileId', asyncHandler(async (req, res) => {
    const { profileId } = req.params;

    const [profiles] = await db.query('SELECT * FROM Profiles WHERE profile_id = ?', [profileId]);
    if (profiles.length === 0) return res.status(404).json({ error: "Pet not found" });
    
    const pet = profiles[0];

    // validation for checking type
    const species = (pet.type || 'dog').toLowerCase();

    // convert weight to kg if it's currently in lb
    let weightInKg = pet.weight; 
    if (pet.unit === 'lb' || !pet.unit) {
        weightInKg = pet.weight * 0.453592;
    }

    const payload = {
        species: species,
        weight: weightInKg
    };

    console.log("Calling Diet Calculation Service : ", payload)
    const response = await axios.post(`${DIET_CALCULATION_URL}/calculate/calories`, payload);
    res.json({
        daily_target: response.data.daily_caloric_target
    });
}));

app.get('/api/profile/:id/photo', asyncHandler(async function (req, res) {
    const profileId = req.params.id;

    try {
        const [rows] = await db.query(
            "SELECT file_id FROM Profiles WHERE profile_id = ?", 
            [profileId]
        );

        if (!rows || rows.length === 0 || !rows[0].file_id) {
            return res.status(200).json({ imageData: null }); 
        }

        const fileId = rows[0].file_id;

        console.log("Calling File Service with URL parameter(fileId): ", fileId)
        const response = await axios.get(`${FILE_SERVICE_URL}/get-file/${fileId}`);
        
        const imageExtension = response.data.type; 
        const base64Blob = response.data.blob;

        res.json({
            imageData: `data:image/${imageExtension};base64,${base64Blob}`
        });

    } catch (error) {
        console.error("Photo Fetch Error:", error.message);
        res.status(404).json({ error: "Image not found" });
    }
}));

// REGISTER ROUTE
app.post('/register', asyncHandler(async (req, res) => {
    const { email, password } = req.body;
    // Hash the password
    const salt = await bcrypt.genSalt(10);
    const hashedPassword = await bcrypt.hash(password, salt);

    const query = `INSERT INTO Users (email, password_hash) VALUES (?, ?);`;
    await db.query(query, [email, hashedPassword]);

    res.status(201).json({ message: "User registered successfully!" });
}));

// LOGIN ROUTE
app.post('/login', asyncHandler(async (req, res) => {
    const { email, password } = req.body;

    const [users] = await db.query('SELECT * FROM Users WHERE email = ?', [email]);
    const user = users[0];

    if (!user || !(await bcrypt.compare(password, user.password_hash))) {
        return res.status(401).json({ error: "Invalid email or password." });
    }

    res.status(200).json({ 
        message: "Login successful!",
        userId: user.user_id 
    });
}));

// READ ROUTES
app.get('/home/:userId', asyncHandler(async (req, res) => {
    const { userId } = req.params; 
    // Create and execute our queries
    const query1 = `SELECT * FROM Profiles WHERE user_id = ? ORDER BY name ASC;`;
    const [profiles] = await db.query(query1, [userId]);

    res.status(200).json({ profiles });  // Send the results to the frontend
}));

app.get('/profile/:userId', asyncHandler(async (req, res) => {
    const { userId } = req.params;
    // Create and execute our queries
    const query1 = `SELECT * FROM Profiles WHERE user_id = ?;`;
    const [profiles] = await db.query(query1, [userId]);

    res.status(200).json({ profiles });  // Send the results to the frontend
}));

app.get('/health/:userId', asyncHandler(async (req, res) => {
    const { userId } = req.params;
    // Create and execute our queries
    const query1 = `
        SELECT DailyCheckins.* FROM DailyCheckins 
        JOIN Profiles ON DailyCheckins.profile_id = Profiles.profile_id 
        WHERE Profiles.user_id = ?`;
    const [dailyCheckIns] = await db.query(query1, [userId]);
    const query2 = `
        SELECT VetRecords.* FROM VetRecords 
        JOIN Profiles ON VetRecords.profile_id = Profiles.profile_id 
        WHERE Profiles.user_id = ?`;
    const [vetRecords] = await db.query(query2, [userId]);
    const [profiles] = await db.query('SELECT * FROM Profiles WHERE user_id = ? ORDER BY name ASC;', [userId]);

    res.status(200).json({ dailyCheckIns, vetRecords, profiles });  // Send the results to the frontend
}));

// CREATE ROUTE
app.post('/home/quick-checkin', asyncHandler(async (req, res) => {
    // Parse frontend form information
    const data = req.body;
    
    // Create and execute our queries
    const query1 = `CALL sp_create_daily_checkin(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, @new_id);`;

    await db.query(query1, [
        data.pet_id,
        data.date,             
        data.food_morning, 
        data.food_treat,
        data.food_night,
        data.toilet_pee,
        data.toilet_poop,
        data.mood,             
        'n/a',                
        'Quick check-in from Home' 
    ]);

    const query2 = `SELECT @new_id AS new_id;`;
    const [[rows]] = await db.query(query2);
    
    res.status(201).json({ 
        message: "Quick check-in saved!", 
        id: rows.new_id 
    });
}));

app.post('/profile/create', asyncHandler(async function (req, res) {
    // Parse frontend form information
    let data = req.body;

    // Casting
    const userIdInt = parseInt(data.user_id, 10);
    const profileAgeInt = parseInt(data.create_profile_age, 10);

    // Create and execute our queries
    const query1 = `CALL sp_create_profile(?, ?, ?, ?, ?, ?, ?, ?, @new_id);`;

    await db.query(query1, [
        userIdInt,
        data.create_profile_name,
        data.create_profile_gender,
        profileAgeInt,
        data.create_profile_type,
        data.create_profile_breed,
        data.create_profile_weight,
        data.create_profile_unit
    ]);

    const [idRows] = await db.query("SELECT @new_id AS new_id;");
    const newProfileId = idRows[0].new_id;

    console.log(`CREATE Profiles. ID: ${newProfileId} ` +
        `Name: ${data.create_profile_name} `
    );

    // file microservice 
    if (data.photo_full_path) {
        try {
            const fullPath = data.photo_full_path.trim();

            // find the last slash
            const lastSlashIndex = fullPath.lastIndexOf('/');
            // get file path without last slash
            const filePath = fullPath.substring(0, lastSlashIndex); 

            const fullFileName = fullPath.substring(lastSlashIndex + 1);

            // split the name from the dot
            const lastDotIndex = fullFileName.lastIndexOf('.');
            const fileName = fullFileName.substring(0, lastDotIndex); 
            const fileType = fullFileName.substring(lastDotIndex + 1);

            const fileServicePayload = {
                filePath: filePath,           
                fileName: fileName,        
                type: fileType
            };

            console.log("Calling File Service: ", fileServicePayload)
            const response = await axios.post(`${FILE_SERVICE_URL}/register-file`, fileServicePayload);
            const fileId = response.data.fileId;

            await db.query(
                "UPDATE Profiles SET file_id = ? WHERE profile_id = ?", 
                [fileId, newProfileId]
            );
            console.log(`File registered: ${fileId}`);
        } catch (fileError) {
            console.error('File Service Error:', fileError.message);
        }
    }

    // notification microservice
    if (data.reminder_enabled) {
        try {
            const [hours, minutes] = data.reminder_time.split(':').map(Number);
            let notifyDate = new Date();
            notifyDate.setHours(hours, minutes, 0, 0);
    
            if (notifyDate < new Date()) {
                notifyDate.setDate(notifyDate.getDate() + 1);
            }
            
            // convert it to unix timestamp
            const unixTimestamp = Math.floor(notifyDate.getTime() / 1000);
    
            const microservicePayload = {
                user_id: userIdInt,
                type: "PERIODIC",
                title: `${data.create_profile_name}'s Daily Check-in`,
                message: `Time to see how ${data.create_profile_name} is doing!`,
                notify_at: unixTimestamp,
                interval_seconds: 86400 // 24hrs
            };

            console.log("Calling Notifications Service: ", microservicePayload)
            const response= await axios.post(`${NOTIFICATION_SERVICE_URL}/notification`, microservicePayload);
            const notificationId = response.data.notification_id;
            
            // save notification_id to our db
            await db.query(
                "UPDATE Profiles SET notification_id = ? WHERE profile_id = ?", 
                [notificationId, newProfileId]
            );

            console.log(`Notification ${notificationId} scheduled for ${data.create_profile_name} (Unix: ${unixTimestamp})`);

        } catch (notifyError) {
            console.error('Notification Service Error:', notifyError.message);
        }
    }
    // Send success status to frontend
    res.status(200).json({ message: 'Profile created successfully' });
}));

app.post('/daily_checkin/create', asyncHandler(async function (req, res) {
    // Parse frontend form information
    let data = req.body;

    // Casting
    const profileIdInt = parseInt(data.create_daily_checkin_pet_id, 10);

    // Create and execute our queries
    const query1 = `CALL sp_create_daily_checkin(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, @new_id);`;

    await db.query(query1, [
        profileIdInt,
        data.create_daily_checkin_date,
        data.create_daily_checkin_morning,
        data.create_daily_checkin_treat,
        data.create_daily_checkin_night,
        data.create_daily_checkin_pee,
        data.create_daily_checkin_poop,
        data.create_daily_checkin_mood,
        data.create_daily_checkin_symptoms,
        data.create_daily_checkin_note
    ]);

    const query2 = `SELECT @new_id AS new_id;`;
    const [[rows]] = await db.query(query2);

    console.log(`CREATE DailyCheckins. ID: ${rows.new_id} ` +
        `Name: ${data.create_daily_checkin_date} `
    );

    // Send success status to frontend
    res.status(200).json({ message: 'Daily Check-In created successfully' });
}));

app.post('/vet_record/create', asyncHandler(async function (req, res) {
    // Parse frontend form information
    let data = req.body;

    // Casting
    const profileIdInt = parseInt(data.create_vet_record_pet_id, 10);

    // Create and execute our queries
    const query1 = `CALL sp_create_vet_record(?, ?, ?, ?, ?, ?, @new_id);`;

    await db.query(query1, [
        profileIdInt,
        data.create_vet_record_date,
        data.create_vet_record_clinic,
        data.create_vet_record_diagnosis,
        data.create_vet_record_note,
        data.create_vet_record_pdf
    ]);

    const query2 = `SELECT @new_id AS new_id;`;
    const [[rows]] = await db.query(query2);

    console.log(`CREATE VetRecords. ID: ${rows.new_id} ` +
        `Name: ${data.create_vet_record_date} `
    );

    // Send success status to frontend
    res.status(200).json({ message: 'Vet Record created successfully' });
}));

// DELETE ROUTE
app.delete('/profile/delete', asyncHandler(async function (req, res) {
    const data = req.body;
    const profileId = data.delete_profile_id;

    if (!profileId) {
        return res.status(400).json({ success: false, error: 'Missing ID' });
    }

    const [rows] = await db.query(
        "SELECT notification_id FROM Profiles WHERE profile_id = ?", 
        [profileId]
    );

    if (rows.length > 0 && rows[0].notification_id) {
        const notifId = rows[0].notification_id;
        try {
            console.log("Calling Notification Service with URL parameter : ", notifId)
            await axios.delete(`${NOTIFICATION_SERVICE_URL}/notification/${notifId}`);
            console.log(`Successfully cancelled notification ID: ${notifId}`);
        } catch (microserviceError) {
            console.error('Could not delete from microservice:', microserviceError.message);
        }
    }

    const query = `CALL sp_Delete(?, ?, ?);`;
    await db.query(query, ['Profiles', 'profile_id', data.delete_profile_id]);

    console.log(`Deleted Profile ID: ${data.delete_profile_id}`);
    res.json({ success: true });
}));

app.delete('/daily_checkin/delete', asyncHandler(async function (req, res) {
    const data = req.body;

    if (!data.delete_daily_checkin_id) {
        return res.status(400).json({ success: false, error: 'Missing ID' });
    }
    
    const query = `CALL sp_Delete(?, ?, ?);`;
    
    await db.query(query, ['DailyCheckins', 'daily_checkin_id', data.delete_daily_checkin_id]);

    console.log(`Deleted Daily Check-In ID: ${data.delete_daily_checkin_id}`);
    res.json({ success: true });
}));

app.delete('/vet_record/delete', asyncHandler(async function (req, res) {
    const data = req.body;

    if (!data.delete_vet_record_id) {
        return res.status(400).json({ success: false, error: 'Missing ID' });
    }
    
    const query = `CALL sp_Delete(?, ?, ?);`;
    
    await db.query(query, ['VetRecords', 'vet_record_id', data.delete_vet_record_id]);

    console.log(`Deleted Vet Record ID: ${data.delete_vet_record_id}`);
    res.json({ success: true });
}));

// Global Error Handler
app.use((err, req, res, next) => {
    console.error(">>> SERVER ERROR:", err.stack);

    // handle MySQL duplicate entry
    if (err.errno === 1062) {
        return res.status(400).json({ error: "This record already exists (Duplicate Entry)." });
    }

    // handle MySQL foreign key constraint
    if (err.errno === 1451) {
        return res.status(400).json({ 
            success: false, 
            message: "Cannot delete: This item is currently linked to an active record." 
        });
    }

    // default fallback error
    const statusCode = res.statusCode === 200 ? 500 : res.statusCode;
    res.status(statusCode).json({
        success: false,
        message: err.message || "An unexpected server error occurred."
    });
});


// ########################################
// ########## LISTENER

server.listen(PORT, () => {
    console.log(`Server running on http://localhost:${PORT}`);
    console.log(`- Webhook: http://localhost:${PORT}/webhook`);
    console.log(`- Sockets: http://localhost:${PORT}`);
});
