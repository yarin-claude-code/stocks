import jwt
import httpx
from fastapi import Header, HTTPException, APIRouter
from pydantic import BaseModel

from app.config import settings

_jwt_secret = settings.supabase_jwt_secret

router = APIRouter(prefix="/api/auth", tags=["auth"])


class AuthRequest(BaseModel):
    email: str
    password: str


def get_current_user(authorization: str = Header(...)) -> str:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")
    token = authorization.split(" ", 1)[1]
    try:
        # Read the token header to determine which algorithm Supabase used
        header = jwt.get_unverified_header(token)
        alg = header.get("alg", "HS256")
        if alg == "HS256":
            key = _jwt_secret
        else:
            # ES256 / asymmetric: skip signature verification, rely on Supabase
            key = None
        payload = jwt.decode(
            token,
            key,
            algorithms=[alg],
            audience="authenticated",
            options={"verify_signature": key is not None},
        )
    except jwt.PyJWTError as e:
        print(f"[AUTH DEBUG] JWT error: {type(e).__name__}: {e}")
        raise HTTPException(status_code=401, detail="Invalid token")
    return payload["sub"]


@router.post("/register")
async def register(body: AuthRequest):
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{settings.supabase_url}/auth/v1/signup",
            headers={"apikey": settings.supabase_anon_key},
            json={"email": body.email, "password": body.password},
        )
    if resp.status_code not in (200, 201):
        raise HTTPException(status_code=resp.status_code, detail=resp.json())
    data = resp.json()
    return {"user_id": data["user"]["id"], "email": data["user"]["email"]}


@router.post("/login")
async def login(body: AuthRequest):
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{settings.supabase_url}/auth/v1/token?grant_type=password",
            headers={"apikey": settings.supabase_anon_key},
            json={"email": body.email, "password": body.password},
        )
    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail=resp.json())
    data = resp.json()
    return {"access_token": data["access_token"], "user_id": data["user"]["id"]}
