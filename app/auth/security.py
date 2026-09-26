# app/auth/security.py
# Utilidades de seguridad: hash de contraseñas con passlib y tokens JWT con python-jose

import os
from datetime import datetime, timedelta, timezone
from typing import Optional

from dotenv import load_dotenv
from jose import JWTError, jwt
from passlib.context import CryptContext

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

if not SECRET_KEY:
    raise RuntimeError(
        "SECRET_KEY no esta configurada. Copia .env.example a .env y define una clave "
        "(genera una con: python -c \"import secrets; print(secrets.token_hex(32))\")."
    )

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """Genera el hash seguro de una contraseña en texto plano."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica que una contraseña en texto plano coincida con su hash almacenado."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Genera un token JWT firmado a partir de los datos indicados (ej: {'sub': email})."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> Optional[dict]:
    """Decodifica y valida un token JWT. Devuelve None si es invalido, esta mal firmado o expiro."""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None
