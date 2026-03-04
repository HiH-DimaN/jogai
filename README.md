# 🎰 JOGAI — AI Gambling Assistant для LATAM

**Jogai** (произносится «Жогай») — мультиканальная AI-платформа для гемблинг-аудитории в Латинской Америке. Помогаем игрокам находить выгодные бонусы, анализировать условия казино и управлять банкроллом.

> «Этот бонус 500% — ловушка. Вейджер x60 = нужно прокрутить R$180 000. Вот три бонуса, которые РЕАЛЬНО выгодны.»

---

## 🧠 Что умеет Jogai

| Функция | Описание |
|---------|----------|
| **Jogai Score** | Математический рейтинг бонусов (0-10) |
| **AI-анализ бонуса** | Условия → разбор за 5 секунд на языке пользователя |
| **AI-подбор казино** | Квиз → персональный топ-3 |
| **Обзор слотов** | 12 слотов с верифицированным RTP, tips от AI |
| **Трекер ставок** | ROI, win rate, P&L в валюте пользователя |
| **Банкролл-менеджмент** | Рекомендации по размеру ставок |

---

## 🌐 Мультиязычность (i18n)

Заложена с первого дня. Все пользовательские строки в JSON-файлах, ноль хардкода.

| Язык | ГЕО | Валюта | Фаза |
|------|-----|--------|------|
| 🇧🇷 Португальский (PT-BR) | Бразилия | R$ (BRL) | 1 |
| 🇲🇽 Испанский (ES-MX) | Мексика | MX$ (MXN) | 3 |
| 🇪🇨🇨🇱🇵🇪 Испанский (ES) | Эквадор, Чили, Перу | USD | 4 |

Добавление нового языка = перевод JSON-файлов + seed данные. Ноль изменений кода.

---

## 📦 Архитектура

```
jogai/
├── backend/          # Python: FastAPI + aiogram + Celery
│   ├── app/locales/  # i18n: pt_BR.json, es_MX.json
│   └── app/i18n.py   # хелпер t(key, locale)
├── miniapp/          # React + react-i18next
│   └── public/locales/pt-BR/, es-MX/
├── landing/          # Next.js + next-intl
│   └── messages/pt-BR.json, es-MX.json
├── nginx/
└── docker-compose.yml
```

### Стек

- **Backend:** Python 3.11, FastAPI, aiogram 3.x, SQLAlchemy 2.0, Celery
- **Mini App:** React 18, TailwindCSS, Zustand, **react-i18next**
- **Лендинг:** Next.js 14, TailwindCSS, **next-intl**
- **БД:** PostgreSQL 15 (мультиязычные поля: title_pt, title_es), Redis 7
- **AI:** Claude API / GPT-4o-mini (ответ на {language} пользователя)

---

## 🚀 Быстрый старт

```bash
git clone git@github.com:HiH-DimaN/jogai.git
cd jogai
cp backend/.env.example backend/.env
# Отредактировать .env

docker-compose up --build -d
docker-compose exec backend alembic upgrade head
docker-compose exec backend python -m app.database.seed

curl http://localhost/api/health
# → {"status": "ok", "service": "jogai"}
```

---

## 📋 Документация

| Документ | Описание |
|----------|----------|
| [CLAUDE.md](CLAUDE.md) | Инструкции для Claude Code (читается автоматически) |
| [PROJECT_ARCHITECTURE.md](PROJECT_ARCHITECTURE.md) | Архитектура, БД, API, i18n |
| [PRD.md](PRD.md) | Продуктовые требования |
| [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) | Пошаговый план |
| [CLAUDE_CODE_GUIDE.md](CLAUDE_CODE_GUIDE.md) | Промпты для Claude Code |
| [JOGAI_Полный_Стратегический_План.md](JOGAI_Полный_Стратегический_План.md) | Стратегический план |

---

## 🔐 Авторизация

- **Telegram-бот:** идентификация по telegram_id (middleware)
- **Mini App:** Telegram WebApp initData → POST /api/auth/telegram → JWT
- **API:** Bearer JWT в заголовке Authorization
- **Лендинг:** публичный, без авторизации

---

## 🔧 Переменные окружения

Полный список — в `backend/.env.example`. Ключевые:

| Переменная | Описание |
|------------|----------|
| `DATABASE_URL` | PostgreSQL connection string |
| `REDIS_URL` | Redis connection string |
| `TELEGRAM_BOT_TOKEN` | Токен бота от @BotFather |
| `ANTHROPIC_API_KEY` | API-ключ Claude |
| `DEFAULT_LOCALE` | Локаль по умолчанию (pt_BR) |
| `DEFAULT_GEO` | ГЕО по умолчанию (BR) |
| `TELEGRAM_CHANNEL_BR_ID` | ID канала @jogai_br |
| `TELEGRAM_CHANNEL_MX_ID` | ID канала @jogai_mx |
| `SECRET_KEY` | Секрет для JWT |

---

## 🚢 Деплой

### Локальная разработка
```bash
docker-compose up --build -d
docker-compose exec backend alembic upgrade head
docker-compose exec backend python -m app.database.seed
```

### Продакшен
```bash
# На VPS (Hetzner)
docker-compose -f docker-compose.prod.yml up --build -d
```

Схема CI/CD:
```
git push → GitHub → VPS auto-deploy (или ручной deploy.sh)
```

SSL: Caddy (автоматический Let's Encrypt) или Nginx + Certbot.

---

## 💰 Бизнес-модель

Gambling affiliate: CPA ($20-50 за FTD) + RevShare (25-50% пожизненно) + PRO ($5/мес).

---

## 🗺️ Дорожная карта

| Фаза | Срок | Что |
|------|------|-----|
| Фундамент | Месяц 1-2 | Бот + канал + лендинг (BR, PT-BR) |
| AI-преимущество | Месяц 3-4 | Mini App (PT-BR) |
| Продукт | Месяц 5-7 | Трекер, PRO, Мексика (ES-MX), YouTube |
| Масштаб | Месяц 8-12 | Веб-платформа, 3+ ГЕО |

---

## 📄 Лицензия

Proprietary. All rights reserved.

---

## Текущий статус (Март 2026)

- Шаги 0–9 реализованы (бот, лендинг, mini app, автопостинг, слоты)
- Все фейковые данные удалены — только верифицированная информация
- Каналы @jogai_br и @jogai_mx настроены, автопостинг слотов активен
- **Блокер запуска:** ожидание реальных affiliate ref_id от партнёрских программ

*jogai.fun | @jogai_bot | Март 2026*
