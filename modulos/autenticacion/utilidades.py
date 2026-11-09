from datetime import datetime, timedelta, timezone
import bcrypt
import jwt

LLAVE_SECRETA = "mi_clave_secreta_almacen_2026"
ALGORITMO = "HS256"
MINUTOS_EXPIRACION = 60

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