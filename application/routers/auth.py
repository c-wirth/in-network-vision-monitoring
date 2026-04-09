from fastapi import APIRouter, Depends, HTTPException
from core.db_infrastructure.db_components.schemas import UserAuthBase, UserRead
from application.dependencies import get_auth_service
from application.services.user_auth_service import (
    UserAlreadyExistsError,
    InvalidCredentialsError
)

router = APIRouter()


# ------------------------
# REGISTER
# ------------------------
@router.post("/register", response_model=UserRead)
def register(user: UserAuthBase, auth_service=Depends(get_auth_service)):
    try:
        return auth_service.register_user(user.email, user.password)
    except UserAlreadyExistsError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ------------------------
# LOGIN
# ------------------------
@router.post("/login", response_model=UserRead)
def login(user: UserAuthBase, auth_service=Depends(get_auth_service)):
    try:
        return auth_service.login_user(user.email, user.password)
    except InvalidCredentialsError as e:
        raise HTTPException(status_code=401, detail=str(e))