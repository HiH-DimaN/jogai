#!/bin/bash
set -euo pipefail

# Load env for bot token and alert chat ID
ENV_FILE="/opt/jogai/backend/.env.prod"
if [ -f "$ENV_FILE" ]; then
    TELEGRAM_BOT_TOKEN=$(grep -oP '^TELEGRAM_BOT_TOKEN=\K.*' "$ENV_FILE" || true)
    # Use ALERT_CHAT_ID if set, otherwise fall back to BR channel
    ALERT_CHAT_ID=$(grep -oP '^ALERT_CHAT_ID=\K.*' "$ENV_FILE" || true)
    if [ -z "$ALERT_CHAT_ID" ]; then
        ALERT_CHAT_ID=$(grep -oP '^TELEGRAM_CHANNEL_BR_ID=\K.*' "$ENV_FILE" || true)
    fi
fi

HEALTH_URL="https://jogai.fun/api/health"
TELEGRAM_BOT_TOKEN="${TELEGRAM_BOT_TOKEN:-}"
ALERT_CHAT_ID="${ALERT_CHAT_ID:-}"

if [ -z "$TELEGRAM_BOT_TOKEN" ] || [ -z "$ALERT_CHAT_ID" ]; then
    echo "Missing TELEGRAM_BOT_TOKEN or ALERT_CHAT_ID"
    exit 1
fi

send_alert() {
    local message="$1"
    curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
        -d chat_id="$ALERT_CHAT_ID" \
        -d text="$message" \
        -d parse_mode="HTML" > /dev/null 2>&1
}

HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "$HEALTH_URL" 2>/dev/null || echo "000")

if [ "$HTTP_CODE" != "200" ]; then
    TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
    send_alert "🚨 <b>Jogai DOWN</b>
⏰ ${TIMESTAMP}
🔗 ${HEALTH_URL}
📊 HTTP: ${HTTP_CODE}"
    echo "${TIMESTAMP} FAIL (HTTP ${HTTP_CODE})"
    exit 1
else
    echo "$(date '+%Y-%m-%d %H:%M:%S') OK"
fi
