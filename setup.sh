#!/bin/bash
# ============================================================
# CloudLab Deployment Script — Cloud Task Manager
# CSC 468: Introduction to Cloud Computing
# Author: Joseph Nweke
# ============================================================
# Usage: bash setup.sh
# Run this script on your CloudLab node after cloning the repo.

set -e

echo "========================================"
echo "  Cloud Task Manager — Setup Script"
echo "========================================"

# Step 1: Update system packages
echo "[1/4] Updating system packages..."
sudo apt-get update -y
sudo apt-get install -y curl ca-certificates gnupg lsb-release

# Step 2: Install Docker if not present
if ! command -v docker &> /dev/null; then
    echo "[2/4] Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
    echo "Docker installed."
else
    echo "[2/4] Docker already installed: $(docker --version)"
fi

# Step 3: Install Docker Compose if not present
if ! command -v docker compose &> /dev/null && ! command -v docker-compose &> /dev/null; then
    echo "[3/4] Installing Docker Compose..."
    sudo apt-get install -y docker-compose-plugin
    echo "Docker Compose installed."
else
    echo "[3/4] Docker Compose already installed."
fi

# Step 4: Build and launch containers
echo "[4/4] Building and starting containers..."
sudo docker compose up --build -d

echo ""
echo "========================================"
echo "  Deployment Complete!"
echo "========================================"
PUBLIC_IP=$(curl -s ifconfig.me 2>/dev/null || hostname -I | awk '{print $1}')
echo "  Frontend:  http://${PUBLIC_IP}:5001"
echo "  Backend:   http://${PUBLIC_IP}:5000"
echo "========================================"
echo ""
echo "To view logs:    docker compose logs -f"
echo "To stop:         docker compose down"
echo "To restart:      docker compose restart"
