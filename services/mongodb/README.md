# MongoDB Service

Este directorio contiene la infraestructura necesaria para ejecutar MongoDB como un servicio independiente.

## Iniciar MongoDB

1. Copia `.env-example` a `.env` y reemplaza valores sensibles:

```bash
cd services/mongodb
cp .env-example .env
# Edita .env y reemplaza las contraseñas (no subir .env al repo)
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

Acceso (desarrollo):

- URL: http://localhost:8081
- Usuario: `admin` (por defecto en `.env-example`)
- Contraseña: la que configures en `MONGO_EXPRESS_PASSWORD` dentro de tu `.env`

Estos valores se leen desde `services/mongodb/.env` si lo copias desde `.env-example`.

Ejemplo rápido para cambiar credenciales y levantar la pila (desarrollo):

```bash
cd services/mongodb
cp .env-example .env
# editar .env -> reemplazar REPLACE_WITH_SECURE_PASSWORD
docker compose --env-file .env up -d
```

Buenas prácticas de seguridad:

- No subas nunca tu `.env` al repositorio. Añade `.env` a `.gitignore` local si hace falta.
- Para entornos de producción usa mecanismos de secretos (Docker Secrets, Vault, Kubernetes Secrets). Ejemplo sencillo con Docker Swarm:

```bash
# crear secret (Swarm):
printf "%s" "mi_contraseña_supersegura" | docker secret create mongo_root_password -
# en tu stack/compose (Swarm) referencia el secret en lugar de poner la contraseña en .env
```

Si quieres, adapto el `docker-compose.yml` para leer secretos en un entorno Swarm/producción.
