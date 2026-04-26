# FoodShot — MVP Specification

> Telegram bot for people with diabetes: food photo → calorie count + insulin dose recommendation.

---

## Scope

This document defines the **minimum viable product** of FoodShot.
Everything outside this scope is post-MVP.

---

## Core User Flow

```
User sends food photo
  → Bot downloads the image
  → Vision AI identifies dish + estimates portion (g)
  → Nutrition API fetches macros (carbs, kcal, protein, fat)
  → Calc Engine computes insulin bolus based on user profile
  → Bot replies with structured result card
  → Log entry saved to PostgreSQL
```

---

## Features

### 1. Onboarding (`/start`)

| Field | Description | Example |
|---|---|---|
| `icr` | Insulin-to-carb ratio (g carbs per 1U insulin) | `10` |
| `isf` | Insulin sensitivity factor (mmol/L drop per 1U) | `2.5` |
| `target_bg` | Target blood glucose (mmol/L) | `5.5` |
| `insulin_type` | Rapid-acting brand name | `NovoRapid` |

- Bot guides the user step-by-step via FSM (aiogram states).
- Profile saved to PostgreSQL `users` table.
- User can edit profile anytime with `/settings`.

---

### 2. Food Photo Analysis

- User sends any photo in chat.
- Bot replies: *"Analyzing your meal…"* while processing.
- Vision AI (GPT-4o Vision) extracts:
  - Dish name
  - Estimated weight (grams)
  - Confidence level (high / medium / low)
- If confidence is **low** → bot asks user to confirm or correct the dish name.

---

### 3. Nutrition Lookup (REST API)

- Primary: **USDA FoodData Central** (free, no key required for basic use)
- Fallback: **Nutritionix** (free tier: 500 req/day)
- Data fetched per 100g, scaled to estimated portion.

| Macro | Unit |
|---|---|
| Carbohydrates | g |
| Calories | kcal |
| Protein | g |
| Fat | g |

---

### 4. Insulin Dose Calculation

#### Bolus formula

```
carb_dose   = carbs_g / icr
correction  = (current_bg - target_bg) / isf   # only if user provides BG
total_dose  = carb_dose + correction
```

#### Input from user (optional)

- Bot can ask: *"What is your current blood glucose? (skip with /skip)"*
- If skipped → correction dose = 0, only carb bolus is calculated.

#### Output card sent to user

```
🍝 Pasta Bolognese (~250g)

Carbs:    48 g
Calories: 390 kcal
Protein:  18 g
Fat:      12 g

💉 Suggested bolus: 4.8 U (NovoRapid)
   Carb dose:   4.8 U
   Correction:  0.0 U (no BG provided)

⚠️ This is an estimate. Always verify with your doctor.
```

---

### 5. Logging

Every analyzed meal is saved automatically:

```sql
meal_logs (
  id, user_id, created_at,
  dish_name, portion_g,
  carbs_g, kcal, protein_g, fat_g,
  bolus_dose, current_bg,
  photo_file_id
)
```

- `/history` — shows last 10 meals as a list.
- No charts or export in MVP.

---

### 6. Commands

| Command | Description |
|---|---|
| `/start` | Onboarding, create profile |
| `/settings` | Edit ICR / ISF / target BG |
| `/history` | Last 10 meal logs |
| `/help` | Short usage guide |

---

## Technical Stack

| Layer | Technology |
|---|---|
| Bot framework | aiogram 3.x |
| Web server | FastAPI (webhook handler) |
| Vision AI | OpenAI GPT-4o Vision API |
| Nutrition data | USDA FoodData Central REST API |
| Database | PostgreSQL + SQLAlchemy (async) |
| State management | Redis (aiogram FSMContext) |
| Environment | Docker + docker-compose |
| Config | `.env` via `pydantic-settings` |

---

## Project Structure

```
foodshot/
├── bot/
│   ├── handlers/
│   │   ├── start.py        # onboarding FSM
│   │   ├── photo.py        # photo handler → analysis pipeline
│   │   ├── history.py      # /history command
│   │   └── settings.py     # /settings FSM
│   ├── keyboards/          # inline keyboards
│   ├── states.py           # FSM state groups
│   └── middlewares.py      # user injection middleware
├── services/
│   ├── vision.py           # GPT-4o Vision wrapper
│   ├── nutrition.py        # USDA / Nutritionix client
│   └── calc.py             # insulin bolus formula
├── db/
│   ├── models.py           # SQLAlchemy models
│   └── crud.py             # async DB queries
├── api/
│   └── webhook.py          # FastAPI app + /webhook endpoint
├── core/
│   └── config.py           # pydantic Settings
├── docker-compose.yml
├── Dockerfile
└── .env.example
```

---

## Database Schema

```sql
CREATE TABLE users (
  id          BIGINT PRIMARY KEY,   -- Telegram user_id
  username    TEXT,
  icr         FLOAT NOT NULL,       -- g carbs / 1U
  isf         FLOAT NOT NULL,       -- mmol/L drop / 1U
  target_bg   FLOAT NOT NULL,       -- mmol/L
  insulin_type TEXT,
  created_at  TIMESTAMP DEFAULT NOW()
);

CREATE TABLE meal_logs (
  id           SERIAL PRIMARY KEY,
  user_id      BIGINT REFERENCES users(id),
  created_at   TIMESTAMP DEFAULT NOW(),
  dish_name    TEXT,
  portion_g    FLOAT,
  carbs_g      FLOAT,
  kcal         FLOAT,
  protein_g    FLOAT,
  fat_g        FLOAT,
  bolus_dose   FLOAT,
  current_bg   FLOAT,              -- nullable
  photo_file_id TEXT
);
```

---

## Environment Variables

```env
BOT_TOKEN=
OPENAI_API_KEY=
USDA_API_KEY=          # optional, higher rate limits
NUTRITIONIX_APP_ID=    # optional fallback
NUTRITIONIX_API_KEY=   # optional fallback
DATABASE_URL=postgresql+asyncpg://user:pass@db:5432/foodshot
REDIS_URL=redis://redis:6379/0
WEBHOOK_URL=https://yourdomain.com/webhook
```

---

## Out of Scope (Post-MVP)

- Meal history charts / export to CSV
- CGM integration (Dexcom, Libre)
- Basal rate recommendations
- Multiple insulin types per user
- Web dashboard
- Internationalization (i18n)
- Push reminders

---

## Disclaimer

> FoodShot provides **estimates only**. It is not a medical device and does not replace advice from a qualified healthcare professional. Always consult your doctor before adjusting insulin doses.

---

*FoodShot MVP — v0.1*
*License: Business Source License 1.1 (BUSL-1.1)*
