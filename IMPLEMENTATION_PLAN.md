# JOGAI — IMPLEMENTATION PLAN

**Проект:** Jogai — AI Gambling Assistant для LATAM
**Версия:** 2.0 | Февраль 2026

---

## ОБЩИЕ ПРАВИЛА ДЛЯ АГЕНТА

> Эти правила действуют на протяжении ВСЕХ шагов. Перечитывай при каждой новой сессии.

1. **Контекст:** Перед каждым шагом перечитывай PROJECT_ARCHITECTURE.md — там полная архитектура, БД, API, i18n.
2. **Последовательность:** Не забегай вперёд. Шаг N не использует код из шага N+1.
3. **Работоспособность:** После каждого шага проект должен запускаться (`docker-compose up --build`).
4. **Async:** Используй async/await везде в Python (SQLAlchemy, aiogram, FastAPI).
5. **i18n:** ВСЕ пользовательские строки — через `t(key, locale)`. Ноль хардкода текста.
6. **Валюта:** Только через `format_currency(amount, locale)`. Никаких "R$" или "MX$" в коде.
7. **AI-промпты:** Всегда с `{language}` и `{currency_symbol}`. Не хардкодить язык.
8. **verdict_key:** Jogai Score возвращает ключ i18n (`"verdict_good"`), не текст. Хендлер делает `t(verdict_key, locale)`.
9. **Промпты в файлах:** AI-промпты храни в `backend/app/prompts/*.md`, не в коде.
10. **Языки:** Код и комментарии — английский. Пользовательский интерфейс — PT-BR/ES-MX. Документация — русский.
11. **Коммиты:** После каждого завершённого шага — коммит с описанием.
12. **Проверки:** В конце каждого шага выполни все проверки из раздела «Проверки».

---

## ОБЗОР ШАГОВ

```
ШАГ 0:  Скелет проекта + i18n инфраструктура                  ~4-5 часов
ШАГ 1:  Telegram-бот — /start, /bonus (через t())             ~4-6 часов
ШАГ 2:  Jogai Score + AI-анализ (ответ на {language})          ~4-5 часов
ШАГ 3:  AI-подбор казино + /sport                              ~3-4 часа
ШАГ 4:  SEO-лендинг (next-intl, /pt-BR/)                      ~4-5 часов
ШАГ 5:  Автопостинг Celery (мульти-канал)                      ~4-5 часов
ШАГ 6:  Mini App — дашборд + анализатор (react-i18next)        ~6-8 часов
ШАГ 7:  Mini App — квиз + дайджест + рефералы                  ~5-6 часов
ШАГ 8:  Трекер ставок + банкролл (мультивалюта)                ~5-6 часов
ШАГ 9:  Мексика (es_MX.json + seed MX) + PRO                   ~4-5 часов
ШАГ 10: Веб-платформа + SEO                                    ~5-7 часов
ШАГ 11: Автоматизация + деплой                                  ~4-5 часов
ИТОГО: ~53-67 часов
```

---

## ШАГ 0: СКЕЛЕТ ПРОЕКТА + i18n

**Цель:** Инфраструктура, БД с мультиязычными полями, i18n хелпер, Docker.

### Что создаём

1. **Структура папок** — backend/, miniapp/, landing/, nginx/ (все подпапки из PROJECT_ARCHITECTURE раздел 4)
2. **backend/requirements.txt** — fastapi, aiogram, sqlalchemy, anthropic, etc.
3. **backend/app/config.py** — Pydantic Settings, DEFAULT_LOCALE, DEFAULT_GEO
4. **backend/app/database/models.py** — ВСЕ таблицы с мультиязычными полями: `title_pt`/`title_es`, `description_pt`/`description_es`, `verdict_key`, `locale`, `geo`
5. **backend/app/i18n.py** — хелпер `t(key, locale, **kwargs)`, `get_user_locale()`, `get_language_name()`
6. **backend/app/locales/pt_BR.json** — ВСЕ строки бота на PT-BR (50+ ключей)
7. **backend/app/locales/es_MX.json** — копия pt_BR.json (заглушка, перевод на шаге 9)
8. **backend/app/utils/formatters.py** — `format_currency(amount, locale)`, `format_date()`
9. **backend/app/main.py** — FastAPI + health + заглушки роутеров
10. **backend/app/api/deps.py** — `get_locale()` из query/header
11. **docker-compose.yml**, **nginx.conf**, **alembic**, **.gitignore**, **Justfile**

### Проверки

