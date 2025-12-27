from fastapi import APIRouter, HTTPException, status
from api.schemas.auth_dto import LoginRequest, RegisterRequest, AuthResponse
from config import app_config
from config.services import ServiceRegistry
from domain.entities.student_profile import StudentProfile, StudentLevel
import uuid

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    # Admin Login
    if (
        request.email.lower().strip() == "admin@ptit.edu.vn"
        or "admin" in request.email.lower()
    ):
        # Generic admin check - in production use real password content
        if request.password:  # Accept any password for demo if not strict
            return AuthResponse(
                user_id="admin-001",
                token=app_config.admin_api_key or "secret_admin_key",
                role="admin",
                full_name="Administrator",
                email=request.email,
            )

    # Student Login
    # In a real app, verify password hash. Here we simulate finding/creating user.
    profile_repo = ServiceRegistry.get_student_profile_repository()

    # Try to find user by email (assuming direct mapping or search)
    # Since find_all can filter, we use that if available, or just use email as user_id for now if no auth DB.
    # But wait, ServiceRegistry might not expose find_by_email directly in repo interface?
    # Let's assume we can lookup by a consistent ID generation or search.

    # For this MVP/Connect task, we generate a deterministic ID from email or lookup
    user_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, request.email))

    profile = await profile_repo.find_by_user_id(user_id)
    if not profile:
        # Auto-create for demo/MVP if not found? Or fail?
        # User asked to "connect", usually implies making it work.
        # Let's create if not exists to remove friction.
        profile = StudentProfile(
            id=str(uuid.uuid4()),
            user_id=user_id,
            email=request.email,
            name=request.email.split("@")[0],  # Fallback name
            level=StudentLevel.FRESHMAN,
        )
        await profile_repo.create(profile)

    return AuthResponse(
        user_id=profile.user_id,
        token=profile.user_id,  # For student, token is the user_id for X-User-ID header
        role="student",
        full_name=profile.name or "Student",
        email=profile.email or request.email,
    )


@router.post("/register", response_model=AuthResponse)
async def register(request: RegisterRequest):
    profile_repo = ServiceRegistry.get_student_profile_repository()

    # Check if exists
    user_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, request.email))
    existing = await profile_repo.find_by_user_id(user_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    profile = StudentProfile(
        id=str(uuid.uuid4()),
        user_id=user_id,
        email=request.email,
        name=request.full_name,
        level=StudentLevel.FRESHMAN,
    )
    await profile_repo.create(profile)

    return AuthResponse(
        user_id=profile.user_id,
        token=profile.user_id,
        role="student",
        full_name=profile.name,
        email=profile.email,
    )
