"use client";

import { useState, useEffect, useRef } from "react";
import { Fingerprint } from "lucide-react";
import styles from "./FingerprintScanner.module.css";

export default function FingerprintScanner({ onScanComplete }) {
    const [scanning, setScanning] = useState(false);
    const [progress, setProgress] = useState(0);
    const intervalRef = useRef(null);

    const startScan = () => {
        setScanning(true);
        setProgress(0);
        // Vibrate device if possible
        if (typeof navigator !== 'undefined' && navigator.vibrate) {
            navigator.vibrate(50);
        }
    };

    const stopScan = () => {
        setScanning(false);
        setProgress(0);
        if (intervalRef.current) clearInterval(intervalRef.current);
    };

    useEffect(() => {
        if (scanning) {
            intervalRef.current = setInterval(() => {
                setProgress((prev) => {
                    if (prev >= 100) {
                        clearInterval(intervalRef.current);
                        onScanComplete();
                        return 100;
                    }
                    return prev + 2; // ~1500ms to 100% (50 ticks * 30ms approx?) No, 2 per check?
                    // Let's adjust manually
                });
            }, 30);
        }
        return () => {
            if (intervalRef.current) clearInterval(intervalRef.current);
        };
    }, [scanning, onScanComplete]);

    return (
        <div className={styles.container}>
            <div
                className={`${styles.scanner} ${scanning ? styles.active : ''}`}
                onMouseDown={startScan}
                onMouseUp={stopScan}
                onMouseLeave={stopScan}
                onTouchStart={startScan}
                onTouchEnd={stopScan}
            >
                <Fingerprint size={64} className={styles.icon} />
                <svg className={styles.ring} viewBox="0 0 100 100">
                    <circle
                        cx="50" cy="50" r="45"
                        fill="none"
                        stroke="rgba(255,255,255,0.2)"
                        strokeWidth="5"
                    />
                    <circle
                        cx="50" cy="50" r="45"
                        fill="none"
                        stroke="var(--success)"
                        strokeWidth="5"
                        strokeDasharray="283"
                        strokeDashoffset={283 - (2.83 * progress)}
                        className={styles.pRing}
                    />
                </svg>
            </div>
            <p className={styles.instruction}>
                {scanning ? "Scanning..." : "Press and hold to scan fingerprint"}
            </p>
        </div>
    );
}
