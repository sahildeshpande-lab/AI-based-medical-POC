#!/bin/bash
set -e

echo "Building Medical POC Application..."
echo "===================================="

echo "Step 1: Installing backend dependencies..."
pip install -r requirements.txt

echo ""
echo "Step 2: Installing frontend dependencies..."
cd frontend
npm install

echo ""
echo "Step 3: Building frontend..."
npm run build

echo ""
echo "Build complete! Application ready for deployment."
