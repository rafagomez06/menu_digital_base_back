--DROP TABLE ctl_usuarios_sistema_menu

CREATE TABLE ctl_usuarios_sistema_menu (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    activo INTEGER DEFAULT 1 CHECK (activo IN (0, 1)),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_creacion VARCHAR(100) NULL,
    host_creacion VARCHAR(100) NULL,
    fecha_modificacion TIMESTAMP,
    usuario_modificacion VARCHAR(100)
);