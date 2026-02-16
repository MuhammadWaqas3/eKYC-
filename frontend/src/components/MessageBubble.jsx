import { useState, useEffect } from "react";
import { Bot, User, Check, CheckCheck } from "lucide-react";
import styles from "./MessageBubble.module.css";

export default function MessageBubble({ message }) {
    const isBot = message.role === "bot";
    const [tickStatus, setTickStatus] = useState('sent'); // sent, delivered, read
    const [time, setTime] = useState(''); // <-- client-side timestamp

    // Client-side tick simulation
    useEffect(() => {
        if (!isBot) {
            const timer1 = setTimeout(() => setTickStatus('delivered'), 1000);
            const timer2 = setTimeout(() => setTickStatus('read'), 2500);
            return () => {
                clearTimeout(timer1);
                clearTimeout(timer2);
            };
        }
    }, [isBot]);

    // Render timestamp **only on client**
    useEffect(() => {
        setTime(new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }));
    }, [message.timestamp]);

    return (
        <div className={`${styles.container} ${isBot ? styles.bot : styles.user}`}>
            <div className={styles.avatar}>
                {isBot ? <Bot size={20} /> : <User size={20} />}
            </div>
            <div className={styles.content}>
                {message.type === 'link' && message.actionUrl ? (
                    <div>
                        <p className={styles.text}>{message.content}</p>
                        <a
                            href={message.actionUrl}
                            target="_blank"
                            rel="noopener noreferrer"
                            className={styles.actionButton}
                        >
                            Verify Identity &rarr;
                        </a>
                    </div>
                ) : (
                    <p className={styles.text}>{message.content}</p>
                )}
                <div className={styles.meta}>
                    <span className={styles.time}>{time}</span> {/* use client-side time */}
                    {!isBot && (
                        <span className={`${styles.ticks} ${tickStatus === 'read' ? styles.read : ''}`}>
                            {tickStatus === 'sent' && <Check size={14} />}
                            {tickStatus === 'delivered' && <CheckCheck size={14} />}
                            {tickStatus === 'read' && <CheckCheck size={14} color="#3b82f6" />}
                        </span>
                    )}
                </div>
            </div>
        </div>
    );
}
