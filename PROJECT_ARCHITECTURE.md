# JOGAI — PROJECT ARCHITECTURE

**Проект:** Jogai — AI Gambling Assistant для LATAM
**Версия:** 2.0 | Февраль 2026

---

## 1. ОБЗОР СИСТЕМЫ

Jogai — мультиканальная AI-платформа для гемблинг-аудитории в Латинской Америке. Система с первого дня поддерживает мультиязычность (i18n) — запускаемся на PT-BR, добавление ES-MX = перевод JSON-файлов без изменений кода.

```
┌─────────────────────────────────────────────────────────────┐
│                        NGINX (reverse proxy)                │
│                       port 80 / 443                         │
└──────┬──────────────────┬───────────────────┬───────────────┘
       │                  │                   │
       ▼                  ▼                   ▼
┌──────────────┐  ┌──────────────┐  ┌─────────────────────┐
│  Landing     │  │   Backend    │  │  Telegram Bot        │
│  (Next.js)   │  │  (FastAPI)   │  │  (aiogram 3.x)      │
│  jogai.fun   │  │  /api/*      │  │  @jogai_bot          │
│  next-intl   │  │  port 8000   │  │  locales/*.json      │
│  port 3000   │  │              │  │  i18n.py → t()       │
└──────────────┘  └──────┬───────┘  └──────────┬──────────┘
                         │                     │
              ┌──────────┼─────────────────────┘
              ▼          ▼
     ┌──────────────────────────┐
     │    Shared Services       │
     │  ┌────────┐ ┌─────────┐  │
     │  │PostgreSQL│ │ Redis  │  │
     │  │  :5432  │ │ :6379  │  │
     │  └────────┘ └─────────┘  │
     │  ┌────────────────────┐  │
     │  │  Claude / GPT API  │  │
     │  │  ответ на {language}│  │
     │  └────────────────────┘  │
     └──────────────────────────┘
```

---

## 2. ЯЗЫКОВАЯ ПОЛИТИКА (i18n)

### 2.1. Принцип

**Ни одна пользовательская строка не хардкодится.** Все тексты — в JSON-файлах локализации. Код работает через ключи: `t("welcome")`, не `"Oi! Eu sou o Jogai..."`.

### 2.2. Поддерживаемые локали

| Код | Язык | ГЕО | Валюта | Фаза |
|-----|------|-----|--------|------|
| `pt_BR` | Португальский (Бразилия) | 🇧🇷 BR | R$ (BRL) | 1 (месяц 1) |
| `es_MX` | Испанский (Мексика) | 🇲🇽 MX | MX$ (MXN) | 3 (месяц 5–6) |
| `es` | Испанский (общий) | 🇪🇨🇨🇱🇵🇪 | USD / локальная | 4 (месяц 8+) |

### 2.3. Определение языка пользователя

```
ПРИОРИТЕТ:
1. user.locale в БД (если пользователь выбрал вручную)
2. Telegram language_code ('pt' → pt_BR, 'es' → es_MX)
3. Фоллбэк: pt_BR

МАППИНГ:
  'pt', 'pt-BR', 'pt-br' → pt_BR
  'es', 'es-MX', 'es-mx', 'es-AR', 'es-CL', 'es-PE', 'es-EC' → es_MX
  всё остальное → pt_BR
```

### 2.4. Где живут переводы

| Компонент | Библиотека | Путь к файлам |
|-----------|-----------|---------------|
| **Telegram-бот** | Свой хелпер `t()` | `backend/app/locales/pt_BR.json`, `es_MX.json` |
| **Mini App** | react-i18next | `miniapp/public/locales/pt-BR/translation.json` |
| **Лендинг** | next-intl | `landing/messages/pt-BR.json`, `es-MX.json` |
| **AI-промпты** | Параметр `{language}` | `backend/app/prompts/*.md` |
| **БД-контент** | Мультиязычные поля | `title_pt`, `title_es`, `description_pt`, `description_es` |

### 2.5. Чеклист добавления нового языка (es-MX)

