# API Almacén (PIA)

API REST para administrar un almacén: usuarios con roles, proveedores, clientes, categorías, inventario y movimientos de mercancía (entradas y salidas que actualizan el stock automáticamente).

**Tecnologías:** Python, FastAPI, Pydantic, SQLAlchemy, MySQL 8, JWT y bcrypt. Dependencias administradas con Poetry.

---

## 1. Programas que necesitas

Poetry instala las **librerías de Python** del proyecto, pero no los programas. Estos se instalan aparte, una sola vez:

| Programa | Versión | Para qué | Dónde |
|---|---|---|---|
| Python | 3.10 o superior (probado con 3.13 y 3.14) | Ejecutar la API | python.org (marca **"Add python.exe to PATH"**) |
| MySQL Server | 8.0 o superior | La base de datos | dev.mysql.com/downloads/mysql |
| MySQL Workbench | Cualquiera reciente | Crear la base y ver los datos | dev.mysql.com/downloads/workbench |
| Git | Cualquiera reciente | Descargar el proyecto | git-scm.com |
| Visual Studio Code | Opcional | Editar y ejecutar | code.visualstudio.com |

Comprueba en una terminal nueva:

```bash
python --version
git --version
```

> Si `python` abre la Microsoft Store, desactiva los alias en **Configuración → Aplicaciones → Configuración avanzada de aplicaciones → Alias de ejecución de aplicaciones** (python.exe y python3.exe).

---

## 2. Descargar el proyecto

```bash
git clone https://github.com/Azael945/PIA_Almacen.git
cd PIA_Almacen
```

---

## 3. Instalar las librerías

**Opción A, con Poetry (recomendada):**

```bash
python -m pip install poetry
python -m poetry install
```

**Opción B, con un entorno virtual y pip:**

```bash
python -m venv venv
.\venv\Scripts\activate
pip install fastapi uvicorn sqlalchemy pymysql cryptography pyjwt bcrypt "pydantic[email]" python-dotenv
```

