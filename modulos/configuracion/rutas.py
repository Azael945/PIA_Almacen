from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text

from database.conexion import obtener_db                     # conexión 
from modulos.almacen.rutas import verificar_acceso_almacen   # Admin o Editor o ???client?
from .esquemas import ProveedorEntrada, ProveedorRespuesta
from .esquemas import ProveedorEntrada, ProveedorRespuesta, ClienteEntrada, ClienteRespuesta

router_proveedores = APIRouter( 
    prefix="/proveedores",
    tags=["Proveedores"],
    dependencies=[Depends(verificar_acceso_almacen)]  
)

router_clientes = APIRouter(
    prefix="/clientes",
    tags=["Clientes"],
    dependencies=[Depends(verificar_acceso_almacen)]   
)


SQL_PROVEEDOR = """
    SELECT id_proveedor, nombre, celular, correo, rfc, fecha_alta, activo
    FROM proveedor
"""     
SQL_CLIENTE = """
    SELECT id_cliente, nombre, celular, correo, activo
    FROM cliente
"""


#PROVEEDORES
def buscar_proveedor(db: Session, id_proveedor: int):
    """Regresa el proveedor o corta con 404 si no existe."""
    fila = db.execute(text(SQL_PROVEEDOR + " WHERE id_proveedor = :id"),
                      {"id": id_proveedor}).mappings().first()
    if fila is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No existe un proveedor con id {id_proveedor}")
    return fila

def validar_rfc_unico(db: Session, rfc: str, id_proveedor: int = 0):
    """Regla de negocio: el RFC no se repite, ni siquiera con proveedores dados de baja.
    Al editar, se excluye al propio proveedor (id_proveedor)."""
    existe = db.execute(
        text("SELECT 1 FROM proveedor WHERE rfc = :rfc AND id_proveedor <> :id"),
        {"rfc": rfc, "id": id_proveedor}
    ).first()
    if existe:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Ya existe un proveedor con el RFC {rfc}")

# GET /proveedores/ -> solo activos
# GET /proveedores/?incluir_inactivos=true  -> todos
@router_proveedores.get("/", response_model=List[ProveedorRespuesta])
def listar_proveedores(incluir_inactivos: bool = False, db: Session = Depends(obtener_db)):
    filtro = "" if incluir_inactivos else " WHERE activo = 1"
    return db.execute(text(SQL_PROVEEDOR + filtro + " ORDER BY nombre")).mappings().all()

#GET /proveedores/{id_proveedor}
@router_proveedores.get("/{id_proveedor}", response_model=ProveedorRespuesta)
def obtener_proveedor(id_proveedor: int, db: Session = Depends(obtener_db)):
    return buscar_proveedor(db, id_proveedor)

#POST /proveedores/
@router_proveedores.post("/", response_model=ProveedorRespuesta, status_code=status.HTTP_201_CREATED)
def crear_proveedor(proveedor: ProveedorEntrada, db: Session = Depends(obtener_db)):
    validar_rfc_unico(db, proveedor.rfc)
    resultado = db.execute(text("""
        INSERT INTO proveedor (nombre, celular, correo, rfc)
        VALUES (:nombre, :celular, :correo, :rfc)
    """), proveedor.model_dump())
    db.commit()
    return buscar_proveedor(db, resultado.lastrowid)

# PUT /proveedores/{id_proveedor}   
@router_proveedores.put("/{id_proveedor}", response_model=ProveedorRespuesta)
def actualizar_proveedor(id_proveedor: int, proveedor: ProveedorEntrada, db: Session = Depends(obtener_db)):
    buscar_proveedor(db, id_proveedor)
    validar_rfc_unico(db, proveedor.rfc, id_proveedor)
    db.execute(text("""
        UPDATE proveedor
        SET nombre = :nombre, celular = :celular, correo = :correo, rfc = :rfc
        WHERE id_proveedor = :id
    """), {**proveedor.model_dump(), "id": id_proveedor})
    db.commit()
    return buscar_proveedor(db, id_proveedor)

# DELETE /proveedores/{id_proveedor}  
@router_proveedores.delete("/{id_proveedor}")
def eliminar_proveedor(id_proveedor: int, db: Session = Depends(obtener_db)):
    proveedor = buscar_proveedor(db, id_proveedor)
    if not proveedor["activo"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="El proveedor ya estaba dado de baja")
    db.execute(text("UPDATE proveedor SET activo = 0 WHERE id_proveedor = :id"), {"id": id_proveedor})
    db.commit()
    return {"mensaje": "Proveedor dado de baja correctamente"}



#CLIENTES
def buscar_cliente(db: Session, id_cliente: int):
    """Regresa el cliente o corta con 404 si no existe."""
    fila = db.execute(text(SQL_CLIENTE + " WHERE id_cliente = :id"),
                      {"id": id_cliente}).mappings().first()
    if fila is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No existe un cliente con id {id_cliente}")
    return fila

# GET /clientes/   (?incluir_inactivos=true)
@router_clientes.get("/", response_model=List[ClienteRespuesta])
def listar_clientes(incluir_inactivos: bool = False, db: Session = Depends(obtener_db)):
    filtro = "" if incluir_inactivos else " WHERE activo = 1"
    return db.execute(text(SQL_CLIENTE + filtro + " ORDER BY nombre")).mappings().all()

# GET /clientes/{id_cliente}
@router_clientes.get("/{id_cliente}", response_model=ClienteRespuesta)
def obtener_cliente(id_cliente: int, db: Session = Depends(obtener_db)):
    return buscar_cliente(db, id_cliente)

# POST /clientes/
@router_clientes.post("/", response_model=ClienteRespuesta, status_code=status.HTTP_201_CREATED)
def crear_cliente(cliente: ClienteEntrada, db: Session = Depends(obtener_db)):
    # El id y activo los pone MySQL
    resultado = db.execute(text("""
        INSERT INTO cliente (nombre, celular, correo)
        VALUES (:nombre, :celular, :correo)
    """), cliente.model_dump())
    db.commit()
    return buscar_cliente(db, resultado.lastrowid)

# PUT /clientes/{id_cliente}  
@router_clientes.put("/{id_cliente}", response_model=ClienteRespuesta)
def actualizar_cliente(id_cliente: int, cliente: ClienteEntrada, db: Session = Depends(obtener_db)):
    buscar_cliente(db, id_cliente)
    db.execute(text("""
        UPDATE cliente
        SET nombre = :nombre, celular = :celular, correo = :correo
        WHERE id_cliente = :id
    """), {**cliente.model_dump(), "id": id_cliente})
    db.commit()
    return buscar_cliente(db, id_cliente)

# DELETE /clientes/{id_cliente} 
@router_clientes.delete("/{id_cliente}")
def eliminar_cliente(id_cliente: int, db: Session = Depends(obtener_db)):
    cliente = buscar_cliente(db, id_cliente)
    if not cliente["activo"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="El cliente ya estaba dado de baja")
    db.execute(text("UPDATE cliente SET activo = 0 WHERE id_cliente = :id"), {"id": id_cliente})
    db.commit()
    return {"mensaje": "Cliente dado de baja correctamente"}