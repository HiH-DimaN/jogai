# Инструкции для Claude Code

## Контекст проекта
Перед выполнением любой задачи прочитай PROJECT_ARCHITECTURE.md — там полная архитектура.
План реализации — в IMPLEMENTATION_PLAN.md. Выполняй шаги строго последовательно.
Стратегический план — в JOGAI_Полный_Стратегический_План.md.
Готовые промпты для каждого шага — в CLAUDE_CODE_GUIDE.md.

## О проекте
**Jogai** — мультиканальная AI-платформа для гемблинг-аудитории в Латинской Америке (LATAM).
Монетизация: CPA + RevShare (gambling affiliate).
Мультиязычность (i18n) заложена с первого дня: PT-BR → ES-MX → ES.

## Правила
1. Перед каждым шагом перечитывай PROJECT_ARCHITECTURE.md
2. Не забегай вперёд — только текущий шаг
3. После каждого шага проект должен запускаться
4. Используй async везде (Python)
5. Промпты/шаблоны храни в файлах, не хардкодь
6. Все пользовательские строки — через i18n (t(key, locale)), ноль хардкода
7. Валюта — через format_currency(amount, locale), никаких "R$" в коде
8. AI-промпты — с {language} и {currency_symbol}, не хардкодить язык
9. verdict_key — возвращай ключ i18n, не текст
10. Коммить после каждого шага
11. Язык интерфейса пользователя: PT-BR (фаза 1), ES-MX (фаза 3). Код и комментарии: английский. Документация: русский.

## Стек
- **Backend:** Python 3.11+, FastAPI, aiogram 3.x, SQLAlchemy 2.0 (async), Celery, PostgreSQL 15, Redis 7
- **Mini App:** React 18, Vite, TailwindCSS, Zustand, react-i18next
- **Лендинг:** Next.js 14, TailwindCSS, next-intl
- **AI:** Claude API / GPT-4o-mini (ответ на {language} пользователя)
- **Деплой:** Docker Compose, Nginx, Hetzner VPS

## Структура проекта
```
jogai/
├── backend/
│   ├── app/
│   │   ├── config.py           # Pydantic Settings
│   │   ├── main.py             # FastAPI app
│   │   ├── i18n.py             # хелпер t(key, locale)
│   │   ├── locales/            # pt_BR.json, es_MX.json
│   │   ├── database/           # models, engine, seed
│   │   ├── bot/                # aiogram bot + handlers
│   │   ├── api/                # FastAPI routers
│   │   ├── services/           # бизнес-логика
│   │   ├── utils/              # formatters, telegram helpers
│   │   └── prompts/            # AI-промпты с {language}
│   ├── alembic/
│   ├── requirements.txt
│   └── Dockerfile
├── miniapp/                    # React + react-i18next
│   ├── public/locales/         # pt-BR/, es-MX/
│   └── src/
├── landing/                    # Next.js + next-intl
│   ├── messages/               # pt-BR.json, es-MX.json
│   └── src/app/[locale]/
├── nginx/nginx.conf
├── docker-compose.yml
├── CLAUDE.md                   # ← этот файл
├── PROJECT_ARCHITECTURE.md
├── IMPLEMENTATION_PLAN.md
├── PRD.md
├── README.md
├── CLAUDE_CODE_GUIDE.md
└── JOGAI_Полный_Стратегический_План.md
```

## Ключевые принципы i18n
- Бот: `t("welcome", locale)` → locales/pt_BR.json
- Mini App: `{t('greeting')}` → react-i18next → public/locales/pt-BR/translation.json
- Лендинг: `useTranslations()` → next-intl → messages/pt-BR.json
- БД: мультиязычные поля: title_pt, title_es, description_pt, description_es
- AI: промпты с `{language}` и `{currency_symbol}`
- Jogai Score: возвращает verdict_key → хендлер делает t(verdict_key, locale)

