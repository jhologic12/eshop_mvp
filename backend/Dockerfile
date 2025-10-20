# ---------- Etapa base ----------
FROM python:3.10-slim AS base
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar requerimientos e instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar la aplicación
COPY ./app ./app

# ---------- Etapa final ----------
FROM base AS runtime
WORKDIR /app

# Copiar dependencias ya instaladas
COPY --from=base /usr/local/lib/python3.10 /usr/local/lib/python3.10

# Copiar variables de entorno por defecto (puedes reemplazarla luego con Docker Compose)
ENV ENVIRONMENT=production
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Exponer el puerto
EXPOSE 8000

# Comando de inicio
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
