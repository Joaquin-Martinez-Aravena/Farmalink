# FarmaLink – Sistema de Inventario Farmaceutico

Proyecto del ramo **Bases de Datos y Programacion Web**.  
Implementación de un sistema de gestión de inventario para farmacia, con roles de **Administrador** y **Empleado**.

---

## Tecnologias

- **Backend**: FastAPI (Python)
- **Base de datos**: PostgreSQL
- **ORM**: SQLAlchemy (async)
- **Conexión**: asyncpg

---

## Entorno de desarrollo

- **Base de datos**: PostgreSQL 15 (administrado vía PgAdmin4).
- **Backend**: FastAPI (Python 3.11).
- **Cliente BD**: PgAdmin4 (Query Tool para ejecutar scripts).
- **Editor**: VS Code.

---

## Configuracion

**1. Clonar repo:**

git clone https://github.com/tuusuario/farmalink-api.git

cd farmalink-api

**2. Crear entorno virtual:**

python -m venv .venv

source .venv/bin/activate (# Windows: .venv\Scripts\activate)

**3. Instalar dependencias:**

pip install -r requirements.txt

**4. Configurar .env (basado en .env.example):**

DATABASE_URL=postgresql+asyncpg://USER:PASSWORD@HOST:5432/famalink

SECRET_KEY=tu_clave_secreta

# Opcional: Configuración de MongoDB (NoSQL)

# Si deseas habilitar la capa NoSQL con MongoDB, agrega:

MONGODB_URL=mongodb://usuario:password@host:27017

# o para Atlas (DNS seedlist):

MONGODB_URL=mongodb+srv://usuario:password@cluster0.xxxxx.mongodb.net

**5. Ejecutar scripts SQL en PgAdmin4 (Query Tool):**

\i sql/00_schema.sql

\i sql/01_seed.sql

(El archivo 02_consultas.sql contiene ejemplos de consultas adicionales.
Si alguna es destructiva como DROP, DELETE o ALTER,
se recomienda ejecutarla solo de forma manual y con cuidado).

**6. Levantar API:**

      uvicorn app.main:app --reload --port 8000

**7. Probar en Swagger:**

    http://localhost:8000/docs

**8. Notas Importantes:**

El archivo consultas.json sirve para centralizar consultas SQL
(SELECT, JOIN, etc.).
Los INSERT, UPDATE, DELETE deberían manejarse por los endpoints
(/api/productos, /api/proveedores, etc.),
y dejar en consultas.json solo reportes y vistas personalizadas.
