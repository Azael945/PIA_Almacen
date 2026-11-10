from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator

class ProveedorEntrada(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100, examples=["Distribuidora Norte"])
    celular: str = Field(..., pattern=r"^\d{10}$", examples=["8120000000"])
    correo: EmailStr = Field(..., examples=["ventas@norte.mx"])
    rfc: str = Field(..., pattern=r"^[A-ZÑ&]{3,4}\d{6}[A-Z0-9]{3}$", examples=["DNO010101AAA"])

    @field_validator("nombre", "rfc", mode="before")
    @classmethod
    def limpiar_texto(cls, valor, info):
        if isinstance(valor, str):
            valor = valor.strip()
            if info.field_name == "rfc":
                valor = valor.upper()
        return valor


class ProveedorRespuesta(BaseModel):
    id_proveedor: int
    nombre: str
    celular: str
    correo: str
    rfc: str
    fecha_alta: datetime
    activo: bool



class ClienteEntrada(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100, examples=["Abarrotes Don Chuy"])
    celular: Optional[str] = Field(None, pattern=r"^\d{10}$", examples=["8125550001"])
    correo: Optional[EmailStr] = Field(None, examples=["donchuy@correo.mx"])

    @field_validator("nombre", mode="before")
    @classmethod
    def limpiar_nombre(cls, valor):
        return valor.strip() if isinstance(valor, str) else valor


class ClienteRespuesta(BaseModel):
    """Lo que la API DEVUELVE: todas las columnas de la tabla cliente."""
    id_cliente: int
    nombre: str
    celular: Optional[str] = None
    correo: Optional[str] = None
    activo: bool