#!/bin/bash
# Deployment script for ShortlistAI
# Usage: ./deploy.sh

set -e  # Exit on any error

echo "🚀 Starting deployment..."

# Step 1: Stop containers
echo "📦 Step 1/4: Stopping containers..."
sudo docker-compose down

# Step 2: Pull latest code
echo "📥 Step 2/4: Pulling latest code..."
sudo git pull

# Step 3: Build without cache (ensures fresh build)
echo "🔨 Step 3/4: Building containers (no cache)..."
sudo docker-compose build --no-cache

# Step 4: Start containers in detached mode
echo "▶️  Step 4/4: Starting containers..."
sudo docker-compose up -d

# Wait a moment for containers to start
sleep 3

# Check container status
echo "✅ Checking container status..."
sudo docker-compose ps

echo ""
echo "🎉 Deployment complete!"
echo "📊 View logs with: sudo docker-compose logs -f"
echo "🔍 Check backend health: curl http://localhost:3399/api/health"

