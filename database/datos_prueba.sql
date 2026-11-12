-- =====================================================================
--  PIA Almacén · Datos de prueba para la exposición y para todo el equipo
--  Requisito: haber ejecutado antes database/almacen.sql (crea las tablas).
--  Se puede ejecutar las veces que quieras: VACÍA las 8 tablas y las vuelve
--  a llenar, con los mismos ids siempre (así las pruebas dan lo mismo).
--  Contraseña de todos los usuarios: Password123!
-- =====================================================================
USE almacen;

-- 1. Vaciar todo y reiniciar los ids en 1
SET FOREIGN_KEY_CHECKS = 0;
TRUNCATE TABLE movimiento;
TRUNCATE TABLE almacen;
TRUNCATE TABLE producto;
TRUNCATE TABLE usuario;
TRUNCATE TABLE rol;
TRUNCATE TABLE cliente;
TRUNCATE TABLE proveedor;
TRUNCATE TABLE categoria;
SET FOREIGN_KEY_CHECKS = 1;

-- 2. Roles (id 1 Admin, 2 Editor, 3 Usuario)
INSERT INTO rol (nombre, descripcion) VALUES
  ('Admin',   'Gerente: acceso total, administra usuarios'),
  ('Editor',  'Almacenista: catálogos, entradas y salidas'),
  ('Usuario', 'Consulta; hoy sin permisos en la API');

-- 3. Usuarios (Rosa está dada de baja: no puede iniciar sesión)
INSERT INTO usuario (nombre, celular, correo, contrasena, id_rol, activo) VALUES
  ('Angel Admin',     '8110000001', 'angel@almacen.com',  '$2b$12$KCLgPje9Ji1X5osNX9eDf.VQvinw/zmqPJkHVIG9Nwsn42hpi9kwK', 1, TRUE),
  ('Eva Editor',      '8110000002', 'eva@almacen.com',    '$2b$12$KCLgPje9Ji1X5osNX9eDf.VQvinw/zmqPJkHVIG9Nwsn42hpi9kwK', 2, TRUE),
  ('Ulises Usuario',  '8110000003', 'ulises@almacen.com', '$2b$12$KCLgPje9Ji1X5osNX9eDf.VQvinw/zmqPJkHVIG9Nwsn42hpi9kwK', 3, TRUE),
  ('Rosa Exempleada', '8110000004', 'rosa@almacen.com',   '$2b$12$KCLgPje9Ji1X5osNX9eDf.VQvinw/zmqPJkHVIG9Nwsn42hpi9kwK', 2, FALSE);

-- 4. Categorías (Temporada no tiene productos: se puede borrar)
INSERT INTO categoria (nombre, descripcion) VALUES
  ('Abarrotes', 'Productos secos'),
  ('Limpieza',  'Productos para limpiar'),
  ('Bebidas',   'Líquidos para tomar'),
  ('Higiene',   'Cuidado personal'),
  ('Temporada', 'Productos de temporada');

-- 5. Proveedores (Papelera Sur está dada de baja)
INSERT INTO proveedor (nombre, celular, correo, rfc, activo) VALUES
  ('Distribuidora Norte', '8120000000', 'ventas@norte.mx',     'DNO010101AAA', TRUE),
  ('Lácteos del Valle',   '8183334455', 'pedidos@lacteos.mx',  'LVA150320AB1', TRUE),
  ('Bebidas del Bajío',   '4421112233', 'contacto@bajio.mx',   'BBA200415XY2', TRUE),
  ('Papelera Sur',        '8187776655', 'info@papelerasur.mx', 'PSU180101AA9', FALSE);

-- 6. Clientes (Cafetería Central está dada de baja)
INSERT INTO cliente (nombre, celular, correo, activo) VALUES
  ('Abarrotes Don Chuy', '8125550001', 'donchuy@correo.mx',   TRUE),
  ('Tienda La Esquina',  '8125550002', 'laesquina@correo.mx', TRUE),
  ('Minisúper Lupita',   '8125550003', NULL,                  TRUE),
  ('Cafetería Central',  '8125550004', 'cafe@central.mx',     FALSE);

