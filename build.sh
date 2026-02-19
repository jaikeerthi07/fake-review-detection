#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install Python dependencies
pip install -r requirements.txt

# Build Frontend
echo "Building Frontend..."
cd frontend
npm install
npm run build
cd ..

# Move/Ensure static files are where Flask expects them
# Flask is configured with static_folder='frontend/dist' so we leave them there.
