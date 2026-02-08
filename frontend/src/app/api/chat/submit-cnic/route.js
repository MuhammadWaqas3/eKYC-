import { NextResponse } from 'next/server';

export async function POST(request) {
    try {
        const formData = await request.formData();
        const cnicFront = formData.get('cnic_front');
        const cnicBack = formData.get('cnic_back');
        const sessionId = formData.get('session_id');

        const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

        // Forward to backend
        const backendFormData = new FormData();
        backendFormData.append('cnic_front', cnicFront);
        backendFormData.append('cnic_back', cnicBack);
        backendFormData.append('session_id', sessionId);

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
