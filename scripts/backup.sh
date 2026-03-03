#!/bin/bash
set -euo pipefail

BACKUP_DIR="/root/backups/jogai"
DATE=$(date +%Y%m%d_%H%M%S)
CONTAINER="jogai-postgres-1"

mkdir -p "$BACKUP_DIR"

# pg_dump
echo "Creating backup: jogai_${DATE}.sql.gz"
docker exec "$CONTAINER" pg_dump -U jogai jogai | gzip > "${BACKUP_DIR}/jogai_${DATE}.sql.gz"

# Remove backups older than 30 days
find "$BACKUP_DIR" -name "*.sql.gz" -mtime +30 -delete

BACKUP_SIZE=$(du -h "${BACKUP_DIR}/jogai_${DATE}.sql.gz" | cut -f1)
echo "Backup done: jogai_${DATE}.sql.gz (${BACKUP_SIZE})"