## Переменные окружения
Полный список — в PROJECT_ARCHITECTURE.md раздел 8.
Ключевые: DATABASE_URL, REDIS_URL, TELEGRAM_BOT_TOKEN, ANTHROPIC_API_KEY, DEFAULT_LOCALE=pt_BR, DEFAULT_GEO=BR.

## Прогресс реализации

### Шаг 0 — Скелет проекта + i18n
- [x] **0.1** — Структура папок: backend/, miniapp/, landing/, nginx/ + `__init__.py`
- [x] **0.2** — Backend: requirements.txt, .env.example, Dockerfile, config.py
- [x] **0.3** — i18n: i18n.py, locales/pt_BR.json, locales/es_MX.json, formatters.py
- [x] **0.4** — БД: models.py (9 таблиц, i18n-поля, индексы), engine.py, alembic
- [x] **0.5** — main.py, deps.py, 7 роутеров-заглушек
- [x] **0.6** — docker-compose.yml, nginx.conf, Justfile, .env (порты: backend=8001, nginx=8080)
- [x] **0.8** — Alembic migration (9 таблиц), seed (3 казино, 6 бонусов, 1 sport_pick)

### Шаг 1 — Telegram-бот (все строки через t())
- [x] bot.py, middlewares (User/Locale/RateLimit), handlers (start, bonus)
- [x] /start → t("welcome") + 4 кнопки, deep link referral
- [x] /bonus → top-3 по jogai_score WHERE geo, карточки через t(), клики с locale
- [x] services/affiliate.py, utils/telegram.py, bot/polling.py
- [x] main.py обновлён: webhook → aiogram dispatcher

### Шаг 2 — Jogai Score + AI-анализ
- [x] services/llm.py: chat() с {language}/{currency_symbol}, Anthropic + OpenAI, retry 3x
- [x] services/bonus_analyzer.py: calculate_jogai_score() → verdict_key (ключ i18n, не текст!)
- [x] bot/handlers/analyze.py: /analyze с FSM, все строки через t(), verdict через t(verdict_key)
- [x] api/router_analyze.py: POST /api/analyze с Pydantic моделями
- [x] prompts/bonus_analysis.md: шаблон с {language} и {currency_symbol}

### Шаг 3 — AI-подбор казино + спорт
- [x] bot/handlers/casino.py: 5-step FSM квиз, все вопросы/варианты через t()
- [x] services/casino_matcher.py: скоринг + фильтр по geo
- [x] bot/handlers/sport.py: /sport → sport_picks WHERE geo, pick_description_pt/es
- [x] api/router_quiz.py: POST /quiz/start (локализованные вопросы), POST /quiz/result
- [x] prompts/casino_matching.md, sport_analysis.md с {language}

### Шаг 4 — SEO-лендинг (next-intl)
- [x] Next.js 14 + next-intl: package.json, next.config.js (output: standalone), tsconfig.json
- [x] TailwindCSS: jogai-bg/card/border/accent/green/red/text/muted (dark theme)
- [x] i18n: src/i18n.ts, src/middleware.ts (locales: pt-BR, es-MX, prefix: always)
- [x] navigation.ts: createSharedPathnamesNavigation (Link, useRouter, usePathname)
- [x] messages/pt-BR.json, messages/es-MX.json — полные переводы (meta, hero, casinos, bonuses, features, telegram, header, footer)
- [x] layout.tsx: <html lang={locale}>, meta/OG теги, hreflang alternates, NextIntlClientProvider
- [x] page.tsx: Hero + Features (4 карточки) + CasinoTable + BonusTable + TelegramCTA
- [x] Компоненты: CasinoTable, BonusTable, JogaiScoreBadge, TelegramCTA, Header, Footer, LocaleSwitcher
- [x] verdict_key через t() → "EXCELENTE" / "BOM NEGÓCIO" — не хардкод!
- [x] Dockerfile (node:20-slim, multi-stage), docker-compose.yml + nginx.conf обновлены
- [x] Проверено: /pt-BR → lang="pt-BR", /es-MX → lang="es-MX", /api/health → 200
