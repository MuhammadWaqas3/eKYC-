import { NextResponse } from 'next/server';

export async function POST(request) {
    try {
        const formData = await request.formData();
        const cnicFront = formData.get('cnic_front');
        const cnicBack = formData.get('cnic_back');
        const sessionId = formData.get('session_id');

        const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || 'http://process.env.NEXT_PUBLIC_API_URL';

        // Forward to backend /api/chat/submit-cnic endpoint
        const backendFormData = new FormData();
        backendFormData.append('cnic_front', cnicFront);
        backendFormData.append('cnic_back', cnicBack);
        backendFormData.append('session_id', sessionId);

        const response = await fetch(`${BACKEND_URL}/api/chat/submit-cnic`, {
            method: 'POST',
            body: backendFormData
        });

        if (!response.ok) {
            const errorText = await response.text();
            console.error('Backend CNIC upload failed:', errorText);
            throw new Error(`Backend CNIC upload failed: ${response.status}`);
        }

        const data = await response.json();

        return NextResponse.json({
            success: true,
            message: 'CNIC uploaded successfully',
            confirmation_message: data.confirmation_message || null,
            data: data.data
        });

    } catch (error) {
        console.error('CNIC Upload Error:', error);
        return NextResponse.json({
            success: false,
            message: 'Failed to upload CNIC',
            error: error.message
        }, { status: 500 });
    }
}
