# Usamos Python 3.11 liviano
FROM python:3.11-slim

# Evitar archivos .pyc y forzar logs inmediatos
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Carpeta de trabajo dentro del contenedor
WORKDIR /app

# Copiamos SOLO requirements primero para aprovechar la cache
COPY requirements.txt .

# Instalamos dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos TODO el código del proyecto
COPY . .

# Cloud Run usa la variable PORT
ENV PORT=8080
EXPOSE 8080

# Arrancamos FastAPI con Uvicorn
# app.main:app  ->  (carpeta app / archivo main.py / variable FastAPI "app")
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
