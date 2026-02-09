"use client";
import { useState, useRef, useEffect } from "react";
import { Send, Sparkles, Upload } from "lucide-react";
import styles from "./ChatWindow.module.css";
import MessageBubble from "./MessageBubble";
import CameraOverlay from "./CameraOverlay";
import CNICUploadOverlay from "./CNICUploadOverlay";
import FingerprintOverlay from "./FingerprintOverlay";

export default function ChatWindow() {
    const [input, setInput] = useState("");
    const [isTyping, setIsTyping] = useState(false);
    const [sessionId, setSessionId] = useState(null);
    const messagesEndRef = useRef(null);

    // Overlay states
    const [activeOverlay, setActiveOverlay] = useState(null);
    const [verificationStep, setVerificationStep] = useState('idle');
    const [capturedData, setCapturedData] = useState({
        cnicFront: null,
        cnicBack: null,
        selfie: null,
        livenessVideo: null,
        fingerprint: null
    });

    // Initialize session
    useEffect(() => {
        const storedId = localStorage.getItem("chatSessionId") || crypto.randomUUID();
        localStorage.setItem("chatSessionId", storedId);
        setSessionId(storedId);
    }, []);

    // Initial State
    const [chatState, setChatState] = useState({
        messages: [
            {
                id: "1",
                role: "bot",
                content: "Hello! Welcome to Avanza Solutions. I'm your digital assistant.\n\nI can help you open a new bank account in just a few minutes.\n\nTo get started, please tell me your full name.",
                timestamp: Date.now(),
            },
        ],
        step: "ask_name",
        userData: {},
        isLoading: false,
    });

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [chatState.messages, isTyping]);

    const handleSend = async () => {
        if (!input.trim()) return;

        const userMsg = {
            id: Date.now().toString(),
            role: "user",
            content: input,
            timestamp: Date.now(),
        };

        setChatState((prev) => ({
            ...prev,
            messages: [...prev.messages, userMsg],
            isLoading: true,
        }));
        setInput("");
        setIsTyping(true);

        // Communicate with API
        try {
            const response = await fetch("/api/chat", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    message: input,
                    session_id: sessionId,
                    currentState: {
                        step: chatState.step,
                        userData: chatState.userData,
                    }
                }),
            });

            const data = await response.json();

            // Simulate delay for realism
            setTimeout(() => {
                setIsTyping(false);
                setChatState((prev) => ({
                    ...prev,
                    messages: [...prev.messages, ...data.newMessages],
                    step: data.nextStep || prev.step,
                    userData: { ...prev.userData, ...data.updatedUserData },
                    isLoading: false,
                }));

                // Check if we should show verification button
                if (data.action === "show_verification_button") {
                    setVerificationStep('ready_for_docs');
                }
            }, 300);

        } catch (error) {
            console.error("Chat Error", error);
            setIsTyping(false);
        }
    };

    const handleKeyDown = (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    // Start verification process
    const startVerification = () => {
        setVerificationStep('cnic');
        setActiveOverlay('cnic');

        // Add bot message
        const botMsg = {
            id: Date.now().toString(),
            role: "bot",
            content: "Great! Let's start with your CNIC. Please upload both front and back images of your CNIC.",
            timestamp: Date.now(),
        };
        setChatState(prev => ({
            ...prev,
            messages: [...prev.messages, botMsg]
        }));
    };

    // Handle CNIC Upload (both front and back)
    const handleCNICUpload = async (data) => {
        setCapturedData(prev => ({ ...prev, cnicFront: data.front, cnicBack: data.back }));
        setActiveOverlay(null);

        // Send CNIC data to backend
        try {
            const formData = new FormData();
            // data.front and data.back are now File objects, not base64 strings
            formData.append('cnic_front', data.front);
            formData.append('cnic_back', data.back);
            formData.append('session_id', sessionId);

            await fetch('/api/chat/submit-cnic', {
                method: 'POST',
                body: formData
            });
        } catch (error) {
            console.error('CNIC upload error:', error);
        }

        const botMsg = {
            id: Date.now().toString(),
            role: "bot",
            content: "✓ CNIC uploaded successfully! Next, let's verify your face with a liveness check.",
            timestamp: Date.now(),
        };
        setChatState(prev => ({
            ...prev,
            messages: [...prev.messages, botMsg]
        }));

        // Move to face verification
        setTimeout(() => {
            setVerificationStep('face');
            setActiveOverlay('selfie');
        }, 1500);
    };

    // Handle Selfie/Face capture
    const handleFaceCapture = async (data) => {
        setCapturedData(prev => ({ ...prev, selfie: data.image, livenessVideo: data.video }));
        setActiveOverlay(null);

        // Send face data to backend
        try {
            const formData = new FormData();
            formData.append('selfie', dataURLtoFile(data.image, 'selfie.jpg'));
            if (data.video) {
                formData.append('liveness_video', data.video, 'liveness.webm');
            }
            formData.append('session_id', sessionId);

            await fetch('/api/chat/submit-face', {
                method: 'POST',
                body: formData
            });
        } catch (error) {
            console.error('Face upload error:', error);
        }

        const botMsg = {
            id: Date.now().toString(),
            role: "bot",
            content: "✓ Face verification complete! Finally, let's capture your fingerprint.",
            timestamp: Date.now(),
        };
        setChatState(prev => ({
            ...prev,
            messages: [...prev.messages, botMsg]
        }));

        // Move to fingerprint
        setTimeout(() => {
            setVerificationStep('fingerprint');
            setActiveOverlay('fingerprint');
        }, 1500);
    };

    // Handle Fingerprint capture
    const handleFingerprintCapture = async (data) => {
        setCapturedData(prev => ({ ...prev, fingerprint: data }));
        setActiveOverlay(null);

        // Send fingerprint data to backend
        try {
            await fetch('/api/chat/submit-fingerprint', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    fingerprint_data: data,
                    session_id: sessionId
                })
            });
        } catch (error) {
            console.error('Fingerprint upload error:', error);
        }

        const botMsg = {
            id: Date.now().toString(),
            role: "bot",
            content: "🎉 Excellent! All verification steps are complete. Your account is being processed. You'll receive confirmation shortly.",
            timestamp: Date.now(),
        };
        setChatState(prev => ({
            ...prev,
            messages: [...prev.messages, botMsg]
        }));

        setVerificationStep('complete');
    };

    // Helper function to convert dataURL to File
    const dataURLtoFile = (dataurl, filename) => {
        const arr = dataurl.split(',');
        const mime = arr[0].match(/:(.*?);/)[1];
        const bstr = atob(arr[1]);
        let n = bstr.length;
        const u8arr = new Uint8Array(n);
        while (n--) {
            u8arr[n] = bstr.charCodeAt(n);
        }
        return new File([u8arr], filename, { type: mime });
    };

    return (
        <div className={styles.wrapper}>
            <header className={styles.header}>
                <div className={styles.logo}>
                    <Sparkles size={24} className={styles.logoIcon} />
                    <span>Avanza Solutions</span>
                </div>
                <div className={styles.status}>
                    <span className={styles.dot}></span> Online
                </div>
            </header>

            <div className={styles.messagesArea}>
                {chatState.messages.map((msg) => (
                    <MessageBubble key={msg.id} message={msg} />
                ))}
                {isTyping && (
                    <div className={styles.typingIndicator}>
                        <span></span><span></span><span></span>
                    </div>
                )}

                {/* Show verification button when ready */}
                {verificationStep === 'ready_for_docs' && (
                    <div className={styles.actionButtonWrapper}>
                        <button className={styles.verificationBtn} onClick={startVerification}>
                            <Upload size={20} />
                            Upload / Scan Documents
                        </button>
                    </div>
                )}

                <div ref={messagesEndRef} />
            </div>

            <div className={styles.inputArea}>
                <div className={styles.inputWrapper}>
                    <input
                        type="text"
                        className={styles.input}
                        placeholder="Type your message..."
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={handleKeyDown}
                        disabled={chatState.isLoading}
                    />
                    <button
                        className={styles.sendBtn}
                        onClick={handleSend}
                        disabled={!input.trim() || chatState.isLoading}
                    >
                        <Send size={20} />
                    </button>
                </div>
            </div>

            {/* Upload/Camera Overlays */}
            {activeOverlay === 'cnic' && (
                <CNICUploadOverlay
                    onCapture={handleCNICUpload}
                    onClose={() => setActiveOverlay(null)}
                />
            )}
            {activeOverlay === 'selfie' && (
                <CameraOverlay
                    mode="selfie"
                    onCapture={handleFaceCapture}
                    onClose={() => setActiveOverlay(null)}
                />
            )}
            {activeOverlay === 'fingerprint' && (
                <FingerprintOverlay
                    onCapture={handleFingerprintCapture}
                    onClose={() => setActiveOverlay(null)}
                />
            )}
        </div>
    );
}
