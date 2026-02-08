"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { Camera, RefreshCw, CheckCircle, X } from "lucide-react";
import styles from "./CameraOverlay.module.css";

export default function CameraOverlay({ mode, onCapture, onClose }) {
    const [stream, setStream] = useState(null);
    const [capturedImage, setCapturedImage] = useState(null);
    const [capturedVideo, setCapturedVideo] = useState(null);
    const [isRecording, setIsRecording] = useState(false);
    const [livenessStatus, setLivenessStatus] = useState("");

    const videoRef = useRef(null);
    const canvasRef = useRef(null);
    const mediaRecorderRef = useRef(null);
    const chunksRef = useRef([]);

    const isSelfie = mode === 'selfie';
    const isCNICFront = mode === 'cnic-front';
    const isCNICBack = mode === 'cnic-back';

    const startCamera = useCallback(async () => {
        try {
            const constraints = {
                video: {
                    facingMode: isSelfie ? "user" : "environment",
                    width: { ideal: 1280 },
                    height: { ideal: 720 },
                },
            };

            const mediaStream = await navigator.mediaDevices.getUserMedia(constraints);
            setStream(mediaStream);

            if (videoRef.current) {
                videoRef.current.srcObject = mediaStream;
            }
        } catch (err) {
            console.error("Camera Error:", err);
            alert("Could not access camera. Please allow permissions.");
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
        setLivenessStatus("Recording... Please blink and move your head slightly.");
        recorder.start();

        setTimeout(() => {
            if (recorder.state !== 'inactive') {
                recorder.stop();
                setIsRecording(false);
                setLivenessStatus("Recording Captured!");
            }
        }, 4000);
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
            return isRecording ? livenessStatus : "Position your face and press record for liveness check";
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
                                    {isRecording && <div className={styles.recordingIndicator}>REC</div>}
                                    <div className={styles.scannerLine}></div>
                                </div>
                            </div>

                            <canvas ref={canvasRef} style={{ display: "none" }} />
                        </div>

                        <div className={styles.controls}>
                            <button
                                className={`${styles.captureBtn} ${isRecording ? styles.recording : ''}`}
                                onClick={handleCaptureStart}
                                disabled={isRecording}
                                title={isSelfie ? "Record Liveness" : "Capture"}
                            >
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
