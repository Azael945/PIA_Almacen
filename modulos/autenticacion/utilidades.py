import os
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from dotenv import load_dotenv

# Lee las variables del archivo .env (que NO se sube a GitHub)
load_dotenv()

LLAVE_SECRETA = os.getenv("JWT_SECRET_KEY")
if not LLAVE_SECRETA:
    raise RuntimeError(
        "Falta la variable JWT_SECRET_KEY. Agrégala al archivo .env "
        "(genera una con: python -c \"import secrets; print(secrets.token_hex(32))\")."
    )

ALGORITMO = os.getenv("JWT_ALGORITMO", "HS256")
MINUTOS_EXPIRACION = int(os.getenv("JWT_MINUTOS_EXPIRACION", "60"))

def verificar_contrasena(plain_password: str, password_db: str) -> bool:
    # Compara la contraseña plana enviada con el hash Bcrypt de MySQL.
    try:
        plain_bytes = plain_password.encode('utf-8')
        hashed_bytes = password_db.encode('utf-8')
        return bcrypt.checkpw(plain_bytes, hashed_bytes)
    except Exception:
        return False

def crear_token_acceso(datos: dict) -> str:
    datos_a_codificar = datos.copy()
    expiracion = datetime.now(timezone.utc) + timedelta(minutes=MINUTOS_EXPIRACION)
    datos_a_codificar.update({"exp": expiracion})
    return jwt.encode(datos_a_codificar, LLAVE_SECRETA, algorithm=ALGORITMO)

def encriptar_contrasena(plain_password: str) -> str:
    # Genera el hash Bcrypt que se guarda en la base de datos.
    return bcrypt.hashpw(plain_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
