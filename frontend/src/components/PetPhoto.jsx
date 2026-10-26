import React, { useState, useEffect } from 'react';

const PetPhoto = ({ profileId, backendURL, defaultImage, className = "profile-img-large", alt = "Pet Profile" }) => {
    const [imageSrc, setImageSrc] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchPhoto = async () => {
            try {
                const response = await fetch(`${backendURL}/api/profile/${profileId}/photo`);
                const data = await response.json();

                // If imageData is null or undefined, imageSrc stays null
                if (data.imageData) {
                    setImageSrc(data.imageData);
                } else {
                    setImageSrc(null);
                }
            } catch (err) {
                console.error("Failed to load pet photo:", err);
                setImageSrc(null);
            } finally {
                setLoading(false);
            }
        };

        fetchPhoto();
    }, [profileId, backendURL]);

    if (loading) {
        return (
            <div className="profile-photo-container">
                <img src={defaultImage} alt="Loading..." className="profile-img-large loading-fade" />
            </div>
        );
    }

    return (
        <div className="profile-photo-container">
            <img 
                src={imageSrc || defaultImage} 
                alt={alt}
                className={className}
            />
        </div>
    );
};
export default PetPhoto;