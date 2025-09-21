
-- === 3 INSERT ===
INSERT INTO categoria (nombre) VALUES ('Suplementos');
INSERT INTO proveedor (razon_social, contacto) VALUES ('Distribuidora Salud', 'Carlos Pérez');
INSERT INTO producto (cod_producto, nombre, id_categoria, umbral_stock, estado)
VALUES ('VITA100','Vitamina C 100mg', 3, 15, 'ACT');

-- === 2 UPDATE ===
UPDATE producto SET umbral_stock = 30 WHERE cod_producto = 'PARA500';
UPDATE proveedor SET telefono = '22223333' WHERE razon_social = 'Farmadistribuidora Ltda.';

-- === 3 SELECT (2 con JOIN) ===
-- 1) simple
SELECT * FROM categoria;

-- 2) JOIN producto-categoria
SELECT p.nombre, c.nombre AS categoria
FROM producto p
JOIN categoria c ON c.id_categoria = p.id_categoria;

-- 3) JOIN compra-detalle-producto
SELECT co.id_compra, co.fecha_compra, pr.nombre AS producto, d.cantidad, d.costo_unitario
FROM compra co
JOIN detalle_compra d ON d.id_compra = co.id_compra
JOIN producto pr ON pr.id_producto = d.id_producto;

-- === 2 ALTER ===
ALTER TABLE producto ADD COLUMN IF NOT EXISTS descripcion VARCHAR(255);
ALTER TABLE proveedor ADD COLUMN IF NOT EXISTS activo BOOLEAN DEFAULT TRUE;

-- === 1 DROP ===
ALTER TABLE producto DROP COLUMN IF EXISTS descripcion;

-- === 2 DELETE ===
DELETE FROM producto WHERE cod_producto = 'VITA100';
DELETE FROM proveedor WHERE razon_social = 'Distribuidora Salud';