```
□ Скопировать backend/app/locales/pt_BR.json → es_MX.json → перевести
□ Скопировать miniapp/public/locales/pt-BR/translation.json → es-MX/
□ Скопировать landing/messages/pt-BR.json → es-MX.json
□ Добавить 'es-MX' в next.config.js locales
□ Seed: казино + бонусы с geo={MX}, title_es, description_es
□ Создать Telegram-канал @jogai_mx
□ Добавить TELEGRAM_CHANNEL_MX_ID в .env
□ Ноль изменений в коде
```

### 2.6. Валюта и форматирование

| Locale | Валюта | Символ | Число | Дата | Платежи |
|--------|--------|--------|-------|------|---------|
| pt_BR | BRL | R$ | 1.234,56 | 14/02/2026 | PIX |
| es_MX | MXN | MX$ | 1,234.56 | 14/02/2026 | SPEI |

---

## 3. ТЕХНОЛОГИЧЕСКИЙ СТЕК

| Слой | Технология | Версия | Назначение |
|------|-----------|--------|------------|
| **Telegram-бот** | Python + aiogram | 3.x | Бот, команды, inline-кнопки |
| **Backend API** | Python + FastAPI | 0.110+ | REST API |
| **Mini App** | React 18 + react-i18next | 18.x | Telegram Mini App |
| **SEO-лендинг** | Next.js 14 + next-intl | 14.x | jogai.fun |
| **БД** | PostgreSQL | 15 | Данные |
| **Кэш** | Redis | 7 | Кэш, rate limiting |
| **Task queue** | Celery | 5.x | Автопостинг, парсинг |
| **AI** | Claude API / GPT-4o-mini | — | Анализ, контент |
| **Деплой** | Docker Compose | — | Контейнеризация |
| **Хостинг** | Hetzner | — | VPS $5–20/мес |

---

## 4. СТРУКТУРА ПРОЕКТА

