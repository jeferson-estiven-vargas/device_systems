# app/middlewares/rate_limiter.py
from slowapi import Limiter
from slowapi.util import get_remote_address

# Limita por IP del cliente. Se importa desde main.py (para registrar el
# exception handler y el middleware) y desde las rutas que llevan limite
# (@limiter.limit("N/minute")).
limiter = Limiter(key_func=get_remote_address)