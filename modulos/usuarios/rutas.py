from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List
import jwt

from database.conexion import obtener_db
from modulos.autenticacion.utilidades import LLAVE_SECRETA, ALGORITMO, encriptar_contrasena
from .esquemas import UsuarioCrear, UsuarioActualizar, UsuarioResponse

router = APIRouter(
    prefix="/usuarios",
    tags=["Usuarios"]
)

esquema_seguridad = HTTPBearer()

def verificar_acceso_usuarios(
    credenciales: HTTPAuthorizationCredentials = Depends(esquema_seguridad),
    db: Session = Depends(obtener_db)
):
    error_401 = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido o expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(credenciales.credentials, LLAVE_SECRETA, algorithms=[ALGORITMO])
        id_usuario = payload.get("sub")
        if not id_usuario:
            raise error_401

        resultado = db.execute(text("""
            SELECT r.nombre
            FROM usuario u
            INNER JOIN rol r ON u.id_rol = r.id_rol
            WHERE u.id_usuario = :id_usuario AND u.activo = 1
        """), {"id_usuario": id_usuario}).fetchone()

        if not resultado:
            raise error_401

        # Solo el Admin puede gestionar usuarios
        if resultado.nombre != "Admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acceso denegado. Se requiere rol de Admin"
            )
        return payload
    except jwt.PyJWTError:
        raise error_401


SQL_USUARIO = """
    SELECT u.id_usuario, u.nombre, u.celular, u.correo, u.fecha_alta,
           u.activo, u.id_rol, r.nombre AS rol
    FROM usuario u
    LEFT JOIN rol r ON u.id_rol = r.id_rol
"""

def buscar_usuario(db: Session, id_usuario: int):
    fila = db.execute(text(SQL_USUARIO + " WHERE u.id_usuario = :id"), {"id": id_usuario}).mappings().first()
    if not fila:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return fila

def validar_correo_y_rol(db: Session, correo: str, id_rol: int, id_usuario: int = 0):
    existe = db.execute(
        text("SELECT 1 FROM usuario WHERE correo = :correo AND id_usuario <> :id"),
        {"correo": correo, "id": id_usuario}
    ).first()
    if existe:
        raise HTTPException(status_code=400, detail="El correo ya está registrado")
    rol = db.execute(text("SELECT 1 FROM rol WHERE id_rol = :id"), {"id": id_rol}).first()
    if not rol:
        raise HTTPException(status_code=400, detail="El rol no existe")


@router.get("/", response_model=List[UsuarioResponse], dependencies=[Depends(verificar_acceso_usuarios)])
def listar_usuarios(db: Session = Depends(obtener_db)):
    return db.execute(text(SQL_USUARIO)).mappings().all()


@router.get("/{id_usuario}", response_model=UsuarioResponse, dependencies=[Depends(verificar_acceso_usuarios)])
def obtener_usuario(id_usuario: int, db: Session = Depends(obtener_db)):
    return buscar_usuario(db, id_usuario)


@router.post("/", response_model=UsuarioResponse, status_code=201, dependencies=[Depends(verificar_acceso_usuarios)])
def crear_usuario(usuario: UsuarioCrear, db: Session = Depends(obtener_db)):
    validar_correo_y_rol(db, usuario.correo, usuario.id_rol)
    # El ID lo genera la base de datos; la contraseña se guarda encriptada
    resultado = db.execute(
        text("""
            INSERT INTO usuario (nombre, celular, correo, contrasena, id_rol)
            VALUES (:nombre, :celular, :correo, :contrasena, :id_rol)
        """),
        {"nombre": usuario.nombre, "celular": usuario.celular, "correo": usuario.correo,
         "contrasena": encriptar_contrasena(usuario.contrasena), "id_rol": usuario.id_rol}
    )
    db.commit()
    return buscar_usuario(db, resultado.lastrowid)


@router.put("/{id_usuario}", response_model=UsuarioResponse, dependencies=[Depends(verificar_acceso_usuarios)])
def actualizar_usuario(id_usuario: int, usuario: UsuarioActualizar, db: Session = Depends(obtener_db)):
    buscar_usuario(db, id_usuario)
    validar_correo_y_rol(db, usuario.correo, usuario.id_rol, id_usuario)
    datos = {"nombre": usuario.nombre, "celular": usuario.celular, "correo": usuario.correo,
             "id_rol": usuario.id_rol, "activo": usuario.activo, "id": id_usuario}
    sql = "UPDATE usuario SET nombre=:nombre, celular=:celular, correo=:correo, id_rol=:id_rol, activo=:activo"
    if usuario.contrasena:
        sql += ", contrasena=:contrasena"
        datos["contrasena"] = encriptar_contrasena(usuario.contrasena)
    db.execute(text(sql + " WHERE id_usuario=:id"), datos)
    db.commit()
    return buscar_usuario(db, id_usuario)


@router.delete("/{id_usuario}", dependencies=[Depends(verificar_acceso_usuarios)])
def eliminar_usuario(id_usuario: int, db: Session = Depends(obtener_db)):
    # No se borra de la BD, solo se marca como inactivo
    buscar_usuario(db, id_usuario)
    db.execute(text("UPDATE usuario SET activo = 0 WHERE id_usuario = :id"), {"id": id_usuario})
    db.commit()
    return {"mensaje": "Usuario desactivado correctamente"}
