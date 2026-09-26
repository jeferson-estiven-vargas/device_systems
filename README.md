# device_systems

API REST desarrollada con **FastAPI** para la gestión de usuarios, dispositivos y préstamos del sistema `device_systems`. Esta es la evolución final del proyecto (EV11): una API **protegida y lista para producción**, con autenticación OAuth2 + JWT, hash de contraseñas, autorización por roles, middleware personalizado, CORS y rate limiting.

## Descripción de la API

`device_systems` expone los recursos:

- `/auth` — registro, login y perfil del usuario autenticado.
- `/users` — gestión de usuarios.
- `/devices` — gestión de dispositivos (protegido por rol).
- `/loans` — gestión de préstamos.

Funcionalidades principales:

- Registro de usuarios con contraseña segura (hash con `bcrypt` vía `passlib`).
- Autenticación OAuth2 con tokens JWT (`python-jose`).
- Protección de rutas mediante dependencias (`get_current_active_user`, `require_roles`, `require_admin`).
- Autorización basada en roles (`admin`, `support`, `user`).
- Middleware personalizado de trazabilidad (tiempo de respuesta, `X-Request-ID`, logging).
- CORS configurado para clientes frontend autorizados.
- Rate limiting con `slowapi` en endpoints sensibles.
- Validaciones avanzadas con Pydantic v2.

## Tecnologías utilizadas

| Tecnología | Uso |
|---|---|
| Python | Lenguaje base |
| FastAPI | Framework principal de la API |
| Pydantic v2 | Validación y serialización de datos |
| SQLAlchemy | ORM y persistencia |
| Alembic | Migraciones de base de datos |
| Uvicorn | Servidor ASGI |
| passlib[bcrypt] (bcrypt==4.0.1) | Hash seguro de contraseñas |
| python-jose[cryptography] | Generación y validación de tokens JWT |
| python-dotenv | Carga de variables de entorno desde `.env` |
| python-multipart | Procesamiento de formularios (login OAuth2) |
| slowapi | Rate limiting |
| Swagger UI / ReDoc | Documentación automática |

## Estructura del proyecto

```
device_systems/
├── app/
│   ├── main.py                          # Punto de entrada: FastAPI, CORS, middleware, rate limiter, routers
│   ├── auth/
│   │   ├── auth_routes.py               # Endpoints /auth (register, login, me)
│   │   ├── auth_service.py              # Lógica de registro y autenticación
│   │   └── security.py                  # Hash de contraseñas y JWT (crear/validar)
│   ├── database/
│   │   └── connection.py                # Engine, SessionLocal, Base declarativa
│   ├── models/
│   │   ├── user_model.py                # User (con hashed_password, role, is_active)
│   │   ├── device_model.py              # Device
│   │   └── loan_model.py                # Loan
│   ├── schemas/
│   │   ├── user_schema.py               # Schemas de User
│   │   ├── device_schema.py             # Schemas de Device
│   │   ├── loan_schema.py               # Schemas de Loan
│   │   └── auth_schema.py               # UserRegister, UserLogin, Token, TokenData
│   ├── routes/
│   │   ├── user_routes.py               # Endpoints /users
│   │   ├── device_routes.py             # Endpoints /devices (protegidos por rol)
│   │   ├── loan_routes.py               # Endpoints /loans
│   │   └── user_loan_routes.py          # Endpoints de préstamos por usuario
│   ├── services/
│   │   ├── user_service.py
│   │   ├── device_service.py
│   │   └── loan_service.py
│   ├── dependencies/
│   │   ├── database_dependency.py       # get_db
│   │   ├── user_dependencies.py
│   │   ├── device_dependencies.py
│   │   ├── loan_dependencies.py
│   │   └── auth_dependency.py           # get_current_user, get_current_active_user, require_roles, require_admin
│   └── middlewares/
│       ├── request_middleware.py        # Trazabilidad: X-Process-Time, X-Request-ID, logging
│       └── rate_limiter.py              # Instancia compartida de Limiter (slowapi)
├── alembic/
│   └── versions/
├── .env                                 # Variables de entorno (no versionado)
├── .env.example                         # Plantilla de variables de entorno
├── alembic.ini
├── requirements.txt
└── README.md
```

## Variables de entorno

Copia `.env.example` a `.env` y define:

