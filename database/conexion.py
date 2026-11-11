import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker, declarative_base

# Lee las variables del archivo .env (que NO se sube a GitHub)
load_dotenv()

if not os.getenv("DB_PASSWORD"):
    raise RuntimeError(
        "Falta la variable DB_PASSWORD. Crea un archivo .env en la raíz del proyecto "
        "(copia .env.example y llena tus datos)."
    )

# URL.create arma la URL y escapa solo los caracteres especiales de la contraseña
DATABASE_URL = URL.create(
    drivername="mysql+pymysql",
    username=os.getenv("DB_USER", "root"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST", "localhost"),
    port=int(os.getenv("DB_PORT", "3306")),
    database=os.getenv("DB_NAME", "almacen"),
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Función para obtener la sesión en cada petición
def obtener_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
