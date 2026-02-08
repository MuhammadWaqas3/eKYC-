#!/bin/bash

# eKYC System Quick Start Script
# This script initializes and starts the complete eKYC system

echo "🚀 Starting eKYC Digital Banking System..."
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Step 1: Initialize Database
echo -e "${BLUE}Step 1: Initializing Database...${NC}"
cd backend
python scripts/init_db.py
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Database initialized successfully${NC}"
else
    echo -e "${RED}✗ Database initialization failed${NC}"
    exit 1
fi
echo ""

# Step 2: Start Backend
echo -e "${BLUE}Step 2: Starting Backend Server...${NC}"
echo "Backend will run on http://localhost:8000"
python main.py &
BACKEND_PID=$!
echo -e "${GREEN}✓ Backend started (PID: $BACKEND_PID)${NC}"
echo ""

# Wait for backend to start
sleep 3

# Step 3: Start Frontend
echo -e "${BLUE}Step 3: Starting Frontend Server...${NC}"
cd ../frontend
echo "Frontend will run on http://localhost:3000"
npm run dev &
FRONTEND_PID=$!
echo -e "${GREEN}✓ Frontend started (PID: $FRONTEND_PID)${NC}"
echo ""

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}✓ eKYC System is now running!${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📱 Frontend:  http://localhost:3000"
echo "🔧 Backend:   http://localhost:8000"
echo "📚 API Docs:  http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Wait for user interrupt
trap "echo ''; echo 'Stopping services...'; kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
