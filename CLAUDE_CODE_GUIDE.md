# ИНСТРУКЦИЯ: Работа с Claude Code для проекта JOGAI

**Цель:** Полное руководство — от создания папки до рабочего продукта.
**Формат:** Промпты для Claude Code в VS Code. Копируй → вставляй → жди результат.
**Ключевое:** Мультиязычность (i18n) с первого дня. Все строки в JSON, ноль хардкода.

---

## ПОДГОТОВКА (один раз, вручную)

### 1. Создаём папку и репозиторий

```bash
mkdir -p ~/projects/jogai
cd ~/projects/jogai
git init
git remote add origin git@github.com:YOUR_USERNAME/jogai.git
```

### 2. Кладём документы в корень

```
PROJECT_ARCHITECTURE.md
IMPLEMENTATION_PLAN.md
PRD.md
README.md
```

### 3. Создаём .gitignore

```bash
cat > .gitignore << 'EOF'
__pycache__/
*.pyc
.venv/
venv/
node_modules/
dist/
.next/
.env
backend/.env
.vscode/
.idea/
.DS_Store
*.log
EOF
```

### 4. Запускаем Claude Code

```bash
code ~/projects/jogai
# В терминале VS Code:
claude
```

---

## ШАГ 0: ИНИЦИАЛИЗАЦИЯ ПРОЕКТА + i18n

### Промпт 0.1 — Контекст + структура папок

```
Прочитай PROJECT_ARCHITECTURE.md в корне проекта.

Создай ВСЮ структуру папок из раздела 4 "СТРУКТУРА ПРОЕКТА":
- backend/app/ и подпапки: database, bot, bot/handlers, api, services, utils, prompts, locales
- backend/alembic/versions/
- miniapp/src/ и подпапки: api, pages, components, stores, types
- miniapp/public/locales/pt-BR/, miniapp/public/locales/es-MX/
- landing/src/app/[locale]/ и подпапки: casinos, bonuses, guides
- landing/src/components/
- landing/messages/
- nginx/

В каждой Python-папке создай __init__.py.
Покажи дерево папок.
```

### Промпт 0.2 — Backend: конфиг + зависимости + Docker

```
Создай backend-инфраструктуру. Сверяйся с PROJECT_ARCHITECTURE.md разделы 3, 8.

1. backend/requirements.txt — зависимости из IMPLEMENTATION_PLAN.md шаг 0
2. backend/.env.example — ВСЕ переменные из раздела 8 PROJECT_ARCHITECTURE.md (включая DEFAULT_LOCALE=pt_BR, DEFAULT_GEO=BR, TELEGRAM_CHANNEL_BR_ID, TELEGRAM_CHANNEL_MX_ID)
3. backend/Dockerfile — Python 3.11-slim, pip install, CMD uvicorn
4. backend/app/config.py — Pydantic Settings, DEFAULT_LOCALE, DEFAULT_GEO, все переменные

Только эти 4 файла.
```

### Промпт 0.3 — i18n: хелпер + locales

```
Создай систему мультиязычности. Сверяйся с PROJECT_ARCHITECTURE.md раздел 5.

1. backend/app/i18n.py — ПОЛНОСТЬЮ как в разделе 5.1:
   - t(key, locale, **kwargs) — загрузка JSON, кэш, подстановка {param}
   - get_user_locale(language_code, saved_locale) — определение локали
   - get_language_name(locale) — "português brasileiro" / "español latinoamericano"
   - SUPPORTED_LOCALES, DEFAULT_LOCALE

2. backend/app/locales/pt_BR.json — ПОЛНЫЙ файл со ВСЕМИ ключами из раздела 5.1 PROJECT_ARCHITECTURE.md (50+ ключей: welcome, кнопки, анализ, квиз, спорт, трекер, про, ошибки, канал, валюта)

3. backend/app/locales/es_MX.json — ТОЧНАЯ КОПИЯ pt_BR.json (заглушка, перевод на шаге 9). Но с заменой: currency_symbol → "MX$", currency_code → "MXN"

4. backend/app/utils/formatters.py — LOCALE_CONFIG с pt_BR и es_MX:
   - format_currency(amount, locale) → "R$1.500,00" / "MX$1,500.00"
   - format_date(dt, locale)

Проверь: python -c "from app.i18n import t; print(t('welcome', 'pt_BR'))"
```

