FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# system deps for optional PDF libs (kept minimal)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml .
# Optional: `setup.cfg` may be absent in editable installs; skip copying it to avoid
# failing the build when it's not present in the repo.
COPY App/ ./App/
COPY README.md ./

# Install runtime dependencies via pip
RUN pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir .

EXPOSE 8000

CMD ["uvicorn", "App.main:app", "--host", "0.0.0.0", "--port", "8000"]
