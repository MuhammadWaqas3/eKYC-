"use client";

import { useState, useRef, useEffect } from "react";
import { Camera, CheckCircle, X, RefreshCw, FlipHorizontal } from "lucide-react";
import styles from "./FingerprintOverlay.module.css";

export default function FingerprintOverlay({ onCapture, onClose }) {
    const [capturedImage, setCapturedImage] = useState(null);
    const [isCameraActive, setIsCameraActive] = useState(false);
    const [error, setError] = useState(null);
    const [facingMode, setFacingMode] = useState('user');

    const videoRef = useRef(null);
    const canvasRef = useRef(null);
    const streamRef = useRef(null);

    // Start camera when component mounts
    useEffect(() => {
        if (!capturedImage) {
            startCamera();
        }
        return () => {
            stopCamera();
        };
    }, [facingMode]);

    const startCamera = async () => {
        // Check browser support
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            setIsCameraActive(false);
            setError('Camera not supported. Please use a modern browser with camera access enabled.');
            return;
        }

        try {
            setError(null);
            setIsCameraActive(true);

            if (streamRef.current) {
                streamRef.current.getTracks().forEach(track => track.stop());
            }

            // Try with full constraints first
            let constraints = {
                video: {
                    facingMode: facingMode,
                    width: { ideal: 1920, max: 1920 },
                    height: { ideal: 1080, max: 1080 }
                }
            };

            let stream;
            try {
                stream = await navigator.mediaDevices.getUserMedia(constraints);
            } catch (firstError) {
                console.warn('Camera attempt 1 failed, trying simpler constraints:', firstError);
                // Fallback to simpler constraints
                constraints = {
                    video: { facingMode: facingMode }
                };
                try {
                    stream = await navigator.mediaDevices.getUserMedia(constraints);
                } catch (secondError) {
                    console.warn('Camera attempt 2 failed, trying basic video:', secondError);
                    // Final fallback
                    stream = await navigator.mediaDevices.getUserMedia({ video: true });
                }
            }

            streamRef.current = stream;

            setTimeout(() => {
                if (videoRef.current) {
                    videoRef.current.srcObject = stream;
                }
            }, 100);

        } catch (err) {
            console.error('Camera access error:', err);
            setIsCameraActive(false);

            let errorMessage = 'Could not access camera. ';
            if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
                errorMessage += 'Please allow camera permissions in your browser.';
            } else if (err.name === 'NotFoundError') {
                errorMessage += 'No camera found on your device.';
            } else if (err.name === 'NotReadableError') {
                errorMessage += 'Camera is in use by another app.';
            } else {
                errorMessage += 'Please check permissions and try again.';
            }

            setError(errorMessage);
        }
    };

    const stopCamera = () => {
        if (streamRef.current) {
            streamRef.current.getTracks().forEach(track => track.stop());
            streamRef.current = null;
        }
        setIsCameraActive(false);
    };

    const captureImage = () => {
        if (!videoRef.current || !canvasRef.current) return;

        const video = videoRef.current;
        const canvas = canvasRef.current;

        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;

        const ctx = canvas.getContext('2d');
        ctx.drawImage(video, 0, 0);

        canvas.toBlob((blob) => {
            const file = new File([blob], 'fingerprint.jpg', { type: 'image/jpeg' });
            setCapturedImage(file);
            stopCamera();
        }, 'image/jpeg', 0.95);
    };

    const retakeImage = () => {
        setCapturedImage(null);
        startCamera();
    };

    const handleConfirm = () => {
        if (capturedImage) {
            onCapture(capturedImage);
        }
    };

    return (
        <div className={styles.overlay}>
            <div className={styles.overlayContent}>
                <button className={styles.closeBtn} onClick={onClose}>
                    <X size={24} />
                </button>

                <h2 className={styles.title}>
                    {capturedImage ? '✅ Review Fingerprint Image' : '📸 Capture Fingerprint'}
                </h2>

                <p className={styles.subtitle}>
                    {capturedImage
                        ? 'Check the image before submitting'
                        : 'Place your finger in view and capture'
                    }
                </p>

                {error && (
                    <div className={styles.error}>
                        ⚠️ {error}
                    </div>
                )}

                {/* Camera View */}
                {!capturedImage && (
                    <div className={styles.cameraContainer}>
                        {isCameraActive ? (
                            <div className={styles.videoWrapper}>
                                <video
                                    ref={videoRef}
                                    autoPlay
                                    playsInline
                                    muted
                                    className={styles.video}
                                    style={{
                                        transform: facingMode === 'user' ? 'scaleX(-1)' : 'none'
                                    }}
                                />

                                <button
                                    onClick={() => setFacingMode(prev => prev === 'user' ? 'environment' : 'user')}
                                    className={styles.flipBtn}
                                >
                                    <FlipHorizontal size={24} />
                                </button>

                                <div className={styles.guidanceBox}>
                                    <div className={styles.guidanceLabel}>
                                        FINGERPRINT
                                    </div>
                                </div>
                            </div>
                        ) : (
                            <div className={styles.cameraPlaceholder}>
                                <Camera size={48} style={{ opacity: 0.5, marginBottom: '20px' }} />
                                <p style={{ color: 'rgba(255, 255, 255, 0.6)' }}>
                                    Camera not active. Please allow camera access.
                                </p>
                            </div>
                        )}

                        {/* Capture Button */}
                        {isCameraActive && (
                            <button
                                onClick={captureImage}
                                className={styles.captureBtn}
                            >
                                <Camera size={28} />
                                Capture Fingerprint
                            </button>
                        )}
                    </div>
                )}

                {/* Preview captured image */}
                {capturedImage && (
                    <div className={styles.previewContainer}>
                        <div className={styles.previewWrapper}>
                            <img
                                src={URL.createObjectURL(capturedImage)}
                                alt="Fingerprint"
                                className={styles.previewImage}
                            />
                            <button
                                onClick={retakeImage}
                                className={styles.retakeBtn}
                            >
                                <RefreshCw size={16} />
                                Retake
                            </button>
                        </div>
                    </div>
                )}

                {/* Confirm Button */}
                {capturedImage && (
                    <button
                        onClick={handleConfirm}
                        className={styles.confirmBtn}
                    >
                        <CheckCircle size={24} />
                        Confirm & Continue
                    </button>
                )}

                {/* Hidden canvas for image capture */}
                <canvas ref={canvasRef} style={{ display: 'none' }} />
            </div>
        </div>
    );
}
