# eKYC Frontend

Premium Next.js frontend for Pakistan digital banking eKYC system.

## Features

- 🎨 **Premium UI/UX** - Banking-grade design with glassmorphism and smooth animations
- 📱 **Mobile-First** - Fully responsive, optimized for mobile devices
- 📷 **Camera Integration** - Live camera feeds for CNIC, selfie, and liveness detection
- 🔒 **Secure** - JWT token validation and encrypted communication
- ⚡ **Fast** - Built with Next.js 14 App Router and React 19
- 🎭 **Animated** - Framer Motion for smooth transitions

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS 4
- **Animations**: Framer Motion
- **Icons**: Lucide React
- **HTTP Client**: Axios

## Getting Started

### Prerequisites

- Node.js 18+ and npm

### Installation

```bash
# Install dependencies
npm install

# Create environment file
cp .env.local.example .env.local

# Update .env.local with your backend URL
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Development

```bash
# Run development server
npm run dev

# Open http://localhost:3000
```

### Build

```bash
# Build for production
npm run build

# Start production server
npm start
```

## Project Structure

```
src/
├── app/                    # Next.js app router pages
│   ├── page.tsx           # Homepage
│   ├── verify/            # Verification flow
│   │   └── page.tsx       # Main verification page
│   ├── layout.tsx         # Root layout
│   └── globals.css        # Global styles
├── components/
│   ├── ui/                # Reusable UI components
│   │   ├── Button.tsx
│   │   ├── Card.tsx
│   │   └── ProgressSteps.tsx
│   └── verification/      # Verification step components
│       ├── CNICUpload.tsx
│       ├── SelfieCapture.tsx
│       ├── LivenessCheck.tsx
│       ├── FingerprintCapture.tsx
│       └── SuccessScreen.tsx
└── lib/
    ├── api.ts             # API client
    └── utils.ts           # Utility functions
```

## Verification Flow

1. **Token Validation** - Validates JWT token from URL
2. **CNIC Upload** - Upload front and back of CNIC card
3. **Selfie Capture** - Live camera selfie with face guide
4. **Liveness Check** - Video recording with blink and head turn detection
5. **Fingerprint** - Simulated fingerprint capture
6. **Success** - Account created confirmation

## API Integration

The frontend communicates with the FastAPI backend through the API client (`src/lib/api.ts`).

### Endpoints Used

- `POST /api/verify/validate-token` - Validate JWT token
- `POST /api/verify/upload-cnic` - Upload CNIC images
- `POST /api/verify/upload-selfie` - Upload selfie
- `POST /api/verify/liveness-check` - Submit liveness video
- `POST /api/verify/submit-fingerprint` - Submit fingerprint data
- `POST /api/verify/finalize` - Finalize verification

## Camera Permissions

The app requires camera access for:
- CNIC photo capture
- Selfie capture
- Liveness video recording

Users will be prompted to grant camera permissions when accessing these features.

## Browser Compatibility

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

Mobile browsers with camera API support required.

## Design System

### Colors

- **Primary**: Emerald green (#10b981)
- **Accent**: Purple (#a855f7)
- **Background**: Dark (#0a0a0a)
- **Foreground**: Light gray (#fafafa)

### Components

All components follow a consistent design language with:
- Glassmorphism effects
- Smooth animations
- Responsive layouts
- Accessibility features

## License

Proprietary - Digital Bank eKYC System
