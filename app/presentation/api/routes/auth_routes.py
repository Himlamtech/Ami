"""Authentication routes - Refactored with Clean Architecture."""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from app.presentation.api.schemas.auth_dto import (
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from app.application.use_cases.auth import (
    LoginUserInput,
    RegisterUserInput,
)
from app.domain.exceptions.user_exceptions import (
    UserNotFoundException,
    UserAlreadyExistsException,
    InvalidCredentialsException,
    UserNotActiveException,
)
from app.infrastructure.factory import get_factory


router = APIRouter(prefix="/auth", tags=["authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest):
    """Register new user."""
    try:
        factory = get_factory()
        use_case = factory.create_register_use_case()
        
        result = await use_case.execute(
            RegisterUserInput(
                username=request.username,
                email=request.email,
                password=request.password,
                full_name=request.full_name,
            )
        )
        
        return UserResponse(
            id=result.user.id,
            username=result.user.username,
            email=result.user.email,
            full_name=result.user.full_name,
            is_active=result.user.is_active,
            role_ids=result.user.role_ids,
        )
        
    except UserAlreadyExistsException as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/login", response_model=TokenResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login and get JWT token."""
    try:
        factory = get_factory()
        use_case = factory.create_login_use_case()
        jwt_handler = factory.get_jwt_handler()
        
        result = await use_case.execute(
            LoginUserInput(
                username=form_data.username,
                password=form_data.password,
            )
        )
        
        access_token = jwt_handler.create_access_token(
            data={
                "sub": result.user.username,
                "user_id": result.user.id,
                "role_ids": result.user.role_ids,
            }
        )
        
        return TokenResponse(access_token=access_token)
        
    except (UserNotFoundException, InvalidCredentialsException, UserNotActiveException) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Get current authenticated user."""
    try:
        factory = get_factory()
        use_case = factory.create_verify_token_use_case()
        
        user = await use_case.execute(token)
        
        return UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            is_active=user.is_active,
            role_ids=user.role_ids,
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
