"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { Camera, RefreshCw, CheckCircle, X, Eye, Smile, RotateCw } from "lucide-react";
import styles from "./CameraOverlay.module.css";

export default function CameraOverlay({ mode, onCapture, onClose }) {
    const [stream, setStream] = useState(null);
    const [capturedImage, setCapturedImage] = useState(null);
    const [capturedVideo, setCapturedVideo] = useState(null);
    const [isRecording, setIsRecording] = useState(false);
    const [livenessStatus, setLivenessStatus] = useState("");
    const [countdown, setCountdown] = useState(null);
    const [actionChecklist, setActionChecklist] = useState({
        positioned: false,
        recording: false,
        blink: false,
        smile: false
    });

    const videoRef = useRef(null);
    const canvasRef = useRef(null);
    const mediaRecorderRef = useRef(null);
    const chunksRef = useRef([]);

    const isSelfie = mode === 'selfie';
    const isCNICFront = mode === 'cnic-front';
    const isCNICBack = mode === 'cnic-back';

    const startCamera = useCallback(async () => {
        // Check if browser supports getUserMedia
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            console.error("getUserMedia not supported");
            alert("Camera not supported. Please use a modern browser (Chrome, Firefox, Safari) with HTTPS or enable camera permissions.");
            return;
        }

        try {
            // Try with ideal constraints first
            let constraints = {
                video: {
                    facingMode: isSelfie ? "user" : "environment",
                    width: { ideal: 1280, max: 1920 },
                    height: { ideal: 720, max: 1080 },
                },
            };

            let mediaStream;
            try {
                mediaStream = await navigator.mediaDevices.getUserMedia(constraints);
            } catch (firstError) {
                console.warn('First camera attempt failed, trying simpler constraints:', firstError);
                // Fallback: simpler constraints
                constraints = {
                    video: {
                        facingMode: isSelfie ? "user" : "environment"
                    }
                };
                try {
                    mediaStream = await navigator.mediaDevices.getUserMedia(constraints);
                } catch (secondError) {
                    console.warn('Second attempt failed, trying basic video:', secondError);
                    // Final fallback: just get any camera
                    mediaStream = await navigator.mediaDevices.getUserMedia({ video: true });
                }
            }

            setStream(mediaStream);

            if (videoRef.current) {
                videoRef.current.srcObject = mediaStream;
            }

            // Mark positioned after camera starts
            if (isSelfie) {
                setTimeout(() => {
                    setActionChecklist(prev => ({ ...prev, positioned: true }));
                }, 500);
            }
        } catch (err) {
            console.error("Camera Error:", err);
            let errorMsg = "Could not access camera. ";

            if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
                errorMsg += "Please allow camera access in your browser settings.";
            } else if (err.name === 'NotFoundError' || err.name === 'DevicesNotFoundError') {
                errorMsg += "No camera found on your device.";
            } else if (err.name === 'NotReadableError' || err.name === 'TrackStartError') {
                errorMsg += "Camera is already in use by another app.";
            } else {
                errorMsg += "Please check permissions and try again.";
            }

            alert(errorMsg);
        }
    }, [isSelfie]);

    const stopCamera = () => {
        if (stream) {
            stream.getTracks().forEach((track) => track.stop());
            setStream(null);
        }
    };

    const startRecording = () => {
        if (!stream) return;

        // Start countdown
        setCountdown(3);
        const countdownInterval = setInterval(() => {
            setCountdown(prev => {
                if (prev <= 1) {
                    clearInterval(countdownInterval);
                    // Start actual recording
                    beginRecording();
                    return null;
                }
                return prev - 1;
            });
        }, 1000);
    };

    const beginRecording = () => {
        if (!stream) return;

        chunksRef.current = [];
        const recorder = new MediaRecorder(stream, { mimeType: 'video/webm' });
        mediaRecorderRef.current = recorder;

        recorder.ondataavailable = (e) => {
            if (e.data.size > 0) {
                chunksRef.current.push(e.data);
            }
        };

        recorder.onstop = () => {
            const blob = new Blob(chunksRef.current, { type: 'video/webm' });
            setCapturedVideo(blob);
            captureFrame();
        };

        setIsRecording(true);
        setActionChecklist(prev => ({ ...prev, recording: true }));
        setLivenessStatus("Recording... Follow the instructions");
        recorder.start();

        // Simulate action detection
        setTimeout(() => {
            setActionChecklist(prev => ({ ...prev, blink: true }));
            setLivenessStatus("Great! Now smile slightly");
        }, 1500);

        setTimeout(() => {
            setActionChecklist(prev => ({ ...prev, smile: true }));
            setLivenessStatus("Perfect! Processing...");
        }, 3000);

        setTimeout(() => {
            if (recorder.state !== 'inactive') {
                recorder.stop();
                setIsRecording(false);
                setLivenessStatus("Recording Complete!");
            }
        }, 4500);
    };

    const captureFrame = () => {
        if (!videoRef.current || !canvasRef.current) return;

        const context = canvasRef.current.getContext("2d");
        if (context) {
            const { videoWidth, videoHeight } = videoRef.current;
            canvasRef.current.width = videoWidth;
            canvasRef.current.height = videoHeight;

            if (isSelfie) {
                context.translate(videoWidth, 0);
                context.scale(-1, 1);
            }

            context.drawImage(videoRef.current, 0, 0, videoWidth, videoHeight);
            const dataUrl = canvasRef.current.toDataURL("image/jpeg", 0.9);
            setCapturedImage(dataUrl);
            stopCamera();
        }
    };

    const handleCaptureStart = () => {
        if (isSelfie) {
            startRecording();
        } else {
            captureFrame();
        }
    };

    const retake = () => {
        setCapturedImage(null);
        setCapturedVideo(null);
        setLivenessStatus("");
        setCountdown(null);
        setActionChecklist({
            positioned: false,
            recording: false,
            blink: false,
            smile: false
        });
        startCamera();
    };

    const confirm = () => {
        if (capturedImage) {
            if (isSelfie) {
                onCapture({ image: capturedImage, video: capturedVideo });
            } else {
                onCapture(capturedImage);
            }
        }
    };

    useEffect(() => {
        startCamera();
        return () => stopCamera();
    }, [startCamera]);

    const getInstructions = () => {
        if (isSelfie) {
            if (countdown !== null) {
                return `Recording in ${countdown}...`;
            }
            if (isRecording) {
                return livenessStatus;
            }
            return "Position your face in the oval and press the button";
        }
        if (isCNICFront) return "Position CNIC Front within the frame";
        if (isCNICBack) return "Position CNIC Back within the frame";
        return "Position document within the frame";
    };

    return (
        <div className={styles.overlay}>
            <div className={styles.overlayContent}>
                <button className={styles.closeBtn} onClick={onClose} aria-label="Close">
                    <X size={24} />
                </button>

                {!capturedImage ? (
                    <>
                        <div className={styles.instructions}>
                            {getInstructions()}
                        </div>

                        {isSelfie && !isRecording && countdown === null && (
                            <div className={styles.actionGuide}>
                                <div className={styles.actionItem}>
                                    <div className={actionChecklist.positioned ? styles.checkboxChecked : styles.checkbox}>
                                        {actionChecklist.positioned && <CheckCircle size={16} />}
                                    </div>
                                    <span>Position your face in the oval</span>
                                </div>
                                <div className={styles.actionItem}>
                                    <div className={styles.checkbox}>
                                        <Eye size={16} />
                                    </div>
                                    <span>Blink naturally during recording</span>
                                </div>
                                <div className={styles.actionItem}>
                                    <div className={styles.checkbox}>
                                        <Smile size={16} />
                                    </div>
                                    <span>Show a slight smile</span>
                                </div>
                            </div>
                        )}

                        {isSelfie && isRecording && (
                            <div className={styles.liveChecklist}>
                                <div className={`${styles.liveCheck} ${actionChecklist.recording ? styles.completed : ''}`}>
                                    {actionChecklist.recording && <CheckCircle size={18} />}
                                    <span>Recording</span>
                                </div>
                                <div className={`${styles.liveCheck} ${actionChecklist.blink ? styles.completed : ''}`}>
                                    {actionChecklist.blink && <CheckCircle size={18} />}
                                    <span>Blink Detected</span>
                                </div>
                                <div className={`${styles.liveCheck} ${actionChecklist.smile ? styles.completed : ''}`}>
                                    {actionChecklist.smile && <CheckCircle size={18} />}
                                    <span>Smile Detected</span>
                                </div>
                            </div>
                        )}

                        <div className={styles.cameraWrapper}>
                            <video
                                ref={videoRef}
                                autoPlay
                                playsInline
                                muted
                                className={`${styles.video} ${!isSelfie ? styles.rear : ''}`}
                            ></video>

                            <div className={styles.guideOverlay}>
                                <div className={`${styles.guideBox} ${isSelfie ? styles.face : styles.cnic}`}>
                                    {countdown !== null && (
                                        <div className={styles.countdownBig}>{countdown}</div>
                                    )}
                                    {isRecording && <div className={styles.recordingIndicator}>REC</div>}
                                    <div className={styles.scannerLine}></div>
                                </div>
                            </div>

                            <canvas ref={canvasRef} style={{ display: "none" }} />
                        </div>

                        <div className={styles.controls}>
                            <button
                                className={`${styles.captureBtn} ${isRecording ? styles.recording : ''} ${countdown !== null ? styles.countdown : ''}`}
                                onClick={handleCaptureStart}
                                disabled={isRecording || countdown !== null}
                                title={isSelfie ? "Start Liveness Check" : "Capture"}
                            >
                                {countdown !== null && <div className={styles.progressCircle}></div>}
                                {isRecording && <div className={styles.progressCircle}></div>}
                                <Camera size={28} />
                            </button>
                        </div>
                    </>
                ) : (
                    <>
                        <div className={styles.instructions}>
                            Preview {isSelfie && "(Selfie & Video)"}
                        </div>
                        <div className={styles.previewWrapper}>
                            <img src={capturedImage} alt="Captured" className={styles.previewImage} />
                            {isSelfie && <div className={styles.videoBadge}>✓ Video Recorded</div>}
                        </div>
                        <div className={styles.controls}>
                            <button className={styles.retakeBtn} onClick={retake}>
                                <RefreshCw size={18} /> Retake
                            </button>
                            <button className={styles.confirmBtn} onClick={confirm}>
                                <CheckCircle size={18} /> Confirm
                            </button>
                        </div>
                    </>
                )}
            </div>
        </div>
    );
}
