// "use client";

// import { useState, useRef, useEffect } from "react";
// import { Camera, CheckCircle, X, RefreshCw, FlipHorizontal } from "lucide-react";
// import styles from "./CameraOverlay.module.css";

// export default function CNICCameraOverlay({ onCapture, onClose }) {
//     const [step, setStep] = useState("front"); // front/back
//     const [frontImage, setFrontImage] = useState(null);
//     const [backImage, setBackImage] = useState(null);
//     const [isCameraActive, setIsCameraActive] = useState(false);
//     const [error, setError] = useState(null);
//     const [facingMode, setFacingMode] = useState("user");

//     const videoRef = useRef(null);
//     const canvasRef = useRef(null);
//     const streamRef = useRef(null);

//     // Start camera safely
//     useEffect(() => {
//         if (typeof window === "undefined") return; // SSR safety

//         if (!frontImage || !backImage) {
//             const id = setTimeout(() => startCamera(), 100); // ensure videoRef mounted
//             return () => clearTimeout(id);
//         }
//     }, [facingMode, frontImage, backImage]);

//     // Stop camera on unmount
//     useEffect(() => {
//         return () => stopCamera();
//     }, []);

//     const startCamera = async () => {
//         if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
//             setError("Camera not supported on this device/browser.");
//             return;
//         }

//         try {
//             setError(null);
//             setIsCameraActive(true);

//             // Stop previous stream
//             if (streamRef.current) {
//                 streamRef.current.getTracks().forEach((track) => track.stop());
//             }

//             const stream = await navigator.mediaDevices.getUserMedia({
//                 video: { facingMode, width: { ideal: 1920 }, height: { ideal: 1080 } },
//             });

//             streamRef.current = stream;

//             if (videoRef.current) {
//                 videoRef.current.srcObject = stream;
//             } else {
//                 console.warn("Video element not ready yet");
//             }
//         } catch (err) {
//             console.error("Camera access error:", err);
//             setIsCameraActive(false);
//             setError('Could not access camera. Please use "Upload File" instead.');
//         }
//     };

//     const stopCamera = () => {
//         if (streamRef.current) {
//             streamRef.current.getTracks().forEach((track) => track.stop());
//             streamRef.current = null;
//         }
//         setIsCameraActive(false);
//     };

//     const captureImage = () => {
//         if (!videoRef.current || !canvasRef.current) return;

//         const video = videoRef.current;
//         const canvas = canvasRef.current;

//         canvas.width = video.videoWidth;
//         canvas.height = video.videoHeight;

//         const ctx = canvas.getContext("2d");
//         ctx.drawImage(video, 0, 0);

//         canvas.toBlob((blob) => {
//             if (!blob) return;
//             const file = new File([blob], `cnic_${step}.jpg`, { type: "image/jpeg" });
//             processFile(file);
//         }, "image/jpeg", 0.95);
//     };

//     const handleFileUpload = (e) => {
//         const file = e.target.files[0];
//         if (file) processFile(file);
//     };

//     const processFile = (file) => {
//         if (step === "front") {
//             setFrontImage(file);
//             setStep("back");
//             startCamera(); // reset for back
//         } else {
//             setBackImage(file);
//             stopCamera();
//         }
//     };

//     const retakeImage = (side) => {
//         if (side === "front") {
//             setFrontImage(null);
//             setStep("front");
//         } else {
//             setBackImage(null);
//             setStep("back");
//         }
//         startCamera();
//     };

//     const handleConfirm = () => {
//         if (frontImage && backImage) onCapture({ front: frontImage, back: backImage });
//     };

//     const bothCaptured = frontImage && backImage;

//     return (
//         <div className={styles.overlay}>
//             <div className={styles.overlayContent}>
//                 <button className={styles.closeBtn} onClick={onClose}>
//                     <X size={24} />
//                 </button>

//                 <h2>
//                     {bothCaptured
//                         ? "✅ Review Your CNIC Images"
//                         : `📸 Capture CNIC ${step.toUpperCase()}`}
//                 </h2>

//                 {error && <div className={styles.error}>⚠️ {error}</div>}

//                 {!bothCaptured && (
//                     <div className={styles.cameraWrapper}>
//                         {isCameraActive ? (
//                             <div className={styles.videoContainer}>
//                                 <video
//                                     ref={videoRef}
//                                     autoPlay
//                                     playsInline
//                                     muted
//                                     style={{
//                                         transform: facingMode === "user" ? "scaleX(-1)" : "none",
//                                     }}
//                                 />
//                                 <button
//                                     className={styles.flipBtn}
//                                     onClick={() =>
//                                         setFacingMode((prev) =>
//                                             prev === "user" ? "environment" : "user"
//                                         )
//                                     }
//                                 >
//                                     <FlipHorizontal size={26} />
//                                 </button>
//                             </div>
//                         ) : (
//                             <div className={styles.placeholder}>
//                                 <Camera size={48} />
//                                 <p>Camera not active. Use upload below.</p>
//                             </div>
//                         )}