```
jogai/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── config.py                  # Pydantic Settings
│   │   ├── main.py                    # FastAPI app
│   │   ├── i18n.py                    # ★ хелпер t(key, locale, **kwargs)
│   │   ├── locales/                   # ★ переводы бота
│   │   │   ├── pt_BR.json            # PT-BR (все строки)
│   │   │   └── es_MX.json            # ES-MX (фаза 3, копия для перевода)
│   │   ├── database/
│   │   │   ├── __init__.py
│   │   │   ├── engine.py
│   │   │   ├── models.py             # мультиязычные поля
│   │   │   └── seed.py               # seed с title_pt, description_pt
│   │   ├── bot/
│   │   │   ├── __init__.py
│   │   │   ├── bot.py
│   │   │   ├── middlewares.py         # ★ LocaleMiddleware (определяет locale)
│   │   │   └── handlers/
│   │   │       ├── __init__.py
│   │   │       ├── start.py           # t("welcome", locale)
│   │   │       ├── bonus.py           # t("bonus_day_title", locale)
│   │   │       ├── analyze.py         # AI отвечает на locale
│   │   │       ├── casino.py          # квиз на locale
│   │   │       ├── sport.py
│   │   │       ├── tracker.py
│   │   │       ├── referral.py
│   │   │       └── pro.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── deps.py               # ★ get_locale() из query/header
│   │   │   ├── router_bonuses.py      # title_pt или title_es по locale
│   │   │   ├── router_casinos.py
│   │   │   ├── router_analyze.py
│   │   │   ├── router_quiz.py
│   │   │   ├── router_tracker.py
│   │   │   ├── router_digest.py
│   │   │   └── router_auth.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── llm.py                # ★ chat(prompt, msg, language=...)
│   │   │   ├── bonus_analyzer.py      # verdict_key (не текст!)
│   │   │   ├── casino_matcher.py
│   │   │   ├── content_generator.py   # ★ генерация на нужном языке
│   │   │   ├── bonus_parser.py
│   │   │   ├── sport_analyzer.py
│   │   │   ├── digest_builder.py
│   │   │   └── affiliate.py
│   │   ├── utils/
│   │   │   ├── __init__.py
│   │   │   ├── telegram.py
│   │   │   └── formatters.py          # ★ format_currency(amount, locale)
│   │   └── prompts/                   # ★ все с {language}
│   │       ├── bonus_analysis.md
│   │       ├── casino_matching.md
│   │       ├── content_post.md
│   │       └── sport_analysis.md
│   ├── alembic/
│   │   ├── env.py
│   │   └── versions/
│   ├── alembic.ini
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
│
├── miniapp/
│   ├── public/
│   │   └── locales/                   # ★ i18n Mini App
│   │       ├── pt-BR/
│   │       │   └── translation.json
│   │       └── es-MX/                 # (фаза 3)
│   │           └── translation.json
│   ├── src/
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   ├── i18n.ts                    # ★ react-i18next config
│   │   ├── api/client.ts
│   │   ├── pages/
│   │   │   ├── Home.tsx               # {t('greeting', {name})}
│   │   │   ├── Analyze.tsx
│   │   │   ├── Quiz.tsx
│   │   │   ├── Tracker.tsx
│   │   │   └── Digest.tsx
│   │   ├── components/
│   │   │   ├── BonusCard.tsx
│   │   │   ├── JogaiScore.tsx
│   │   │   ├── CasinoCard.tsx
│   │   │   ├── AnalysisResult.tsx
│   │   │   ├── QuizStep.tsx
│   │   │   └── BetEntry.tsx
│   │   ├── stores/
│   │   │   ├── user.ts
│   │   │   ├── bonuses.ts
│   │   │   └── tracker.ts
│   │   └── types/index.ts
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   └── Dockerfile
│
├── landing/
│   ├── messages/                      # ★ i18n лендинга
│   │   ├── pt-BR.json
│   │   └── es-MX.json                 # (фаза 3)
│   ├── src/
│   │   ├── i18n.ts                    # ★ next-intl config
│   │   ├── app/
│   │   │   ├── [locale]/              # ★ /pt-BR/casinos, /es-MX/casinos
│   │   │   │   ├── page.tsx
│   │   │   │   ├── layout.tsx         # <html lang={locale}>
│   │   │   │   ├── casinos/
│   │   │   │   │   ├── page.tsx
│   │   │   │   │   └── [slug]/page.tsx
│   │   │   │   ├── bonuses/page.tsx
│   │   │   │   └── guides/
│   │   │   │       ├── page.tsx
│   │   │   │       └── [slug]/page.tsx
│   │   │   └── layout.tsx
│   │   └── components/
│   │       ├── CasinoTable.tsx
│   │       ├── BonusTable.tsx
│   │       ├── JogaiScoreBadge.tsx
│   │       ├── TelegramCTA.tsx
│   │       ├── Header.tsx
│   │       ├── Footer.tsx
│   │       └── LocaleSwitcher.tsx     # ★ переключатель языка
│   ├── next.config.js                 # i18n locales config
│   ├── package.json
│   ├── tailwind.config.js
│   └── Dockerfile
│
├── nginx/nginx.conf
├── docker-compose.yml
├── docker-compose.prod.yml
├── .gitignore
├── Justfile
├── README.md
├── PROJECT_ARCHITECTURE.md
├── IMPLEMENTATION_PLAN.md
├── PRD.md
└── CLAUDE_CODE_GUIDE.md
```

---

## 5. i18n — ДЕТАЛЬНАЯ РЕАЛИЗАЦИЯ

### 5.1. Бот: locales/ + хелпер t()

