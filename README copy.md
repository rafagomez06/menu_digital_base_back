# Menú Digital — Backend API

API REST desarrollada con **Python + Flask + SQLAlchemy + PostgreSQL**.

## Stack
- Python 3.11+
- Flask 3.x
- Flask-SQLAlchemy + Flask-Migrate
- Flask-JWT-Extended (autenticación)
- Flask-Bcrypt (hash de contraseñas)
- Flask-CORS
- PostgreSQL + psycopg2
- Pillow (validación y optimización de imágenes)

## Setup inicial

### 1. Clonar y crear entorno virtual
```bash
python -m venv venv

```
### 1.1.- Ejecutar comando segun el caso
```bash
source venv/bin/activate # Mac/Linux

venv\Scripts\activate  # Windows
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Configurar variables de entorno
```bash
cp .env.template .env
# Editar .env con tus credenciales de PostgreSQL
```

### 4. Levantar el servidor
```bash
flask run
# o
python run.py
```

La API estará disponible en: `http://localhost:5000`

## Flujo de migraciones (cambios en modelos)

Cada vez que modifiques un modelo (nueva columna, nueva tabla, etc.):
```bash
flask db migrate -m "descripcion del cambio"
flask db upgrade
```
