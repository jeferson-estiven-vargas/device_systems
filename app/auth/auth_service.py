# app/auth/auth_service.py
from typing import Optional
from sqlalchemy.orm import Session

from app.auth.security import get_password_hash, verify_password
from app.models.user_model import User
from app.services import user_service


def registrar_usuario(db: Session, datos: dict) -> User:
    """Crea un usuario nuevo hasheando la contrasena. Asume que el email ya fue validado como unico."""
    datos = dict(datos)
    password_plano = datos.pop("password")
    datos["hashed_password"] = get_password_hash(password_plano)
    return user_service.crear_usuario(db, datos)


def autenticar_usuario(db: Session, email: str, password: str) -> Optional[User]:
    """Verifica credenciales de login. Devuelve el usuario si son correctas, None si no."""
    usuario = user_service.buscar_usuario_por_email(db, email)
    if not usuario:
        return None
    if not verify_password(password, usuario.hashed_password):
        return None
    return usuario
