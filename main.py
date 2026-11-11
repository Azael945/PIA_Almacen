from fastapi import FastAPI
from modulos.autenticacion.rutas import router as autenticacion_router
from modulos.almacen.rutas import router as almacen_router
from modulos.usuarios.rutas import router as usuarios_router
from modulos.configuracion.rutas import router_proveedores, router_clientes, router_categorias

app = FastAPI(
    title="API Almacen",
    description="Sistema de gestión de almacén",
    version="1.0.0"
)

app.include_router(autenticacion_router)
app.include_router(almacen_router)
#usuarios
app.include_router(usuarios_router)
#configuracion
app.include_router(router_proveedores)
app.include_router(router_clientes)
app.include_router(router_categorias)