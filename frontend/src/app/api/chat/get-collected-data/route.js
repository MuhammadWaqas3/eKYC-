import { NextResponse } from 'next/server';

export async function GET(request) {
    try {
        const { searchParams } = new URL(request.url);
        const session_id = searchParams.get('session_id');

        if (!session_id) {
            return NextResponse.json({
                success: false,
                message: 'Missing session ID'
            }, { status: 400 });
        }

        const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

        // Forward GET request to backend
        const response = await fetch(`${BACKEND_URL}/api/chat/get-collected-data?session_id=${session_id}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || 'Failed to fetch collected data');
        }

        const data = await response.json();

        return NextResponse.json(data);

    } catch (error) {
        console.error('Get Collected Data Error:', error);
        return NextResponse.json({
            success: false,
            message: error.message || 'Failed to fetch collected data'
        }, { status: 500 });
    }
}
