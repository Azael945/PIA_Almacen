from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class AlmacenDespliegueResponse(BaseModel):
    codigo: str
    producto: str
    fecha_alta: Optional[datetime] = None
    descripcion: Optional[str] = None
    categoria: Optional[str] = None
    stock_actual: int
    estado_stock: str  # "En stock si > 5", "Stock bajo si <= 5" o "Fuera de stock si = 0"

    class Config:
        from_attributes = True