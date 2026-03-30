from fastapi import HTTPException, status

from auth.password import hash_password, verify_password
from auth.jwt import create_access_token, create_refresh_token
from models.user import User
from schemas.auth import SignupRequest, LoginRequest


async def signup(data: SignupRequest) -> tuple[User, str, str]:
    existing = await User.find_one(User.email == data.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    user = User(
        name=data.name,
        email=data.email,
        password_hash=hash_password(data.password),
    )
    await user.insert()

    access_token = create_access_token(str(user.id))
    refresh_token = create_refresh_token(str(user.id))
    return user, access_token, refresh_token


async def login(data: LoginRequest) -> tuple[User, str, str]:
    user = await User.find_one(User.email == data.email)
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    access_token = create_access_token(str(user.id))
    refresh_token = create_refresh_token(str(user.id))
    return user, access_token, refresh_token
