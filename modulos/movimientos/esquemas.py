from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, Field, model_validator


class MovimientoCrear(BaseModel):
    """Lo que el usuario ENVÍA para registrar un movimiento.
    El id y la fecha los genera la base de datos; el usuario sale del token."""
    tipo: Literal["Entrada", "Salida"] = Field(..., examples=["Entrada"])
    id_producto: int = Field(..., gt=0, examples=[1])
    cantidad: int = Field(..., gt=0, examples=[10])
    id_proveedor: Optional[int] = Field(None, gt=0, examples=[1])
    id_cliente: Optional[int] = Field(None, gt=0, examples=[None])
    descripcion: Optional[str] = Field(None, max_length=255, examples=["Reabasto semanal"])

    @model_validator(mode="after")
    def validar_segun_tipo(self):
        # Regla de negocio: una entrada la surte un proveedor; una salida va a un cliente.
        if self.tipo == "Entrada":
            if self.id_proveedor is None:
                raise ValueError("Una Entrada requiere id_proveedor")
            if self.id_cliente is not None:
                raise ValueError("Una Entrada no lleva id_cliente")
        else:
            if self.id_cliente is None:
                raise ValueError("Una Salida requiere id_cliente")
            if self.id_proveedor is not None:
                raise ValueError("Una Salida no lleva id_proveedor")
        return self

    @model_validator(mode="after")
    def limpiar_descripcion(self):
        if self.descripcion is not None:
            self.descripcion = self.descripcion.strip() or None
        return self


class MovimientoRespuesta(BaseModel):
    """Lo que la API DEVUELVE al consultar movimientos."""
    id_movimiento: int
    tipo: str
    fecha: datetime
    codigo_producto: str
    producto: str
    cantidad: int
    proveedor: Optional[str] = None
    cliente: Optional[str] = None
    usuario: str
    descripcion: Optional[str] = None


class MovimientoRegistrado(MovimientoRespuesta):
    """Respuesta del POST: el movimiento y cómo quedó el stock."""
    stock_anterior: int
    stock_actual: int