//                         <button className={styles.captureBtn} onClick={captureImage}>
//                             <Camera size={30} />
//                             Capture {step.toUpperCase()}
//                         </button>

//                         <label className={styles.uploadBtn}>
//                             📁 Upload File Manually
//                             <input type="file" accept="image/*" onChange={handleFileUpload} />
//                         </label>
//                     </div>
//                 )}

//                 {(frontImage || backImage) && (
//                     <div className={styles.previewGrid}>
//                         {frontImage && (
//                             <div>
//                                 <h3>
//                                     <CheckCircle size={22} /> CNIC Front
//                                 </h3>
//                                 <img src={URL.createObjectURL(frontImage)} alt="CNIC Front" />
//                                 <button onClick={() => retakeImage("front")}>
//                                     <RefreshCw size={18} /> Retake
//                                 </button>
//                             </div>
//                         )}
//                         {backImage && (
//                             <div>
//                                 <h3>
//                                     <CheckCircle size={22} /> CNIC Back
//                                 </h3>
//                                 <img src={URL.createObjectURL(backImage)} alt="CNIC Back" />
//                                 <button onClick={() => retakeImage("back")}>
//                                     <RefreshCw size={18} /> Retake
//                                 </button>
//                             </div>
//                         )}
//                     </div>
//                 )}

//                 {bothCaptured && (
//                     <button className={styles.confirmBtn} onClick={handleConfirm}>
//                         <CheckCircle size={26} /> Confirm & Continue
//                     </button>
//                 )}

//                 <canvas ref={canvasRef} style={{ display: "none" }} />
//             </div>
//         </div>
//     );
// }


"use client";

import { useState, useRef, useEffect } from "react";
import { Camera, X, RefreshCw, CheckCircle, FlipHorizontal } from "lucide-react";

export default function CNICCameraOverlay({ onCapture, onClose }) {
    const videoRef = useRef(null);
    const canvasRef = useRef(null);
    const streamRef = useRef(null);

    const [step, setStep] = useState("front"); // front | back
    const [frontImage, setFrontImage] = useState(null);
    const [backImage, setBackImage] = useState(null);

    const [cameraActive, setCameraActive] = useState(false);
    const [facingMode, setFacingMode] = useState("environment");
    const [error, setError] = useState(null);

    // Cleanup on unmount
    useEffect(() => {
        return () => stopCamera();
    }, []);

    const startCamera = async () => {
        if (
            typeof navigator === "undefined" ||
            !navigator.mediaDevices ||
            !navigator.mediaDevices.getUserMedia
        ) {
            setError("Camera not supported on this browser. Please upload image.");
            return;
        }

        try {
            setError(null);

            if (streamRef.current) stopCamera();

            // Try with full constraints first
            let constraints = {
                video: {
                    facingMode: { ideal: facingMode },
                    width: { ideal: 1280, max: 1920 },
                    height: { ideal: 720, max: 1080 }
                }
            };

            let stream;
            try {
                stream = await navigator.mediaDevices.getUserMedia(constraints);
            } catch (firstError) {
                console.warn('Camera attempt 1 failed, trying simpler constraints:', firstError);
                // Fallback to basic facingMode only
                constraints = {
                    video: { facingMode: facingMode }
                };
                try {
                    stream = await navigator.mediaDevices.getUserMedia(constraints);
                } catch (secondError) {
                    console.warn('Camera attempt 2 failed, trying basic video:', secondError);
                    // Final fallback: any camera
                    stream = await navigator.mediaDevices.getUserMedia({ video: true });
                }
            }

            streamRef.current = stream;
            setCameraActive(true);

            setTimeout(() => {
                if (videoRef.current) {
                    videoRef.current.srcObject = stream;
                }
            }, 100);
        } catch (err) {
            console.error("Camera error:", err);
            setCameraActive(false);

            let errorMsg = "Could not access camera. ";
            if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
                errorMsg += "Please allow camera permissions. Use upload instead.";
            } else if (err.name === 'NotFoundError') {
                errorMsg += "No camera found. Use upload instead.";
            } else if (err.name === 'NotReadableError') {
                errorMsg += "Camera in use by another app. Use upload instead.";
            } else {
                errorMsg += "Use upload instead.";
            }

            setError(errorMsg);
        }
    };

    const stopCamera = () => {
        if (streamRef.current) {
            streamRef.current.getTracks().forEach(t => t.stop());
            streamRef.current = null;
        }
        setCameraActive(false);
    };

    const captureImage = () => {
        if (!videoRef.current || !canvasRef.current) return;

        const video = videoRef.current;
        const canvas = canvasRef.current;

        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;

        const ctx = canvas.getContext("2d");
        ctx.drawImage(video, 0, 0);

        canvas.toBlob(blob => {
            const file = new File(
                [blob],
                `cnic_${step}.jpg`,
                { type: "image/jpeg" }
            );

            if (step === "front") {
                setFrontImage(file);
                setStep("back");
            } else {
                setBackImage(file);
                stopCamera();
            }
        }, "image/jpeg", 0.95);
    };

    const handleUpload = e => {
        const file = e.target.files?.[0];
        if (!file) return;

        if (step === "front") {
            setFrontImage(file);
            setStep("back");
        } else {
            setBackImage(file);
        }
    };

    const retake = side => {
        if (side === "front") {
            setFrontImage(null);
            setStep("front");
        } else {
            setBackImage(null);
            setStep("back");
        }
        startCamera();
    };

    const confirmImages = () => {
        if (frontImage && backImage) {
            onCapture({ front: frontImage, back: backImage });
        }
    };

    const bothCaptured = frontImage && backImage;

    return (
        <div style={overlay}>
            <div style={card}>
                <button onClick={onClose} style={closeBtn}>
                    <X />
                </button>

                <h2 style={title}>
                    {bothCaptured
                        ? "Review CNIC Images"
                        : `Capture CNIC ${step.toUpperCase()}`}
                </h2>

                {error && <p style={errorBox}>{error}</p>}

                {!bothCaptured && (
                    <>
                        {!cameraActive && (
                            <button style={primaryBtn} onClick={startCamera}>
                                <Camera /> Open Camera
                            </button>
                        )}

                        {cameraActive && (
                            <>
                                <video
                                    ref={videoRef}
                                    autoPlay
                                    playsInline
                                    muted
                                    style={videoStyle}
                                />

                                <div style={controls}>
                                    <button onClick={captureImage} style={captureBtn}>
                                        Capture {step}
                                    </button>

                                    <button
                                        onClick={() =>
                                            setFacingMode(m =>
                                                m === "user" ? "environment" : "user"
                                            )
                                        }
                                        style={secondaryBtn}
                                    >
                                        <FlipHorizontal />
                                    </button>
                                </div>
                            </>
                        )}

                        <label style={uploadBtn}>
                            Upload Image
                            <input
                                type="file"
                                accept="image/*"
                                onChange={handleUpload}
                                hidden
                            />
                        </label>
                    </>
                )}

                {(frontImage || backImage) && (
                    <div style={previewGrid}>
                        {frontImage && (
                            <Preview
                                label="Front"
                                file={frontImage}
                                onRetake={() => retake("front")}
                            />
                        )}
                        {backImage && (
                            <Preview
                                label="Back"
                                file={backImage}
                                onRetake={() => retake("back")}
                            />
                        )}
                    </div>
                )}

                {bothCaptured && (
                    <button style={confirmBtn} onClick={confirmImages}>
                        <CheckCircle /> Confirm & Continue
                    </button>
                )}

                <canvas ref={canvasRef} style={{ display: "none" }} />
            </div>
        </div>
    );
}

