import { NextResponse } from 'next/server';
import { createUser, getUser } from '@/lib/db';
import { v4 as uuidv4 } from 'uuid';

export async function POST(request) {
    try {
        const body = await request.json();
        const { message, currentState, session_id } = body;
        const { step, userData } = currentState;

        const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || 'http://process.env.NEXT_PUBLIC_API_URL';

        // 1. Call Python Backend for LLM Reply & DB Storage
        const backendResponse = await fetch(`${BACKEND_URL}/api/chat/webhook`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: message,
                user_id: userData?.id || null,
                session_id: session_id || null
            }),
        });

        if (!backendResponse.ok) {
            throw new Error(`Backend Error: ${backendResponse.statusText}`);
        }

        const backendData = await backendResponse.json();
        let botReply = backendData.reply;
        const verificationLink = backendData.verification_link;

        // 2. Integration with Onboarding Flow
        let nextStep = step;
        let updatedUserData = { ...userData };

        if (step === 'ask_name' && message.length >= 2) {
            updatedUserData.name = message;
            nextStep = 'ask_email';
        } else if (step === 'ask_email' && message.includes('@')) {
            updatedUserData.email = message;
            nextStep = 'ask_phone';
        } else if (step === 'ask_phone') {
            updatedUserData.phone = message;
            nextStep = 'await_verification';
        }

        // ✅ UPDATED: Determine message type and action URL
        let type = 'text';
        let actionUrl = null;

        // Check for links in the bot reply text (or use backend provided link)
        const linkMatch = botReply.match(/https?:\/\/[^\s]+/);
        if (linkMatch) {
            type = 'link';
            actionUrl = linkMatch[0];
            // ✅ Remove the URL from the message text (requires botReply to be 'let')
            botReply = botReply.replace(linkMatch[0], '').trim();
            nextStep = 'verification_sent';
        } else if (verificationLink) {
            type = 'link';
            actionUrl = verificationLink;
            nextStep = 'verification_sent';
        }

        return NextResponse.json({
            newMessages: [{
                id: Date.now().toString(),
                role: 'bot',
                content: botReply,
                timestamp: Date.now(),
                type: verificationLink ? 'text' : 'text', // No more link type
                actionUrl: null // No redirection
            }],
            nextStep,
            updatedUserData,
            action: verificationLink ? 'show_verification_button' : null // Signal to show button
        });

    } catch (error) {
        console.error('Chat API Error:', error);
        return NextResponse.json({
            newMessages: [{
                id: Date.now().toString(),
                role: 'bot',
                content: "I'm having trouble connecting to my brain right now. Please make sure the backend server is running.",
                timestamp: Date.now(),
            }],
            nextStep: 'error',
            updatedUserData: {},
        }, { status: 500 });
    }
}