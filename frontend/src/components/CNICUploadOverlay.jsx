"use client";

import { useState, useRef } from "react";
import { Upload, CheckCircle, X, FileImage, RefreshCw } from "lucide-react";
import styles from "./CameraOverlay.module.css";

export default function CNICUploadOverlay({ onCapture, onClose }) {
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

            const reader = new FileReader();
            reader.onloadend = () => {
                setBackPreview(reader.result);
            };
            reader.readAsDataURL(file);
        }
    };

    const handleConfirm = () => {
        if (frontImage && backImage) {
            // Send actual File objects, not base64 previews
            onCapture({ front: frontImage, back: backImage });
        }
    };

    const bothSelected = frontImage && backImage;

    return (
        <div className={styles.overlay}>
            <div className={styles.overlayContent} style={{
                maxWidth: '900px',
                width: '90%',
                maxHeight: '90vh',
                overflowY: 'auto',
                padding: '40px'
            }}>
                <button className={styles.closeBtn} onClick={onClose}>
                    <X size={24} />
                </button>

                <h2 style={{
                    color: 'white',
                    marginBottom: '30px',
                    textAlign: 'center',
                    fontSize: '1.8rem',
                    fontWeight: '600'
                }}>
                    Upload CNIC (Front and Back)
                </h2>

                <div style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
                    gap: '30px',
                    width: '100%',
                    marginBottom: '30px'
                }}>
                    {/* Front Image Upload */}
                    <div style={{ width: '100%' }}>
                        <h3 style={{
                            display: 'flex',
                            alignItems: 'center',
                            color: '#10b981',
                            fontSize: '1.1rem',
                            fontWeight: '600',
                            marginBottom: '15px'
                        }}>
                            <FileImage size={22} style={{ marginRight: '10px' }} />
                            CNIC Front
                        </h3>

                        {!frontPreview ? (
                            <div
                                onClick={() => frontInputRef.current?.click()}
                                style={{
                                    display: 'flex',
                                    flexDirection: 'column',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    padding: '50px 30px',
                                    background: 'linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(5, 150, 105, 0.05) 100%)',
                                    border: '3px dashed #10b981',
                                    borderRadius: '16px',
                                    cursor: 'pointer',
                                    minHeight: '220px',
                                    transition: 'all 0.3s ease'
                                }}
                                onMouseEnter={(e) => {
                                    e.currentTarget.style.background = 'linear-gradient(135deg, rgba(16, 185, 129, 0.2) 0%, rgba(5, 150, 105, 0.1) 100%)';
                                    e.currentTarget.style.borderColor = '#34d399';
                                    e.currentTarget.style.transform = 'scale(1.02)';
                                }}
                                onMouseLeave={(e) => {
                                    e.currentTarget.style.background = 'linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(5, 150, 105, 0.05) 100%)';
                                    e.currentTarget.style.borderColor = '#10b981';
                                    e.currentTarget.style.transform = 'scale(1)';
                                }}
                            >
                                <Upload size={56} style={{ color: '#10b981', marginBottom: '16px' }} />
                                <p style={{ color: 'white', fontSize: '1.1rem', marginBottom: '8px', fontWeight: '500' }}>
                                    Click to upload front image
                                </p>
                                <span style={{ color: 'rgba(255, 255, 255, 0.6)', fontSize: '0.9rem' }}>
                                    JPG, PNG (Max 10MB)
                                </span>
                                <input
                                    ref={frontInputRef}
                                    type="file"
                                    accept="image/jpeg,image/jpg,image/png"
                                    onChange={handleFrontChange}
                                    style={{ display: 'none' }}
                                />
                            </div>
                        ) : (
                            <div style={{ position: 'relative', width: '100%' }}>
                                <img
                                    src={frontPreview}
                                    alt="CNIC Front"
                                    style={{
                                        width: '100%',
                                        borderRadius: '12px',
                                        border: '3px solid #10b981',
                                        boxShadow: '0 4px 20px rgba(16, 185, 129, 0.3)'
                                    }}
                                />
                                <button
                                    onClick={() => {
                                        setFrontImage(null);
                                        setFrontPreview(null);
                                        if (frontInputRef.current) frontInputRef.current.value = '';
                                    }}
                                    style={{
                                        display: 'flex',
                                        alignItems: 'center',
                                        gap: '8px',
                                        padding: '12px 20px',
                                        background: '#10b981',
                                        color: 'white',
                                        border: 'none',
                                        borderRadius: '8px',
                                        cursor: 'pointer',
                                        fontSize: '1rem',
                                        fontWeight: '500',
                                        margin: '16px auto 0',
                                        transition: 'all 0.2s',
                                        boxShadow: '0 2px 10px rgba(16, 185, 129, 0.3)'
                                    }}
                                    onMouseEnter={(e) => {
                                        e.currentTarget.style.background = '#059669';
                                        e.currentTarget.style.transform = 'translateY(-2px)';
                                    }}
                                    onMouseLeave={(e) => {
                                        e.currentTarget.style.background = '#10b981';
                                        e.currentTarget.style.transform = 'translateY(0)';
                                    }}
                                >
                                    <RefreshCw size={18} />
                                    Change
                                </button>
                            </div>
                        )}
                    </div>

                    {/* Back Image Upload */}
                    <div style={{ width: '100%' }}>
                        <h3 style={{
                            display: 'flex',
                            alignItems: 'center',
                            color: '#3b82f6',
                            fontSize: '1.1rem',
                            fontWeight: '600',
                            marginBottom: '15px'
                        }}>
                            <FileImage size={22} style={{ marginRight: '10px' }} />
                            CNIC Back
                        </h3>

                        {!backPreview ? (
                            <div
                                onClick={() => backInputRef.current?.click()}
                                style={{
                                    display: 'flex',
                                    flexDirection: 'column',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    padding: '50px 30px',
                                    background: 'linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(37, 99, 235, 0.05) 100%)',
                                    border: '3px dashed #3b82f6',
                                    borderRadius: '16px',
                                    cursor: 'pointer',
                                    minHeight: '220px',
                                    transition: 'all 0.3s ease'
                                }}
                                onMouseEnter={(e) => {
                                    e.currentTarget.style.background = 'linear-gradient(135deg, rgba(59, 130, 246, 0.2) 0%, rgba(37, 99, 235, 0.1) 100%)';
                                    e.currentTarget.style.borderColor = '#60a5fa';
                                    e.currentTarget.style.transform = 'scale(1.02)';
                                }}
                                onMouseLeave={(e) => {
                                    e.currentTarget.style.background = 'linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(37, 99, 235, 0.05) 100%)';
                                    e.currentTarget.style.borderColor = '#3b82f6';
                                    e.currentTarget.style.transform = 'scale(1)';
                                }}
                            >
                                <Upload size={56} style={{ color: '#3b82f6', marginBottom: '16px' }} />
                                <p style={{ color: 'white', fontSize: '1.1rem', marginBottom: '8px', fontWeight: '500' }}>
                                    Click to upload back image
                                </p>
                                <span style={{ color: 'rgba(255, 255, 255, 0.6)', fontSize: '0.9rem' }}>
                                    JPG, PNG (Max 10MB)
                                </span>
                                <input
                                    ref={backInputRef}
                                    type="file"
                                    accept="image/jpeg,image/jpg,image/png"
                                    onChange={handleBackChange}
                                    style={{ display: 'none' }}
                                />
                            </div>
                        ) : (
                            <div style={{ position: 'relative', width: '100%' }}>
                                <img
                                    src={backPreview}
                                    alt="CNIC Back"
                                    style={{
                                        width: '100%',
                                        borderRadius: '12px',
                                        border: '3px solid #3b82f6',
                                        boxShadow: '0 4px 20px rgba(59, 130, 246, 0.3)'
                                    }}
                                />
                                <button
                                    onClick={() => {
                                        setBackImage(null);
                                        setBackPreview(null);
                                        if (backInputRef.current) backInputRef.current.value = '';
                                    }}
                                    style={{
                                        display: 'flex',
                                        alignItems: 'center',
                                        gap: '8px',
                                        padding: '12px 20px',
                                        background: '#3b82f6',
                                        color: 'white',
                                        border: 'none',
                                        borderRadius: '8px',
                                        cursor: 'pointer',
                                        fontSize: '1rem',
                                        fontWeight: '500',
                                        margin: '16px auto 0',
                                        transition: 'all 0.2s',
                                        boxShadow: '0 2px 10px rgba(59, 130, 246, 0.3)'
                                    }}
                                    onMouseEnter={(e) => {
                                        e.currentTarget.style.background = '#2563eb';
                                        e.currentTarget.style.transform = 'translateY(-2px)';
                                    }}
                                    onMouseLeave={(e) => {
                                        e.currentTarget.style.background = '#3b82f6';
                                        e.currentTarget.style.transform = 'translateY(0)';
                                    }}
                                >
                                    <RefreshCw size={18} />
                                    Change
                                </button>
                            </div>
                        )}
                    </div>
                </div>

                <button
                    onClick={handleConfirm}
                    disabled={!bothSelected}
                    style={{
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        gap: '12px',
                        width: '100%',
                        padding: '18px 32px',
                        marginTop: '30px',
                        background: bothSelected
                            ? 'linear-gradient(135deg, #10b981 0%, #059669 100%)'
                            : 'rgba(107, 114, 128, 0.5)',
                        color: 'white',
                        border: 'none',
                        borderRadius: '12px',
                        fontSize: '1.2rem',
                        fontWeight: '600',
                        cursor: bothSelected ? 'pointer' : 'not-allowed',
                        transition: 'all 0.3s',
                        boxShadow: bothSelected ? '0 4px 20px rgba(16, 185, 129, 0.4)' : 'none'
                    }}
                    onMouseEnter={(e) => {
                        if (bothSelected) {
                            e.currentTarget.style.transform = 'translateY(-2px)';
                            e.currentTarget.style.boxShadow = '0 6px 30px rgba(16, 185, 129, 0.5)';
                        }
                    }}
                    onMouseLeave={(e) => {
                        if (bothSelected) {
                            e.currentTarget.style.transform = 'translateY(0)';
                            e.currentTarget.style.boxShadow = '0 4px 20px rgba(16, 185, 129, 0.4)';
                        }
                    }}
                >
                    <CheckCircle size={24} />
                    Confirm & Continue
                </button>
            </div>
        </div>
    );
}