**backend/app/i18n.py:**
```python
import json
from pathlib import Path
from typing import Optional

LOCALES_DIR = Path(__file__).parent / "locales"
_cache: dict[str, dict] = {}

SUPPORTED_LOCALES = ["pt_BR", "es_MX"]
DEFAULT_LOCALE = "pt_BR"

LANGUAGE_NAMES = {
    "pt_BR": "português brasileiro",
    "es_MX": "español latinoamericano",
}

def _load_locale(locale: str) -> dict:
    if locale not in _cache:
        path = LOCALES_DIR / f"{locale}.json"
        if path.exists():
            _cache[locale] = json.loads(path.read_text(encoding="utf-8"))
        else:
            _cache[locale] = _load_locale(DEFAULT_LOCALE)
    return _cache[locale]

def t(key: str, locale: str = DEFAULT_LOCALE, **kwargs) -> str:
    strings = _load_locale(locale)
    text = strings.get(key, key)
    if kwargs:
        try:
            text = text.format(**kwargs)
        except (KeyError, IndexError):
            pass
    return text

def get_user_locale(language_code: Optional[str], saved_locale: Optional[str] = None) -> str:
    if saved_locale and saved_locale in SUPPORTED_LOCALES:
        return saved_locale
    if language_code:
        lang = language_code.lower().replace("-", "_")
        if lang.startswith("pt"):
            return "pt_BR"
        if lang.startswith("es"):
            return "es_MX"
    return DEFAULT_LOCALE

def get_language_name(locale: str) -> str:
    return LANGUAGE_NAMES.get(locale, LANGUAGE_NAMES[DEFAULT_LOCALE])
```

