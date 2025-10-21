
-- Categorías
INSERT INTO categoria (nombre) VALUES ('Antibióticos');
INSERT INTO categoria (nombre) VALUES ('Analgésicos');
INSERT INTO categoria (nombre) VALUES ('Vitaminas');

-- Usuarios
INSERT INTO usuario (nombre, rol) VALUES ('Administrador', 'ADMIN');
INSERT INTO usuario (nombre, rol) VALUES ('Empleado1', 'EMPLEADO');

-- Proveedores
INSERT INTO proveedor (razon_social, contacto, telefono, email)
VALUES ('Farmadistribuidora Ltda.', 'María Soto', '987654321', 'ventas@farmadis.cl');

-- Productos
INSERT INTO producto (cod_producto, nombre, id_categoria, umbral_stock, estado)
VALUES ('AMOX500','Amoxicilina 500mg', 1, 10, 'ACT');

INSERT INTO producto (cod_producto, nombre, id_categoria, umbral_stock, estado)
VALUES ('PARA500','Paracetamol 500mg', 2, 20, 'ACT');

-- Compra inicial + detalle + lote
INSERT INTO compra (id_proveedor, fecha_compra, total, id_usuario_registra)
VALUES (1, CURRENT_DATE, 50.00, 1);

INSERT INTO detalle_compra (id_compra, id_producto, cantidad, costo_unitario)
VALUES (1, 1, 10, 5.00);

INSERT INTO lote (id_producto, id_compra, fecha_venc, stock_lote)
VALUES (1, 1, CURRENT_DATE + INTERVAL '6 months', 10);
