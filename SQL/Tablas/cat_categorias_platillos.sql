--DROP TABLE cat_categorias_platillos
CREATE TABLE cat_categorias_platillos (
    id_categoria SERIAL PRIMARY KEY,
    descripcion VARCHAR(30),
    activo INTEGER DEFAULT 1 CHECK (activo IN (0, 1))
);