### Промпт 0.4 — БД: models с мультиязычными полями

```
Создай базу данных. Сверяйся с PROJECT_ARCHITECTURE.md раздел 6.

1. backend/app/database/engine.py — async engine, sessionmaker, get_session()
2. backend/app/database/models.py — ВСЕ 9 таблиц из раздела 6.1.

КРИТИЧНО — мультиязычные поля:
- users: locale VARCHAR(10) DEFAULT 'pt_BR', geo VARCHAR(5) DEFAULT 'BR'
- casinos: description_pt, description_es, spei_supported
- bonuses: title_pt, title_es, max_bonus_currency, verdict_key (не текст!), geo[]
- clicks: locale
- analyses: verdict_key, locale
- bets: bet_currency
- posts: content_pt, content_es, telegram_channel, geo
- sport_picks: pick_description_pt, _es, analysis_pt, _es, geo[]

Все индексы из раздела 6.2 (включая idx_users_locale, idx_users_geo, idx_clicks_locale, idx_posts_geo).

3. backend/alembic.ini
4. backend/alembic/env.py

Не запускай alembic revision.
```

### Промпт 0.5 — main.py + роутеры

```
Создай backend/app/main.py и роутеры-заглушки.

main.py:
- FastAPI app с lifespan
- GET /api/health → {"status": "ok", "service": "jogai"}
- POST /bot/webhook — заглушка
- Подключи роутеры: bonuses, casinos, analyze, quiz, tracker, digest, auth

Роутеры-заглушки:
- router_bonuses.py, router_casinos.py, router_analyze.py, router_quiz.py, router_tracker.py, router_digest.py, router_auth.py

api/deps.py:
- get_session()
- get_current_user() — заглушка
- get_locale(locale: str = Query("pt_BR")) → str — ★ определение локали из query параметра
```

### Промпт 0.6 — Docker Compose + Nginx

```
Создай инфраструктуру. Сверяйся с PROJECT_ARCHITECTURE.md раздел 9.

1. docker-compose.yml:
   - postgres:15 (jogai/jogai_password/jogai)
   - redis:7-alpine
   - backend (build ./backend, env_file, port 8000, volume, --reload)
   - nginx:alpine (port 80)

2. nginx/nginx.conf: /api/ → backend:8000, /bot/ → backend:8000

3. Justfile: dev, down, migrate, makemigration, logs, seed

4. backend/.env — для разработки:
   DATABASE_URL, REDIS_URL, SECRET_KEY=dev-secret, TELEGRAM_BOT_TOKEN=placeholder
   ANTHROPIC_API_KEY=placeholder, LLM_PROVIDER=anthropic
   DEFAULT_LOCALE=pt_BR, DEFAULT_GEO=BR
   TELEGRAM_CHANNEL_BR_ID=placeholder, TELEGRAM_CHANNEL_MX_ID=placeholder
```

### Промпт 0.7 — Проверка

```
Проведи полную проверку шага 0:

1. find . -type f | grep -v node_modules | grep -v __pycache__ | grep -v .git | sort
2. cd backend && python -c "from app.i18n import t; print(t('welcome', 'pt_BR'))"
3. cd backend && python -c "from app.i18n import t; print(t('currency_symbol', 'es_MX'))"
4. cd backend && python -c "from app.utils.formatters import format_currency; print(format_currency(1500, 'pt_BR'))"
5. cd backend && python -c "from app.database.models import Base; print(list(Base.metadata.tables.keys()))"
6. cd backend && python -c "from app.main import app; print('main OK')"
7. docker-compose config

Если ошибки — исправь.
```

### Промпт 0.8 — Сборка + миграция + seed

