import { useNavigate } from "react-router-dom";
import React, { useState } from 'react';
import { DOG_BREEDS, CAT_BREEDS, AGES } from '/data/petData';
import "../CreateProfileForm.css";

const INITIAL_FORM_STATE = {
    create_profile_name: '',
    create_profile_type: 'dog',
    create_profile_gender: 'boy',
    create_profile_age: 1,
    create_profile_breed: '',
    create_profile_weight: '',
    create_profile_unit: 'lb',
    photo_full_path: '',
    reminder_enabled: false,
    reminder_time: '20:00'
};

const AddProfile = ({ backendURL }) => {
    const navigate = useNavigate();
    const [formData, setFormData] = useState(INITIAL_FORM_STATE);

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prevState => ({
            ...prevState,
            [name]: value
        }));
    };

    // --- Microservice Integration ---
    const handleUnitConversion = async (newUnit) => {
        if (!formData.create_profile_weight) {
            setFormData(prev => ({ ...prev, create_profile_unit: newUnit }));
            return;
        }

        try {
            const response = await fetch(`${backendURL}/api/convert`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    value: parseFloat(formData.create_profile_weight),
                    from_unit: formData.create_profile_unit,
                    to_unit: newUnit
                }),
            });

            const data = await response.json();
            
            if (data && data.rounded_val !== undefined) {
                setFormData((prev) => ({
                    ...prev,
                    create_profile_weight: data.rounded_val,
                    create_profile_unit: newUnit
                }));
            } else {
                console.error("Conversion error:", data.error);
            }
        } catch (error) {
            console.error("Could not connect to conversion service:", error);
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        
        // Retrieve the logged-in user's ID
        const currentUserId = localStorage.getItem('userId');
        
        // Combine the form data with the user ID
        const profileData = {
            ...formData,
            user_id: currentUserId 
        };

        try {
            const response = await fetch(backendURL + '/profile/create', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(profileData),
            });

            if (response.ok) {
                alert("Profile created successfully.");
                navigate("/profile");
                setFormData(INITIAL_FORM_STATE);
            } else {
                alert("Error creating profile.");
            }
        } catch (error) {
            console.error('Error during form submission:', error);
        }
        navigate("/profile");
      };

    return (
        <div className="home-main-card">
            <div className="header-container">
                <h2 className="section-header">Add New Pet Profile</h2>
            </div>
    
            <form className="pet-form" onSubmit={handleSubmit}>
                <div className="form-content">
                    {/* Left Side: Photo Path & Preview */}
                    <div className="photo-upload-section">
                        <div className="image-placeholder">
                            <span className="placeholder-icon">🐾</span>
                            <p>Pet Photo</p>
                        </div>
                        <div className="path-input-group">
                            <label htmlFor="photo_full_path">Photo Full Path</label>
                            <input
                                type="text"
                                name="photo_full_path"
                                id="photo_full_path"
                                placeholder="C:\Users\Documents\dog.jpg"
                                value={formData.photo_full_path}
                                onChange={handleChange}
                            />
                            <small>Paste the absolute path to your image.</small>
                        </div>
                    </div>
    
                    {/* Right Side: Input Fields */}
                    <div className="fields-section">
                        <div className="form-group">
                            <label>Name</label>
                            <input type="text" name="create_profile_name" value={formData.create_profile_name} onChange={handleChange} />
                        </div>
    
                        <div className="form-group">
                            <label>Gender</label>
                            <select name="create_profile_gender" value={formData.create_profile_gender} onChange={handleChange}>
                                <option value="boy">Boy</option>
                                <option value="girl">Girl</option>
                            </select>
                        </div>
    
                        <div className="form-group">
                            <label>Age</label>
                            <select name="create_profile_age" value={formData.create_profile_age} onChange={handleChange}>
                                {AGES.map(age => (
                                    <option key={age} value={age}>{age} {age === 1 ? 'year' : 'years'} old</option>
                                ))}
                            </select>
                        </div>
    
                        <div className="form-group">
                            <label>Pet Type</label>
                            <select name="create_profile_type" value={formData.create_profile_type} onChange={handleChange}>
                                <option value="dog">Dog</option>
                                <option value="cat">Cat</option>
                            </select>
                        </div>
    
                        <div className="form-group">
                            <label>Breed</label>
                            <select name="create_profile_breed" value={formData.create_profile_breed} onChange={handleChange}>
                                <option value="">Select a Breed</option>
                                {(formData.create_profile_type === 'dog' ? DOG_BREEDS : CAT_BREEDS).map(breed => (
                                    <option key={breed} value={breed}>{breed}</option>
                                ))}
                            </select>
                        </div>
    
                        <div className="form-group">
                            <label>Weight</label>
                            <div className="input-with-unit">
                                <input type="number" name="create_profile_weight" value={formData.create_profile_weight} onChange={handleChange} />
                                <select className="unit-selector" name="create_profile_unit" value={formData.create_profile_unit} onChange={(e) => handleUnitConversion(e.target.value)}>
                                    <option value="lb">lb</option>
                                    <option value="kg">kg</option>
                                </select>
                            </div>
                        </div>
                    </div>
                </div>
    
                {/* Bottom Section: Notifications & Button */}
                <div className="reminder-section">
                    <div className="reminder-box">
                        <input
                            type="checkbox"
                            id="reminder_enabled"
                            name="reminder_enabled"
                            checked={formData.reminder_enabled}
                            onChange={handleChange}
                        />
                        <label htmlFor="reminder_enabled">Remind me for daily check-ins</label>
                        
                        {formData.reminder_enabled && (
                            <input
                                type="time"
                                className="time-picker"
                                name="reminder_time"
                                value={formData.reminder_time}
                                onChange={handleChange}
                            />
                        )}
                    </div>
    
                    <button type="submit" className="save-btn">
                        Save Profile
                    </button>
                </div>
            </form>
        </div>
    );
};
export default AddProfile;