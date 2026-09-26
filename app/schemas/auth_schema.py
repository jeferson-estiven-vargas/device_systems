# app/schemas/auth_schema.py
import re
from typing import Literal, Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


class UserRegister(BaseModel):
    """Datos requeridos para registrar un usuario nuevo (POST /auth/register)."""

    name: str = Field(..., min_length=3)
    email: EmailStr
    password: str = Field(
        ...,
        min_length=8,
        description="Minimo 8 caracteres, con al menos una mayuscula, una minuscula y un numero, sin espacios",
    )
    role: Literal["admin", "support", "user"]

    @field_validator("password")
    @classmethod
    def password_segura(cls, value: str) -> str:
        if " " in value:
            raise ValueError("La contrasena no puede contener espacios en blanco")
        if not re.search(r"[A-Z]", value):
            raise ValueError("La contrasena debe tener al menos una letra mayuscula")
        if not re.search(r"[a-z]", value):
            raise ValueError("La contrasena debe tener al menos una letra minuscula")
        if not re.search(r"\d", value):
            raise ValueError("La contrasena debe tener al menos un numero")
        return value


class UserLogin(BaseModel):
    """Credenciales para autenticarse (POST /auth/login)."""

    email: EmailStr
    password: str = Field(..., min_length=1)


class Token(BaseModel):
    """Respuesta del login: token JWT generado."""

    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Datos extraidos del payload de un token JWT decodificado."""

    email: Optional[EmailStr] = None