```
Запусти проект:

1. docker-compose up --build -d
2. docker-compose ps
3. curl http://localhost/api/health
4. Если ошибки — docker-compose logs backend, исправь
5. docker-compose exec backend alembic revision --autogenerate -m "initial"
6. docker-compose exec backend alembic upgrade head
7. docker-compose exec postgres psql -U jogai -d jogai -c "\dt"
   → Должно быть 9 таблиц

8. Создай backend/app/database/seed.py:
   - 4 казино (PIN-UP, 1WIN, BET365, RIVALO) с description_pt, description_es (заглушка), geo=[BR,MX], pix_supported
   - 5-6 бонусов с title_pt, title_es (заглушка), max_bonus_currency=BRL, verdict_key, jogai_score, geo=[BR]
   - 1 sport_pick с pick_description_pt, analysis_pt, geo=[BR]

9. docker-compose exec backend python -m app.database.seed
10. SELECT name, geo FROM casinos; SELECT title_pt, verdict_key, geo FROM bonuses;
```

### Промпт 0.9 — Коммит

```
Закоммить и запуш: "Step 0: Project skeleton + i18n infrastructure (locales, t() helper, multilingual DB)"
```

---

## ШАГ 1: TELEGRAM-БОТ (все строки через t())

```
Прочитай IMPLEMENTATION_PLAN.md раздел "ШАГ 1".
Перечитай PROJECT_ARCHITECTURE.md разделы 4 (bot/), 5 (i18n), 6 (БД).

КРИТИЧЕСКИ ВАЖНО: Ни одна строка текста для пользователя не хардкодится в Python!
Все тексты через t(key, locale). Пример: t("welcome", locale), НЕ "Oi! Eu sou o Jogai...".

Создай:
1. bot/bot.py — Bot + Dispatcher + webhook
2. bot/middlewares.py:
   - UserMiddleware: upsert user в БД с locale (из get_user_locale) и geo
   - LocaleMiddleware: определяет locale → data["locale"]
   - RateLimitMiddleware: Redis, t("error_rate_limit", locale)
3. bot/handlers/start.py — /start с t("welcome", locale), 4 кнопки t("btn_bonuses", locale) etc.
   Deep link: /start ref_CODE → referred_by
4. bot/handlers/bonus.py — /bonus → SELECT bonuses WHERE 'BR' = ANY(geo) ORDER BY jogai_score DESC LIMIT 3
   Карточка: t("bonus_card", locale, casino=..., title=bonus.title_pt, wagering=..., score=..., verdict=t(bonus.verdict_key, locale))
   Валюта: format_currency(bonus.max_bonus_amount, locale)
   Callback click:{bonus_id} → INSERT clicks с locale
5. services/affiliate.py
6. utils/telegram.py — format_bonus_card(bonus, locale), format_casino_card(casino, locale)
7. bot/polling.py — для локального тестирования

Обнови main.py с webhook endpoint.
Проверь: /start → текст из pt_BR.json, /bonus → карточки с R$ и вердикт через t().
```

После: `Закоммить и запуш: "Step 1: Telegram bot with i18n (t() everywhere, locale middleware)"`

---

## ШАГ 2: JOGAI SCORE + AI-АНАЛИЗ

```
Прочитай IMPLEMENTATION_PLAN.md раздел "ШАГ 2".
Перечитай PROJECT_ARCHITECTURE.md разделы 5.4 (AI промпты), 9 (Jogai Score).

Создай:
1. services/llm.py — chat(prompt, msg, language="português brasileiro", currency_symbol="R$")
   Подставляет {language} и {currency_symbol} в промпт. Retry 3x, timeout 30s.
2. services/bonus_analyzer.py:
   - calculate_jogai_score() → возвращает verdict_key (ключ!), НЕ текст
   - parse_bonus_conditions(text, language, currency) — AI парсит
   - analyze_bonus(text, locale) — полная цепочка
3. bot/handlers/analyze.py — /analyze с t("analyze_prompt", locale), AI анализ,
   результат: t("analyze_result_title", locale), t("analyze_wagering", locale, ...), t(verdict_key, locale)
   Валюта: format_currency()
4. api/router_analyze.py — POST /api/analyze {text, locale}
5. prompts/bonus_analysis.md — с {language} и {currency_symbol}

Проверь: "Bonus 200% ate R$2000, wagering x45" → анализ на PT-BR, verdict через t().
```

После: `Закоммить и запуш: "Step 2: Jogai Score + AI analysis (multilingual prompts, verdict_key)"`

---

## ШАГ 3: AI-ПОДБОР КАЗИНО + СПОРТ

