"""Seed script to populate MongoDB with sample data."""
import sys
import os
import asyncio
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta
from database import init_db, close_db
from models.user import User
from models.task import Task
from models.session import StudySession
from models.alert import Alert
from auth.password import hash_password


async def seed():
    await init_db()

    # Check if already seeded
    existing = await User.find_one(User.email == "demo@burnoutbeacon.com")
    if existing:
        print("Database already has demo user. Skipping seed.")
        await close_db()
        return

    # Create sample user
    user = User(
        name="Demo User",
        email="demo@burnoutbeacon.com",
        password_hash=hash_password("password123"),
    )
    await user.insert()

    # Create sample tasks
    now = datetime.utcnow()
    tasks_data = [
        {"title": "DBMS Assignment - Normalization", "category": "Computer Science", "priority": "high", "status": "in_progress", "deadline": now + timedelta(days=3), "estimated_minutes": 180},
        {"title": "Physics Lab Report", "category": "Physics", "priority": "critical", "status": "todo", "deadline": now + timedelta(days=1), "estimated_minutes": 120},
        {"title": "Linear Algebra Problem Set", "category": "Math", "priority": "medium", "status": "todo", "deadline": now + timedelta(days=5), "estimated_minutes": 90},
        {"title": "React Portfolio Project", "category": "Computer Science", "priority": "medium", "status": "in_progress", "deadline": now + timedelta(days=7), "estimated_minutes": 360},
        {"title": "English Essay - Shakespeare", "category": "English", "priority": "low", "status": "done", "deadline": now - timedelta(days=2), "estimated_minutes": 60, "completed_at": now - timedelta(days=3)},
        {"title": "OS Revision - Process Scheduling", "category": "Computer Science", "priority": "high", "status": "todo", "deadline": now + timedelta(days=2), "estimated_minutes": 150},
        {"title": "Chemistry Lab Prep", "category": "Chemistry", "priority": "medium", "status": "done", "deadline": now - timedelta(days=1), "estimated_minutes": 45, "completed_at": now - timedelta(days=1)},
        {"title": "Data Structures - AVL Trees", "category": "Computer Science", "priority": "high", "status": "todo", "deadline": now + timedelta(days=4), "estimated_minutes": 120},
    ]

    task_objects = []
    for td in tasks_data:
        task = Task(user_id=user.id, **td)
        await task.insert()
        task_objects.append(task)

    # Create sample sessions (past few days)
    sessions_created = 0
    for days_ago in range(7, 0, -1):
        day = now - timedelta(days=days_ago)
        for hour_offset in [9, 14, 20]:
            if days_ago % 2 == 0 and hour_offset == 20:
                continue
            start = day.replace(hour=hour_offset, minute=0, second=0)
            duration = [45, 60, 90, 30][days_ago % 4]
            end = start + timedelta(minutes=duration)
            task_idx = (days_ago + hour_offset) % len(task_objects)
            session = StudySession(
                user_id=user.id,
                task_id=task_objects[task_idx].id,
                actual_start=start,
                actual_end=end,
                actual_duration_min=duration,
                session_type="deep_work",
                focus_rating=[3, 4, 5, 4, 3][days_ago % 5],
                was_completed=days_ago % 3 != 0,
            )
            await session.insert()
            sessions_created += 1

    # Create sample alerts
    alerts_data = [
        {"alert_type": "deadline_risk", "severity": "critical", "title": "Physics Lab Report Due Tomorrow", "message": "You have 120 minutes of work remaining but the deadline is in less than 24 hours."},
        {"alert_type": "burnout_risk", "severity": "warning", "title": "High Workload Detected", "message": "You've had 3 heavy workload days in a row. Consider taking a lighter day."},
        {"alert_type": "inactivity", "severity": "info", "title": "Math Needs Attention", "message": "Linear Algebra Problem Set has had no activity in 3 days."},
    ]

    for ad in alerts_data:
        alert = Alert(user_id=user.id, **ad)
        await alert.insert()

    print("Seed complete! Created:")
    print(f"  - 1 user (demo@burnoutbeacon.com / password123)")
    print(f"  - {len(tasks_data)} tasks")
    print(f"  - {sessions_created} sessions")
    print(f"  - {len(alerts_data)} alerts")

    await close_db()


if __name__ == "__main__":
    asyncio.run(seed())
