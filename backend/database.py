import certifi
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from config import settings

client: AsyncIOMotorClient | None = None


async def init_db():
    global client
    client = AsyncIOMotorClient(
        settings.MONGODB_URL,
        tlsCAFile=certifi.where(),
        serverSelectionTimeoutMS=10000,
    )
    db = client[settings.DATABASE_NAME]

    from models.user import User
    from models.task import Task
    from models.session import StudySession
    from models.alert import Alert
    from models.metric import ProductivityMetric
    from models.burnout import BurnoutAssessment
    from models.recommendation import Recommendation

    await init_beanie(
        database=db,
        document_models=[
            User,
            Task,
            StudySession,
            Alert,
            ProductivityMetric,
            BurnoutAssessment,
            Recommendation,
        ],
    )


async def close_db():
    global client
    if client:
        client.close()
