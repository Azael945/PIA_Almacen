from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Ajusta tu usuario, contraseña local, host y puerto de MySQL
DATABASE_URL = f"mysql+pymysql://root:ANZ3298r4g65@localhost:3306/almacen"

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