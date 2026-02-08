import { NextResponse } from 'next/server';
import { updateUserVerification, getUser } from '@/lib/db';

export async function POST(request) {
    try {
        const body = await request.json();
        const { token, data } = body; // data contains images and fingerprint flag

        if (!token) {
            return NextResponse.json({ error: "Missing token" }, { status: 400 });
        }

        const user = getUser(token);
        if (!user) {
            return NextResponse.json({ error: "Invalid token" }, { status: 404 });
        }

        // In a real app, here we would:
        // 1. Send CNIC images to OCR service
        // 2. Match Selfie with CNIC photo
        // 3. Verify Fingerprint with NADRA
        // 4. Check for duplicates

        // Mocking successful verification:
        if (data.cnicFront && data.cnicBack && data.selfie && data.fingerprint) {
            updateUserVerification(token, {
                cnicFront: true,
                cnicBack: true,
                selfie: true,
                fingerprint: true,
            });

            return NextResponse.json({ success: true });
        } else {
            return NextResponse.json({ error: "Incomplete data" }, { status: 400 });
        }

    } catch (e) {
        console.error(e);
        return NextResponse.json({ error: "Internal Error" }, { status: 500 });
    }
}
