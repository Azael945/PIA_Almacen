from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text

from database.conexion import obtener_db
from .esquemas import SolicitudLogin, RespuestaToken
from .utilidades import verificar_contrasena, crear_token_acceso

router = APIRouter(
    prefix="/auth",
    tags=["Autenticación"]
)

@router.post("/login", response_model=RespuestaToken)
def login(credenciales: SolicitudLogin, db: Session = Depends(obtener_db)):
    # Buscar usuario por correo
    sql_query = text("SELECT id_usuario, correo, contrasena, id_rol, activo FROM usuario WHERE correo = :correo")
    resultado = db.execute(sql_query, {"correo": credenciales.correo}).fetchone()

    # Si no existe o no está activo
    if not resultado or not resultado.activo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas o usuario inactivo"
        )

    # Comparar directamente texto contra texto
    contrasena_valida = verificar_contrasena(credenciales.contrasena, resultado.contrasena)

    if not contrasena_valida:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas"
        )

    # Generar JWT si coinciden
    token_jwt = crear_token_acceso(datos={
        "sub": str(resultado.id_usuario),
        "correo": resultado.correo,
        "rol": resultado.id_rol
    })

    return {
        "access_token": token_jwt,
        "token_type": "bearer",
        "mensaje": "Conexión a MySQL exitosa e Inicio de sesión correcto"
    }