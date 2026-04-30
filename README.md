# El Destripador de PDFs

API REST en Python para la ingestión, validación y extracción de texto de documentos PDF.

La aplicación permite cargar archivos PDF con un nombre asociado, validar su formato y tamaño, extraer el texto usando `pypdf`, generar un checksum SHA-256 para detectar duplicados y almacenar la información en MongoDB.

## Características

- Carga de archivos PDF usando `multipart/form-data`.
- Validación de extensión `.pdf`, tamaño máximo configurable y firma PDF.
- Extracción de texto en memoria sin escribir el PDF en disco.
- Generación de checksum SHA-256 para evitar documentos duplicados.
- Persistencia de metadatos y texto extraído en MongoDB.
- CRUD de documentos almacenados.
- Endpoint para extraer o recuperar el texto ya procesado.

## Estructura del proyecto

    El-Destripador-de-PDFs/
    ├── App/
    │   ├── api/                # Rutas y controladores
    │   ├── config/             # Configuración de la aplicación
    │   ├── domain/             # Entidades y modelos de dominio
    │   ├── infrastructure/     # Repositorios e integración con MongoDB
    │   ├── models/             # Modelos de dominio
    │   ├── repositories/       # Acceso a datos
    │   ├── schemas/            # Esquemas de validación y respuesta
    │   ├── services/           # Lógica de negocio
    │   └── utils/              # Utilidades de base de datos
    ├── pyproject.toml          # Configuración del proyecto y dependencias
    └── README.md

## Dependencias principales

- Python 3.13+
- FastAPI
- Uvicorn
- Pydantic / Pydantic Settings
- pypdf
- PyMongo
- python-multipart

Dependencias de desarrollo opcionales:

- pytest
- pytest-asyncio
- httpx
- mongomock
- black
- flake8
- mypy
- isort

## Endpoints principales

### POST `/documents`
Crear un documento a partir de un PDF subido.

Campos del formulario:
- `name`: nombre del documento
- `file`: archivo PDF

### GET `/documents`
Listar documentos con paginación.
Parámetros opcionales:
- `skip`: cantidad de registros a omitir
- `limit`: cantidad máxima de registros

### GET `/documents/{document_id}`
Obtener un documento por su ID.

### PUT `/documents/{document_id}`
Actualizar el nombre de un documento.

Payload JSON:
- `name`: nuevo nombre del documento

### DELETE `/documents/{document_id}`
Eliminar un documento.

### POST `/documents/{document_id}/extract`
Extraer o recuperar el texto del PDF asociado a un documento.

## Modelo de respuesta

El recurso `DocumentResponse` incluye campos como:

- `id`
- `name`
- `original_filename`
- `file_size`
- `checksum`
- `extracted_text`
- `is_processed`
- `created_at`
- `updated_at`

## Configuración

La aplicación carga variables de entorno desde un archivo `.env` mediante `pydantic-settings`.

Variables principales:

- `DATABASE_URL`: URL de MongoDB, por ejemplo `mongodb://localhost:27017`
- `DATABASE_NAME`: nombre de la base de datos
- `DATABASE_TIMEOUT_MS`: tiempo de espera en milisegundos
- `MAX_PDF_SIZE_BYTES`: tamaño máximo permitido para los PDF
- `HOST`: host de arranque
- `PORT`: puerto de la API

Ejemplo de `.env`:

```env
DATABASE_URL=mongodb://localhost:27017
DATABASE_NAME=pdf_extract
DATABASE_TIMEOUT_MS=3000
MAX_PDF_SIZE_BYTES=10485760
HOST=0.0.0.0
PORT=8000
```

## Instalación

1. Clona el repositorio:

```powershell
git clone <repo-url>
cd El-Destripador-de-PDFs
```

2. Crea y activa un entorno virtual:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

3. Instala las dependencias:

```powershell
pip install -e .
```

4. Instala dependencias de desarrollo y PDF opcionales:

```powershell
pip install -e ".[dev,pdf]"
```

## Ejecución

Inicia el servidor con Uvicorn:

```powershell
uvicorn app.main:app --reload
```

La API estará disponible en:

- `http://localhost:8000`
- `http://localhost:8000/docs` (Swagger)
- `http://localhost:8000/redoc` (ReDoc)

## Pruebas

Ejecuta la suite de pruebas:

```powershell
pytest
```

## Notas importantes

- Los PDFs se validan en memoria.
- Se comprueba el checksum para evitar registros duplicados.
- La arquitectura del proyecto está separada en capas de rutas, servicios, dominio e infraestructura.
