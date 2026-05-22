--DROP TABLE ctl_platillos

CREATE TABLE ctl_platillos (
    id_platillo SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    precio DECIMAL(10,2) NOT NULL CHECK (precio >= 0),
    categoria_platillo_fk INTEGER NOT NULL REFERENCES cat_categorias_platillos(id_categoria) ON DELETE RESTRICT,
    descripcion VARCHAR(350) NOT NULL,
    imagen_url VARCHAR(100) NOT NULL,
    activo INTEGER DEFAULT 1 CHECK (activo IN (0, 1)),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);