from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from database import init_db, close_db
from routers import auth, tasks, sessions, alerts, analytics, burnout, recommendations, reports, cron


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await close_db()


app = FastAPI(
    title="Burnout Beacon API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http://localhost:\d+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(tasks.router)
app.include_router(sessions.router)
app.include_router(alerts.router)
app.include_router(analytics.router)
app.include_router(burnout.router)
app.include_router(recommendations.router)
app.include_router(reports.router)
app.include_router(cron.router)


@app.get("/api/health")
async def health():
    return {"status": "ok"}
