# API Almacén (PIA)

API REST para la gestión de un almacén: productos, proveedores, clientes, usuarios y movimientos de inventario (entradas y salidas con actualización automática de stock).

**Tecnologías:** Python, FastAPI, Pydantic, SQLAlchemy, MySQL, JWT y bcrypt. Dependencias administradas con Poetry.

## Estructura

| Carpeta | Contenido |
|---|---|
| `main.py` | Punto de entrada; registra todos los routers |
| `database/` | Conexión a MySQL (`conexion.py`) y script de tablas (`almacen.sql`) |
| `modulos/autenticacion/` | Login y generación de tokens JWT |
| `modulos/usuarios/` | CRUD de usuarios (solo Admin) |
| `modulos/configuracion/` | CRUD de proveedores, clientes y categorías |
| `modulos/almacen/` | Despliegue de productos con estado de stock |
| `modulos/movimientos/` | Entradas y salidas de mercancía; actualiza el stock |

## Requisitos
- Python 3.10 o superior
- MySQL Server 8 o superior
- Poetry (`python -m pip install poetry`)

## Instalación

**1. Base de datos.** En MySQL Workbench:
```sql
CREATE DATABASE almacen;
```
Después ejecuta el script `database/almacen.sql` e inserta los roles:
```sql
use almacen;
INSERT INTO rol (nombre, descripcion) VALUES
('Admin', 'Administrador'), ('Editor', 'Editor'), ('Usuario', 'Usuario');
```

**2. Variables de entorno.** Copia `.env.example` a un archivo nuevo llamado `.env` (en la raíz) y llena tus datos:
```
DB_USER=root
DB_PASSWORD=tu_contraseña_de_mysql
DB_HOST=localhost
DB_PORT=3306
DB_NAME=almacen
JWT_SECRET_KEY=una_llave_larga_y_aleatoria
```
Genera la llave JWT con:
```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```
El archivo `.env` **no se sube a GitHub**; cada integrante crea el suyo.

**3. Dependencias.** En la carpeta del proyecto:
```powershell
python -m poetry config virtualenvs.in-project true
python -m poetry install
```

**4. Usuario Admin.** Genera el hash de tu contraseña:
```powershell
python -m poetry run python -c "import bcrypt; print(bcrypt.hashpw(b'TuContrasena', bcrypt.gensalt()).decode())"
```
E insértalo en MySQL, pegando el hash:
```sql
INSERT INTO usuario (nombre, celular, correo, contrasena, id_rol)
VALUES ('Admin', '8112345678', 'admin@almacen.com', 'PEGA_AQUI_EL_HASH',
        (SELECT id_rol FROM rol WHERE nombre = 'Admin'));
```

## Ejecución
```powershell
python -m poetry run uvicorn main:app --reload
```
Abre `http://127.0.0.1:8000/docs`, inicia sesión en `POST /auth/login`, copia el token y pégalo en el botón **Authorize**.

## Notas del equipo
- Se usa `bcrypt` para las contraseñas porque `argon2-cffi` no era compatible con la versión de Python utilizada.
- Los borrados de proveedores, clientes y usuarios son lógicos (se marcan como inactivos).
