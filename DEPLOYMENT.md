# JOGAI — Деплой и инфраструктура

## 1. Приоритеты запуска

### Фаза 1 — MVP (сейчас)
Фокус: **канал + бот**. Mini App и лендинг — отложить.

```
✅ Канал @JOGAI_V — регулярный контент (Celery автопостинг)
✅ Бот @jogai_bot — /start, /bonus, /analyze, /casino, /sport
✅ Backend API — FastAPI + PostgreSQL + Redis
✅ Celery — автопостинг в канал (bonus_day, sport, slot)
❌ Mini App — отложить до фазы 2
❌ Лендинг — отложить до фазы 2
```

### Фаза 2 — расширение (~500+ юзеров бота)
```
→ Задеплоить Mini App
→ Задеплоить лендинг jogai.fun
→ Настроить SSL (Let's Encrypt / Caddy)
→ Подключить домен
```

### Фаза 3 — Мексика
```
→ Перевести es_MX.json
→ Seed MX казино/бонусы
→ Канал @jogai_mx
```

---

## 2. Сервер

### Рекомендуемые характеристики

**Минимум (MVP, <1000 юзеров):**
- 2 vCPU
- 4 GB RAM
- 40 GB SSD
- ~$5–10/мес

**Рекомендуется (до 5000 юзеров):**
- 4 vCPU (AMD EPYC)
- 8 GB RAM
- 80 GB NVMe SSD
- ~$15–20/мес

### Потребление ресурсов по контейнерам

| Контейнер | RAM | CPU | Примечание |
|-----------|-----|-----|------------|
| PostgreSQL | ~200 MB | Low | Основная БД |
| Redis | ~50 MB | Low | Кэш + Celery broker |
| Backend (FastAPI) | ~150 MB | Medium | API + webhook бота |
| Celery Worker | ~150 MB | Low | Автопостинг, фоновые задачи |
| Celery Beat | ~50 MB | Minimal | Планировщик |
| Nginx | ~20 MB | Minimal | Reverse proxy |
| **Итого MVP** | **~620 MB** | | Без Mini App и лендинга |
| Mini App (nginx) | ~20 MB | Minimal | Статика (фаза 2) |
| Landing (Next.js) | ~200 MB | Low | SSR (фаза 2) |
| **Итого полный** | **~840 MB** | | Все сервисы |

### Локация сервера

**Литва — лучший выбор** из двух вариантов:
- Ближе к ЦОД Telegram (Амстердам, Лондон)
- Нет проблем с доступом к Telegram API (в отличие от РФ)
- Нет риска блокировок/VPN-проблем для внешних сервисов
- EU-юрисдикция — проще с платежами, API-ключами, партнёрками
- Latency до LATAM ~150–200ms (приемлемо для бота и API)

**Россия — риски:**
- Telegram API может быть нестабилен (исторически блокировали)
- Anthropic API — могут быть ограничения из РФ
- Партнёрские программы (gambling) — юрисдикционные вопросы
- Хуже connectivity до LATAM

### Рекомендуемые хостинги

| Провайдер | Локация | План | Цена | Примечание |
|-----------|---------|------|------|------------|
| Hetzner | Хельсинки/Фалькенштайн | CPX21 | €8/мес | 3 vCPU, 4GB, 80GB — оптимально для MVP |
| Hetzner | Хельсинки | CPX31 | €15/мес | 4 vCPU, 8GB — с запасом на рост |
| Timeweb Cloud | Литва | — | ~600₽/мес | Если нужна оплата в ₽ |

---

## 3. Деплой MVP (канал + бот)

### 3.1. Подготовка сервера

```bash
# SSH на сервер
ssh root@YOUR_SERVER_IP

# Обновление
apt update && apt upgrade -y

# Docker
curl -fsSL https://get.docker.com | sh
apt install -y docker-compose-plugin

# Git
apt install -y git
```

### 3.2. Клонирование и настройка

```bash
git clone https://github.com/HiH-DimaN/jogai.git /opt/jogai
cd /opt/jogai

# Создать .env для бэкенда
cp backend/.env.example backend/.env
nano backend/.env
```

### 3.3. Переменные окружения (backend/.env)

```env
# ОБЯЗАТЕЛЬНЫЕ для MVP
DATABASE_URL=postgresql+asyncpg://jogai:STRONG_PASSWORD@postgres:5432/jogai
REDIS_URL=redis://redis:6379/0
TELEGRAM_BOT_TOKEN=your_real_bot_token
TELEGRAM_CHANNEL_BR_ID=-100xxxxxxxxxx
ANTHROPIC_API_KEY=sk-ant-xxxxx
SECRET_KEY=GENERATE_RANDOM_64_CHAR_STRING

# Настройки
ENVIRONMENT=production
DEFAULT_LOCALE=pt_BR
DEFAULT_GEO=BR
LLM_PROVIDER=anthropic
LLM_MODEL=claude-sonnet-4-20250514

# Партнёрские (заполнить реальными)
BET365_REF_ID=your_ref
RIVALO_REF_ID=your_ref
```

### 3.4. Запуск (только бот + бэкенд)

```bash
cd /opt/jogai

# Запустить только нужные сервисы (без miniapp и landing)
docker compose up -d postgres redis backend celery-worker celery-beat nginx

# Проверка
docker compose ps
docker compose logs backend --tail 20

# Миграции
docker compose exec backend alembic upgrade head

# Seed данных
docker compose exec backend python -m app.database.seed

# Health check
curl http://localhost:8080/api/health
```

### 3.5. Настройка бота

```bash
# Webhook (после настройки SSL)
curl -X POST "https://api.telegram.org/bot<TOKEN>/setWebhook" \
  -d "url=https://YOUR_DOMAIN/bot/webhook"

# Или polling (для начала, без домена)
# В docker-compose: command: python -m app.bot.polling
```

---

## 4. Подключение Mini App (фаза 2)

Когда наберётся аудитория (~500+ юзеров):

### 4.1. Деплой

```bash
cd /opt/jogai
docker compose up -d --build miniapp
# nginx уже настроен на /miniapp/ → miniapp:5173
```

### 4.2. BotFather

```
1. Открыть @BotFather
2. /mybots → @jogai_bot
3. Bot Settings → Menu Button
4. Задать URL: https://jogai.fun/miniapp/
5. Задать текст кнопки: Jogai App
```

### 4.3. Кнопка в боте

Кнопка `btn_miniapp` в /start уже отправляет WebAppInfo.
Нужно только задать URL в коде:

```python
# bot/handlers/start.py — уже есть кнопка "📊 Abrir Jogai App"
# Нужен HTTPS URL для WebApp
WebAppInfo(url="https://jogai.fun/miniapp/")
```

### 4.4. Требования

- **HTTPS обязателен** — Telegram не откроет Mini App по HTTP
- **SSL:** Let's Encrypt (certbot) или Caddy (автоматический SSL)
- **Домен:** jogai.fun (или любой с SSL)

---

## 5. SSL (Let's Encrypt)

```bash
apt install -y certbot python3-certbot-nginx

# Получить сертификат (nginx должен слушать 80 порт)
certbot --nginx -d jogai.fun -d www.jogai.fun

# Авторенью (автоматически через cron)
certbot renew --dry-run
```

---

## 6. Бэкапы

```bash
# Ежедневный бэкап PostgreSQL (добавить в cron)
docker compose exec postgres pg_dump -U jogai jogai | gzip > /opt/backups/jogai_$(date +%Y%m%d).sql.gz

# Crontab
0 3 * * * /opt/jogai/scripts/backup.sh
```

---

*Версия 1.0 | Март 2026*
