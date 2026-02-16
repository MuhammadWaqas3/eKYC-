"use client";

import { useState } from "react";
import { CheckCircle, Edit, AlertCircle } from "lucide-react";
import styles from "./ConfirmationScreen.module.css";

export default function ConfirmationScreen({ userData, onConfirm, onEdit }) {
    const [isSubmitting, setIsSubmitting] = useState(false);

    const handleConfirm = async () => {
        setIsSubmitting(true);
        await onConfirm();
        setIsSubmitting(false);
    };

    // Map of field labels for display with nice icons
    const fields = [
        { key: "name", label: "Full Name", icon: "👤" },
        { key: "father_name", label: "Father's Name", icon: "👨" },
        { key: "cnic_number", label: "CNIC Number", icon: "🆔" },
        { key: "dob", label: "Date of Birth", icon: "📅" },
        { key: "email", label: "Email Address", icon: "📧" },
        { key: "phone", label: "Phone Number", icon: "📱" },
        { key: "account_type", label: "Account Type", icon: "🏦" }
    ];

    return (
        <div className={styles.overlay}>
            <div className={styles.container}>
                <div className={styles.header}>
                    <div className={styles.iconWrapper}>
                        <CheckCircle size={48} className={styles.checkIcon} />
                    </div>
                    <h2 className={styles.title}>Verify Your Information</h2>
                    <p className={styles.subtitle}>
                        Please review all the details we've collected. Make sure everything is correct before proceeding.
                    </p>
                </div>

                <div className={styles.dataGrid}>
                    {fields.map(field => {
                        const value = userData[field.key];
                        const isEmpty = !value || value === "Not Available" || value === "Not Detected";

                        return (
                            <div key={field.key} className={styles.dataItem}>
                                <div className={styles.fieldLabel}>
                                    <span className={styles.fieldIcon}>{field.icon}</span>
                                    {field.label}
                                </div>
                                <div className={`${styles.fieldValue} ${isEmpty ? styles.empty : ''}`}>
                                    {isEmpty ? (
                                        <span className={styles.notAvailable}>
                                            <AlertCircle size={14} /> Not Available
                                        </span>
                                    ) : value}
                                </div>
                            </div>
                        );
                    })}
                </div>

                <div className={styles.confirmationText}>
                    <p>✓ By confirming, you agree that all the information provided above is accurate and complete.</p>
                </div>

                <div className={styles.actions}>
                    <button
                        className={styles.editBtn}
                        onClick={onEdit}
                        disabled={isSubmitting}
                    >
                        <Edit size={18} />
                        Need Changes
                    </button>
                    <button
                        className={styles.confirmBtn}
                        onClick={handleConfirm}
                        disabled={isSubmitting}
                    >
                        {isSubmitting ? (
                            <span className={styles.loader}></span>
                        ) : (
                            <>
                                <CheckCircle size={18} />
                                Confirm & Submit
                            </>
                        )}
                    </button>
                </div>
            </div>
        </div>
    );
}
