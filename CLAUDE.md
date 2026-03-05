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

## !!! ГЛАВНОЕ ПРАВИЛО — ТОЛЬКО РЕАЛЬНЫЕ ДАННЫЕ !!!
**Jogai — это гемблинг-проект. Люди рискуют своими деньгами на основе информации из наших каналов, чатбота и лендинга.**

**ЗАПРЕЩЕНО** показывать пользователям вымышленные, приблизительные или непроверенные данные:
- Бонусы (проценты, суммы, wagering, дедлайны) — ТОЛЬКО верифицированные из официальных источников
- Казино — ТОЛЬКО реально работающие в целевом регионе
- Слоты (RTP, volatility) — ТОЛЬКО из документации провайдеров
- Спортивные прогнозы — ТОЛЬКО на основе реальных данных

**Каждый бонус в БД ОБЯЗАН иметь источник** (официальный сайт казино, review-сайт типа legalbet.mx, sportytrader.com и т.д.).
Если данные нельзя верифицировать — их НЕ ДОЛЖНО БЫТЬ в системе. Лучше показать пустое состояние, чем фейковые данные.

**Без реальных, достоверных данных нет смысла реализовывать и запускать этот проект.**

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
- [x] **0.8** — Alembic migration (9 таблиц), seed (4 казино, 12 слотов — только верифицированные данные)

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
- [x] page.tsx: Hero + Features (4 карточки) + CasinoTable + HowItWorks + TelegramCTA
- [x] Компоненты: CasinoTable, HowItWorks, JogaiScoreBadge, TelegramCTA, Header, Footer, LocaleSwitcher
- [x] verdict_key через t() → "EXCELENTE" / "BOM NEGÓCIO" — не хардкод!
- [x] Dockerfile (node:20-slim, multi-stage), docker-compose.yml + nginx.conf обновлены
- [x] Проверено: /pt-BR → lang="pt-BR", /es-MX → lang="es-MX", /api/health → 200

### Шаг 5 — Автопостинг Celery (мульти-канал)
- [x] celery_app.py: Redis broker, beat schedule (09:00 bonus, 14:00 slot, 18:00 sport, hourly expire)
- [x] services/content_generator.py: AI generate_bonus_post + fallback шаблон, generate_sport_post
- [x] services/channel_poster.py: CHANNELS dict {BR: {id, locale}, MX: {id, locale}} — оба канала активны
- [x] Задачи: task_post_bonus_day, task_post_sport_pick, task_post_slot_review, task_post_weekly_top, task_deactivate_expired
- [x] prompts/content_post.md: шаблон с {language} и {currency_symbol}
- [x] docker-compose.yml: celery-worker + celery-beat контейнеры
- [x] Все тексты через t() + format_currency(), вердикт через t(verdict_key, locale)
- [x] Проверено: worker ready (4 tasks), beat started, bonus_day → пост в БД на PT-BR

### Шаг 6 — Mini App (react-i18next, dashboard, analyzer)
- [x] React 18 + Vite + TailwindCSS: package.json, vite.config.ts, tsconfig.json, tailwind.config.js
- [x] Тёмная тема jogai (bg/card/border/accent/green/red/text/muted), mobile-first
- [x] i18n: src/i18n.ts (getTelegramLocale() → pt-BR/es-MX), i18next-http-backend
- [x] public/locales/pt-BR/translation.json, es-MX/translation.json (~40 ключей)
- [x] API client: axios + X-Telegram-Init-Data header + locale в params
- [x] Types: Bonus, Casino, AnalysisResult, UserData, AuthResponse
- [x] Zustand store: user, token, isAuthenticated
- [x] Utils: formatCurrency(amount, locale) → R$/MX$ с правильными разделителями
- [x] Components: Layout (header + nav), BonusCard, JogaiScore (color by score), AnalysisResult
- [x] Pages: Home (greeting + бонусы из GET /api/bonuses), Analyze (форма → POST /api/analyze)
- [x] App.tsx: Telegram WebApp init (ready/expand/colors), auto-auth, BrowserRouter
- [x] Backend router_auth.py: POST /auth/telegram (HMAC-SHA256 initData → JWT), GET /auth/me
- [x] Backend router_bonuses.py: GET /bonuses?geo&locale → DB query, title_pt/es по locale, format_currency
- [x] Backend deps.py: get_current_user (HTTPBearer + JWT decode)
- [x] Dockerfile (node:20-slim multi-stage → nginx:alpine, SPA fallback)
- [x] docker-compose.yml: miniapp service, nginx.conf: /miniapp/ → miniapp:5173
- [x] Все тексты через t() — ноль хардкода, verdict_key → t(verdict_key)
- [x] TypeScript чистый (tsc --noEmit), Vite build OK

