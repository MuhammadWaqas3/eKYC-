import { NextResponse } from 'next/server';

export async function POST(request) {
    try {
        const formData = await request.formData();
        const fingerprint_image = formData.get('fingerprint_image');
        const session_id = formData.get('session_id');

        if (!fingerprint_image || !session_id) {
            return NextResponse.json({
                success: false,
                message: 'Missing fingerprint image or session ID'
            }, { status: 400 });
        }

        const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || 'http://process.env.NEXT_PUBLIC_API_URL';

        // Create FormData for backend
        const backendFormData = new FormData();
        backendFormData.append('fingerprint_image', fingerprint_image);
        backendFormData.append('session_id', session_id);

        // Forward to backend /api/chat/submit-fingerprint endpoint
        const response = await fetch(`${BACKEND_URL}/api/chat/submit-fingerprint`, {
            method: 'POST',
            body: backendFormData
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || 'Backend fingerprint submission failed');
        }

        const data = await response.json();

        return NextResponse.json({
            success: true,
            message: 'Fingerprint captured successfully',
            data
        });

    } catch (error) {
        console.error('Fingerprint Submission Error:', error);
        return NextResponse.json({
            success: false,
            message: error.message || 'Failed to submit fingerprint'
        }, { status: 500 });
    }
}