- [ ] Docker контейнеры running, /api/health → ok
- [ ] `t("welcome", "pt_BR")` → приветствие на PT-BR
- [ ] `t("welcome", "es_MX")` → то же (заглушка, перевод позже)
- [ ] `format_currency(1500, "pt_BR")` → `"R$1.500,00"`
- [ ] Alembic: 9 таблиц с полями locale, geo, title_pt, title_es, verdict_key

---

## ШАГ 1: TELEGRAM-БОТ — БАЗОВЫЙ

**Цель:** Бот на PT-BR. Все строки через `t(key, locale)`. Ноль хардкода.

### Что создаём

1. **bot/bot.py** — Bot + Dispatcher + webhook
2. **bot/middlewares.py** — UserMiddleware (upsert user с locale/geo), LocaleMiddleware (определяет locale → `data["locale"]`), RateLimitMiddleware
3. **bot/handlers/start.py** — `/start` с `t("welcome", locale)` + 4 inline-кнопки из locales + deep link referral
4. **bot/handlers/bonus.py** — `/bonus` → топ-3 из БД WHERE geo, текст `title_pt`/`title_es` по locale, вердикт `t(verdict_key, locale)`, валюта `format_currency(amount, locale)`
5. **services/affiliate.py** — `get_affiliate_link(casino_slug, user_id)`
6. **utils/telegram.py** — `format_bonus_card(bonus, locale)`, `format_casino_card(casino, locale)`
7. **database/seed.py** — 3 казино + 5-6 бонусов с title_pt, description_pt, verdict_key, geo

### Ключевое правило

Каждый хендлер получает `locale` из middleware и передаёт в `t()`:
```python
async def cmd_start(message: Message, locale: str):
    await message.answer(t("welcome", locale))
```

### Проверки

- [ ] /start → текст из locales/pt_BR.json
- [ ] /bonus → карточки с R$ валютой, вердикт через t(verdict_key)
- [ ] Клик → запись в clicks с locale

---

## ШАГ 2: JOGAI SCORE + AI-АНАЛИЗ

**Цель:** AI анализирует бонусы и отвечает на языке пользователя.

### Что создаём

1. **services/llm.py** — `chat(prompt, msg, language=..., currency_symbol=...)` с подстановкой {language} и {currency_symbol} в промпт
2. **services/bonus_analyzer.py** — `calculate_jogai_score()` возвращает `verdict_key` (ключ для i18n); `analyze_bonus(text, locale)` — парсинг + расчёт
3. **bot/handlers/analyze.py** — `/analyze` → AI отвечает на locale, все строки через t()
4. **api/router_analyze.py** — POST /api/analyze с locale в body
5. **prompts/bonus_analysis.md** — содержит `{language}` и `{currency_symbol}`

### Ключевое

AI промпт получает язык: `"Отвечай на {language}"` → `"Отвечай на português brasileiro"`. Jogai Score возвращает `verdict_key="verdict_bad"`, хендлер делает `t("verdict_bad", locale)` → «NAO RECOMENDADO» (PT) или «NO RECOMENDADO» (ES).

### Проверки

- [ ] Анализ бонуса → ответ на PT-BR
- [ ] Verdict через t(), валюта через format_currency()

---

## ШАГ 3: AI-ПОДБОР КАЗИНО + СПОРТ

**Цель:** Квиз из locales, казино фильтруются по ГЕО, спорт по ГЕО.

### Что создаём

