FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md ./
COPY app ./app
RUN mkdir -p App \
    && printf "import os\n__path__.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app')))\n" > App/__init__.py
RUN mkdir -p App/static \
    && if [ -d app/static ]; then cp -r app/static/* App/static/ || true; fi

RUN pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir .

RUN useradd --create-home --home-dir /home/appuser appuser
RUN chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
