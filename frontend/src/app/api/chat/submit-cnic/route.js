import { NextResponse } from 'next/server';

export async function POST(request) {
    try {
        const formData = await request.formData();
        const cnicFront = formData.get('cnic_front');
        const cnicBack = formData.get('cnic_back');
        const sessionId = formData.get('session_id');

        const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

        // Forward to backend - backend expects token as form field
        const backendFormData = new FormData();
        backendFormData.append('front_image', cnicFront);
        backendFormData.append('back_image', cnicBack);
        // Generate or retrieve token - for now using session_id as token
        // TODO: Implement proper JWT token generation/retrieval
        backendFormData.append('token', sessionId || 'test-token');

        const response = await fetch(`${BACKEND_URL}/api/verify/upload-cnic`, {
            method: 'POST',
            body: backendFormData
        });

        if (!response.ok) {
            throw new Error('Backend CNIC upload failed');
        }

        const data = await response.json();

        return NextResponse.json({
            success: true,
            message: 'CNIC uploaded successfully',
            data
        });

    } catch (error) {
        console.error('CNIC Upload Error:', error);
        return NextResponse.json({
            success: false,
            message: 'Failed to upload CNIC'
        }, { status: 500 });
    }
}
