from fastapi import APIRouter, Depends, HTTPException
from application.dependencies import get_auth_service
from fastapi.security import OAuth2PasswordRequestForm
from core.db_infrastructure.db_components.schemas import UserAuthBase, UserRead, Token
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

@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service=Depends(get_auth_service)
):
    try:
        return auth_service.login_user(
            email=form_data.username,
            password=form_data.password
        )
    except InvalidCredentialsError as e:
        raise HTTPException(status_code=401, detail=str(e))

# @router.post("/login", response_model=Token)
# def login(user: UserAuthBase, auth_service=Depends(get_auth_service)):
#     try:
#         return auth_service.login_user(user.email, user.password)
#     except InvalidCredentialsError as e:
#         raise HTTPException(status_code=401, detail=str(e))