-- 7. Productos (Galletas está dado de baja: no admite movimientos)
INSERT INTO producto (codigo, nombre, precio_compra, precio_venta, id_categoria, id_proveedor, activo) VALUES
  ('P-001', 'Arroz 1kg',         18.50, 25.00, 1,    1, TRUE),
  ('P-002', 'Frijol 1kg',        22.00, 30.00, 1,    1, TRUE),
  ('P-003', 'Cloro 1L',          12.00, 18.00, 2,    1, TRUE),
  ('P-004', 'Jabón barra',        9.00, 14.00, NULL, 1, TRUE),
  ('P-005', 'Leche 1L',          19.00, 26.00, 3,    2, TRUE),
  ('P-006', 'Refresco 2L',       21.00, 32.00, 3,    3, TRUE),
  ('P-007', 'Pasta dental',      24.00, 38.00, 4,    1, TRUE),
  ('P-008', 'Agua 1L',            6.00, 12.00, 3,    3, TRUE),
  ('P-009', 'Galletas surtidas', 15.00, 22.00, 1,    1, FALSE);

-- 8. Historial: cada stock del paso 9 es igual a sus entradas menos sus salidas
INSERT INTO movimiento (tipo, cantidad, fecha, descripcion, id_producto, id_usuario, id_proveedor, id_cliente) VALUES
  ('Entrada',  50, '2026-11-02 09:10:00', 'Compra semanal',    1, 2, 1, NULL),
  ('Entrada',  20, '2026-11-02 09:15:00', 'Compra semanal',    2, 2, 1, NULL),
  ('Entrada',  12, '2026-11-02 09:20:00', 'Compra semanal',    3, 2, 1, NULL),
  ('Entrada',  10, '2026-11-02 09:25:00', 'Compra semanal',    4, 2, 1, NULL),
  ('Entrada',  15, '2026-11-02 09:30:00', 'Compra semanal',    7, 2, 1, NULL),
  ('Entrada',  10, '2026-11-02 09:35:00', 'Compra semanal',    9, 2, 1, NULL),
  ('Entrada',  60, '2026-11-03 08:00:00', 'Pedido de lácteos', 5, 1, 2, NULL),
  ('Entrada',  48, '2026-11-03 08:30:00', 'Pedido de bebidas', 6, 1, 3, NULL),
  ('Entrada', 100, '2026-11-03 08:35:00', 'Pedido de bebidas', 8, 1, 3, NULL),
  ('Salida',   10, '2026-11-04 11:00:00', 'Venta',             1, 2, NULL, 1),
  ('Salida',   17, '2026-11-04 11:05:00', 'Venta',             2, 2, NULL, 1),
  ('Salida',   12, '2026-11-05 12:40:00', 'Venta',             3, 2, NULL, 2),
  ('Salida',    5, '2026-11-05 12:45:00', 'Venta',             4, 2, NULL, 2),
  ('Salida',   24, '2026-11-06 10:00:00', 'Venta',             5, 2, NULL, 3),
  ('Salida',   46, '2026-11-07 16:20:00', 'Venta grande',      6, 1, NULL, 2),
  ('Salida',    6, '2026-11-08 09:00:00', 'Venta',             5, 2, NULL, 1),
  ('Salida',   30, '2026-11-09 13:00:00', 'Venta',             8, 2, NULL, 3);

-- 9. Stock actual de cada producto
INSERT INTO almacen (id_producto, stock_actual, descripcion) VALUES
  (1, 40, 'Pasillo A'), (2,  3, 'Pasillo A'), (3,  0, 'Pasillo B'),
  (4,  5, 'Pasillo B'), (5, 30, 'Refrigerador 1'), (6,  2, 'Pasillo C'),
  (7, 15, 'Pasillo D'), (8, 70, 'Pasillo C'), (9, 10, 'Bodega');

-- 10. Comprobación: la columna "revision" debe decir "cuadra" en los 9 productos
SELECT p.codigo, p.nombre, a.stock_actual,
       SUM(CASE WHEN m.tipo = 'Entrada' THEN m.cantidad ELSE -m.cantidad END) AS calculado,
       IF(SUM(CASE WHEN m.tipo = 'Entrada' THEN m.cantidad ELSE -m.cantidad END) = a.stock_actual,
          'cuadra', 'NO CUADRA') AS revision
FROM producto p
JOIN almacen a ON a.id_producto = p.id_producto
LEFT JOIN movimiento m ON m.id_producto = p.id_producto
GROUP BY p.id_producto, p.codigo, p.nombre, a.stock_actual
ORDER BY p.codigo;
