# app/middlewares/request_middleware.py
import logging
import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

logger = logging.getLogger("device_systems")
logging.basicConfig(level=logging.INFO)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware global de trazabilidad.

    - Mide el tiempo de respuesta de cada peticion.
    - Agrega las cabeceras X-Process-Time, X-App-Name y X-Request-ID.
    - Propaga el X-Request-ID recibido del cliente, o genera uno nuevo si no viene.
    - Registra metodo, ruta y codigo de estado de cada peticion en el log.
    """

    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4())[:8])
        start_time = time.perf_counter()

        response = await call_next(request)

        process_time = time.perf_counter() - start_time
        response.headers["X-Process-Time"] = f"{process_time:.4f}"
        response.headers["X-App-Name"] = "device_systems"
        response.headers["X-Request-ID"] = request_id

        logger.info(
            "%s %s -> %s (%.4fs) [%s]",
            request.method,
            request.url.path,
            response.status_code,
            process_time,
            request_id,
        )

        return response