**backend/app/locales/pt_BR.json** (полный файл):
```json
{
  "welcome": "👋 Oi! Eu sou o Jogai — seu assistente inteligente de cassinos e bônus.",
  "welcome_question": "O que quer fazer?",
  "btn_bonuses": "🎁 Ver melhores bônus de hoje",
  "btn_casino": "🎰 Qual cassino é melhor pra mim?",
  "btn_analyze": "🔍 Analisar um bônus",
  "btn_miniapp": "📊 Abrir Jogai App",
  "bonus_day_title": "🔥 TOP BÔNUS DE HOJE ({date}):",
  "bonus_card": "🏆 [{casino}] — {title}\nWagering: x{wagering} | Prazo: {deadline} dias\n⭐ Jogai Score: {score}/10 — {verdict}",
  "btn_get_bonus": "👉 Pegar bônus",
  "analyze_prompt": "Mande as condições do bônus — texto, screenshot ou link.",
  "analyze_result_title": "📊 ANÁLISE DO BÔNUS:",
  "analyze_deposit": "Depósito: {currency}{amount}",
  "analyze_bonus_line": "Bônus: {currency}{amount} ({percent}%)",
  "analyze_total": "Total na conta: {currency}{amount}",
  "analyze_wagering": "Wagering: x{multiplier} = {currency}{total}",
  "analyze_deadline": "Prazo: {days} dias",
  "analyze_max_bet": "Aposta máx: {currency}{amount}",
  "analyze_bets_needed": "Apostas necessárias: {count} ({per_day}/dia = {per_hour}/hora)",
  "analyze_expected_loss": "Perda esperada: {currency}{amount}",
  "analyze_profit_chance": "Chance real de lucro: ~{percent}%",
  "verdict_excellent": "EXCELENTE",
  "verdict_good": "BOM NEGÓCIO",
  "verdict_caution": "CUIDADO",
  "verdict_bad": "NÃO RECOMENDADO",
  "verdict_label_excellent": "⚠️ VEREDICTO: EXCELENTE!",
  "verdict_label_good": "⚠️ VEREDICTO: BOM NEGÓCIO",
  "verdict_label_caution": "⚠️ VEREDICTO: CUIDADO",
  "verdict_label_bad": "⚠️ VEREDICTO: NÃO RECOMENDADO",
  "analyze_see_recommended": "💡 Quer ver bônus que REALMENTE valem a pena?",
  "btn_see_recommended": "🎁 Ver bônus recomendados",
  "casino_q1": "O que você mais gosta de jogar?",
  "casino_q1_slots": "🎰 Slots",
  "casino_q1_crash": "💥 Crash",
  "casino_q1_sports": "⚽ Apostas",
  "casino_q1_table": "🃏 Poker/Mesa",
  "casino_q2": "Quanto quer depositar?",
  "casino_q2_low": "Até R$50",
  "casino_q2_medium": "R$50–200",
  "casino_q2_high": "R$200–1000",
  "casino_q2_vip": "R$1000+",
  "casino_q3": "Como prefere pagar?",
  "casino_q3_pix": "PIX",
  "casino_q3_crypto": "Cripto",
  "casino_q3_card": "Cartão",
  "casino_q4": "O que é mais importante pra você?",
  "casino_q4_bonus": "Bônus grande",
  "casino_q4_wagering": "Wagering baixo",
  "casino_q4_withdraw": "Saque rápido",
  "casino_q5": "Experiência com cassinos online?",
  "casino_q5_beginner": "Iniciante",
  "casino_q5_intermediate": "Intermediário",
  "casino_q5_advanced": "Experiente",
  "casino_result_title": "🎯 SEU CASSINO IDEAL:",
  "casino_match": "{percent}% match!",
  "casino_best_for": "✅ Melhor para: {features}",
  "casino_bonus_line": "🎁 Bônus: {bonus}",
  "casino_withdraw_line": "⚡ Saque: {time}",
  "btn_register": "👉 Criar conta",
  "sport_title": "⚽ APOSTA DO DIA:",
  "sport_match": "{home} vs {away}",
  "sport_analysis": "📊 Análise: {text}",
  "sport_recommendation": "💡 Jogai AI recomenda: {pick} (odd {odds})",
  "btn_bet": "👉 Apostar",
  "sport_no_match": "Nenhum jogo relevante hoje. Volte amanhã! ⚽",
  "referral_your_link": "🔗 Seu link de convite:",
  "referral_coins_balance": "💰 Seus Jogai Coins: {coins}",
  "referral_reward": "Convide um amigo → +5 Jogai Coins!",
  "tracker_added": "✅ Aposta registrada!",
  "tracker_stats_title": "📊 SUAS ESTATÍSTICAS:",
  "tracker_roi": "ROI: {value}%",
  "tracker_win_rate": "Win rate: {value}%",
  "tracker_profit": "Lucro/Prejuízo: {currency}{value}",
  "tracker_best_game": "Melhor jogo: {game}",
  "tracker_worst_game": "Pior jogo: {game}",
  "bankroll_recommendation": "💡 Seu bankroll: {currency}{amount} → aposta recomendada: {currency}{bet}",
  "pro_title": "⭐ JOGAI PRO",
  "pro_description": "Análise avançada, estatísticas completas, bônus exclusivos.",
  "pro_price": "{currency}{amount}/mês",
  "pro_activated": "✅ PRO ativado! Válido até {date}.",
  "pro_expired": "Sua assinatura PRO expirou. Renove para continuar!",
  "error_generic": "❌ Ops, algo deu errado. Tente novamente.",
  "error_rate_limit": "⏳ Muitas solicitações. Aguarde um momento.",
  "currency_symbol": "R$",
  "currency_code": "BRL",
  "channel_bonus_day": "🎁 BÔNUS DO DIA: [{casino}] — {title}\n⭐ Jogai Score: {score}/10 — {verdict}\n⏰ Válido até {expires}",
  "channel_slot_review": "🎰 SLOT DO DIA: {name} — RTP {rtp}%, volatilidade {volatility}\n💡 {tip}\nMelhor cassino: [{casino}]",
  "channel_sport": "⚽ APOSTA DO DIA: {match}\n📊 {analysis}\n💡 Jogai AI recomenda: {pick} (odd {odds})",
  "channel_win": "🏆 RESULTADO: {text}"
}
```

### 5.2. Mini App: react-i18next

**miniapp/src/i18n.ts:**
```typescript
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import Backend from 'i18next-http-backend';

const getTelegramLocale = (): string => {
  const lang = window.Telegram?.WebApp?.initDataUnsafe?.user?.language_code || 'pt';
  return lang.startsWith('es') ? 'es-MX' : 'pt-BR';
};

i18n
  .use(Backend)
  .use(initReactI18next)
  .init({
    lng: getTelegramLocale(),
    fallbackLng: 'pt-BR',
    supportedLngs: ['pt-BR', 'es-MX'],
    backend: { loadPath: '/locales/{{lng}}/translation.json' },
    interpolation: { escapeValue: false },
  });

export default i18n;
```

