import hashlib
import hmac
import json
from datetime import datetime, timedelta, timezone
from urllib.parse import parse_qs

from fastapi import APIRouter, Depends, HTTPException, status
from jose import jwt
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_session
from app.config import settings
from app.database.models import User
from app.i18n import get_user_locale

router = APIRouter(prefix="/auth", tags=["auth"])

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 30


class TelegramAuthRequest(BaseModel):
    init_data: str


class UserResponse(BaseModel):
    id: int
    username: str | None
    first_name: str | None
    locale: str
    geo: str
    jogai_coins: int
    is_pro: bool


class AuthResponse(BaseModel):
    access_token: str
    user: UserResponse


def validate_init_data(init_data: str, bot_token: str) -> dict | None:
    """Validate Telegram Mini App initData using HMAC-SHA256."""
    try:
        parsed = parse_qs(init_data)
        received_hash = parsed.get("hash", [None])[0]
        if not received_hash:
            return None

        # Build check string: sorted key=value pairs excluding hash
        pairs = []
        for key, values in parsed.items():
            if key != "hash":
                pairs.append(f"{key}={values[0]}")
        pairs.sort()
        check_string = "\n".join(pairs)

        # HMAC-SHA256 with secret key derived from bot token
        secret_key = hmac.new(
            b"WebAppData", bot_token.encode(), hashlib.sha256
        ).digest()
        calculated_hash = hmac.new(
            secret_key, check_string.encode(), hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(calculated_hash, received_hash):
            return None

        user_data = parsed.get("user", [None])[0]
        if not user_data:
            return None

        return json.loads(user_data)
    except Exception:
        return None


def create_access_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    return jwt.encode(
        {"sub": str(user_id), "exp": expire},
        settings.secret_key,
        algorithm=ALGORITHM,
    )


@router.post("/telegram", response_model=AuthResponse)
async def auth_telegram(
    body: TelegramAuthRequest,
    session: AsyncSession = Depends(get_session),
):
    # In development, allow bypass if no bot token configured
    user_data = validate_init_data(body.init_data, settings.telegram_bot_token)

    if not user_data and settings.environment == "development":
        # Fallback for dev: try to parse user from raw init_data
        try:
            parsed = parse_qs(body.init_data)
            raw = parsed.get("user", [None])[0]
            if raw:
                user_data = json.loads(raw)
        except Exception:
            pass

    if not user_data or "id" not in user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Telegram initData",
        )

    telegram_id = user_data["id"]
    language_code = user_data.get("language_code", "pt")
    locale = get_user_locale(language_code)
    geo = "MX" if locale == "es_MX" else "BR"

    # Upsert user
    result = await session.execute(select(User).where(User.id == telegram_id))
    user = result.scalar_one_or_none()

    if user:
        user.username = user_data.get("username")
        user.first_name = user_data.get("first_name")
        user.language_code = language_code
        user.last_active_at = datetime.now(timezone.utc)
    else:
        user = User(
            id=telegram_id,
            username=user_data.get("username"),
            first_name=user_data.get("first_name"),
            language_code=language_code,
            locale=locale,
            geo=geo,
        )
        session.add(user)

    await session.commit()
    await session.refresh(user)

    token = create_access_token(user.id)

    return AuthResponse(
        access_token=token,
        user=UserResponse(
            id=user.id,
            username=user.username,
            first_name=user.first_name,
            locale=user.locale,
            geo=user.geo,
            jogai_coins=user.jogai_coins,
            is_pro=user.is_pro,
        ),
    )


@router.get("/me", response_model=UserResponse)
async def get_me(
    user: User = Depends(get_current_user),
):
    return UserResponse(
        id=user.id,
        username=user.username,
        first_name=user.first_name,
        locale=user.locale,
        geo=user.geo,
        jogai_coins=user.jogai_coins,
        is_pro=user.is_pro,
    )
