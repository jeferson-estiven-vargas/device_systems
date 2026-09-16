# app/dependencies/database_dependency.py
# Dependencia que entrega una sesion de base de datos a cada peticion

from app.database.connection import SessionLocal


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()