### 5.3. Лендинг: next-intl

**URL-структура:**
```
jogai.fun/pt-BR/           → главная PT-BR (дефолт)
jogai.fun/pt-BR/casinos    → рейтинг казино
jogai.fun/es-MX/           → главная ES-MX (фаза 3)
```

### 5.4. AI-промпты с {language}

Все промпты содержат `{language}` — бэкенд подставляет язык из locale пользователя.

```markdown
# prompts/bonus_analysis.md

Ты — AI-аналитик бонусов казино Jogai.
ЯЗЫК: Отвечай пользователю ТОЛЬКО на {language}. Не используй другие языки.
ВАЛЮТА: используй {currency_symbol} для денежных сумм.
...
```

### 5.5. API: контент по locale

API возвращает контент на нужном языке через `?locale=pt_BR`:

```python
# router_bonuses.py
@router.get("/bonuses")
async def get_bonuses(geo: str = "BR", locale: str = "pt_BR", ...):
    bonuses = await get_active_bonuses(geo=geo)
    # Выбираем title_pt или title_es в зависимости от locale
    lang_suffix = "pt" if locale.startswith("pt") else "es"
    for b in bonuses:
        b["title"] = getattr(b, f"title_{lang_suffix}")
        b["verdict"] = t(b.verdict_key, locale)
    ...
```

---

## 6. БАЗА ДАННЫХ

### 6.1. Таблицы

