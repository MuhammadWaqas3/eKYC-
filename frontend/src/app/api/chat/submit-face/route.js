import { NextResponse } from 'next/server';

export async function POST(request) {
    try {
        const formData = await request.formData();
        const selfie = formData.get('selfie');
        const livenessVideo = formData.get('liveness_video');
        const sessionId = formData.get('session_id');

        const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || 'http://process.env.NEXT_PUBLIC_API_URL';

        // Forward to backend /api/chat/submit-face endpoint
        const backendFormData = new FormData();
        backendFormData.append('selfie', selfie);
        if (livenessVideo) {
            backendFormData.append('liveness_video', livenessVideo);
        }
        backendFormData.append('session_id', sessionId);

        const response = await fetch(`${BACKEND_URL}/api/chat/submit-face`, {
            method: 'POST',
            body: backendFormData
        });

        if (!response.ok) {
            throw new Error('Backend selfie upload failed');
        }

        const data = await response.json();

        return NextResponse.json({
            success: true,
            message: 'Face verification completed',
            data
        });

    } catch (error) {
        console.error('Face Upload Error:', error);
        return NextResponse.json({
            success: false,
            message: 'Failed to upload face data'
        }, { status: 500 });
    }
}
