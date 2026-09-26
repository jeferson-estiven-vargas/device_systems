# app/dependencies/auth_dependency.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.auth.security import decode_access_token
from app.dependencies.database_dependency import get_db
from app.models.user_model import User
from app.services import user_service

# tokenUrl apunta al endpoint de login para que Swagger sepa donde pedir el token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

credenciales_invalidas = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="No se pudo validar el token de acceso",
    headers={"WWW-Authenticate": "Bearer"},
)


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """Decodifica el token JWT y devuelve el usuario autenticado. 401 si el token es invalido, esta expirado o el usuario ya no existe."""
    payload = decode_access_token(token)
    if payload is None:
        raise credenciales_invalidas

    email = payload.get("sub")
    if email is None:
        raise credenciales_invalidas

    usuario = user_service.buscar_usuario_por_email(db, email)
    if usuario is None:
        raise credenciales_invalidas

    return usuario


def get_current_active_user(usuario: User = Depends(get_current_user)) -> User:
    """Exige ademas que el usuario autenticado este activo (is_active=True)."""
    if not usuario.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El usuario esta inactivo",
        )
    return usuario

def require_roles(*roles_permitidos: str):
    """Fabrica de dependencias: exige que el usuario autenticado tenga uno de los roles indicados. 403 si no cumple."""

    def _verificar_rol(usuario: User = Depends(get_current_active_user)) -> User:
        if usuario.role not in roles_permitidos:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Se requiere alguno de estos roles: {', '.join(roles_permitidos)}",
            )
        return usuario

    return _verificar_rol


require_admin = require_roles("admin")
require_admin_or_support = require_roles("admin", "support")