```sql
CREATE TABLE users (
    id BIGINT PRIMARY KEY,                    -- telegram_id
    username VARCHAR(255),
    first_name VARCHAR(255),
    language_code VARCHAR(10),                -- из Telegram
    locale VARCHAR(10) DEFAULT 'pt_BR',       -- ★ i18n
    geo VARCHAR(5) DEFAULT 'BR',              -- ★ страна
    preferred_games TEXT[],
    preferred_deposit VARCHAR(50),
    preferred_payment VARCHAR(50),
    jogai_coins INTEGER DEFAULT 0,
    is_pro BOOLEAN DEFAULT FALSE,
    pro_expires_at TIMESTAMP,
    referred_by BIGINT REFERENCES users(id),
    referral_code VARCHAR(20) UNIQUE,
    created_at TIMESTAMP DEFAULT NOW(),
    last_active_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE casinos (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    logo_url TEXT,
    description_pt TEXT,                       -- ★ PT-BR
    description_es TEXT,                       -- ★ ES-MX
    min_deposit DECIMAL(10,2),
    pix_supported BOOLEAN DEFAULT TRUE,        -- BR
    spei_supported BOOLEAN DEFAULT FALSE,      -- ★ MX
    crypto_supported BOOLEAN DEFAULT FALSE,
    withdrawal_time VARCHAR(100),
    affiliate_program VARCHAR(100),
    affiliate_link_template TEXT,
    ref_id VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    geo TEXT[] DEFAULT '{BR}',
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE bonuses (
    id SERIAL PRIMARY KEY,
    casino_id INTEGER REFERENCES casinos(id),
    title_pt VARCHAR(500),                     -- ★ PT-BR
    title_es VARCHAR(500),                     -- ★ ES-MX
    bonus_percent INTEGER,
    max_bonus_amount DECIMAL(10,2),
    max_bonus_currency VARCHAR(5) DEFAULT 'BRL', -- ★ BRL / MXN
    wagering_multiplier DECIMAL(5,1),
    wagering_deadline_days INTEGER,
    max_bet DECIMAL(10,2),
    free_spins INTEGER DEFAULT 0,
    no_deposit BOOLEAN DEFAULT FALSE,
    jogai_score DECIMAL(3,1),
    verdict_key VARCHAR(50),                   -- ★ ключ i18n: 'verdict_excellent'
    expected_loss DECIMAL(10,2),
    profit_probability DECIMAL(5,2),
    affiliate_link TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    starts_at TIMESTAMP,
    expires_at TIMESTAMP,
    geo TEXT[] DEFAULT '{BR}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE clicks (
    id SERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id),
    bonus_id INTEGER REFERENCES bonuses(id),
    casino_id INTEGER REFERENCES casinos(id),
    source VARCHAR(50),
    locale VARCHAR(10),                        -- ★ из какой локали
    clicked_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE analyses (
    id SERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id),
    input_text TEXT,
    input_type VARCHAR(20) DEFAULT 'text',
    parsed_bonus_percent INTEGER,
    parsed_wagering DECIMAL(5,1),
    parsed_deadline INTEGER,
    parsed_max_bet DECIMAL(10,2),
    jogai_score DECIMAL(3,1),
    verdict_key VARCHAR(50),                   -- ★ ключ i18n
    ai_response TEXT,
    locale VARCHAR(10) DEFAULT 'pt_BR',        -- ★ язык ответа
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE bets (
    id SERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id),
    casino_id INTEGER REFERENCES casinos(id),
    game_type VARCHAR(50),
    game_name VARCHAR(255),
    bet_amount DECIMAL(10,2),
    bet_currency VARCHAR(5) DEFAULT 'BRL',     -- ★ BRL / MXN
    result_amount DECIMAL(10,2),
    profit DECIMAL(10,2),
    note TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE posts (
    id SERIAL PRIMARY KEY,
    post_type VARCHAR(50),
    title VARCHAR(500),
    content_pt TEXT,                            -- ★ PT-BR
    content_es TEXT,                            -- ★ ES-MX
    media_url TEXT,
    bonus_id INTEGER REFERENCES bonuses(id),
    casino_id INTEGER REFERENCES casinos(id),
    telegram_message_id BIGINT,
    telegram_channel VARCHAR(50),              -- ★ какой канал
    scheduled_at TIMESTAMP,
    published_at TIMESTAMP,
    geo VARCHAR(5) DEFAULT 'BR',
    status VARCHAR(20) DEFAULT 'draft'
);

CREATE TABLE sport_picks (
    id SERIAL PRIMARY KEY,
    match_name VARCHAR(500),
    league VARCHAR(100),
    pick_description_pt TEXT,                   -- ★ PT-BR
    pick_description_es TEXT,                   -- ★ ES-MX
    odds DECIMAL(5,2),
    analysis_pt TEXT,                            -- ★
    analysis_es TEXT,                            -- ★
    casino_id INTEGER REFERENCES casinos(id),
    affiliate_link TEXT,
    result VARCHAR(20),
    match_date TIMESTAMP,
    geo TEXT[] DEFAULT '{BR}',
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE referrals (
    id SERIAL PRIMARY KEY,
    referrer_id BIGINT REFERENCES users(id),
    referred_id BIGINT REFERENCES users(id),
    coins_awarded INTEGER DEFAULT 5,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 6.2. Индексы

```sql
CREATE INDEX idx_users_locale ON users(locale);
CREATE INDEX idx_users_geo ON users(geo);
CREATE INDEX idx_users_referral_code ON users(referral_code);
CREATE INDEX idx_bonuses_active_geo ON bonuses(is_active, geo) WHERE is_active = TRUE;
CREATE INDEX idx_bonuses_score ON bonuses(jogai_score DESC);
CREATE INDEX idx_clicks_locale ON clicks(locale);
CREATE INDEX idx_posts_geo ON posts(geo);
CREATE INDEX idx_sport_picks_geo ON sport_picks(geo);
```

---

## 7. API ENDPOINTS

Все эндпоинты с контентом принимают `?locale=pt_BR` или `Accept-Language: pt-BR`.

| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/api/health` | Health check |
| POST | `/bot/webhook` | Telegram webhook |
| GET | `/api/bonuses?geo=BR&locale=pt_BR` | Бонусы |
| GET | `/api/bonuses/{id}?locale=pt_BR` | Детали бонуса |
| GET | `/api/casinos?geo=BR&locale=pt_BR` | Казино |
| GET | `/api/casinos/{slug}?locale=pt_BR` | Детали казино |
| POST | `/api/analyze` | AI-анализ (locale в body) |
| POST | `/api/quiz/start` | Квиз |
| POST | `/api/quiz/answer` | Ответ квиза |
| GET | `/api/quiz/result` | Результат |
| GET | `/api/digest` | Дайджест (auth, locale из профиля) |
| GET | `/api/sport/today?geo=BR` | Ставка дня |
| POST | `/api/auth/telegram` | initData → JWT |
| GET | `/api/auth/me` | Пользователь + locale |
| GET | `/api/tracker/bets` | Ставки |
| POST | `/api/tracker/bets` | Добавить ставку |
| GET | `/api/tracker/stats` | Статистика |

