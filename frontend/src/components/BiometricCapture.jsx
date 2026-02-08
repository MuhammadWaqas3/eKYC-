"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { Camera, RefreshCw, CheckCircle, Smartphone, User, Loader2 } from "lucide-react";
import styles from "./BiometricCapture.module.css";

export default function BiometricCapture({ mode, onCapture }) {
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
            captureFrame(); // Also capture a frame for the selfie image
        };

        setIsRecording(true);
        setLivenessStatus("Recording... Please blink and move your head slightly.");
        recorder.start();

        // Record for 4 seconds
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

    return (
        <div className={styles.container}>
            {!capturedImage ? (
                <>
                    <div className={styles.instructions}>
                        {isSelfie ? (
                            isRecording ? livenessStatus : "Position your face and press record"
                        ) : (
                            mode === 'cnic-front' ? "Scan CNIC Front" : "Scan CNIC Back"
                        )}
                    </div>

                    <div className={styles.cameraWrapper}>
                        <video
                            ref={videoRef}
                            autoPlay
                            playsInline
                            muted
                            className={`${styles.video} ${!isSelfie ? styles.rear : ''}`}
                        ></video>

                        <div className={styles.overlay}>
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
                        </button>
                    </div>
                </>
            ) : (
                <>
                    <div className={styles.instructions}>
                        Preview Capture {isSelfie && " (Selfie & Video)"}
                    </div>
                    <div className={styles.previewWrapper}>
                        <img src={capturedImage} alt="Captured" className={styles.previewImage} />
                        {isSelfie && <div className={styles.videoBadge}>Video Recorded</div>}
                    </div>
                    <div className={styles.controls}>
                        <button className="btn" style={{ background: 'rgba(255,255,255,0.1)', color: 'white' }} onClick={retake}>
                            <RefreshCw size={18} style={{ marginRight: 8 }} /> Retake
                        </button>
                        <button className="btn" onClick={confirm}>
                            <CheckCircle size={18} style={{ marginRight: 8 }} /> Confirm
                        </button>
                    </div>
                </>
            )}
        </div>
    );
}
