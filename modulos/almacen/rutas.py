from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List
import jwt

from database.conexion import obtener_db
from modulos.autenticacion.utilidades import LLAVE_SECRETA, ALGORITMO  # Solo importamos constantes
from .esquemas import AlmacenDespliegueResponse

router = APIRouter(
    prefix="/almacen",
    tags=["Almacén"]
)

# Esquema para habilitar el botón "Authorize" en Swagger UI
esquema_seguridad = HTTPBearer()

def verificar_acceso_almacen(
    credenciales: HTTPAuthorizationCredentials = Depends(esquema_seguridad),
    db: Session = Depends(obtener_db)
):
    token = credenciales.credentials
    error_401 = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido o expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        #Decodificar el token JWT
        payload = jwt.decode(token, LLAVE_SECRETA, algorithms=[ALGORITMO])
        id_usuario = payload.get("sub")
        
        if not id_usuario:
            raise error_401

        #Consultar a MySQL el nombre del rol del usuario mediante JOIN
        query_rol = text("""
            SELECT r.nombre 
            FROM usuario u
            INNER JOIN rol r ON u.id_rol = r.id_rol
            WHERE u.id_usuario = :id_usuario AND u.activo = 1
        """)
        resultado = db.execute(query_rol, {"id_usuario": id_usuario}).fetchone()

        if not resultado:
            raise error_401

        nombre_rol = resultado.nombre  # Devuelve 'Admin', 'Editor' o 'Usuario'

        #Validar si el rol es 'Admin' o 'Editor'
        if nombre_rol not in ["Admin", "Editor"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acceso denegado. Se requiere rol de Admin o Editor"
            )

        return payload

    except jwt.PyJWTError:
        raise error_401



@router.get(
    "/despliegue", 
    response_model=List[AlmacenDespliegueResponse],
    dependencies=[Depends(verificar_acceso_almacen)]  # Exige login y rol válido
)
def obtener_despliegue_almacen(db: Session = Depends(obtener_db)):
    query_sql = text("""
        SELECT 
            p.codigo,
            p.nombre AS producto,
            p.fecha_alta,
            a.descripcion,
            c.nombre AS categoria,
            a.stock_actual
        FROM almacen a
        INNER JOIN producto p ON a.id_producto = p.id_producto
        LEFT JOIN categoria c ON p.id_categoria = c.id_categoria
    """)

    resultado = db.execute(query_sql).mappings().all()

    respuesta = []
    for fila in resultado:
        stock = fila["stock_actual"]
        
        if stock == 0:
            estado = "Fuera de stock"
        elif stock < 5:
            estado = "Stock bajo"
        else:
            estado = "En stock"

        item = {
            "codigo": fila["codigo"],
            "producto": fila["producto"],
            "fecha_alta": fila["fecha_alta"],
            "descripcion": fila["descripcion"],
            "categoria": fila["categoria"] if fila["categoria"] else "Sin Categoría",
            "stock_actual": stock,
            "estado_stock": estado
        }
        respuesta.append(item)

    return respuesta