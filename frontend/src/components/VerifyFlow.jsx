"use client";

import { useState, useEffect } from "react";
import axios from "axios";
import styles from "./VerifyFlow.module.css";
import BiometricCapture from "./BiometricCapture";
import CNICUpload from "./CNICUpload";
import FingerprintScanner from "./FingerprintScanner";
import { ShieldCheck, CheckCircle, ArrowRight, AlertTriangle, Loader2 } from "lucide-react";

const API_BASE = "http://localhost:8000/api/verify";

export default function VerifyFlow({ token }) {
    const [step, setStep] = useState(0);
    const [data, setData] = useState({
        cnicFront: null,
        cnicBack: null,
        selfie: null,
        livenessVideo: null,
        fingerprint: false,
    });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const [extractedData, setExtractedData] = useState(null);

    // Helper to convert DataURL to Blob
    const dataURLtoBlob = (dataurl) => {
        const arr = dataurl.split(',');
        const mime = arr[0].match(/:(.*?);/)[1];
        const bstr = atob(arr[1]);
        let n = bstr.length;
        const u8arr = new Uint8Array(n);
        while (n--) {
            u8arr[n] = bstr.charCodeAt(n);
        }
        return new Blob([u8arr], { type: mime });
    };

    const handleCNICCapture = async (front, back) => {
        setLoading(true);
        setError("");
        try {
            const formData = new FormData();
            formData.append("token", token);
            formData.append("front_image", dataURLtoBlob(front), "front.jpg");
            formData.append("back_image", dataURLtoBlob(back), "back.jpg");

            const response = await axios.post(`${API_BASE}/upload-cnic?token=${token}`, formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });

            if (response.data.success && response.data.extracted_data) {
                setExtractedData(response.data.extracted_data);
                setStep(2); // Move to Selfie step
            } else {
                // If success is true but no data, it's a validation error
                const msg = response.data.message || (response.data.validation_errors?.join(", ")) || "CNIC verification failed.";
                setError(msg);
                setStep(1); // Reset to CNIC upload so they can retake
            }
        } catch (e) {
            console.error(e);
            setError(e.response?.data?.detail || "Error uploading CNIC. Please try again.");
            setStep(1); // Reset on error
        } finally {
            setLoading(false);
        }
    };

    const handleSelfieCapture = async (selfieData) => {
        setLoading(true);
        setError("");
        try {
            // 1. Upload Selfie for Face Matching
            const selfieFormData = new FormData();
            selfieFormData.append("token", token);
            selfieFormData.append("selfie_image", dataURLtoBlob(selfieData.image), "selfie.jpg");

            const faceResponse = await axios.post(`${API_BASE}/upload-selfie?token=${token}`, selfieFormData);

            if (!faceResponse.data.is_match) {
                setError("Face match failed. Please ensure the selfie matches your CNIC.");
                setLoading(false);
                return;
            }

            // 2. Upload Video for Liveness Check
            if (selfieData.video) {
                const livenessFormData = new FormData();
                livenessFormData.append("token", token);
                livenessFormData.append("liveness_video", selfieData.video, "liveness.webm");

                await axios.post(`${API_BASE}/liveness-check?token=${token}`, livenessFormData);
            }

            setStep(3); // Move to Fingerprint
        } catch (e) {
            console.error(e);
            setError(e.response?.data?.detail || "Verification failed. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    const finalize = async () => {
        setLoading(true);
        setError("");
        try {
            const response = await axios.post(`${API_BASE}/finalize?token=${token}`);
            if (response.data.success) {
                setStep(5); // Success
            }
        } catch (e) {
            console.error(e);
            setError("Finalization failed.");
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className={styles.container}>
                <div className={styles.processing}>
                    <Loader2 className={styles.spinner} />
                    <p>AI processing in progress... This may take a moment.</p>
                </div>
            </div>
        );
    }

    return (
        <div className={styles.container}>
            <header className={styles.header}>
                <ShieldCheck className={styles.icon} size={32} />
                <h1>Identity Verification</h1>
            </header>

            <div className={styles.content}>
                {error && (
                    <div className={styles.errorBox}>
                        <AlertTriangle size={20} />
                        <p>{error}</p>
                        <button onClick={() => setError("")}>Dismiss</button>
                    </div>
                )}

                {step === 0 && (
                    <div className={styles.intro}>
                        <p>Welcome. To secure your account, we need to verify your identity using AI-powered biometrics.</p>
                        <ul className={styles.list}>
                            <li>Scan your CNIC (Front & Back)</li>
                            <li>Take a Live Selfie with blink detection</li>
                            <li>Fingerprint Verification</li>
                        </ul>
                        <button className="btn" onClick={() => setStep(1)}>
                            Start Verification <ArrowRight size={18} style={{ marginLeft: 8 }} />
                        </button>
                    </div>
                )}

                {step === 1 && (
                    <CNICUpload
                        onCapture={(frontImg, backImg) => {
                            handleCNICCapture(frontImg, backImg);
                        }}
                    />
                )}

                {step === 2 && (
                    <BiometricCapture
                        mode="selfie"
                        onCapture={(selfieData) => {
                            handleSelfieCapture(selfieData);
                        }}
                    />
                )}

                {step === 3 && (
                    <div className={styles.stepContainer}>
                        <h2>Fingerprint Verification</h2>
                        <p>Place your thumb on the scanner. (Simulated for this demo)</p>
                        <button className="btn" onClick={() => finalize()}>
                            Complete Verification
                        </button>
                    </div>
                )}

                {step === 5 && (
                    <div className={styles.success}>
                        <CheckCircle size={64} className={styles.successIcon} />
                        <h2>Verification Successful!</h2>
                        <p>Your account has been officially opened and high-security checks passed.</p>
                        <p className={styles.note}>You can now close this window and return to the chat.</p>
                    </div>
                )}
            </div>

            <div className={styles.progress}>
                <div className={styles.progressBar} style={{ width: `${(step / 5) * 100}%` }}></div>
            </div>
        </div>
    );
}
