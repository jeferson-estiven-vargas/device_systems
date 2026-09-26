# app/auth/auth_routes.py
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.auth import auth_service
from app.auth.security import create_access_token
from app.dependencies.auth_dependency import get_current_active_user
from app.dependencies.database_dependency import get_db
from app.middlewares.rate_limiter import limiter
from app.models.user_model import User
from app.schemas.auth_schema import Token, UserRegister
from app.schemas.user_schema import UserResponse
from app.services import user_service

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un usuario con contrasena segura",
    description="Crea un usuario nuevo validando nombre, email unico, contrasena segura y rol permitido. La contrasena se guarda como hash, nunca en texto plano.",
    response_description="Usuario creado, sin exponer la contrasena",
    responses={
        400: {"description": "El correo ya esta registrado"},
        422: {"description": "Error de validacion (contrasena debil, rol invalido, etc.)"},
    },
)
@limiter.limit("3/minute")
def registrar(request: Request, datos: UserRegister, db: Session = Depends(get_db)):
    if user_service.buscar_usuario_por_email(db, datos.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe un usuario registrado con el correo {datos.email}",
        )
    return auth_service.registrar_usuario(db, datos.model_dump())


@router.post(
    "/login",
    response_model=Token,
    summary="Autenticar usuario y generar token JWT",
    description=(
        "Flujo OAuth2 Password: envia 'username' (el email del usuario) y "
        "'password' como form-data. Compatible con el boton Authorize de Swagger."
    ),
    response_description="Token de acceso tipo bearer",
    responses={401: {"description": "Correo o contrasena incorrectos"}},
)
@limiter.limit("5/minute")
def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    usuario = auth_service.autenticar_usuario(db, form_data.username, form_data.password)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contrasena incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_access_token({"sub": usuario.email})
    return Token(access_token=token)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Consultar el usuario autenticado",
    description="Devuelve los datos del usuario dueno del token enviado en el header Authorization: Bearer <token>.",
    response_description="Datos del usuario autenticado",
    responses={401: {"description": "Token invalido, ausente o expirado"}},
)
def obtener_usuario_actual(usuario_actual: User = Depends(get_current_active_user)):
    return usuario_actual