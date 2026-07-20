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

## Interfaz de administración web (mongo-express)

Hemos incluido un cliente web ligero `mongo-express` para administración en desarrollo.

Acceso (por defecto):

- URL: http://localhost:8081
- Usuario: `admin`
- Contraseña: `password`

Estos valores vienen de `services/mongodb/.env` si lo copias desde `.env-example`.

Para cambiar credenciales, crea `services/mongodb/.env` y modifica:

```text
MONGO_INITDB_ROOT_USERNAME=admin
MONGO_INITDB_ROOT_PASSWORD=<tu_password_segura>
MONGO_EXPRESS_USER=admin
MONGO_EXPRESS_PASSWORD=<tu_password_segura>
MONGO_EXPRESS_PORT=8081
```

Levantar los servicios:

```powershell
cd services/mongodb
docker compose --env-file .env up -d
```

Luego abre `http://localhost:8081` y autentica con las credenciales definidas.
