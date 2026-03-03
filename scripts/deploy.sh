#!/bin/bash
set -euo pipefail

SERVER="root@155.212.230.139"
PROJECT_DIR="/root/jogai"

echo "=== Jogai Deploy ==="

# 1. Git pull
echo "[1/4] Pulling latest code..."
ssh "$SERVER" "cd $PROJECT_DIR && git pull origin main"

# 2. Build and restart
echo "[2/4] Building containers..."
ssh "$SERVER" "cd $PROJECT_DIR && docker compose -f docker-compose.prod.yml build"

echo "[3/4] Starting services..."
ssh "$SERVER" "cd $PROJECT_DIR && docker compose -f docker-compose.prod.yml up -d"

# 3. Alembic migrations
echo "[4/4] Running migrations..."
ssh "$SERVER" "cd $PROJECT_DIR && docker compose -f docker-compose.prod.yml exec -T backend alembic upgrade head"

# 4. Health check
echo "Waiting for services to start..."
sleep 10
if ssh "$SERVER" "curl -sf http://localhost:8000/api/health > /dev/null 2>&1"; then
    echo "Health check: OK"
else
    echo "WARNING: Health check failed! Check logs with:"
    echo "  ssh $SERVER 'cd $PROJECT_DIR && docker compose -f docker-compose.prod.yml logs backend --tail=50'"
fi

echo "=== Deploy complete! ==="
