# Dockerfile para Sistema de Biblioteca
# Basado en Python 3.11 (compatible con Spyne)

FROM python:3.11-slim

# Variables de entorno
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Información del mantenedor
LABEL maintainer="Sistema de Biblioteca U3"
LABEL description="Sistema de gestión de biblioteca con SOAP y REST API"

# Crear directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema necesarias para lxml y otras bibliotecas
RUN apt-get update && apt-get install -y \
    gcc \
    libxml2-dev \
    libxslt-dev \
    python3-dev \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements primero (para aprovechar cache de Docker)
COPY requirements.txt .

# Instalar dependencias Python
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copiar el resto del código
COPY . .

# Crear directorio para archivos estáticos
RUN mkdir -p /app/staticfiles

# Recolectar archivos estáticos
RUN python manage.py collectstatic --noinput || true

# Exponer puerto
EXPOSE 8000

# Script de inicio que ejecuta migraciones y inicia el servidor
CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]