/* ---------- Preview Component ---------- */

function Preview({ label, file, onRetake }) {
    return (
        <div style={{ textAlign: "center" }}>
            <h4>{label}</h4>
            <img
                src={URL.createObjectURL(file)}
                alt={label}
                style={{ width: "100%", borderRadius: 12 }}
            />
            <button onClick={onRetake} style={secondaryBtn}>
                <RefreshCw /> Retake
            </button>
        </div>
    );
}

/* ---------- Styles ---------- */

const overlay = {
    position: "fixed",
    inset: 0,
    background: "rgba(0,0,0,0.85)",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    zIndex: 9999
};

const card = {
    background: "#0f172a",
    padding: 24,
    borderRadius: 16,
    width: "95%",
    maxWidth: 520,
    color: "white",
    position: "relative"
};

const title = { textAlign: "center", marginBottom: 16 };

const closeBtn = {
    position: "absolute",
    top: 12,
    right: 12,
    background: "none",
    border: "none",
    color: "white",
    cursor: "pointer"
};

const errorBox = {
    background: "#7f1d1d",
    padding: 10,
    borderRadius: 8,
    textAlign: "center"
};

const videoStyle = {
    width: "100%",
    borderRadius: 12,
    marginTop: 12
};

const controls = {
    display: "flex",
    gap: 12,
    marginTop: 12
};

const primaryBtn = {
    width: "100%",
    padding: 14,
    fontSize: 16,
    background: "#10b981",
    border: "none",
    borderRadius: 10,
    cursor: "pointer",
    color: "white"
};

const captureBtn = {
    flex: 1,
    padding: 12,
    background: "#3b82f6",
    border: "none",
    borderRadius: 10,
    color: "white"
};

const secondaryBtn = {
    padding: 10,
    background: "#334155",
    border: "none",
    borderRadius: 10,
    color: "white"
};

const uploadBtn = {
    display: "block",
    marginTop: 16,
    textAlign: "center",
    padding: 12,
    borderRadius: 10,
    background: "#1e293b",
    cursor: "pointer"
};

const previewGrid = {
    display: "grid",
    gridTemplateColumns: "1fr 1fr",
    gap: 12,
    marginTop: 16
};

const confirmBtn = {
    width: "100%",
    marginTop: 20,
    padding: 14,
    background: "#22c55e",
    border: "none",
    borderRadius: 12,
    fontSize: 16,
    color: "white"
};