> Si PowerShell no deja ejecutar `activate`, corre una vez `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.

---

## 4. Configurar tu archivo `.env`

La contraseña de MySQL y la llave de los tokens **no están en el código**: cada quien las pone en su propio archivo `.env`, que **nunca se sube a GitHub**.

**4.1** Copia la plantilla:

```bash
Copy-Item .env.example .env
```

**4.2** Genera tu llave JWT (es la que firma los tokens de inicio de sesión):

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

**4.3** Abre `.env` y llénalo con **tus** datos:

```
DB_USER=root
DB_PASSWORD=tu_contraseña_de_mysql
DB_HOST=localhost
DB_PORT=3306
DB_NAME=almacen
JWT_SECRET_KEY=pega_aqui_la_llave_del_paso_4.2
```

| Variable | Qué es |
|---|---|
| `DB_USER` | Usuario de MySQL (normalmente `root`) |
| `DB_PASSWORD` | Contraseña de ese usuario. **Obligatoria** |
| `DB_HOST` | Dónde está MySQL (`localhost` = tu computadora) |
| `DB_PORT` | Puerto de MySQL: `3306` por defecto. Si instalaste MySQL "side-by-side", puede ser `3307` |
| `DB_NAME` | Nombre de la base: `almacen` |
| `JWT_SECRET_KEY` | Llave para firmar los tokens. **Obligatoria** |

**4.4** Comprueba que Git ignora tu `.env`:

```bash
git check-ignore .env
```

Debe imprimir `.env`. Si no imprime nada, **no hagas `git add`** y revisa el `.gitignore`.

---

## 5. Crear la base de datos

En MySQL Workbench, abre tu conexión (la del puerto de tu `.env`) y ejecuta **en este orden** (botón del rayo ⚡ o **Ctrl+Shift+Enter**):

1. ```sql
   CREATE DATABASE almacen;
   ```
2. **File → Open SQL Script…** → `database/almacen.sql` → ejecutar todo. Crea las 8 tablas.
3. **File → Open SQL Script…** → `database/datos_prueba.sql` → ejecutar todo. Carga los datos de prueba. Al final muestra una tabla donde los 9 productos deben decir **"cuadra"**.

> El script de datos de prueba se puede volver a ejecutar cuando quieras: vacía las tablas y deja todo como al inicio, con los mismos ids.

---

## 6. Ejecutar la API

Con Poetry:

```bash
python -m poetry run uvicorn main:app --reload
```

Con el entorno virtual activo:

```bash
uvicorn main:app --reload
```

Debe terminar con `Application startup complete.` Deja esa terminal abierta. Para detener el servidor: **Ctrl+C**.

---

## 7. Usar Swagger

1. Abre **http://127.0.0.1:8000/docs**.
2. En `POST /auth/login` → **Try it out** → pega y presiona **Execute**:
   ```json
   { "correo": "angel@almacen.com", "contrasena": "Password123!" }
   ```
3. Copia el valor de `access_token` (texto largo que empieza con `eyJ`, sin comillas).
4. Botón **Authorize 🔒** (arriba a la derecha) → pega el token **sin escribir "Bearer"** → **Authorize** → **Close**. Los candados se cierran.
5. Abre cualquier endpoint → **Try it out** → **Execute**.

> El token dura **60 minutos**. Si empiezas a recibir 401, vuelve a hacer login y Authorize. Si recargas la página, también hay que repetir Authorize. Para cambiar de usuario: **Authorize → Logout**.

### Usuarios de prueba (contraseña `Password123!`)

| Correo | Rol | Puede |
|---|---|---|
| `angel@almacen.com` | Admin | Todo |
| `eva@almacen.com` | Editor | Todo excepto usuarios y borrar categorías |
| `ulises@almacen.com` | Usuario | Solo iniciar sesión (lo demás responde 403) |
| `rosa@almacen.com` | Editor dada de baja | Nada: el login responde 401 |

---

## 8. Problemas comunes

| Si ves | Haz |
|---|---|
| `RuntimeError: Falta la variable DB_PASSWORD` o `JWT_SECRET_KEY` | No existe tu `.env` o le falta ese dato (paso 4) |
| `uvicorn` no se reconoce | Activa el entorno (`.\venv\Scripts\activate`) o usa `python -m poetry run uvicorn ...` |
| `'cryptography' package is required` | `pip install cryptography` (o `python -m poetry add cryptography`) |
| Error 500 en el login y `Access denied` o `Can't connect` en la terminal | Contraseña o puerto incorrectos en `.env`, o MySQL apagado |
| `Unknown database 'almacen'` | Falta el paso 5.1 |
| 401 después de un rato | El token venció: login y Authorize otra vez |
| En Workbench el rayo está desactivado | La pestaña no está conectada: abre primero tu conexión |

---

## 9. Estructura

```
main.py                    Punto de entrada: registra los routers
database/
  almacen.sql              Crea las 8 tablas
  datos_prueba_exposicion.sql  Datos de prueba (se puede repetir)
  conexion.py              Conexión a MySQL (lee el .env)
modulos/
  autenticacion/           Login, tokens JWT y contraseñas
  almacen/                 Inventario y guardia de roles
  usuarios/                CRUD de usuarios (solo Admin)
  configuracion/           CRUD de proveedores, clientes y categorías
  movimientos/             Entradas, salidas e historial
pyproject.toml, poetry.lock  Dependencias (Poetry)
.env.example               Plantilla de variables (sin secretos)
```

**Notas**

- Proveedores, clientes y usuarios no se borran: se marcan como inactivos (baja lógica).
- Una categoría solo se borra si no tiene productos, y solo el Admin puede hacerlo.
- Los movimientos no se editan ni se borran: un error se corrige con un movimiento contrario.
- Se usa `bcrypt` para las contraseñas porque `argon2-cffi` no era compatible con la versión de Python utilizada al inicio del proyecto.
