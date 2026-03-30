# Burnout Beacon

A full-stack productivity and wellness app that tracks work sessions, manages tasks, monitors burnout risk, and provides actionable recommendations to maintain a healthy work-life balance.

## Tech Stack

| Layer    | Technology                                      |
| -------- | ----------------------------------------------- |
| Frontend | Next.js 14, React 18, TypeScript, Recharts      |
| Backend  | FastAPI, Pydantic v2, Python 3                   |
| Database | MongoDB (Motor + Beanie ODM)                     |
| Auth     | JWT (python-jose) + bcrypt                       |

## Project Structure

```
BurnoutBacon/
├── frontend/          # Next.js app
│   └── src/
│       ├── app/       # Pages (dashboard, tasks, focus, analytics, alerts, reports, planner)
│       ├── components/ # UI components & layout shell
│       ├── context/   # Auth & Timer providers
│       ├── hooks/     # Custom hooks (useTasks, useSessions)
│       └── lib/       # API client, types, utils
├── backend/           # FastAPI server
│   ├── routers/       # Route handlers (auth, tasks, sessions, alerts, analytics, burnout, recommendations, reports, cron)
│   ├── services/      # Business logic
│   ├── models/        # Beanie document models
│   ├── schemas/       # Pydantic request/response schemas
│   ├── auth/          # JWT & password utilities
│   ├── cron/          # Scheduled jobs
│   ├── scripts/       # Seed scripts
│   ├── config.py      # App settings
│   ├── database.py    # DB connection
│   └── main.py        # App entrypoint
└── .gitignore
```

## Getting Started

### Prerequisites

- Node.js 18+
- Python 3.11+
- MongoDB instance (local or Atlas)

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file in `backend/` with your config (MongoDB URI, JWT secret, etc.), then run:

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`. Health check: `GET /api/health`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The app will be available at `http://localhost:3000`.

## Features

- **Dashboard** -- overview of burnout risk, recent sessions, and key metrics
- **Task Management** -- create, update, and organize tasks
- **Focus Timer** -- timed work sessions with tracking
- **Burnout Monitoring** -- risk scoring and alert system
- **Analytics** -- charts and trends via Recharts
- **Smart Recommendations** -- personalized suggestions to reduce burnout
- **Reports** -- generated summaries of work patterns
- **Planner** -- schedule and reschedule tasks intelligently
- **Cron Jobs** -- automated background processing

## License

MIT