---

## 8. ПЕРЕМЕННЫЕ ОКРУЖЕНИЯ

```env
DATABASE_URL=postgresql+asyncpg://jogai:password@postgres:5432/jogai
REDIS_URL=redis://redis:6379/0
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHANNEL_BR_ID=-100xxxxxxxxxx
TELEGRAM_CHANNEL_MX_ID=-100xxxxxxxxxx
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
LLM_PROVIDER=anthropic
LLM_MODEL=claude-sonnet-4-20250514
PINUP_REF_ID=jogai_12345
ONEWIN_REF_ID=jogai_67890
BET365_REF_ID=jogai_11111
RIVALO_REF_ID=jogai_22222
SECRET_KEY=your-secret-key
APP_URL=https://jogai.fun
ENVIRONMENT=development
DEFAULT_LOCALE=pt_BR
DEFAULT_GEO=BR
ODDS_API_KEY=your_key
FOOTBALL_API_KEY=your_key
POSTHOG_KEY=your_key
```

---

## 9. JOGAI SCORE — АЛГОРИТМ

Алгоритм одинаковый для всех локалей. Возвращает `verdict_key` (ключ для `t()`), не текст.

```python
def calculate_jogai_score(...) -> dict:
    # ... математика ...
    if jogai_score >= 8.0:
        verdict_key = "verdict_excellent"
    elif jogai_score >= 6.0:
        verdict_key = "verdict_good"
    elif jogai_score >= 4.0:
        verdict_key = "verdict_caution"
    else:
        verdict_key = "verdict_bad"
    return {"jogai_score": jogai_score, "verdict_key": verdict_key, ...}
```

Вывод для пользователя: `t(verdict_key, user.locale)` → "EXCELENTE" / "BOM NEGÓCIO" / "¡EXCELENTE!" / "BUEN NEGOCIO"

---

## 10. CELERY ЗАДАЧИ

| Задача | Расписание | Описание |
|--------|-----------|----------|
| `post_bonus_day` | 09:00 по ТЗ каждого ГЕО | Бонус дня → канал(ы) |
| `post_slot_review` | 14:00 | Обзор слота |
| `post_sport_pick` | 18:00 | Ставка дня |
| `send_digest` | 08:00 | Дайджест (на locale каждого юзера) |
| `parse_bonuses` | каждые 6ч | Парсинг бонусов |
| `deactivate_expired` | каждый час | Деактивация |

Часовые пояса: BR = UTC-3, MX = UTC-6.

---

## 11. TELEGRAM-КАНАЛЫ

| ГЕО | Канал | Env | Язык | Фаза |
|-----|-------|-----|------|------|
| BR | @jogai_br | TELEGRAM_CHANNEL_BR_ID | pt_BR | 1 |
| MX | @jogai_mx | TELEGRAM_CHANNEL_MX_ID | es_MX | 3 |

Автопостинг публикует в каждый канал на своём языке:
```python
for geo, channel_id, locale in get_active_channels():
    bonus = get_best_bonus(geo=geo)
    text = t("channel_bonus_day", locale, casino=..., title=..., score=..., verdict=t(bonus.verdict_key, locale), expires=...)
    await post_to_channel(channel_id, text)
```

---

*Версия 2.0 | Февраль 2026*
