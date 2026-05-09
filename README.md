<h1 align="center">FoodShot</h1>

<p align="center">
  Telegram bot for people with diabetes: send a food photo, get carbs, calories, portion estimate, and an insulin bolus suggestion.
</p>

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/PYTHON-3.11--3.13-3776AB?style=for-the-badge&logo=python&logoColor=white">
  <img alt="aiogram" src="https://img.shields.io/badge/AIOGRAM-3.x-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white">
  <img alt="FastAPI" src="https://img.shields.io/badge/FASTAPI-WEBHOOK-009688?style=for-the-badge&logo=fastapi&logoColor=white">
  <img alt="PostgreSQL" src="https://img.shields.io/badge/POSTGRESQL-ASYNC-4169E1?style=for-the-badge&logo=postgresql&logoColor=white">
  <img alt="Redis" src="https://img.shields.io/badge/REDIS-FSM-DC382D?style=for-the-badge&logo=redis&logoColor=white">
  <img alt="Docker" src="https://img.shields.io/badge/DOCKER-COMPOSE-2496ED?style=for-the-badge&logo=docker&logoColor=white">
</p>

<p align="center">
  <img alt="OpenAI" src="https://img.shields.io/badge/OPENAI-VISION-111111?style=for-the-badge&logo=openai&logoColor=white">
  <img alt="USDA" src="https://img.shields.io/badge/USDA-NUTRITION-4B7F2A?style=for-the-badge">
  <img alt="Localization" src="https://img.shields.io/badge/I18N-EN%20%7C%20UK-FFB000?style=for-the-badge">
  <img alt="License" src="https://img.shields.io/badge/LICENSE-BUSL--1.1-555555?style=for-the-badge">
</p>

---

FoodShot is a practical Telegram assistant for meal estimation. A user sends a photo of food, the bot recognizes the dish, estimates the portion, fetches nutrition data, asks for current glucose if needed, and calculates a suggested insulin dose using the user's personal settings.

> FoodShot gives estimates only. It is not a medical device and does not replace advice from a qualified healthcare professional.

## Demo

The bot works directly inside Telegram:

- recognizes the dish from a photo;
- estimates portion weight and confidence;
- calculates carbs and calories;
- lets the user adjust the portion with inline buttons;
- asks for current blood glucose or accepts `/skip`;
- returns a bolus breakdown and saves the meal history.

## How It Works

```text
Photo in Telegram
  -> FastAPI webhook receives Telegram update
  -> aiogram handler downloads the image
  -> Vision AI detects dish, portion, confidence
  -> Nutrition service fetches macros
  -> User adjusts portion and enters glucose
  -> Calc engine computes bolus
  -> Result is sent back and saved to PostgreSQL
```

## Features

| Feature | Description |
| --- | --- |
| Food photo analysis | Detects dish name, estimated weight, and confidence level. |
| Nutrition lookup | Gets carbs, calories, protein, and fat from nutrition data. |
| Portion correction | Inline buttons let the user adjust grams before calculation. |
| Bolus calculation | Uses ICR, ISF, target glucose, current glucose, and carbs. |
| Personal profile | Stores insulin ratio, sensitivity, target glucose, insulin type, and language. |
| Meal history | Saves meals and shows the last 10 logs via `/history`. |
| Localization | Supports English and Ukrainian. |
| Docker setup | Runs bot, PostgreSQL, and Redis with Docker Compose. |

## Architecture

<p align="center">
  <img src="doc/foodshot_architecture.svg" alt="FoodShot architecture" width="820">
</p>

| Layer | Stack |
| --- | --- |
| Client | Telegram |
| Bot runtime | aiogram 3.x, FSM handlers |
| Web server | FastAPI webhook endpoint |
| Vision | OpenAI GPT-4o |
| Nutrition | USDA FoodData Central |
| Calculation | Custom bolus engine |
| State | Redis |
| Database | PostgreSQL, async SQLAlchemy |
| Deployment | Docker, Docker Compose |

## Commands

| Command | Purpose |
| --- | --- |
| `/start` | Register profile: ICR, ISF, target glucose, insulin type. |
| `/settings` | Edit profile values and change language. |
| `/history` | Show the last 10 meals. |
| `/help` | Show a short usage hint. |
| `/skip` | Skip current glucose during meal analysis. |

## Bolus Formula

FoodShot keeps the calculation transparent:

```text
carb_dose  = carbs_g / icr
correction = (current_bg - target_bg) / isf
total      = carb_dose + correction
```

Correction is used only when the user provides current glucose and it is above the target.

## Project Structure

```text
.
├── api/
│   └── webhook.py          # FastAPI app and Telegram webhook
├── bot/
│   ├── handlers/           # start, photo, settings, history, help
│   ├── keyboards/          # reply and inline keyboards
│   ├── states.py           # aiogram FSM states
│   └── i18n_middleware.py  # language detection
├── core/
│   ├── config.py           # pydantic settings
│   └── i18n.py             # runtime translations
├── db/
│   ├── models.py           # SQLAlchemy models
│   ├── crud.py             # async DB operations
│   └── database.py         # engine and session setup
├── services/
│   ├── vision.py           # OpenAI vision wrapper
│   ├── nutrition.py        # nutrition data client
│   └── calc.py             # bolus calculation
├── doc/
│   ├── foodshot_architecture.svg
│   └── tg_fries.png
├── docker-compose.yml
├── Dockerfile
├── Taskfile.yml
└── pyproject.toml
```

## Environment

Create `.env` from the example:

```bash
cp .env.example .env
```

Required values:

```env
BOT_TOKEN=your_telegram_bot_token
OPENAI_API_KEY=your_openai_api_key
USDA_API_KEY=your_usda_api_key

POSTGRES_USER=foodshot
POSTGRES_PASSWORD=foodshot_pass
POSTGRES_DB=foodshot

DATABASE_URL=postgresql+asyncpg://foodshot:foodshot_pass@localhost:5432/foodshot
REDIS_URL=redis://localhost:6379/0

WEBHOOK_URL=https://your-ngrok-domain.ngrok-free.app/webhook
PORT=8000
```

For Docker Compose, the bot container overrides database and Redis hosts internally:

```text
DATABASE_URL -> db:5432
REDIS_URL    -> redis:6379
```

That keeps `.env` convenient for local development while Docker services still talk to each other by service name.

## Quick Start

Install dependencies:

```bash
task install
```

Start PostgreSQL and Redis only:

```bash
task infra
```

Run FastAPI locally with reload:

```bash
task dev
```

Run the full Docker stack:

```bash
task up
```

Show logs:

```bash
task logs
```

Stop services:

```bash
task down
```

## Webhook Setup

Expose port `8000` with ngrok:

```bash
ngrok http 8000
```

Set the Telegram webhook URL in `.env`:

```env
WEBHOOK_URL=https://your-ngrok-domain.ngrok-free.app/webhook
```

The app registers this URL on startup:

```text
POST /webhook
```

If Telegram keeps calling an old URL, inspect it with:

```bash
curl -s "https://api.telegram.org/bot$BOT_TOKEN/getWebhookInfo"
```

## Data Model

FoodShot stores:

- `users`: Telegram id, username, ICR, ISF, target glucose, insulin type, language.
- `meal_logs`: dish, portion, macros, suggested bolus, current glucose, photo id, timestamp.

## Safety

Food recognition, portion estimation, nutrition databases, and insulin formulas can be wrong. FoodShot is an assistant for estimation, not a clinical decision system.

Always verify calculations before making insulin decisions and follow the treatment plan agreed with a qualified healthcare professional.
