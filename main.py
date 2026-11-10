from fastapi import FastAPI
from modulos.autenticacion.rutas import router as autenticacion_router
from modulos.almacen.rutas import router as almacen_router

app = FastAPI(
    title="API Almacen",
    description="Sistema de gestión de almacén",
    version="1.0.0"
)

app.include_router(autenticacion_router)
app.include_router(almacen_router)
app.include_router(usuarios_router)
