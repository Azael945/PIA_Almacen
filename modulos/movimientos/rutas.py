from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from database.conexion import obtener_db
from modulos.almacen.rutas import verificar_acceso_almacen  # Admin o Editor
from .esquemas import MovimientoCrear, MovimientoRespuesta, MovimientoRegistrado

router = APIRouter(
    prefix="/movimientos",
    tags=["Movimientos"],
    dependencies=[Depends(verificar_acceso_almacen)]  # Exige login y rol Admin/Editor
)

SQL_MOVIMIENTO = """
    SELECT m.id_movimiento, m.tipo, m.fecha, m.cantidad, m.descripcion,
           p.codigo AS codigo_producto, p.nombre AS producto,
           pr.nombre AS proveedor, c.nombre AS cliente, u.nombre AS usuario
    FROM movimiento m
    INNER JOIN producto p ON m.id_producto = p.id_producto
    INNER JOIN usuario u ON m.id_usuario = u.id_usuario
    LEFT JOIN proveedor pr ON m.id_proveedor = pr.id_proveedor
    LEFT JOIN cliente c ON m.id_cliente = c.id_cliente
"""


def buscar_movimiento(db: Session, id_movimiento: int):
    """Regresa el movimiento o corta con 404 si no existe."""
    fila = db.execute(text(SQL_MOVIMIENTO + " WHERE m.id_movimiento = :id"),
                      {"id": id_movimiento}).mappings().first()
    if fila is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No existe un movimiento con id {id_movimiento}")
    return fila


def validar_producto(db: Session, id_producto: int):
    """Bloquea la fila de stock (FOR UPDATE) para que dos movimientos simultáneos
    no lean el mismo stock, y valida que el producto exista y esté activo."""
    fila = db.execute(text("""
        SELECT p.codigo, p.nombre, p.activo, a.stock_actual
        FROM producto p
        INNER JOIN almacen a ON a.id_producto = p.id_producto
        WHERE p.id_producto = :id
        FOR UPDATE
    """), {"id": id_producto}).mappings().first()
    if fila is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No existe el producto {id_producto} en el almacén")
    if not fila["activo"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"El producto '{fila['nombre']}' está inactivo")
    return fila


def validar_activo(db: Session, tabla: str, columna_id: str, valor: int, etiqueta: str):
    """Valida que el proveedor o cliente exista y esté activo.
    (tabla y columna_id son fijos del código, nunca vienen del usuario)"""
    fila = db.execute(text(f"SELECT nombre, activo FROM {tabla} WHERE {columna_id} = :id"),
                      {"id": valor}).mappings().first()
    if fila is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No existe un {etiqueta} con id {valor}")
    if not fila["activo"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"El {etiqueta} '{fila['nombre']}' está dado de baja")


# POST /movimientos/  -> PROCESO CENTRAL: registra el movimiento y actualiza el stock
@router.post("/", response_model=MovimientoRegistrado, status_code=status.HTTP_201_CREATED)
def registrar_movimiento(
    datos: MovimientoCrear,
    db: Session = Depends(obtener_db),
    token: dict = Depends(verificar_acceso_almacen)   # de aquí sale el usuario que opera
):
    id_usuario = int(token["sub"])

    try:
        # 1. Validar producto (y bloquear su stock hasta el commit)
        producto = validar_producto(db, datos.id_producto)
        stock_anterior = producto["stock_actual"]

        # 2. Validar quién surte (entrada) o quién recibe (salida)
        if datos.tipo == "Entrada":
            validar_activo(db, "proveedor", "id_proveedor", datos.id_proveedor, "proveedor")
        else:
            validar_activo(db, "cliente", "id_cliente", datos.id_cliente, "cliente")

        # 3. Regla de negocio: no se puede sacar más de lo que hay
        if datos.tipo == "Salida" and datos.cantidad > stock_anterior:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(f"Stock insuficiente para '{producto['nombre']}': "
                        f"hay {stock_anterior} y se solicitan {datos.cantidad}")
            )

        # 4. Calcular el nuevo stock
        if datos.tipo == "Entrada":
            stock_nuevo = stock_anterior + datos.cantidad
        else:
            stock_nuevo = stock_anterior - datos.cantidad

        # 5. Actualizar stock + registrar movimiento (misma transacción)
        db.execute(text("UPDATE almacen SET stock_actual = :stock WHERE id_producto = :id"),
                   {"stock": stock_nuevo, "id": datos.id_producto})
        resultado = db.execute(text("""
            INSERT INTO movimiento (tipo, cantidad, descripcion, id_producto,
                                    id_usuario, id_proveedor, id_cliente)
            VALUES (:tipo, :cantidad, :descripcion, :id_producto,
                    :id_usuario, :id_proveedor, :id_cliente)
        """), {"tipo": datos.tipo, "cantidad": datos.cantidad, "descripcion": datos.descripcion,
               "id_producto": datos.id_producto, "id_usuario": id_usuario,
               "id_proveedor": datos.id_proveedor, "id_cliente": datos.id_cliente})
        db.commit()

    except HTTPException:
        db.rollback()   # una validación falló: no se guarda nada
        raise
    except Exception:
        db.rollback()   # error inesperado: se deshace todo para no dejar el stock a medias
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="No se pudo registrar el movimiento")

    registrado = dict(buscar_movimiento(db, resultado.lastrowid))
    registrado["stock_anterior"] = stock_anterior
    registrado["stock_actual"] = stock_nuevo
    return registrado


# GET /movimientos/   (filtros opcionales: ?tipo=Entrada  ?id_producto=1)
@router.get("/", response_model=List[MovimientoRespuesta])
def listar_movimientos(
    tipo: Optional[str] = Query(None, pattern="^(Entrada|Salida)$"),
    id_producto: Optional[int] = Query(None, gt=0),
    db: Session = Depends(obtener_db)
):
    sql = SQL_MOVIMIENTO + " WHERE 1 = 1"
    parametros = {}
    if tipo:
        sql += " AND m.tipo = :tipo"
        parametros["tipo"] = tipo
    if id_producto:
        sql += " AND m.id_producto = :id_producto"
        parametros["id_producto"] = id_producto
    sql += " ORDER BY m.fecha DESC, m.id_movimiento DESC"
    return db.execute(text(sql), parametros).mappings().all()


# GET /movimientos/{id_movimiento}
@router.get("/{id_movimiento}", response_model=MovimientoRespuesta)
def obtener_movimiento(id_movimiento: int, db: Session = Depends(obtener_db)):
    return buscar_movimiento(db, id_movimiento)
