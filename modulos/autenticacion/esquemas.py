from pydantic import BaseModel, EmailStr, Field

class SolicitudLogin(BaseModel):
    correo: EmailStr = Field(..., example="angel@almacen.com")
    contrasena: str = Field(..., example="Password123!")

class RespuestaToken(BaseModel):
    access_token: str
    token_type: str = "bearer"
    mensaje: str