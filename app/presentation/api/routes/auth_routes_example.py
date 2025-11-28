"""
Example: Refactored Auth Routes using Clean Architecture.

This demonstrates how to use Use Cases in presentation layer.
Compare with old app/api/auth_routes.py to see the improvement.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Optional

# Use Cases (Application Layer)
from app.application.use_cases.auth import (
    LoginUserUseCase,
    LoginUserInput,
    RegisterUserUseCase,
    RegisterUserInput,
    VerifyTokenUseCase,
)

# Domain exceptions
from app.domain.exceptions.user_exceptions import (
    UserNotFoundException,
    UserAlreadyExistsException,
    InvalidCredentialsException,
    UserNotActiveException,
)

# Infrastructure (will be injected via dependencies)
from app.infrastructure.auth import JWTHandler, PasswordHasher
from app.infrastructure.repositories.mongodb_user_repository import MongoDBUserRepository
from app.infrastructure.db.mongodb import get_database


router = APIRouter(prefix="/auth", tags=["authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


# ===== DTOs (Data Transfer Objects) =====

class RegisterRequest(BaseModel):
    """Registration request DTO."""
    username: str
    email: str
    password: str
    full_name: Optional[str] = None


class LoginResponse(BaseModel):
    """Login response DTO."""
    access_token: str
    token_type: str = "bearer"
    user_id: str
    username: str


class UserResponse(BaseModel):
    """User response DTO."""
    id: str
    username: str
    email: str
    full_name: Optional[str]
    is_active: bool


# ===== Dependency Injection =====

async def get_user_repository():
    """Get user repository instance."""
    db = await get_database()
    return MongoDBUserRepository(db)


async def get_password_hasher():
    """Get password hasher instance."""
    return PasswordHasher()


async def get_jwt_handler():
    """Get JWT handler instance."""
    return JWTHandler()


async def get_login_use_case(
    user_repo: MongoDBUserRepository = Depends(get_user_repository),
    password_hasher: PasswordHasher = Depends(get_password_hasher),
):
    """Get login use case with dependencies."""
    return LoginUserUseCase(user_repo, password_hasher)


async def get_register_use_case(
    user_repo: MongoDBUserRepository = Depends(get_user_repository),
    password_hasher: PasswordHasher = Depends(get_password_hasher),
):
    """Get register use case with dependencies."""
    return RegisterUserUseCase(user_repo, password_hasher)


async def get_verify_token_use_case(
    user_repo: MongoDBUserRepository = Depends(get_user_repository),
    jwt_handler: JWTHandler = Depends(get_jwt_handler),
):
    """Get verify token use case with dependencies."""
    return VerifyTokenUseCase(user_repo, jwt_handler)


# ===== Routes =====

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    use_case: RegisterUserUseCase = Depends(get_register_use_case),
):
    """
    Register new user.
    
    Clean Architecture Benefits:
    - Route is thin, just handles HTTP concerns
    - Business logic in use case
    - Domain validation in value objects
    - Easy to test use case independently
    """
    try:
        # Use case handles all business logic
        result = await use_case.execute(
            RegisterUserInput(
                username=request.username,
                email=request.email,
                password=request.password,
                full_name=request.full_name,
            )
        )
        
        # Map domain entity to DTO
        return UserResponse(
            id=result.user.id,
            username=result.user.username,
            email=result.user.email,
            full_name=result.user.full_name,
            is_active=result.user.is_active,
        )
        
    except UserAlreadyExistsException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )
    except ValueError as e:  # From value object validation
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/login", response_model=LoginResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    use_case: LoginUserUseCase = Depends(get_login_use_case),
    jwt_handler: JWTHandler = Depends(get_jwt_handler),
):
    """
    Login user and return JWT token.
    
    Clean Architecture Benefits:
    - Credential validation in use case
    - Password verification abstracted
    - Token generation separate concern
    """
    try:
        # Use case validates credentials
        result = await use_case.execute(
            LoginUserInput(
                username=form_data.username,
                password=form_data.password,
            )
        )
        
        # Infrastructure layer creates token
        access_token = jwt_handler.create_access_token(
            data={
                "sub": result.user.username,
                "user_id": result.user.id,
                "role_ids": result.user.role_ids,
            }
        )
        
        return LoginResponse(
            access_token=access_token,
            user_id=result.user.id,
            username=result.user.username,
        )
        
    except (UserNotFoundException, InvalidCredentialsException, UserNotActiveException) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    use_case: VerifyTokenUseCase = Depends(get_verify_token_use_case),
):
    """
    Get current authenticated user.
    
    Clean Architecture Benefits:
    - Token verification in use case
    - User retrieval abstracted
    - Easy to add authorization logic
    """
    try:
        user = await use_case.execute(token)
        
        return UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            is_active=user.is_active,
        )
        
    except (InvalidCredentialsException, UserNotFoundException, UserNotActiveException) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


# ===== Comparison with Old Code =====
"""
OLD WAY (in app/api/auth_routes.py):
- Direct database access in routes
- Business logic mixed with HTTP logic
- Hard to test
- Tight coupling

@router.post("/login")
async def login(request: LoginRequest, db=Depends(get_db)):
    # Direct DB access ❌
    user_doc = await db["users"].find_one({"username": request.username})
    
    # Business logic in route ❌
    if not user_doc:
        raise HTTPException(...)
    
    # Password verification in route ❌
    if not verify_password(request.password, user_doc["hashed_password"]):
        raise HTTPException(...)
    
    # Token creation in route ❌
    token = create_access_token(...)
    
    return {"access_token": token}


NEW WAY (Clean Architecture):
- Use cases handle business logic ✅
- Routes are thin, just HTTP concerns ✅
- Easy to test each layer ✅
- Loose coupling via interfaces ✅

@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    use_case: LoginUserUseCase = Depends(get_login_use_case),
):
    result = await use_case.execute(...)  # ✅ Business logic in use case
    token = jwt_handler.create_access_token(...)  # ✅ Infrastructure concern
    return LoginResponse(...)  # ✅ Clean return

Benefits:
1. Testability: Can test use case without FastAPI
2. Maintainability: Clear separation of concerns
3. Flexibility: Easy to swap implementations
4. Reusability: Use cases can be used in different contexts (CLI, gRPC, etc.)
"""