### Шаг 7 — Mini App: Quiz + Digest + Referrals (all i18n)
- [x] i18n: +29 ключей pt-BR + es-MX (nav_quiz/digest/referrals, quiz_*, digest_*, referral_*)
- [x] Types: +QuizOption, QuizQuestion, QuizResult, ReferralStats; +referral_code в UserData
- [x] CasinoResultCard.tsx: карточка казино (match%, бонус, deposit, withdrawal, affiliate link)
- [x] Quiz.tsx: 5-step quiz → POST /api/quiz/start + /result → CasinoResultCard list
- [x] Digest.tsx: GET /api/digest → BonusCard list по geo юзера (auth required)
- [x] Referrals.tsx: GET /api/referrals/stats → ссылка + монеты + copy + Telegram share
- [x] App.tsx: +3 routes (/quiz, /digest, /referrals)
- [x] Layout.tsx: nav 2→5 кнопок (Home/Quiz/Analyze/Digest/Referrals)
- [x] Backend router_referrals.py: GET /referrals/stats (auth) → code, link, coins, count
- [x] Backend router_digest.py: переписан из заглушки → top-5 бонусов по user.geo (auth)
- [x] Backend router_auth.py: +referral_code в UserResponse
- [x] Bot handlers/referral.py: /referral → ссылка + монеты + reward text
- [x] Bot polling.py + main.py: +referral_router зарегистрирован
- [x] Celery digest_builder.py: send_digest() → DM активным юзерам (30d), task_send_digest
- [x] celery_app.py: +include digest_builder, +beat "send-daily-digest" 08:00 BRT
- [x] TypeScript чистый (tsc --noEmit), Vite build OK, Python syntax OK

### Шаг 8 — Трекер ставок (мультивалюта)
- [x] i18n: +30 ключей pt-BR + es-MX (nav_tracker, tracker_*)
- [x] Types: +BetData, BetCreateData, BetStats
- [x] Backend router_tracker.py: GET /tracker/bets, POST /tracker/bets, GET /tracker/stats (auth, bet_currency по user.geo)
- [x] Bot handlers/tracker.py: /bet (FSM ввод) + /stats (ROI, win rate, bankroll recommendation)
- [x] Bot polling.py + main.py: +tracker_router зарегистрирован
- [x] Tracker.tsx: форма новой ставки (game_type, name, amount, result), карточки статистики (profit, ROI, win rate, best/worst game), список последних ставок
- [x] App.tsx: +route /tracker
- [x] Layout.tsx: nav 5→6 кнопок (Home/Quiz/Analyze/Tracker/Digest/Referrals), компактный стиль
- [x] Валюта через formatCurrency() — BRL для BR, MXN для MX
- [x] TypeScript чистый (tsc --noEmit), Vite build OK (133 модуля), Python syntax OK

