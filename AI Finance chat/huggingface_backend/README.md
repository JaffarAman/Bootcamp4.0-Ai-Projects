---
title: Finance Agent API
emoji: 💰
colorFrom: indigo
colorTo: blue
sdk: docker
pinned: false
---

# Finance Agent API

FastAPI backend for the AI-Powered Financial Operations Agent.

## Environment Variables (Secrets)

Set these in your HuggingFace Space → **Settings → Repository Secrets**:

| Variable | Description |
|---|---|
| `GOOGLE_API_KEY` | Your Google Gemini API key |
| `DATABASE_URL` | PostgreSQL connection string (e.g. from Supabase, Neon, or Railway) |

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Health check |
| POST | `/api/v1/chat` | AI chat interface |
| POST | `/api/v1/transaction` | Add a transaction |
| GET | `/api/v1/transactions` | List transactions |
| GET | `/api/v1/summary` | Financial summary |
| GET | `/api/v1/charts` | Chart data |
| GET | `/api/v1/categories` | List categories |

## Notes

- This Space uses the **Docker** SDK — it runs the FastAPI app on port **7860**.
- Make sure your `DATABASE_URL` points to a **cloud PostgreSQL** database (not localhost).
  - Free options: [Supabase](https://supabase.com), [Neon](https://neon.tech), [Railway](https://railway.app)
