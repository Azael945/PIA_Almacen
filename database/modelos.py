from sqlalchemy import Column, Integer, String, Boolean, DateTime, Numeric, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.conexion import Base


class Categoria(Base):
    __tablename__ = 'categoria'

    id_categoria = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(50), nullable=False, unique=True)
    descripcion = Column(String(255))

    productos = relationship("Producto", back_populates="categoria")


class Rol(Base):
    __tablename__ = 'rol'

    id_rol = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(Enum('Usuario', 'Admin', 'Editor'), nullable=False, unique=True)
    descripcion = Column(String(255))

    usuarios = relationship("Usuario", back_populates="rol")


class Proveedor(Base):
    __tablename__ = 'proveedor'

    id_proveedor = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    celular = Column(String(30), nullable=False)
    correo = Column(String(100), nullable=False)
    rfc = Column(String(50), nullable=False, unique=True)
    fecha_alta = Column(DateTime, server_default=func.now())
    activo = Column(Boolean, default=True)

    productos = relationship("Producto", back_populates="proveedor")
    movimientos = relationship("Movimiento", back_populates="proveedor")


class Cliente(Base):
    __tablename__ = 'cliente'

    id_cliente = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    celular = Column(String(30))
    correo = Column(String(100))

    movimientos = relationship("Movimiento", back_populates="cliente")


class Usuario(Base):
    __tablename__ = 'usuario'

    id_usuario = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(50), nullable=False)
    celular = Column(String(30), nullable=False)
    correo = Column(String(100), nullable=False, unique=True)
    contrasena = Column(String(255), nullable=False)
    fecha_alta = Column(DateTime, server_default=func.now())
    activo = Column(Boolean, default=True)
    id_rol = Column(Integer, ForeignKey('rol.id_rol', ondelete='RESTRICT'))

    rol = relationship("Rol", back_populates="usuarios")
    movimientos = relationship("Movimiento", back_populates="usuario")


class Producto(Base):
    __tablename__ = 'producto'

    id_producto = Column(Integer, primary_key=True, autoincrement=True)
    codigo = Column(String(30), nullable=False, unique=True)
    nombre = Column(String(50), nullable=False)
    fecha_alta = Column(DateTime, server_default=func.now())
    activo = Column(Boolean, default=True)
    precio_compra = Column(Numeric(10, 2), nullable=False, default=0.00)
    precio_venta = Column(Numeric(10, 2), nullable=False, default=0.00)
    id_categoria = Column(Integer, ForeignKey('categoria.id_categoria', ondelete='RESTRICT'))
    id_proveedor = Column(Integer, ForeignKey('proveedor.id_proveedor', ondelete='RESTRICT'))

    categoria = relationship("Categoria", back_populates="productos")
    proveedor = relationship("Proveedor", back_populates="productos")
    almacen = relationship("Almacen", back_populates="producto", uselist=False)
    movimientos = relationship("Movimiento", back_populates="producto")


class Almacen(Base):
    __tablename__ = 'almacen'

    id_producto = Column(Integer, ForeignKey('producto.id_producto', ondelete='RESTRICT'), primary_key=True)
    stock_actual = Column(Integer, nullable=False, default=0)
    descripcion = Column(String(255))

    producto = relationship("Producto", back_populates="almacen")


class Movimiento(Base):
    __tablename__ = 'movimiento'

    id_movimiento = Column(Integer, primary_key=True, autoincrement=True)
    tipo = Column(Enum('Entrada', 'Salida'), nullable=False)
    cantidad = Column(Integer, nullable=False)
    fecha = Column(DateTime, server_default=func.now())
    descripcion = Column(String(255))
    id_producto = Column(Integer, ForeignKey('producto.id_producto', ondelete='RESTRICT'), nullable=False)
    id_usuario = Column(Integer, ForeignKey('usuario.id_usuario', ondelete='RESTRICT'), nullable=False)
    id_proveedor = Column(Integer, ForeignKey('proveedor.id_proveedor', ondelete='RESTRICT'), nullable=True)
    id_cliente = Column(Integer, ForeignKey('cliente.id_cliente', ondelete='RESTRICT'), nullable=True)

    producto = relationship("Producto", back_populates="movimientos")
    usuario = relationship("Usuario", back_populates="movimientos")
    proveedor = relationship("Proveedor", back_populates="movimientos")
    cliente = relationship("Cliente", back_populates="movimientos")