```
SECRET_KEY=genera-una-clave-con-python -c "import secrets; print(secrets.token_hex(32))"
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Se cargan con `python-dotenv` al iniciar la aplicación.

## Instalación y ejecución

```bash
git clone <url-del-repositorio>
cd device_systems
git checkout device_systems_security

# Crea y activa el entorno virtual, luego:
pip install -r requirements.txt

# Configura tu .env (ver sección anterior)

alembic upgrade head

uvicorn app.main:app --reload
```

El servidor queda disponible en:

- API: `http://127.0.0.1:8000`
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## Roles del sistema

| Rol | Descripción |
|---|---|
| `admin` | Acceso total: crear, actualizar y eliminar dispositivos; gestionar préstamos. |
| `support` | Puede crear y actualizar dispositivos, gestionar devoluciones de préstamos; no puede eliminar dispositivos. |
| `user` | Puede consultar usuarios/dispositivos y crear préstamos, sin permisos administrativos. |

## Tabla de endpoints y protección

| Recurso | Método | Ruta | Protección |
|---|---|---|---|
| Auth | POST | `/auth/register` | Pública (3/minuto) |
| Auth | POST | `/auth/login` | Pública (5/minuto) |
| Auth | GET | `/auth/me` | Autenticado |
| Usuarios | GET | `/users` | Autenticado (30/minuto) |
| Usuarios | GET | `/users/{user_id}` | Autenticado |
| Usuarios | GET | `/users/{user_id}/loans` | Autenticado |
| Usuarios | POST/PUT/PATCH/DELETE | `/users/{user_id}` | Sin protección adicional* |
| Dispositivos | GET | `/devices`, `/devices/{id}` | Pública |
| Dispositivos | POST | `/devices` | admin o support |
| Dispositivos | PUT | `/devices/{device_id}` | admin o support |
| Dispositivos | PATCH | `/devices/{device_id}` | Sin protección adicional* |
| Dispositivos | DELETE | `/devices/{device_id}` | admin |
| Préstamos | GET | `/loans` | Sin protección adicional* |
| Préstamos | POST | `/loans` | Autenticado (10/minuto) |
| Préstamos | PATCH | `/loans/{loan_id}/return` | admin o support |
| Préstamos | GET | `/loans/details` | admin o support |

\* Decisión documentada: la guía no exige proteger estas rutas en esta evolución; quedan pendientes para una futura iteración.

## Autenticación: registro, login y tokens

### Registro — `POST /auth/register`

```json
{
  "name": "Nombre Apellido",
  "email": "usuario@example.com",
  "password": "MiPass123",
  "role": "user"
}
```

La contraseña debe tener mínimo 8 caracteres, al menos una mayúscula, una minúscula, un número, y no contener espacios. La contraseña nunca se guarda en texto plano: se hashea con `bcrypt` antes de persistirse, y el campo `hashed_password` nunca se expone en las respuestas.

### Login — `POST /auth/login`

Recibe las credenciales como **form-data** (estándar `OAuth2PasswordRequestForm`, campo `username` = email), no como JSON — esto permite que el botón **Authorize** de Swagger funcione automáticamente.

**Respuesta:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Perfil autenticado — `GET /auth/me`

Requiere header `Authorization: Bearer <token>`. Retorna los datos del usuario dueño del token, sin `hashed_password`.

## Middleware personalizado

Cada petición pasa por `request_tracing_middleware`, que agrega:

- `X-App-Name: device_systems`
- `X-Process-Time`: tiempo de procesamiento en segundos.
- `X-Request-ID`: identificador único de la petición (reutiliza el del cliente si lo envía, o genera uno nuevo).

Además, registra en el log el método, la ruta, el código de estado y la duración de cada petición.

## Configuración de CORS

Se configuró `CORSMiddleware` permitiendo los orígenes de desarrollo local `http://localhost:5173` (Vite) y `http://localhost:3000` (React), con `allow_credentials=True`, `allow_methods=["*"]` y `allow_headers=["*"]`.

**¿Por qué no usar `allow_origins=["*"]` en producción cuando hay credenciales?**

El comodín `"*"` combinado con `allow_credentials=True` está prohibido por la especificación CORS (y Starlette lo rechaza en tiempo de ejecución). La razón es de seguridad: si el servidor aceptara credenciales desde *cualquier* origen sin distinción, un sitio malicioso podría hacer peticiones autenticadas a la API en nombre de un usuario con sesión activa, sin que el navegador lo impidiera — justo lo que CORS existe para evitar. Por eso, en producción, `allow_origins` debe listar explícitamente los dominios exactos del frontend autorizado.