```
Прочитай IMPLEMENTATION_PLAN.md раздел "ШАГ 3".

Создай:
1. bot/handlers/casino.py — FSM квиз, ВСЕ вопросы и варианты через t():
   t("casino_q1", locale), t("casino_q1_slots", locale), t("casino_q2_low", locale) etc.
   Суммы в t() уже содержат правильную валюту для ГЕО.
   Результат: казино WHERE user.geo = ANY(geo)
2. services/casino_matcher.py — скоринг, фильтр по geo
3. bot/handlers/sport.py — /sport → sport_picks WHERE user.geo = ANY(geo)
   Текст: pick_description_pt или _es по locale
4. api/router_quiz.py
5. prompts/casino_matching.md, sport_analysis.md — с {language}

Проверь: квиз на PT-BR, казино geo=BR, /sport → Série A.
```

После: `Закоммить и запуш: "Step 3: Casino quiz (i18n) + sport pick (geo-filtered)"`

---

## ШАГ 4: SEO-ЛЕНДИНГ (next-intl)

```
Прочитай IMPLEMENTATION_PLAN.md раздел "ШАГ 4".
Перечитай PROJECT_ARCHITECTURE.md раздел 5.3 (next-intl).

Создай:
1. landing/ — Next.js 14 + next-intl + TailwindCSS
2. landing/messages/pt-BR.json — ВСЕ строки лендинга на PT-BR (hero, таблицы, кнопки, footer, meta)
3. landing/messages/es-MX.json — копия-заглушка
4. landing/src/i18n.ts — next-intl config (locales: ['pt-BR'], defaultLocale: 'pt-BR')
5. landing/next.config.js — withNextIntl
6. landing/src/app/[locale]/page.tsx — Hero + CasinoTable + BonusTable + TelegramCTA
   Контент: description_pt / description_es по locale, валюта по locale
   <html lang={locale}>
7. landing/src/app/[locale]/layout.tsx
8. Компоненты: CasinoTable, BonusTable, JogaiScoreBadge, TelegramCTA, Header, Footer, LocaleSwitcher (скрыт при 1 locale)
9. SEO: meta tags, OG — на языке locale
10. landing/Dockerfile, обновить docker-compose.yml + nginx.conf

Стиль: тёмная тема, mobile-first, гемблинг-эстетика.
Проверь: localhost/pt-BR/ → лендинг, <html lang="pt-BR">, тексты из messages.
```

После: `Закоммить и запуш: "Step 4: SEO landing (next-intl, /pt-BR/, casino table)"`

---

## ШАГ 5: АВТОПОСТИНГ CELERY

```
Прочитай IMPLEMENTATION_PLAN.md раздел "ШАГ 5".

Создай:
1. celery_app.py — config + beat
2. services/content_generator.py — generate_bonus_post(bonus, locale) — AI на {language}
3. services/channel_poster.py — dict CHANNELS = {"BR": {id, locale: "pt_BR"}}
   Фаза 3 добавит "MX". Постит в канал: t("channel_bonus_day", locale, ...) + format_currency()
4. prompts/content_post.md — с {language}
5. Обновить docker-compose: celery worker + beat

Проверь: задача → пост в канал BR на PT-BR.
```

После: `Закоммить и запуш: "Step 5: Celery autoposting (multi-channel ready, i18n)"`

---

## ШАГ 6: MINI APP (react-i18next)

```
Прочитай IMPLEMENTATION_PLAN.md раздел "ШАГ 6".
Перечитай PROJECT_ARCHITECTURE.md раздел 5.2 (react-i18next).

Создай:
1. miniapp/ — React 18 + Vite + TailwindCSS + react-i18next + i18next-http-backend
2. miniapp/src/i18n.ts — определяет язык из Telegram WebApp language_code:
   'pt' → 'pt-BR', 'es' → 'es-MX', fallback 'pt-BR'
3. miniapp/public/locales/pt-BR/translation.json — ВСЕ строки Mini App
4. miniapp/public/locales/es-MX/translation.json — копия-заглушка
5. pages/Home.tsx — {t('greeting', {name})}, бонусы ?geo=BR&locale=pt-BR
6. pages/Analyze.tsx — POST /api/analyze {text, locale}
7. Компоненты: BonusCard с {t('btn_get_bonus')}, JogaiScore, AnalysisResult
   Валюта: вспомогательная функция formatCurrency(amount, locale)
8. api/client.ts — axios, Telegram initData
9. backend/api/router_auth.py — POST /api/auth/telegram → JWT + user.locale
10. Обновить docker-compose + nginx

Стиль: мобильный, Telegram-like, тёмная тема.
ВСЕ ТЕКСТЫ ЧЕРЕЗ {t('key')}. Ноль хардкода.

Проверь: Mini App определяет PT-BR, тексты из translation.json.
```

