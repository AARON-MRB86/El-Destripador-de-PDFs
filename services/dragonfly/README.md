# Dragonfly Service

Este directorio contiene la infraestructura preparada para Dragonfly.

## Propósito

- Registrar Dragonfly como un servicio independiente.
- Mantener la aplicación separada de la infraestructura.
- Permitir futura integración sin cambios en el código actual.

## Iniciar Dragonfly

1. Copia `.env-example` a `.env`:

```bash
cd services/dragonfly
cp .env-example .env
```

2. Inicia el servicio:

```bash
docker compose up -d
```

3. La API de Dragonfly quedará escuchando en `http://localhost:8080`.

## Notas

- Este servicio no está integrado en el código de `app/`.
- Está preparado para un futuro donde se pueda agregar Redis, PostgreSQL, Traefik u otros servicios siguiendo la misma estructura.
