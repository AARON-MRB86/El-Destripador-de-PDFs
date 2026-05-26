FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar archivos necesarios
COPY pyproject.toml .
COPY README.md ./
COPY App/ ./App/

# Instalar dependencias
RUN pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir .

# Crear usuario seguro
RUN useradd --create-home --home-dir /home/appuser appuser

# Dar permisos
RUN chown -R appuser:appuser /app

# Cambiar a usuario no root
USER appuser

EXPOSE 8000

CMD ["uvicorn", "App.main:app", "--host", "0.0.0.0", "--port", "8000"]
