from fastapi import FastAPI
from modulos.autenticacion.rutas import router as autenticacion_router

app = FastAPI(
    title="API Almacen",
    description="Sistema de gestión de almacén",
    version="1.0.0"
)

app.include_router(autenticacion_router)
