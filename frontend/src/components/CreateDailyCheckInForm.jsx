import { useNavigate } from "react-router-dom";
import React, { useState } from 'react';
import "../CreateHealthForm.css";
import PetPhoto from '../components/PetPhoto';

const INITIAL_FORM_STATE = {
    create_daily_checkin_pet_id: '',
    create_daily_checkin_date: new Date().toISOString().split('T')[0],
    create_daily_checkin_morning: false,
    create_daily_checkin_treat: false,
    create_daily_checkin_night: false,
    create_daily_checkin_pee: false,
    create_daily_checkin_poop: false,
    create_daily_checkin_mood: 'Neutral',
    create_daily_checkin_symptoms: '',
    create_daily_checkin_note: ''
};

const CreateDailyCheckInForm = ({ profiles = [], backendURL }) => {
    const DEFAULT_PET_IMAGE = "/images/placeholder.png";
    const navigate = useNavigate();
    const [formData, setFormData] = useState(INITIAL_FORM_STATE);

    const handleChange = (e) => {
        const { name, value, type, checked } = e.target;
        setFormData(prevState => ({
            ...prevState,
            [name]: type === 'checkbox' ? checked : value
        }));
    };

    const handleMoodChange = (selectedMood) => {
        setFormData(prevState => ({
            ...prevState,
            create_daily_checkin_mood: selectedMood
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault(); // Prevent default form submission

        // When user forget to select their pet
        if (!formData.create_daily_checkin_pet_id) {
            alert("Please select a pet before saving the record!");
            return;
        }

        try {
            const response = await fetch(backendURL + '/daily_checkin/create', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData),
            });

            if (response.ok) {
                alert("Daily Check-In created successfully.");
                setFormData(INITIAL_FORM_STATE);
            } else {
                alert("Error creating daily check-in.");
            }
            } catch (error) {
                console.error('Error during form submission:', error);
        }
        navigate("/health");
    };

    return (
        <div className="form-content-area">
            <form className="health-form" onSubmit={handleSubmit}>

                {/* Pet Selection */}
                <div className="form-row pet-selection-row">
                    <label className="row-label">Choose Pet:</label>
                    <div className="pet-avatar-selection">
                        {profiles.map((profile) => (
                            <div 
                                key={profile.profile_id} 
                                className={`pet-avatar-item ${formData.create_daily_checkin_pet_id == profile.profile_id ? 'selected' : ''}`}
                                onClick={() => setFormData(prev => ({ ...prev, create_daily_checkin_pet_id: profile.profile_id }))}
                              > 
                                <PetPhoto 
                                    profileId={profile.profile_id} 
                                    backendURL={backendURL} 
                                    defaultImage={DEFAULT_PET_IMAGE}
                                    className="pet-thumb-large"
                                    alt={profile.name}
                                />
                                <span className="pet-avatar-name">{profile.name}</span>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Food Section */}
                <div className="form-row">
                    <label className="row-label">Food :</label>
                    <div className="checkbox-group-refined">
                        <label>Morning <input type="checkbox" name="create_daily_checkin_morning" checked={formData.create_daily_checkin_morning} onChange={handleChange}/></label>
                        <label>Treat <input type="checkbox" name="create_daily_checkin_treat" checked={formData.create_daily_checkin_treat} onChange={handleChange}/></label>
                        <label>Night <input type="checkbox" name="create_daily_checkin_night" checked={formData.create_daily_checkin_night} onChange={handleChange}/></label>
                    </div>
                </div>

                {/* Toilet Section */}
                <div className="form-row">
                    <label className="row-label">Toilet :</label>
                    <div className="checkbox-group-refined">
                        <label>Pee <input type="checkbox" name="create_daily_checkin_pee" checked={formData.create_daily_checkin_pee} onChange={handleChange}/></label>
                        <label>Poop <input type="checkbox" name="create_daily_checkin_poop" checked={formData.create_daily_checkin_poop} onChange={handleChange}/></label>
                    </div>
                </div>

                {/* Mood Section */}
                <div className="form-row">
                    <label className="row-label">Mood :</label>
                    <div className="mood-btns">
                        <button type="button" className={`mood-btn bad ${formData.create_daily_checkin_mood === 'Bad' ? 'selected' : ''}`} onClick={() => handleMoodChange('Bad')}>Bad</button>
                        <button type="button" className={`mood-btn neutral ${formData.create_daily_checkin_mood === 'Neutral' ? 'selected' : ''}`} onClick={() => handleMoodChange('Neutral')}>Neutral</button>
                        <button type="button" className={`mood-btn good ${formData.create_daily_checkin_mood === 'Good' ? 'selected' : ''}`} onClick={() => handleMoodChange('Good')}>Good</button>
                    </div>
                </div>

                {/* Text Inputs */}
                <div className="form-row">
                    <label className="row-label">Symptoms :</label>
                    <input type="text" className="full-input" name="create_daily_checkin_symptoms" value={formData.create_daily_checkin_symptoms} onChange={handleChange} />
                </div>

                <div className="form-row">
                    <label className="row-label">Note :</label>
                    <textarea className="full-input text-area" name="create_daily_checkin_note" value={formData.create_daily_checkin_note} onChange={handleChange} rows="2" />
                </div>

                <div className="save-btn-container">
                  <button type="submit" className="save-btn">Save Daily Check-In</button>
                </div>
            </form>
        </div>
    );
};
export default CreateDailyCheckInForm;