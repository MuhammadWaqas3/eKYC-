"use client";
import { v4 as uuidv4 } from "uuid";
import { useState, useRef, useEffect } from "react";
import { Send, Sparkles, Upload, RefreshCw } from "lucide-react";
import styles from "./ChatWindow.module.css";
import MessageBubble from "./MessageBubble";
import CameraOverlay from "./CameraOverlay";
import CNICCameraOverlay from "./CNICCameraOverlay";
import FingerprintOverlay from "./FingerprintOverlay";
import ConfirmationScreen from "./ConfirmationScreen";

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
    const [collectedUserData, setCollectedUserData] = useState(null);
    const [showConfirmation, setShowConfirmation] = useState(false);

    // Initialize session
    useEffect(() => {
        const storedId = localStorage.getItem("chatSessionId") || uuidv4();
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

        // Check for reset commands
        const resetKeywords = ['new chat', 'start over', 'restart', 'begin again', 'fresh start', 'reset'];
        if (resetKeywords.some(keyword => input.toLowerCase().includes(keyword))) {
            handleReset();
            return;
        }

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

        const userInput = input.toLowerCase().trim();
        setInput("");
        setIsTyping(true);

        // Not needed anymore - confirmation handled by ConfirmationScreen component

        // Normal chat flow with API
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

    // Handle new chat / reset
    const handleReset = () => {
        const resetMsg = {
            id: Date.now().toString(),
            role: "user",
            content: input,
            timestamp: Date.now(),
        };

        setChatState({
            messages: [
                resetMsg,
                {
                    id: (Date.now() + 1).toString(),
                    role: "bot",
                    content: "Of course! Let's start fresh.\n\nHello! Welcome to Avanza Solutions. I'm your digital assistant, and I can help you open a new bank account in just a few minutes.\n\nTo get started, please tell me your full name.",
                    timestamp: Date.now() + 1,
                }
            ],
            step: "ask_name",
            userData: {},
            isLoading: false,
        });

        setInput("");
        setVerificationStep('idle');
        setCapturedData({
            cnicFront: null,
            cnicBack: null,
            selfie: null,
            livenessVideo: null,
            fingerprint: null
        });
        setCollectedUserData(null);
        setShowConfirmation(false);

        // Generate new session ID
        const newSessionId = uuidv4();
        localStorage.setItem("chatSessionId", newSessionId);
        setSessionId(newSessionId);
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

        // Send CNIC data to backend (OCR processes in background)
        try {
            const formData = new FormData();
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

        // Simple success message - NO detailed data yet
        const confirmationMsg = {
            id: Date.now().toString(),
            role: "bot",
            content: "✅ CNIC captured successfully! Processing your information in the background.\n\nNext, let's verify your face with a liveness check.",
            timestamp: Date.now(),
        };

        setChatState(prev => ({
            ...prev,
            messages: [...prev.messages, confirmationMsg]
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
        console.log('[DEBUG] Fingerprint captured:', data);
        setCapturedData(prev => ({ ...prev, fingerprint: data }));
        setActiveOverlay(null);

        // Send fingerprint data to backend (as File)
        try {
            const formData = new FormData();
            formData.append('fingerprint_image', data);
            formData.append('session_id', sessionId);

            console.log('[DEBUG] Uploading fingerprint to backend...');
            const uploadResponse = await fetch('/api/chat/submit-fingerprint', {
                method: 'POST',
                body: formData
            });
            console.log('[DEBUG] Fingerprint upload response:', uploadResponse.status);
        } catch (error) {
            console.error('[ERROR] Fingerprint upload error:', error);
        }

        const processingMsg = {
            id: Date.now().toString(),
            role: "bot",
            content: "✅ Fingerprint captured! Retrieving your information...",
            timestamp: Date.now(),
        };
        setChatState(prev => ({
            ...prev,
            messages: [...prev.messages, processingMsg]
        }));

        // Fetch all collected data from backend and show confirmation screen
        console.log('[DEBUG] Fetching collected data...');
        setTimeout(async () => {
            try {
                const response = await fetch(`/api/chat/get-collected-data?session_id=${sessionId}`);
                console.log('[DEBUG] Get collected data response:', response.status);

                if (response.ok) {
                    const result = await response.json();
                    console.log('[DEBUG] Collected data:', result);
                    setCollectedUserData(result);
                    setShowConfirmation(true);
                    setVerificationStep('awaiting_confirmation');
                    console.log('[DEBUG] Confirmation screen should now be visible');
                } else {
                    console.error('[ERROR] Failed to fetch collected data:', response.statusText);
                    // Show error in chat
                    const errorMsg = {
                        id: Date.now().toString(),
                        role: "bot",
                        content: "⚠️ There was an issue retrieving your data. Please contact support.",
                        timestamp: Date.now(),
                    };
                    setChatState(prev => ({
                        ...prev,
                        messages: [...prev.messages, errorMsg]
                    }));
                }
            } catch (error) {
                console.error('[ERROR] Error fetching collected data:', error);
                // Show error in chat
                const errorMsg = {
                    id: Date.now().toString(),
                    role: "bot",
                    content: "⚠️ Network error. Please check your connection and try again.",
                    timestamp: Date.now(),
                };
                setChatState(prev => ({
                    ...prev,
                    messages: [...prev.messages, errorMsg]
                }));
            }
        }, 1500);
    };

    // Handle confirmation from ConfirmationScreen
    const handleUserConfirmation = async () => {
        setShowConfirmation(false);

        const congratsMsg = {
            id: Date.now().toString(),
            role: "bot",
            content: "🎉 **Congratulations!**\n\nYour account opening request has been successfully submitted!\n\nWelcome to Avanza Solutions! You will receive a confirmation email shortly with your account details.\n\nThank you for choosing us! 🙏",
            timestamp: Date.now(),
        };

        setChatState(prev => ({
            ...prev,
            messages: [...prev.messages, congratsMsg]
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
                <div className={styles.headerRight}>
                    <button
                        className={styles.newChatBtn}
                        onClick={handleReset}
                        title="Start a new conversation"
                    >
                        <RefreshCw size={18} />
                        <span>New Chat</span>
                    </button>
                    <div className={styles.status}>
                        <span className={styles.dot}></span> Online
                    </div>
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
                <CNICCameraOverlay
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

            {/* Confirmation Screen */}
            {showConfirmation && collectedUserData && (
                <ConfirmationScreen
                    userData={collectedUserData}
                    onConfirm={handleUserConfirmation}
                    onEdit={() => setShowConfirmation(false)}
                />
            )}
        </div>
    );
}