### Шаг 9 — Слоты + удаление фейковых данных
- [x] Slot модель: name, provider, rtp, volatility, max_win, features, tip_pt/es, best_casino_id, geo, source
- [x] Alembic миграция: таблица slots
- [x] API router_slots.py: GET /slots?geo → слоты с RTP, tip, casino name
- [x] services/slot_parser.py: AI-парсер описаний слотов + генератор tips
- [x] prompts/slot_parsing.md, slot_tip.md: AI-промпты для парсинга и tips
- [x] Celery: task_post_slot_review (ежедневно 18:00), task_post_weekly_top (суббота)
- [x] Seed: 12 слотов (Pragmatic Play, NetEnt, Play'n GO, Hacksaw) — верифицированный RTP
- [x] **Удалены все фейковые данные:** 12 бонусов (BR+MX), 2 sport picks
- [x] Лендинг: BonusTable → HowItWorks, CasinoTable без фейковых score/bonus колонок
- [x] Лендинг: /bonuses и /casinos/[slug] — пустое состояние с CTA на Telegram-бота
- [x] Бот: /bonus и /sport — нормальное пустое состояние с кнопкой /analyze
- [x] Каналы: BR (-1003872325982) и MX (-1003704249294) настроены
- [x] .env.prod добавлен в .gitignore

### Шаг 10 — Парсер бонусов + данные MX + лендинг с бонусами
- [x] Seed: +2 MX казино (Caliente, Codere) — SPEI, без PIX, geo=["MX"]
- [x] Seed: +9 welcome-бонусов (4 BR + 5 MX) с Jogai Score — верифицированные офферы
- [x] bonus_parser.py: полный переписан — парсинг review/affiliate сайтов (askgamblers, casino.org, oddschecker) вместо casino-сайтов (были 403)
- [x] bonus_parsing.md: +casino_name, фокус на наших казино
- [x] casino_matcher.py: fix min_deposits (мультивалюта) для MX
- [x] config.py + .env.example: +caliente_ref_id, +codere_ref_id
- [x] Лендинг page.tsx: +секция "Лучшие бонусы" (BonusTable) на главной странице
- [x] API: /bonuses?geo=BR → 4 бонуса, /bonuses?geo=MX → 5 бонусов
- [x] API: /casinos?geo=MX → 6 казино (4 общих + Caliente + Codere)
- [x] Лендинг /pt-BR показывает бонусы + казино с Jogai Score
- [x] Лендинг /es-MX показывает MX бонусы + 6 казино
- [x] Каналы: bonus_day теперь имеет данные для постинга (BR + MX)
- [x] Задеплоено и проверено на проде

### Шаг 11 — Контент-автоматизация + двухмодельный AI
- [x] services/sport_odds_parser.py: The Odds API → AI-анализ (gpt-4o) → sport_picks в БД
- [x] services/education_poster.py: 16 тем, AI-генерация, автоматическая ротация
- [x] services/comparison_poster.py: автоподбор пар казино из БД, AI-сравнение
- [x] services/dm_alerts.py: алерты в личку (новый бонус score>=8, экспирация по кликам)
- [x] prompts/sport_odds_analysis.md, education_post.md, casino_comparison.md
- [x] i18n: +dm_new_bonus, +dm_expiring_bonus (pt_BR + es_MX)
- [x] Celery: +5 задач (fetch-sport-picks, post-education, post-comparison, alert-new-bonuses, alert-expiring-bonuses)
- [x] Двухмодельный AI: gpt-4o-mini (посты, анализ) + gpt-4o (парсинг HTML, образование, спорт, сравнения)
- [x] llm.py: параметр heavy=True для сложных задач, timeout 60s
- [x] config.py: llm_model + llm_model_heavy
- [x] engine.py: pool_pre_ping=True (защита от stale DB connections)
- [x] DM rate limit: max 2 алерта/юзер/день
- [x] Всего 13 Celery-задач, worker ready, задеплоено

## Чек-лист запуска

### Блокеры (без них НЕ запускаем)
- [ ] **Affiliate ref_id** — получить реальные коды от партнёрских программ:
  - [ ] PIN-UP (BR + MX)
  - [ ] 1WIN (BR + MX)
  - [ ] Bet365 (MX)
  - [ ] Rivalo (MX)
  - [ ] Caliente (MX)
  - [ ] Codere (MX)
  - После получения: вставить в .env на сервере, обновить seed.py → restart backend
- [ ] **Логотипы казино** — загрузить реальные лого (сейчас URL-заглушки)

### Желательно до запуска
- [ ] Telegram каналы @jogai_br / @jogai_mx — описание, аватар, закреплённый пост
- [ ] Bot description + /setcommands в @BotFather
- [ ] Privacy Policy / Terms на лендинге (требование Telegram для Mini App)
- [ ] Google Search Console + sitemap.xml (SEO-индексация)

### Работает (проверено на проде)
- [x] Сервер: 8 контейнеров, всё healthy
- [x] Landing: /pt-BR (200), /es-MX (200), SSL (Caddy)
- [x] API: casinos BR=4, MX=6 | bonuses BR=2, MX=6 | slots=12
- [x] Bot: @jogai_bot — webhook активен
- [x] Celery: 13 задач, beat + worker running
- [x] AI: gpt-4o-mini + gpt-4o (OpenAI key OK)
- [x] Odds API: ключ подключён
- [x] DB: pool_pre_ping=True, защита от stale connections
