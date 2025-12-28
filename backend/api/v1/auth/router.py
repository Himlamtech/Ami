from fastapi import APIRouter, HTTPException, status, Header
from api.schemas.auth_dto import LoginRequest, RegisterRequest, AuthResponse
from config.services import ServiceRegistry
from domain.entities.student_profile import StudentProfile, StudentLevel
from infrastructure.persistence.mongodb.client import get_database
from application.services.password_service import hash_password, verify_password
from typing import Optional
from datetime import datetime
from bson import ObjectId

router = APIRouter(prefix="/auth", tags=["auth"])


def _normalize_identifier(identifier: str) -> str:
    return identifier.strip().lower()


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    identifier = _normalize_identifier(request.email)
    db = await get_database()

    user = await db.users.find_one(
        {"$or": [{"email": identifier}, {"username": identifier}]}
    )
    if not user or not verify_password(
        request.password, user.get("hashed_password", "")
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive",
        )

    user_id = str(user.get("_id"))
    role = user.get("role", "user")
    full_name = user.get("full_name") or user.get("username") or identifier
    email = user.get("email") or identifier

    return AuthResponse(
        user_id=user_id,
        token=user_id,
        role=role,
        full_name=full_name,
        email=email,
    )


@router.post("/register", response_model=AuthResponse)
async def register(
    request: RegisterRequest,
    x_user_id: Optional[str] = Header(None, alias="X-User-ID"),
):
    if not x_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin access required",
        )

    db = await get_database()
    try:
        admin_user = await db.users.find_one({"_id": ObjectId(x_user_id)})
    except Exception:
        admin_user = None

    if not admin_user or admin_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    if request.password != request.password_confirmation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match",
        )

    email = request.email.strip().lower()
    username = (request.username or email.split("@")[0]).strip().lower()
    role = (request.role or "user").strip().lower()
    if role not in ("user", "manager"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role",
        )
    existing = await db.users.find_one(
        {"$or": [{"email": email}, {"username": username}]}
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    now = datetime.now()
    user_doc = {
        "username": username,
        "email": email,
        "full_name": request.full_name,
        "role": role,
        "hashed_password": hash_password(request.password),
        "is_active": True,
        "created_at": now,
        "updated_at": now,
    }
    result = await db.users.insert_one(user_doc)
    user_id = str(result.inserted_id)

    profile_repo = ServiceRegistry.get_student_profile_repository()
    profile = StudentProfile(
        id=user_id,
        user_id=user_id,
        email=email,
        name=request.full_name,
        level=StudentLevel.FRESHMAN,
    )
    await profile_repo.create(profile)

    return AuthResponse(
        user_id=user_id,
        token=user_id,
        role=role,
        full_name=request.full_name,
        email=email,
    )