1. **bot/handlers/casino.py** — 5 вопросов через t(): `t("casino_q1", locale)`, варианты `t("casino_q1_slots", locale)`. Суммы депозитов в валюте ГЕО. Результат: казино WHERE geo
2. **services/casino_matcher.py** — скоринг по ответам, фильтр по geo
3. **bot/handlers/sport.py** — `/sport` → sport_picks WHERE geo, текст `pick_description_{lang}`
4. **api/router_quiz.py** — POST /api/quiz/* с locale
5. **prompts/casino_matching.md**, **sport_analysis.md** — с {language}

### Проверки

- [ ] Квиз: вопросы на PT-BR, суммы в R$, казино geo=BR
- [ ] /sport → ставка из Série A для BR

---

## ШАГ 4: SEO-ЛЕНДИНГ (next-intl)

**Цель:** jogai.fun/pt-BR/ с таблицами казино/бонусов. i18n структура для es-MX готова.

### Что создаём

1. **landing/** — Next.js 14 + next-intl + TailwindCSS
2. **landing/messages/pt-BR.json** — все строки лендинга
3. **landing/messages/es-MX.json** — заглушка (копия)
4. **landing/src/i18n.ts** — next-intl config
5. **landing/next.config.js** — `locales: ['pt-BR']`, defaultLocale: 'pt-BR'
6. **landing/src/app/[locale]/page.tsx** — Hero + казино + бонусы, `<html lang={locale}>`
7. **landing/src/app/[locale]/layout.tsx** — layout с lang
8. **Компоненты:** CasinoTable, BonusTable, JogaiScoreBadge, TelegramCTA, LocaleSwitcher (скрыт)
9. **landing/Dockerfile** + обновить docker-compose + nginx

### Ключевое

URL: `jogai.fun/pt-BR/`, `jogai.fun/pt-BR/casinos`. API: `?locale=pt-BR&geo=BR`. Компоненты: `description_pt` или `description_es` по locale. Meta: `<html lang="pt-BR">`, `<link hreflang>`.

### Проверки

- [ ] /pt-BR/ открывается, тексты из messages/pt-BR.json
- [ ] API возвращает title_pt, валюта R$
- [ ] `<html lang="pt-BR">`

---

## ШАГ 5: АВТОПОСТИНГ CELERY

**Цель:** Автопостинг в канал. Архитектура мульти-канальная.

### Что создаём

1. **celery_app.py** — config + beat schedule
2. **services/content_generator.py** — AI генерирует посты с `{language}`: `generate_bonus_post(bonus, locale)`
3. **services/channel_poster.py** — dict каналов `{geo: {channel_id, locale}}`, постит в нужный канал на нужном языке
4. **prompts/content_post.md** — с {language}

### Ключевое

```python
CHANNELS = {
    "BR": {"id": TELEGRAM_CHANNEL_BR_ID, "locale": "pt_BR"},
    # "MX": {"id": TELEGRAM_CHANNEL_MX_ID, "locale": "es_MX"},  # шаг 9
}
async def post_bonus_day():
    for geo, ch in CHANNELS.items():
        bonus = get_best_bonus(geo=geo)
        text = t("channel_bonus_day", ch["locale"], casino=..., score=..., verdict=t(bonus.verdict_key, ch["locale"]))
        await bot.send_message(ch["id"], text)
```

### Проверки

- [ ] Celery worker работает
- [ ] Бонус дня публикуется в канал BR на PT-BR

---

## ШАГ 6: MINI APP — ДАШБОРД + АНАЛИЗАТОР (react-i18next)

**Цель:** Mini App с i18n из Telegram language_code.

### Что создаём

1. **miniapp/** — React 18 + Vite + TailwindCSS + react-i18next
2. **miniapp/src/i18n.ts** — определение языка из Telegram WebApp
3. **miniapp/public/locales/pt-BR/translation.json** — все строки Mini App
4. **miniapp/public/locales/es-MX/translation.json** — заглушка
5. **pages/Home.tsx** — `{t('greeting', {name})}`, бонусы WHERE geo, валюта по locale
6. **pages/Analyze.tsx** — POST /api/analyze с locale
7. **Компоненты:** BonusCard с `{t('btn_get_bonus')}`, JogaiScore, AnalysisResult
8. **backend/api/router_auth.py** — initData → JWT + user.locale в ответе
9. **backend/api/router_bonuses.py** — GET /api/bonuses?geo=BR&locale=pt-BR с реальной логикой

### Проверки

- [ ] Mini App из бота, определяет PT-BR из Telegram
- [ ] Все тексты из translation.json
- [ ] Анализатор отвечает на PT-BR

---

## ШАГ 7: MINI APP — КВИЗ + ДАЙДЖЕСТ + РЕФЕРАЛЫ

**Цель:** Квиз, дайджест, рефералы — все с i18n.

### Что создаём

1. **pages/Quiz.tsx** — вопросы из translation.json, суммы в валюте ГЕО
2. **pages/Digest.tsx** — персональный дайджест
3. **backend/services/digest_builder.py** — Celery send_digest: для каждого user → бонусы geo + текст на locale
4. **bot/handlers/referral.py** — `t("referral_your_link", locale)`, `t("referral_coins_balance", locale, coins=...)`

### Проверки

- [ ] Квиз: вопросы и варианты из locales
- [ ] Дайджест: бонусы по ГЕО, текст на locale
- [ ] Реферал: тексты через t()

---

## ШАГ 8: ТРЕКЕР СТАВОК + БАНКРОЛЛ

**Цель:** Трекер с мультивалютностью.

### Что создаём

1. **pages/Tracker.tsx** — ставки в валюте пользователя, интерфейс из translation.json
2. **api/router_tracker.py** — CRUD, статистика в валюте пользователя (bet_currency)
3. **bot/handlers/tracker.py** — `/bet`, `/stats` с t() и format_currency()

### Ключевое

При создании ставки: `bet_currency = "BRL" if user.geo == "BR" else "MXN"`. Статистика: `format_currency(profit, user.locale)`.

### Проверки

- [ ] Ставки записываются с валютой ГЕО
- [ ] Статистика: R$ для BR

---

## ШАГ 9: МЕКСИКА (ES-MX) + PRO

**Цель:** Перевести es_MX.json, добавить MX seed, запустить канал. Ноль изменений кода.

### Что делаем

1. **Перевод backend/app/locales/es_MX.json** — перевести ВСЕ строки на испанский
2. **Перевод miniapp/public/locales/es-MX/translation.json** — перевести
3. **Перевод landing/messages/es-MX.json** — перевести
4. **Обновить landing/next.config.js** — `locales: ['pt-BR', 'es-MX']`
5. **Seed MX данные** — казино с geo={MX}, бонусы с title_es, max_bonus_currency=MXN, geo={MX}
6. **Sport picks** — Liga MX, geo={MX}, pick_description_es
7. **Telegram канал** — создать @jogai_mx, добавить TELEGRAM_CHANNEL_MX_ID
8. **Раскомментировать MX в channel_poster.py** — `"MX": {"id": ..., "locale": "es_MX"}`
9. **PRO подписка** — bot/handlers/pro.py, services/pro.py, цена через locales

### Проверки (критически важно!)

- [ ] Бот: пользователь с language_code='es' → ВСЕ ответы на ES
- [ ] Бот: /bonus → казино geo=MX, title_es, MX$ валюта
- [ ] Mini App: определяет ES-MX, все тексты на испанском
- [ ] Лендинг: jogai.fun/es-MX/ работает
- [ ] Канал @jogai_mx: посты на ES
- [ ] PRO: цена MX$99/мес для MX
- [ ] Ноль сломанных PT-BR функций (регрессия!)

---

## ШАГ 10: ВЕБ-ПЛАТФОРМА + SEO

**Цель:** Полные SEO-страницы с hreflang для двух локалей.

### Что создаём

1. **[locale]/casinos/page.tsx** — рейтинг с фильтрами
2. **[locale]/casinos/[slug]/page.tsx** — обзор: description_{lang}
3. **[locale]/bonuses/page.tsx** — таблица с сортировкой
4. **[locale]/guides/** — статьи
5. **JSON-LD** — локализованный для каждого locale
6. **Sitemap.xml** — с hreflang alternates
7. **`<link rel="alternate" hreflang="pt-BR">`, `<link hreflang="es-MX">`**
8. **LocaleSwitcher** — видимый (теперь 2 локали)

### Проверки

- [ ] /pt-BR/casinos и /es-MX/casinos — разный контент
- [ ] hreflang корректен
- [ ] JSON-LD на нужном языке
- [ ] Sitemap с alternates

---

## ШАГ 11: АВТОМАТИЗАЦИЯ + ДЕПЛОЙ

**Цель:** Парсинг бонусов, деплой на VPS.

### Что создаём

1. **services/bonus_parser.py** — парсинг → AI → seed для нужного ГЕО + обоих языков
2. **docker-compose.prod.yml**, **Caddyfile**, **scripts/**
3. Финальный чеклист

### Чеклист перед деплоем

- [ ] Все env заполнены production значениями
- [ ] BOT_TOKEN, ANTHROPIC_API_KEY production
- [ ] Партнёрские ссылки production
- [ ] SSL для jogai.fun
- [ ] Webhook: https://jogai.fun/bot/webhook
- [ ] pg_dump backup (cron daily)
- [ ] Uptime Kuma: /api/health
- [ ] Rate limiting
- [ ] locales/pt_BR.json — финальная вычитка нативным спикером
- [ ] locales/es_MX.json — финальная вычитка нативным спикером
- [ ] Seed данные заменены на реальные (оба ГЕО)

---

## ТАЙМИНГ

```
НЕДЕЛЯ 1:   Шаг 0-2    (скелет + бот + AI анализ)     ~12-16ч
НЕДЕЛЯ 2:   Шаг 3-5    (квиз + лендинг + автопостинг)  ~11-14ч
НЕДЕЛЯ 3:   Шаг 6-7    (Mini App)                      ~11-14ч
НЕДЕЛЯ 4:   Шаг 8-9    (трекер + Мексика + PRO)        ~9-11ч
НЕДЕЛЯ 5:   Шаг 10-11  (веб-платформа + деплой)        ~9-12ч
ИТОГО: ~53-67 часов за 5 недель
```

---

*Версия 2.0 | Февраль 2026*