## Rate limiting

Implementado con `slowapi`, identificando clientes por dirección IP:

| Endpoint | Límite |
|---|---|
| `POST /auth/register` | 3 por minuto |
| `POST /auth/login` | 5 por minuto |
| `GET /users` | 30 por minuto |
| `POST /loans` | 10 por minuto |

Al superar el límite, la API responde `429 Too Many Requests`.

## Pruebas funcionales mínimas

| # | Escenario |
|---|---|
| 1 | Registro de usuario |
| 2 | Registro con contraseña débil |
| 3 | Registro con email duplicado |
| 4 | Login correcto |
| 5 | Login con contraseña incorrecta |
| 6 | Consulta de `/auth/me` |
| 7 | Acceso a ruta protegida sin token |
| 8 | Acceso con token inválido |
| 9 | Acceso con usuario sin permisos |
| 10 | Creación de dispositivo con rol permitido |
| 11 | Eliminación de dispositivo con rol no permitido |
| 12 | Configuración CORS |
| 13 | Cabeceras generadas por middleware |
| 14 | Activación de rate limiting |
| 15 | Verificación de Swagger/OpenAPI |

## Evidencia de pruebas funcionales

> Las capturas se encuentran en `imagenes/evo11/` dentro del proyecto (ruta local: `C:\Users\El Sarra\Desktop\device_systems\imagenes\evo11`). Reemplaza los nombres de archivo por los de tus propias capturas.

### Estructura del proyecto

![Estructura del proyecto](imagenes/evo11/estructura_proyecto.png)

### Migración Alembic aplicada

![Migración Alembic aplicada](imagenes/evo11/alembic_head.png)

### Registro de usuario

![Registro exitoso](imagenes/evo11/registro_exitoso.png)

### Registro con contraseña débil

![Contraseña débil](imagenes/evo11/contrasena_debil.png)

### Registro con email duplicado

![Email duplicado](imagenes/evo11/correo_duplicado.png)

### Login correcto y token generado

![Login correcto](imagenes/evo11/login_correcto.png)

### Login con contraseña incorrecta

![Contraseña incorrecta](imagenes/evo11/contrasena_incorrecta.png)

### Consulta de /auth/me

![Respuesta sin hashed_password](imagenes/evo11/auth_me.png)

### Acceso a ruta protegida sin token

![Error 401 sin token](imagenes/evo11/sin_token.png)

### Acceso con token inválido

![Error 401 token inválido](imagenes/evo11/token_invalido.png)

### Acceso con usuario sin permisos

![Error 403](imagenes/evo11/usuario_sin_permiso.png)

### Creación de dispositivo con rol permitido

![Dispositivo creado](imagenes/evo11/dispositivo_creado.png)

### Eliminación de dispositivo con rol no permitido

![Error 403 eliminación](imagenes/evo11/usuario_sin_permiso.png)

### Configuración CORS

![Cabeceras access-control](imagenes/evo11/cabeceras_cors.png)

### Cabeceras generadas por middleware

![X-App-Name, X-Process-Time, X-Request-ID](imagenes/evo11/cabeceras_middleware.png)

### Activación de rate limiting

![429 tras exceder el límite](imagenes/evo11/rate_limiting.png)

### Swagger/OpenAPI con OAuth2

![Swagger con candado en rutas protegidas](imagenes/evo11/swagger_openapi.png)

## Reflexión final

Esta actividad transformó `device_systems` en una API lista para producción. La diferencia clave no fue solo agregar login, sino cambiar la forma de pensar cada endpoint: ya no basta con que la lógica de negocio sea correcta, también hay que preguntarse *quién puede llamar a esta ruta*.

Entender el flujo OAuth2 completo (por qué el token lleva `sub` y `exp`, por qué el login usa form-data en vez de JSON, y cómo encadenar dependencias como `require_roles` sin duplicar código) fue el mayor aprendizaje. La dificultad técnica más real fue la incompatibilidad entre `passlib` y versiones recientes de `bcrypt`, resuelta fijando `bcrypt==4.0.1` en `requirements.txt`.

Como siguiente paso, se podrían agregar refresh tokens y un mecanismo de revocación, ya que por ahora un JWT robado sigue siendo válido hasta que expira por sí solo.

## Autor

jeferson estiven vargas
