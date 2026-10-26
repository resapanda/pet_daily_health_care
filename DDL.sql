SET FOREIGN_KEY_CHECKS = 0;

SET AUTOCOMMIT = 0;

--
-- Table structure for table `Users`
--
CREATE
OR
REPLACE
TABLE Users (
    user_id INT NOT NULL AUTO_INCREMENT,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    PRIMARY KEY (user_id)
);

--
-- Dumping data for table `Users`
--
INSERT INTO
    Users (email, password_hash)
VALUES (
        'test@example.com',
        'scrambled_hash_here'
    );

--
-- Table structure for table `Profiles`
--
CREATE
OR
REPLACE
TABLE Profiles (
    profile_id INT NOT NULL AUTO_INCREMENT,
    user_id INT NOT NULL,
    name VARCHAR(50) NOT NULL,
    gender VARCHAR(10) NOT NULL CHECK (gender IN ('boy', 'girl')),
    age INT CHECK (age >= 0),
    breed VARCHAR(100) DEFAULT 'Mixed Breed',
    type VARCHAR(10) DEFAULT 'dog' CHECK (type IN ('dog', 'cat'),
    weight DECIMAL(5, 2) CHECK (weight > 0),
    unit VARCHAR(10) DEFAULT 'lb',
    notification_id INT,
    file_id VARCHAR(8),
    PRIMARY KEY (profile_id),
    CONSTRAINT fk_Users_Profiles FOREIGN KEY (user_id) REFERENCES Users (user_id) ON DELETE CASCADE
);

--
-- Dumping data for table `Profiles`
--
-- TODO: maybe better if you add date_birth and calcurate age automatically
INSERT INTO
    Profiles (
        user_id,
        name,
        gender,
        age,
        breed,
        weight
    )
VALUES (
        1,
        'Mugi',
        'boy',
        '3',
        'american shorthair',
        '11.50'
    ),
    (
        1,
        'Negi',
        'boy',
        '3',
        'american shorthair',
        '13.00'
    );

--
-- Table structure for table `DailyCheckins`
--
CREATE
OR
REPLACE
TABLE DailyCheckins (
    daily_checkin_id INT NOT NULL AUTO_INCREMENT,
    profile_id INT NOT NULL,
    date DATE DEFAULT CURRENT_DATE,
    food_morning BOOLEAN DEFAULT FALSE,
    food_treat BOOLEAN DEFAULT FALSE,
    food_night BOOLEAN DEFAULT FALSE,
    toilet_pee BOOLEAN DEFAULT FALSE,
    toilet_poop BOOLEAN DEFAULT FALSE,
    mood VARCHAR(10) NOT NULL CHECK (
        mood IN ('Bad', 'Neutral', 'Good')
    ),
    symptoms TEXT,
    note TEXT,
    PRIMARY KEY (daily_checkin_id),
    CONSTRAINT fk_Profiles_DailyCheckins FOREIGN KEY (profile_id) REFERENCES Profiles (profile_id) ON DELETE CASCADE
);

--
-- Dumping data for table `DailyCheckins`
--
INSERT INTO
    DailyCheckins (
        profile_id,
        food_morning,
        food_treat,
        food_night,
        toilet_pee,
        toilet_poop,
        mood
    )
VALUES (
        (
            SELECT profile_id
            FROM Profiles
            WHERE
                name = 'Mugi'
        ),
        TRUE,
        TRUE,
        TRUE,
        TRUE,
        TRUE,
        'Good'
    );

--
-- Table structure for table `VetRecords`
--
CREATE
OR
REPLACE
TABLE VetRecords (
    vet_record_id INT NOT NULL AUTO_INCREMENT,
    profile_id INT NOT NULL,
    date DATE DEFAULT CURRENT_DATE,
    clinic VARCHAR(100),
    diagnosis TEXT,
    note TEXT,
    pdf_url VARCHAR(255),
    PRIMARY KEY (vet_record_id),
    CONSTRAINT fk_Profiles_VetRecords FOREIGN KEY (profile_id) REFERENCES Profiles (profile_id) ON DELETE CASCADE
);

--
-- Dumping data for table `VetRecords`
--
INSERT INTO
    VetRecords (profile_id, clinic)
VALUES (
        (
            SELECT profile_id
            FROM Profiles
            WHERE
                name = 'Mugi'
        ),
        'Shoreline animal hospital'
    );

SET FOREIGN_KEY_CHECKS = 1;

COMMIT;