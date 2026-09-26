from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.auth import auth_routes
from app.middlewares.rate_limiter import limiter
from app.middlewares.request_middleware import RequestLoggingMiddleware
from app.routes import device_routes, loan_routes, user_loan_routes, user_routes

app = FastAPI(
    title="device_systems API",
    description="API REST segura para la gestion de usuarios, dispositivos y prestamos del sistema device_systems, con autenticacion OAuth2/JWT, CORS, middleware de trazabilidad y rate limiting.",
    version="5.0.0",
    contact={"name": "Juan Camilo Sarrazola", "email": "camilo@correo.com"},
    openapi_tags=[
        {"name": "Auth", "description": "Registro, login y consulta del usuario autenticado"},
        {"name": "Users", "description": "Operaciones sobre usuarios y su historial de prestamos"},
        {"name": "Devices", "description": "Operaciones CRUD sobre dispositivos y su historial de prestamos"},
        {"name": "Loans", "description": "Gestion de prestamos de dispositivos"},
    ],
)

# Rate limiting: limita peticiones abusivas por IP (ver limites en cada ruta)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# CORS: origenes autorizados para consumir la API desde un frontend en desarrollo.
# En produccion NO se debe usar "*" cuando allow_credentials=True, porque el
# navegador exige que el servidor confirme explicitamente cada origen autorizado
# al enviar credenciales (cookies/tokens); "*" impide identificar quien realmente
# esta autorizado y abre la puerta a que cualquier sitio consuma la API en nombre
# del usuario autenticado.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware personalizado: X-Process-Time, X-App-Name, X-Request-ID y logging
app.add_middleware(RequestLoggingMiddleware)


app.include_router(auth_routes.router)
app.include_router(user_routes.router)
app.include_router(user_loan_routes.router)
app.include_router(device_routes.router)
app.include_router(loan_routes.router)


@app.get("/", tags=["Raiz"])
def raiz():
    return {"mensaje": "Bienvenido a device_systems API v5.0. Visita /docs para ver la documentacion."}