from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text

from database.conexion import obtener_db                     # conexión 
from modulos.almacen.rutas import verificar_acceso_almacen
from modulos.usuarios.rutas import verificar_acceso_usuarios   
from .esquemas import ProveedorEntrada, ProveedorRespuesta, ClienteEntrada, ClienteRespuesta, CategoriaEntrada, CategoriaRespuesta, MoverProductos


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

router_categorias = APIRouter(
    prefix="/categorias",
    tags=["Categorías"],
    dependencies=[Depends(verificar_acceso_almacen)]   # Admin o Editor para todo el router
)


SQL_PROVEEDOR = """
    SELECT id_proveedor, nombre, celular, correo, rfc, fecha_alta, activo
    FROM proveedor
"""     
SQL_CLIENTE = """
    SELECT id_cliente, nombre, celular, correo, activo
    FROM cliente
"""
SQL_CATEGORIA = """
    SELECT c.id_categoria, c.nombre, c.descripcion,
           COUNT(p.id_producto) AS total_productos
    FROM categoria c
    LEFT JOIN producto p ON p.id_categoria = c.id_categoria
"""
SQL_AGRUPAR = " GROUP BY c.id_categoria, c.nombre, c.descripcion"


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

def buscar_categoria(db: Session, id_categoria: int, que: str = "la categoría"):
    """Regresa la categoría con su conteo de productos o corta con 404."""
    fila = db.execute(text(SQL_CATEGORIA + " WHERE c.id_categoria = :id" + SQL_AGRUPAR),
                      {"id": id_categoria}).mappings().first()
    if fila is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No existe {que} con id {id_categoria}")
    return fila

def validar_nombre_unico(db: Session, nombre: str, id_categoria: int = 0):
    """Regla de negocio: no hay dos categorías con el mismo nombre.
    MySQL compara sin distinguir mayúsculas ni acentos: 'bebidas' = 'Bebidas'."""
    existe = db.execute(
        text("SELECT nombre FROM categoria WHERE nombre = :nombre AND id_categoria <> :id"),
        {"nombre": nombre, "id": id_categoria}
    ).first()
    if existe:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Ya existe la categoría '{existe.nombre}'")



# GET /categorias/
@router_categorias.get("/", response_model=List[CategoriaRespuesta])
def listar_categorias(db: Session = Depends(obtener_db)):
    return db.execute(text(SQL_CATEGORIA + SQL_AGRUPAR + " ORDER BY c.nombre")).mappings().all()


# GET /categorias/{id_categoria}
@router_categorias.get("/{id_categoria}", response_model=CategoriaRespuesta)
def obtener_categoria(id_categoria: int, db: Session = Depends(obtener_db)):
    return buscar_categoria(db, id_categoria)


# POST /categorias/
@router_categorias.post("/", response_model=CategoriaRespuesta, status_code=status.HTTP_201_CREATED)
def crear_categoria(categoria: CategoriaEntrada, db: Session = Depends(obtener_db)):
    validar_nombre_unico(db, categoria.nombre)
    resultado = db.execute(text("""
        INSERT INTO categoria (nombre, descripcion)
        VALUES (:nombre, :descripcion)
    """), categoria.model_dump())
    db.commit()
    return buscar_categoria(db, resultado.lastrowid)


# PUT /categorias/{id_categoria}
@router_categorias.put("/{id_categoria}", response_model=CategoriaRespuesta)
def actualizar_categoria(id_categoria: int, categoria: CategoriaEntrada, db: Session = Depends(obtener_db)):
    buscar_categoria(db, id_categoria)
    validar_nombre_unico(db, categoria.nombre, id_categoria)
    db.execute(text("""
        UPDATE categoria
        SET nombre = :nombre, descripcion = :descripcion
        WHERE id_categoria = :id
    """), {**categoria.model_dump(), "id": id_categoria})
    db.commit()
    return buscar_categoria(db, id_categoria)


# Mover todos los productos es el paso previo para poder borrar una categoría que tiene productos.
@router_categorias.post("/{id_categoria}/mover-productos")
def mover_productos(id_categoria: int, destino: MoverProductos, db: Session = Depends(obtener_db)):
    if destino.id_categoria_destino == id_categoria:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="La categoría destino debe ser distinta a la de origen")
    origen = buscar_categoria(db, id_categoria)
    nueva = buscar_categoria(db, destino.id_categoria_destino, "la categoría destino")
    resultado = db.execute(
        text("UPDATE producto SET id_categoria = :destino WHERE id_categoria = :origen"),
        {"destino": destino.id_categoria_destino, "origen": id_categoria}
    )
    db.commit()
    return {"mensaje": f"Se movieron {resultado.rowcount} producto(s) de '{origen['nombre']}' a '{nueva['nombre']}'",
            "productos_movidos": resultado.rowcount}


# DELETE /categorias/{id_categoria}   (borrado real: solo Admin y solo si está vacía)
@router_categorias.delete("/{id_categoria}", dependencies=[Depends(verificar_acceso_usuarios)])
def eliminar_categoria(id_categoria: int, db: Session = Depends(obtener_db)):
    categoria = buscar_categoria(db, id_categoria)
    if categoria["total_productos"] > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(f"No se puede eliminar '{categoria['nombre']}': la usan "
                    f"{categoria['total_productos']} producto(s). Muévelos primero a otra categoría "
                    f"con POST /categorias/{id_categoria}/mover-productos")
        )
    db.execute(text("DELETE FROM categoria WHERE id_categoria = :id"), {"id": id_categoria})
    db.commit()
    return {"mensaje": f"Categoría '{categoria['nombre']}' eliminada"}