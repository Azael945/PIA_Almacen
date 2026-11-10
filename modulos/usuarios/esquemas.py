from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class UsuarioCrear(BaseModel):
    nombre: str
    celular: str
    correo: EmailStr
    contrasena: str
    id_rol: int

class UsuarioActualizar(BaseModel):
    nombre: str
    celular: str
    correo: EmailStr
    id_rol: int
    activo: bool = True
    contrasena: Optional[str] = None  # Solo si se quiere cambiar

class UsuarioResponse(BaseModel):
    id_usuario: int
    nombre: str
    celular: str
    correo: str
    fecha_alta: Optional[datetime] = None
    activo: bool
    id_rol: Optional[int] = None
    rol: Optional[str] = None
