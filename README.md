Instrucciones para la ejecucion del proyecto

1.- Abre el PowerShell en la carpeta del proyecto

2.- Crear el entorno vitual:    python -m venv venv

3.- Activar el entorno vitual:  .\venv\Scripts\activate

4.- Instalar dependencias:      pip install fastapi uvicorn pydantic

5.- Ejecutar el servidor:       uvicorn main:app --reload

6.- Ingresar en navegador web:  http://127.0.0.1:8000/docs

Procesos que se a estado realizando

Librería argon2-cffi no deja porque no es compatible con la versión preliminar de Python

Para la tipo de encriptación se tuvo que utilizar la librería pip install passlib bcrypt 

Instalamos pip install sqlalchemy pymysql para la conexión de la base de datos

Se instalara pip install email-validator para validar que el formato del correo sea valido

Descargar pip install pyjwt