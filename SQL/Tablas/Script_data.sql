/*
DROP TABLE cat_categorias_platillos;
DROP TABLE ctl_platillos;
DROP TABLE ctl_usuarios_sistema_menu;

*/
------


CREATE TABLE cat_categorias_platillos (
    id_categoria SERIAL PRIMARY KEY,
    descripcion VARCHAR(30),
    activo INTEGER DEFAULT 1 CHECK (activo IN (0, 1))
);

CREATE TABLE ctl_platillos (
    id_platillo SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    precio DECIMAL(10,2) NOT NULL CHECK (precio >= 0),
    categoria_platillo_fk INTEGER NOT NULL REFERENCES cat_categorias_platillos(id_categoria) ON DELETE RESTRICT,
    descripcion VARCHAR(300) NOT NULL,
    imagen_url VARCHAR(100) NOT NULL,
    popular SMALLINT DEFAULT 0 CHECK (popular IN (0, 1)),
    activo SMALLINT DEFAULT 1 CHECK (activo IN (0, 1)),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE ctl_usuarios_sistema_menu (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    activo INTEGER DEFAULT 1 CHECK (activo IN (0, 1)),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_creacion VARCHAR(100) NOT NULL,
    host_creacion VARCHAR(100) NOT NULL,
    fecha_modificacion TIMESTAMP,
    usuario_modificacion VARCHAR(100)
);




----------------CARGA INICIAL DE DATOS--------------
INSERT INTO ctl_usuarios_sistema (nombre, password_hash,usuario_creacion,host_creacion) VALUES
	('admin','ADMIN1234','admin',inet_client_addr());

INSERT INTO cat_categorias_platillos (descripcion) VALUES 
    ('Entradas'),
    ('Rollos Naturales'),
    ('Rollos Empanizados'),
    ('Rollos Horneados'),
    ('Arroces'),
    ('Bebidas'),
    ('Postres'),
    ('Ingrediente Extra');

INSERT INTO ctl_platillos (nombre,precio,categoria_platillo_fk,descripcion,imagen_url) VALUES
('Mar y Tierra',110,4,'Sushi Clasico mar y tierra','uploads/img/mar_tierra_sushi.jpg'),
('Tostadas de Ceviche', 85, 2, 'Tostadas crujientes con ceviche de pescado fresco, cebolla morada y cilantro', 'uploads/img/tostadas_ceviche.jpg'),
('Ramen Tonkotsu', 120, 4, 'Caldo de cerdo cremoso con fideos artesanales, chashu, huevo marinado y cebollín', 'uploads/img/ramen_tonkotsu.jpg'),
('Ensalada César', 70, 1, 'Lechuga romana, crutones, queso parmesano y aderezo César casero', 'uploads/img/ensalada_cesar.jpg'),
('Pizza Pepperoni', 95, 3, 'Salsa de tomate, queso mozzarella y pepperoni en pan artesanal', 'uploads/img/pizza_pepperoni.jpg'),
('Tempura de Camarón', 130, 5, 'Camarones empanizados fritos con salsa agridulce', 'uploads/img/tempura_camaron.jpg'),
('Chiles Rellenos', 110, 2, 'Chiles poblanos rellenos de queso, capeados y bañados en salsa de jitomate', 'uploads/img/chiles_rellenos.jpg'),
('Brownie con Helado', 60, 6, 'Brownie de chocolate caliente con bola de helado de vainilla y salsa de caramelo', 'uploads/img/brownie_helado.jpg'),
('Sushi California Roll', 90, 5, 'Rollo de pepino, aguacate, cangrejo y semillas de ajonjolí', 'uploads/img/california_roll.jpg'),
('Fajitas de Pollo', 140, 2, 'Tiras de pollo salteadas con pimientos y cebolla, servidas con tortillas', 'uploads/img/fajitas_pollo.jpg'),
('Sopa de Mariscos', 180, 1, 'Caldo de pescado con camarones, almejas, calamar y vegetales', 'uploads/img/sopa_mariscos.jpg');


---QUERY CON DATOS CARGADOS-------
SELECT * FROM ctl_platillos ctl
Inner join cat_categorias_platillos ct
ON ctl.categoria_platillo_fk = ct.id_categoria


--Reinicia tablas
TRUNCATE TABLE cat_categorias_platillos RESTART IDENTITY CASCADE;
