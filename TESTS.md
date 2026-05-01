# Ejecutar tests

Instrucciones rápidas para ejecutar la suite de pruebas localmente.

1. Activar el entorno virtual del proyecto (Windows PowerShell):

```powershell
(Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned)
& ".venv\Scripts\Activate.ps1"
```

2. Instalar dependencias de desarrollo:

```powershell
python -m pip install -r requirements-dev.txt
```

3. Ejecutar todos los tests:

```powershell
python -m pytest -q
```

4. Ejecutar un test específico:

```powershell
python -m pytest test/test_services_documento_service.py::test_validate_uploaded_pdf_basic -q
```

Notas:
- El proyecto contiene un pequeño `App/config/__init__.py` con valores mínimos necesarios para ejecutar los tests.
- Si usas otro entorno/IDE, ajusta los comandos para activar tu entorno Python.
