"use client";

import { useState } from "react";
import { Fingerprint, CheckCircle, Loader2 } from "lucide-react";
import styles from "./FingerprintOverlay.module.css";
import FingerprintScanner from "./FingerprintScanner";

export default function FingerprintOverlay({ onCapture, onClose }) {
    const [isScanning, setIsScanning] = useState(false);
    const [scanComplete, setScanComplete] = useState(false);

    const handleScan = (data) => {
        setIsScanning(false);
        setScanComplete(true);

        // Wait a moment to show success, then call onCapture
        setTimeout(() => {
            onCapture(data);
        }, 1500);
    };

    const startScan = () => {
        setIsScanning(true);
    };

    return (
        <div className={styles.overlay}>
            <div className={styles.overlayContent}>
                <div className={styles.header}>
                    <h2 className={styles.title}>Fingerprint Verification</h2>
                    <p className={styles.subtitle}>
                        {!isScanning && !scanComplete && "Place your finger on the scanner"}
                        {isScanning && "Scanning in progress..."}
                        {scanComplete && "Fingerprint captured successfully!"}
                    </p>
                </div>

                <div className={styles.scannerArea}>
                    {!isScanning && !scanComplete && (
                        <div className={styles.fingerprintIcon}>
                            <Fingerprint size={120} />
                        </div>
                    )}

                    {isScanning && (
                        <FingerprintScanner onScanComplete={handleScan} />
                    )}

                    {scanComplete && (
                        <div className={styles.successIcon}>
                            <CheckCircle size={120} />
                        </div>
                    )}
                </div>

                {!isScanning && !scanComplete && (
                    <div className={styles.controls}>
                        <button className={styles.cancelBtn} onClick={onClose}>
                            Cancel
                        </button>
                        <button className={styles.startBtn} onClick={startScan}>
                            Start Scan
                        </button>
                    </div>
                )}

                {isScanning && (
                    <div className={styles.scanningText}>
                        <Loader2 className={styles.spinner} size={24} />
                        Capturing fingerprint data...
                    </div>
                )}
            </div>
        </div>
    );
}
