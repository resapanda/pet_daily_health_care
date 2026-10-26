import { useNavigate } from "react-router-dom";
import React, { useState } from 'react';
import "../CreateHealthForm.css";
import PetPhoto from '../components/PetPhoto';

const INITIAL_FORM_STATE = {
    create_vet_record_pet_id: '',
    create_vet_record_date: new Date().toISOString().split('T')[0],
    create_vet_record_clinic: '',
    create_vet_record_diagnosis: '',
    create_vet_record_note: '',
    create_vet_record_pdf: ''
};

const CreateVetRecordForm = ({ profiles = [], backendURL }) => {
    const DEFAULT_PET_IMAGE = "/images/placeholder.png";
    const navigate = useNavigate();
    const [formData, setFormData] = useState(INITIAL_FORM_STATE);

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData((prev) => ({ ...prev, [name]: value }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        // When user forget to select their pet
        if (!formData.create_vet_record_pet_id) {
            alert("Please select a pet before saving the record!");
            return;
        }

        try {
            const response = await fetch(backendURL + '/vet_record/create', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData),
            });

            if (response.ok) {
                alert("Vet Record created successfully.");
                setFormData(INITIAL_FORM_STATE);
            } else {
                alert("Error creating vet record.");
            }
            } catch (error) {
                console.error('Error during form submission:', error);
      }
      navigate("/health");
    };

    return (
        <div className="form-content-area">
            <form className="form-body" onSubmit={handleSubmit}>
                {/* Pet Selection */}
                <div className="form-row pet-selection-row">
                      <label className="row-label">Choose Pet:</label>
                      <div className="pet-avatar-selection">
                          {profiles.map((profile) => (
                              <div 
                                  key={profile.profile_id} 
                                  className={`pet-avatar-item ${formData.create_vet_record_pet_id == profile.profile_id ? 'selected' : ''}`}
                                  onClick={() => setFormData(prev => ({ ...prev, create_vet_record_pet_id: profile.profile_id }))}
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

                  <div className="form-row">
                      <label>Date :</label>
                      <input 
                          type="date" 
                          name="create_vet_record_date"  
                          className="full-input"
                          value={formData.create_vet_record_date}
                          onChange={handleChange}
                      />
                  </div>

                  <div className="form-row">
                      <label>Clinic :</label>
                      <input 
                          type="text" 
                          name="create_vet_record_clinic" 
                          className="full-input"
                          value={formData.create_vet_record_clinic}
                          onChange={handleChange}
                      />
                  </div>

                  <div className="form-row">
                      <label>Diagnosis :</label>
                      <input 
                          type="text" 
                          name="create_vet_record_diagnosis" 
                          className="full-input"
                          value={formData.create_vet_record_diagnosis}
                          onChange={handleChange}
                      />
                  </div>

                  <div className="form-row">
                      <label>Note :</label>
                      <textarea 
                          name="create_vet_record_note" 
                          className="full-input" 
                          rows="4"
                          value={formData.create_vet_record_note}
                          onChange={handleChange}
                      ></textarea>
                  </div>

                  {/* PDF File Upload Section */}
                  <div className="form-row">
                      <label>PDF file :</label>
                      <div className="file-input-wrapper">
                        <input 
                          type="text" 
                          placeholder="Upload PDF file" 
                          readOnly 
                          className="full-input"
                        />
                        <input 
                          type="file" 
                          accept=".pdf" 
                          style={{ display: 'none' }} 
                          id="pdf-upload"
                        />
                      </div>
                  </div>
                  <button type="submit" className="save-btn">Save Vet Visit</button>
            </form>
        </div>
    );
};
export default CreateVetRecordForm;