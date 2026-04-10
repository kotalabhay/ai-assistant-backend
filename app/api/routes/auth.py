"""Authentication routing for login operations."""

from fastapi import APIRouter, HTTPException, status

from app.core.config import settings
from app.core.security import create_access_token
from app.models.schemas import LoginRequest, LoginResponse

router = APIRouter()


@router.post("/login", response_model=LoginResponse)
async def login(credentials: LoginRequest):
    """Authenticates the user and returns a JWT access token.

    Args:
        credentials: The user's username and password.

    Returns:
        A LoginResponse containing the access token.

    Raises:
        HTTPException: If the credentials are invalid.
    """
    if credentials.username != settings.admin_username or credentials.password != settings.admin_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    access_token = create_access_token(data={"sub": credentials.username})
    return LoginResponse(access_token=access_token)
