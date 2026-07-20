# MongoDB Service

Este directorio contiene la infraestructura necesaria para ejecutar MongoDB como un servicio independiente.

## Iniciar MongoDB

1. Copia `.env-example` a `.env`:

```bash
cd services/mongodb
cp .env-example .env
```

2. Inicia el servicio:

```bash
docker compose up -d
```

3. Verifica que MongoDB esté accesible en `mongodb://localhost:27017`.

## Variables de entorno

- `MONGO_INITDB_ROOT_USERNAME`
- `MONGO_INITDB_ROOT_PASSWORD`
- `DATABASE_URL`
- `DATABASE_NAME`
- `DATABASE_TIMEOUT_MS`

## Notas

- El volumen `mongodb_data` mantiene los datos persistentes.
- Esta carpeta es solo infraestructura; la aplicación principal sigue en `app/`.