После: `Закоммить и запуш: "Step 6: Mini App (react-i18next, dashboard, analyzer)"`

---

## ШАГ 7: MINI APP — КВИЗ + ДАЙДЖЕСТ + РЕФЕРАЛЫ

```
Прочитай IMPLEMENTATION_PLAN.md раздел "ШАГ 7".

Создай:
1. pages/Quiz.tsx — вопросы из translation.json: {t('casino_q1')}, {t('casino_q1_slots')}
2. pages/Digest.tsx — бонусы geo + locale пользователя
3. backend/services/digest_builder.py — send_digest: для каждого user → t() на user.locale
4. bot/handlers/referral.py — t("referral_your_link", locale), t("referral_coins_balance", locale, coins=N)

Проверь: квиз из translation.json, дайджест по ГЕО/locale.
```

После: `Закоммить и запуш: "Step 7: Quiz, digest, referrals (all i18n)"`

---

## ШАГ 8: ТРЕКЕР СТАВОК (мультивалюта)

```
Прочитай IMPLEMENTATION_PLAN.md раздел "ШАГ 8".

Создай:
1. pages/Tracker.tsx — {t('tracker_stats_title')}, валюта formatCurrency(amount, locale)
2. api/router_tracker.py — bet_currency = BRL/MXN по user.geo
3. bot/handlers/tracker.py — /bet, /stats с t() и format_currency()
4. Статистика: profit в валюте пользователя

Проверь: ставки с BRL для BR, интерфейс на PT-BR.
```

После: `Закоммить и запуш: "Step 8: Bet tracker (multi-currency, i18n)"`

---

## ШАГ 9: МЕКСИКА (es-MX) + PRO

```
Прочитай IMPLEMENTATION_PLAN.md раздел "ШАГ 9".

ЭТОТ ШАГ — НОЛЬ ИЗМЕНЕНИЙ КОДА. Только переводы и данные:

1. ПЕРЕВЕСТИ backend/app/locales/es_MX.json — ВСЕ значения на испанский
2. ПЕРЕВЕСТИ miniapp/public/locales/es-MX/translation.json — ВСЕ значения
3. ПЕРЕВЕСТИ landing/messages/es-MX.json — ВСЕ значения
4. Обновить landing/next.config.js — locales: ['pt-BR', 'es-MX']
5. Seed MX данные:
   - Казино с geo включающим MX, spei_supported=True
   - Бонусы: title_es, max_bonus_currency=MXN, geo=[MX]
   - Sport picks: Liga MX, pick_description_es, analysis_es, geo=[MX]
6. TELEGRAM_CHANNEL_MX_ID → .env
7. Раскомментировать "MX" в channel_poster.py CHANNELS
8. Показать LocaleSwitcher в лендинге (было скрыто)

PRO подписка:
9. bot/handlers/pro.py — Telegram Stars, t("pro_title", locale), t("pro_price", locale, ...)
10. services/pro.py — управление

ПРОВЕРЬ ВСЁ:
- Бот: language_code='es' → ответы на ES, казино MX, MX$
- Mini App: es-MX → тексты на испанском
- Лендинг: /es-MX/ работает
- Канал MX: посты на ES
- PT-BR: ВСЁ по-прежнему работает (регрессия!)
```

После: `Закоммить и запуш: "Step 9: Mexico launch (es-MX translations, MX seed, PRO subscription)"`

---

## ШАГ 10: ВЕБ-ПЛАТФОРМА + SEO

