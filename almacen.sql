# create database almacen;

# drop table almacen;
# drop table movimiento;
# drop table usuario;
# drop table rol;
# drop table producto;
# drop table cliente;
# drop table proveedor;
# drop table categoria;

use almacen;

create table rol(
    id_rol int auto_increment primary key,
    nombre enum('Usuario', 'Admin', 'Editor') not null unique,
    descripcion varchar(255)
) engine = InnoDB default charset = utf8mb4;

create table usuario(
    id_usuario int auto_increment primary key,
    nombre varchar(50) not null,
    celular varchar(30) not null,
    correo varchar(100) not null unique,
    contrasena varchar(255) not null,
    id_rol int,
    fecha_alta datetime default current_timestamp,
    activo boolean default true,
    foreign key (id_rol) references rol(id_rol) on delete restrict
) engine = InnoDB default charset = utf8mb4;

create table proveedor(
    id_proveedor int auto_increment primary key,
    nombre varchar(100) not null,
    celular varchar(30) not null,
    correo varchar(100) not null,
    rfc varchar(50) not null unique,
    fecha_alta datetime default current_timestamp,
    activo boolean default true
) engine = InnoDB default charset = utf8mb4;

create table categoria(
    id_categoria int auto_increment primary key,
    nombre varchar(50) not null unique,
    descripcion varchar(255)
) engine = InnoDB default charset = utf8mb4;

create table producto(
    id_producto int auto_increment primary key,
    codigo varchar(30) not null unique,
    nombre varchar(50) not null,
    fecha_alta datetime default current_timestamp,
    activo boolean default true,
    precio_compra decimal(10,2) not null default 0.00,
    precio_venta decimal(10,2) not null default 0.00,
    id_categoria int,
    id_proveedor int,
    foreign key (id_categoria) references categoria(id_categoria) on delete restrict,
    foreign key (id_proveedor) references proveedor(id_proveedor) on delete restrict
) engine = InnoDB default charset = utf8mb4;

create table almacen(
    id_producto int primary key,
    stock_actual int not null default 0,
    descripcion varchar(255),
    foreign key (id_producto) references producto(id_producto) on delete restrict
)engine = InnoDB default charset = utf8mb4;

create table cliente(
    id_cliente int auto_increment primary key,
    nombre varchar(100) not null,
    celular varchar(30),
    correo varchar(100)
) engine = InnoDB default charset = utf8mb4;

create table movimiento(
    id_movimiento int auto_increment primary key,
    tipo enum('Entrada', 'Salida') not null,
    cantidad int not null,
    fecha datetime default current_timestamp,
    descripcion varchar(255),
    id_producto int not null,
    id_usuario int not null,
    id_proveedor int null,
    id_cliente int null,
    foreign key (id_producto) references producto(id_producto) on delete restrict,
    foreign key (id_usuario) references usuario(id_usuario) on delete restrict,
    foreign key (id_proveedor) references proveedor(id_proveedor) on delete restrict,
    foreign key (id_cliente) references cliente(id_cliente) on delete restrict
)engine = InnoDB default charset = utf8mb4;