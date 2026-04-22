# El-Destripador-de-PDFs
Repositorio general

El-Destripador-de-PDFs es una API REST desarrollada en Python cuyo propósito es procesar documentos PDF de manera segura y eficiente.
La aplicación permite recibir archivos PDF, validar su formato y tamaño, extraer su contenido textual y generar un checksum para evitar duplicados.
Posteriormente, persiste la información extraída en una base de datos NoSQL y expone operaciones CRUD para la administración de los documentos almacenados.

El proyecto se desarrolla uscando aplicar los principios de arquitectura limpia y metodología TDD para garantizar calidad, mantenibilidad y escalabilidad.

Objetivos del proyecto
Proveer una API confiable para la ingesta de documentos PDF.
Extraer únicamente el contenido textual relevante del archivo.
Garantizar unicidad mediante checksum para evitar duplicados.
Implementar una base de datos NoSQL para persistir la información procesada.
Permitir la gestión completa de los documentos mediante CRUD.
Mantener una base de código modular, desacoplada y testeada.
Funcionalidades principales
Recepción de archivos PDF desde peticiones HTTP.
Validación del tipo y tamaño del documento.
Extracción de texto sin almacenar el PDF en el disco.
Generación de checksum para identificación única.
Persistencia del contenido en una base NoSQL.
Prevención de duplicados.
CRUD completo sobre los documentos almacenados.
Arquitectura del sistema

La estructura del proyecto sigue una arquitectura en capas:
    -Capa de API: controladores, rutas y manejo de solicitudes.
    -Capa de servicios: lógica de negocio y control de flujo.
    -Capa de dominio: entidades, modelos y reglas fundamentales.
    -Capa de infraestructura: repositorios, integraciones y base de datos.
Este diseño favorece la mantenibilidad, extensibilidad y testeo del sistema.

Tecnologías utilizadas
-Python
-FastAPI
-uv (gestor de dependencias y ejecución)
-Base de datos NoSQL
-Pytest (para TDD)
-Metodología de desarrollo

El proyecto se desarrolla empleando Test-Driven Development (TDD), siguiendo el ciclo:
    -Red: escribir una prueba que falle.
    -Green: implementar el código mínimo para pasar la prueba.
    -Refactor: mejorar el código manteniendo las pruebas en verde.
Además, se aplican principios de diseño como:
    -SOLID
    -DRY
    -KISS
    -YAGNI
Todo ello con el objetivo de obtener un código limpio y mantenible.

Restricciones
    -No se almacenan archivos PDF en el sistema de archivos.
    -No se permite la persistencia temporal del archivo durante el procesamiento.
    -No se almacenan documentos duplicados.
Todo archivo debe ser validado antes de ser procesado.


Estructura del proyecto
El-Destripador-de-PDFs/
│
├── app/
│   ├── api/                # Rutas y controladores
│   ├── services/           # Lógica de negocio
│   ├── domain/             # Entidades y reglas
│   ├── infrastructure/     # Base de datos y repositorios
│   └── main.py             # Punto de entrada de la aplicación
│
├── tests/                  # Pruebas unitarias y de integración
│
├── pyproject.toml          # Configuración del proyecto y dependencias
└── README.md


Instalación
Clonar el repositorio:
git clone https://github.com/AARON-MRB86/El-Destripador-de-PDFs.git
cd El-Destripador-de-PDFs

Instalar dependencias:
uv sync

Activar entorno virtual (si fuera necesario):
.\venv\Scripts\activate

Ejecución de la aplicación
    Iniciar el servidor en modo desarrollo:
    uv run uvicorn app.main:app --reload

La API quedará disponible en:
http://localhost:8000

Documentación de la API

FastAPI genera documentación interactiva:

Swagger: http://localhost:8000/docs
ReDoc: http://localhost:8000/redoc
Ejecución de pruebas
uv run pytest

Estado actual

El proyecto se encuentra en etapa inicial de desarrollo.
Se está construyendo la arquitectura, definiendo modelos, configurando el entorno de trabajo y preparando las bases para incorporar las funcionalidades en etapas posteriores.

Próximos pasos
Implementación de endpoints completos.
Integración con la base de datos NoSQL.
Validaciones avanzadas de PDF.
Optimización del proceso de extracción de texto.
Expansión de la suite de pruebas.