```
Прочитай IMPLEMENTATION_PLAN.md раздел "ШАГ 10".

Создай:
1. [locale]/casinos/page.tsx, [locale]/casinos/[slug]/page.tsx — description_{lang} по locale
2. [locale]/bonuses/page.tsx — title_{lang}, валюта по locale
3. [locale]/guides/ — статьи
4. JSON-LD — локализованный
5. Sitemap.xml — с hreflang alternates для pt-BR и es-MX
6. <link rel="alternate" hreflang="pt-BR" />, <link hreflang="es-MX" />
7. LocaleSwitcher — теперь видим (2 языка)

Проверь: /pt-BR/casinos и /es-MX/casinos — разный контент, hreflang.
```

После: `Закоммить и запуш: "Step 10: Web platform (SEO, hreflang, two locales)"`

---

## ШАГ 11: АВТОМАТИЗАЦИЯ + ДЕПЛОЙ

```
Прочитай IMPLEMENTATION_PLAN.md раздел "ШАГ 11".

Создай:
1. services/bonus_parser.py — парсинг → AI → title_pt + title_es + verdict_key + geo
2. docker-compose.prod.yml, Caddyfile, scripts/deploy.sh, scripts/backup.sh

Финальный чеклист:
- [ ] Все env production
- [ ] BOT_TOKEN, API ключи
- [ ] Партнёрские ссылки production
- [ ] SSL для jogai.fun
- [ ] Webhook
- [ ] pg_dump backup
- [ ] Uptime Kuma
- [ ] locales/pt_BR.json — вычитка нативным PT спикером
- [ ] locales/es_MX.json — вычитка нативным ES спикером
- [ ] miniapp locales — вычитка
- [ ] landing messages — вычитка
- [ ] Seed данные → реальные (оба ГЕО)
```

После: `Закоммить и запуш: "Step 11: Automation, deploy, final i18n review"`

---

## КРАТКАЯ ШПАРГАЛКА

| Действие | Команда |
|----------|---------|
| Коммит + пуш | `Закоммить и запуш: "сообщение"` |
| Логи backend | `docker-compose logs backend --tail 50` |
| Починить ошибку | `Вот ошибка: [лог]. Исправь.` |
| Остановить | `Стоп. Только шаг N. Не забегай вперёд.` |
| Пересоздать файл | `Пересоздай файл X. Сверяйся с PROJECT_ARCHITECTURE.md.` |
| Статус | `docker-compose ps && curl http://localhost/api/health` |
| Рестарт | `docker-compose down && docker-compose up --build -d` |
| Миграция | `Создай миграцию alembic: "описание"` |
| Тест бота | `docker-compose exec backend python -m app.bot.polling` |
| Seed | `docker-compose exec backend python -m app.database.seed` |
| Проверить i18n | `docker-compose exec backend python -c "from app.i18n import t; print(t('welcome', 'pt_BR'))"` |
| Проверить валюту | `docker-compose exec backend python -c "from app.utils.formatters import format_currency; print(format_currency(1500, 'pt_BR'))"` |

---

## ТАЙМИНГ

```
НЕДЕЛЯ 1:   Шаг 0-2    ~12-16ч
НЕДЕЛЯ 2:   Шаг 3-5    ~11-14ч
НЕДЕЛЯ 3:   Шаг 6-7    ~11-14ч
НЕДЕЛЯ 4:   Шаг 8-9    ~9-11ч
НЕДЕЛЯ 5:   Шаг 10-11  ~9-12ч
ИТОГО: ~53-67 часов
```

---

## СОВЕТЫ

1. **t() ВЕЗДЕ.** Если видишь строку на PT в Python/React/Next — это баг. Замени на t(key, locale).
2. **verdict_key, не текст.** Jogai Score возвращает "verdict_good", хендлер делает t("verdict_good", locale).
3. **format_currency() ВЕЗДЕ.** Никаких "R$" в коде. Только format_currency(amount, locale).
4. **Шаг 9 = перевод, не код.** Если на шаге 9 нужно менять Python/React код — значит i18n сделан неправильно. Вернись и исправь.
5. **Тестируй оба locale.** После каждого шага: `t("welcome", "pt_BR")` + `t("welcome", "es_MX")`.
6. **Seed данные мультиязычные.** Каждый бонус: title_pt + title_es. Каждое казино: description_pt + description_es.
7. **AI промпты с {language}.** Никогда: "Responda em português". Всегда: "Responda em {language}".
