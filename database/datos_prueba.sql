use almacen;

INSERT INTO rol (nombre, descripcion) VALUES
('Admin', 'Administrador'), ('Editor', 'Editor'), ('Usuario', 'Usuario');

INSERT INTO categoria (nombre, descripcion) VALUES ('Abarrotes', 'Productos de prueba');

INSERT INTO proveedor (nombre, celular, correo, rfc)
VALUES ('Distribuidora Norte', '8120000000', 'ventas@norte.mx', 'DNO010101AAA');

INSERT INTO cliente (nombre, celular, correo)
VALUES ('Abarrotes Don Chuy', '8125550001', 'donchuy@correo.mx');

INSERT INTO producto (codigo, nombre, precio_compra, precio_venta, id_categoria, id_proveedor)
VALUES ('PROD-001', 'Arroz 1kg', 20.00, 28.00, 1, 1);

INSERT INTO almacen (id_producto, stock_actual, descripcion)
VALUES (1, 0, 'Arroz blanco grano largo');

SELECT * FROM rol;
SELECT * FROM producto;
SELECT * FROM almacen;