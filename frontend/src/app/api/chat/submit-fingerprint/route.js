import { NextResponse } from 'next/server';

export async function POST(request) {
    try {
        const body = await request.json();
        const { fingerprint_data, session_id } = body;

        const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

        // Forward to backend
        const response = await fetch(`${BACKEND_URL}/api/verify/fingerprint`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                fingerprint_data,
                session_id
            })
        });

        if (!response.ok) {
            throw new Error('Backend fingerprint submission failed');
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
            message: 'Failed to submit fingerprint'
        }, { status: 500 });
    }
}
