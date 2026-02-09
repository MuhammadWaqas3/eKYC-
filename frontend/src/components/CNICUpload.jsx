"use client";

import { useState, useRef } from "react";
import { Upload, CheckCircle, RefreshCw, FileImage } from "lucide-react";
import styles from "./BiometricCapture.module.css";

export default function CNICUpload({ onCapture }) {
    const [frontImage, setFrontImage] = useState(null);
    const [backImage, setBackImage] = useState(null);
    const [frontPreview, setFrontPreview] = useState(null);
    const [backPreview, setBackPreview] = useState(null);

    const frontInputRef = useRef(null);
    const backInputRef = useRef(null);

    const handleFrontChange = (e) => {
        const file = e.target.files[0];
        if (file && file.type.startsWith('image/')) {
            setFrontImage(file);

            // Create preview
            const reader = new FileReader();
            reader.onloadend = () => {
                setFrontPreview(reader.result);
            };
            reader.readAsDataURL(file);
        }
    };

    const handleBackChange = (e) => {
        const file = e.target.files[0];
        if (file && file.type.startsWith('image/')) {
            setBackImage(file);

            // Create preview
            const reader = new FileReader();
            reader.onloadend = () => {
                setBackPreview(reader.result);
            };
            reader.readAsDataURL(file);
        }
    };

    const clearFront = () => {
        setFrontImage(null);
        setFrontPreview(null);
        if (frontInputRef.current) {
            frontInputRef.current.value = '';
        }
    };

    const clearBack = () => {
        setBackImage(null);
        setBackPreview(null);
        if (backInputRef.current) {
            backInputRef.current.value = '';
        }
    };

    const handleConfirm = () => {
        if (frontImage && backImage) {
            // Send actual File objects, not base64 previews
            onCapture(frontImage, backImage);
        }
    };

    const bothSelected = frontImage && backImage;

    return (
        <div className={styles.container}>
            <div className={styles.instructions}>
                Upload your CNIC (Front and Back)
            </div>

            <div className={styles.uploadContainer}>
                {/* Front Image Upload */}
                <div className={styles.uploadSection}>
                    <h3 className={styles.uploadTitle}>
                        <FileImage size={20} style={{ marginRight: 8 }} />
                        CNIC Front
                    </h3>

                    {!frontPreview ? (
                        <div className={styles.uploadBox} onClick={() => frontInputRef.current?.click()}>
                            <Upload size={48} className={styles.uploadIcon} />
                            <p>Click to upload front image</p>
                            <span className={styles.uploadHint}>JPG, PNG (Max 10MB)</span>
                            <input
                                ref={frontInputRef}
                                type="file"
                                accept="image/jpeg,image/jpg,image/png"
                                onChange={handleFrontChange}
                                style={{ display: 'none' }}
                            />
                        </div>
                    ) : (
                        <div className={styles.previewSection}>
                            <img src={frontPreview} alt="CNIC Front" className={styles.previewImage} />
                            <button
                                className={styles.clearBtn}
                                onClick={clearFront}
                                title="Clear and re-upload"
                            >
                                <RefreshCw size={16} /> Change
                            </button>
                        </div>
                    )}
                </div>

                {/* Back Image Upload */}
                <div className={styles.uploadSection}>
                    <h3 className={styles.uploadTitle}>
                        <FileImage size={20} style={{ marginRight: 8 }} />
                        CNIC Back
                    </h3>

                    {!backPreview ? (
                        <div className={styles.uploadBox} onClick={() => backInputRef.current?.click()}>
                            <Upload size={48} className={styles.uploadIcon} />
                            <p>Click to upload back image</p>
                            <span className={styles.uploadHint}>JPG, PNG (Max 10MB)</span>
                            <input
                                ref={backInputRef}
                                type="file"
                                accept="image/jpeg,image/jpg,image/png"
                                onChange={handleBackChange}
                                style={{ display: 'none' }}
                            />
                        </div>
                    ) : (
                        <div className={styles.previewSection}>
                            <img src={backPreview} alt="CNIC Back" className={styles.previewImage} />
                            <button
                                className={styles.clearBtn}
                                onClick={clearBack}
                                title="Clear and re-upload"
                            >
                                <RefreshCw size={16} /> Change
                            </button>
                        </div>
                    )}
                </div>
            </div>

            <div className={styles.controls}>
                <button
                    className="btn"
                    onClick={handleConfirm}
                    disabled={!bothSelected}
                    style={{ opacity: bothSelected ? 1 : 0.5 }}
                >
                    <CheckCircle size={18} style={{ marginRight: 8 }} />
                    Confirm & Continue
                </button>
            </div>
        </div>
    );
}
