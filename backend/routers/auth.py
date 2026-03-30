from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status

from auth.dependencies import get_current_user
from auth.jwt import decode_token, create_access_token, create_refresh_token
from models.user import User
from schemas.auth import SignupRequest, LoginRequest, UserResponse
from services import auth_service

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _set_tokens(response: Response, access_token: str, refresh_token: str):
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        samesite="lax",
        max_age=30 * 60,
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        samesite="lax",
        max_age=7 * 24 * 60 * 60,
    )


def _user_response(user: User) -> UserResponse:
    return UserResponse(id=str(user.id), name=user.name, email=user.email)


@router.post("/signup", response_model=UserResponse)
async def signup(data: SignupRequest, response: Response):
    user, access_token, refresh_token = await auth_service.signup(data)
    _set_tokens(response, access_token, refresh_token)
    return _user_response(user)


@router.post("/login", response_model=UserResponse)
async def login(data: LoginRequest, response: Response):
    user, access_token, refresh_token = await auth_service.login(data)
    _set_tokens(response, access_token, refresh_token)
    return _user_response(user)


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return {"message": "Logged out"}


@router.get("/me", response_model=UserResponse)
async def me(current_user: User = Depends(get_current_user)):
    return _user_response(current_user)


@router.post("/refresh", response_model=UserResponse)
async def refresh(request: Request, response: Response):
    token = request.cookies.get("refresh_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No refresh token")

    payload = decode_token(token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    user_id = payload["sub"]
    user = await User.get(PydanticObjectId(user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    new_access = create_access_token(str(user.id))
    new_refresh = create_refresh_token(str(user.id))
    _set_tokens(response, new_access, new_refresh)
    return _user_response(user)
