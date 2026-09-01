# Análisis de cumplimiento con TDD — El Destripador de PDFs

Fecha del análisis: 26/08/2026
Autor del análisis: agente de revisión (skill `tdd`)
Alcance: repositorio `El-Destripador-de-PDFs` (API FastAPI + MongoDB), commits hasta `14b15cf` (HEAD).

---

## Veredicto

**El proyecto NO cumple con TDD.**

Los tests existen, pero fueron escritos **después** de la implementación (test-last), están **acoplados a la implementación** (verifican métodos privados), contienen **aserciones tautológicas**, y la suite está **rota en Linux/CI**: `python -m pytest -q` falla en el import de `conftest.py` antes de ejecutar un solo test.

---

## 1. Metodología de evaluación

Los criterios provienen de la skill TDD del proyecto (`.agents/skills/tdd/SKILL.md`):

| # | Criterio | Regla TDD |
|---|----------|-----------|
| C1 | Red antes que green | El test falla primero; luego se escribe solo el código mínimo para pasarlo. |
| C2 | Una slice a la vez | Un seam, un test, una implementación mínima por ciclo (vertical). |
| C3 | Tests en seams públicos | Se testea comportamiento vía interfaz pública, nunca internals. |
| C4 | Sin anti-patrones | Nada tautológico, nada acoplado a implementación, nada de slices horizontales. |
| C5 | Suite verde y reproducible | Los tests pasan en el entorno de CI y no dependen de un filesystem case-insensitive. |
| C6 | Cobertura de caminos críticos | Los flujos de negocio principales están testeados en seams acordados. |

---

## 2. Evidencia recopilada

### 2.1 Estado actual de la suite

```
$ python -m pytest -q
ImportError while loading conftest '.../test/conftest.py'.
test/conftest.py:7: in <module>
    from app.repositories.documento_repository import DocumentRepository
E   ModuleNotFoundError: No module named 'app.repositories'
```

**Causa raíz:** los tests importan el paquete en minúsculas (`app.*`) pero el paquete real es `App` (mayúscula, declarado en `pyproject.toml:38` como `packages = ["App"]`). En Linux (donde corre el CI, `ubuntu-latest`) el import falla. La suite solo "funciona" en Windows por el filesystem case-insensitive.

Verificación adicional: al corregir temporalmente los imports (alias `app` → `App` en `sys.modules`), los 5 tests pasan:

```
5 passed in 0.01s
```

Es decir: la lógica de los tests es ejecutable, pero el paquete bajo test está mal referenciado y nadie lo detecta porque no se corre la suite en Linux.

### 2.2 Historial de git (evidencia del proceso)

| Commit | Fecha | Mensaje | Relevancia TDD |
|--------|-------|---------|----------------|
| `6b963df`, `be70e81`, `4a6cbb7` | — | "implementa gestión completa de documentos PDF" | Implementación completa **sin tests**. |
| `b68e449` | 2026-04-30 | "tests: add unit tests and fixtures; …" | Primer test. **En el mismo commit** se reescriben 298 líneas de `App/services/documento_service.py`. Tests e implementación juntos, test-last, slice horizontal. |
| `8d870fe` | 2026-05-27 | "documentacion de codigo" | Toca tests sin cambios de comportamiento. |
| `523e6bd` | 2026-07-20 | "solucion" | Cambia los imports de los tests de `App.` a `app.` (minúscula). **Rompe la suite en Linux/CI.** |
| `f8b006b` | — | "tests: fix imports, add compatibility _next_document_id" | Se agrega a producción un método solo para acomodar tests viejos (ver 2.4). |
| `14b15cf` | 2026-07-23 | "Fix Docker packaging and Linux import casing" | Corrige el casing en `App/` pero **no** corrige los imports de `test/`. La suite sigue rota. |

No hay ningún commit que muestre un ciclo red → green: no existen tests que hayan fallado primero, ni commits atómicos de "un test + su implementación mínima".

### 2.3 Inventario de tests

| Archivo | Tests | Qué verifica |
|---------|-------|--------------|
| `test/test_models_documento.py` | 1 | Defaults del modelo `Document` |
| `test/test_repositories_documento_repository.py` | 2 | `_serialize`/`_deserialize` y `_next_document_id` |
| `test/test_services_documento_service.py` | 2 | Métodos privados de `DocumentService` + 3 ramas de validación |

**Total: 5 tests** frente a ~824 líneas de implementación en las capas principales (`App/services/documento_service.py` 354, `App/repositories/documento_repository.py` 146, `App/utils/validators.py` 166, `App/utils/pdf_processor.py` 43, `App/api/Routes/document.py` 93).

Sin tests: `App/api/**` (rutas y controladores completos), `App/utils/validators.py`, `App/utils/pdf_processor.py`, y los flujos públicos de `DocumentService`: `create_document` (incluida la detección de duplicados por checksum, `documento_service.py:49-50`), `get_document`, `get_all_documents`, `update_document`, `delete_document`, `extract_text` y la validación de tamaño máximo (`documento_service.py:222-226`).

### 2.4 Anti-patrones detectados en el código de tests

1. **Tests de métodos privados (acoplado a implementación).** Los 5 tests apuntan a internals:
   - `_serialize` / `_deserialize` (`test_repositories_documento_repository.py:25-31`)
   - `_next_document_id` (`test_repositories_documento_repository.py:34-38`)
   - `_normalize_original_filename`, `_calculate_checksum`, `_build_memory_reference` (`test_services_documento_service.py:28-38`)
   - `_validate_uploaded_pdf` (`test_services_documento_service.py:40-54`)

   Cualquier refactor interno de `DocumentService` o `DocumentRepository` rompe estos tests aunque el comportamiento público no cambie.

2. **Código de producción modificado para acomodar tests.** `App/repositories/documento_repository.py:129-134`:

   ```python
   def _next_document_id(self) -> int:
       """Backward-compatible alias for older tests and code that expect `_next_document_id`."""
       return self._next_id()
   ```

   El docstring admite explícitamente que el método existe "for older tests". Esto invierte la dirección de TDD: la implementación quedó condicionada por la forma de los tests, en lugar de que los tests sigan el seam público.

3. **Aserción tautológica.** `test_services_documento_service.py:35-36`:

   ```python
   checksum = svc._calculate_checksum(b"abc")
   assert checksum == hashlib.sha256(b"abc").hexdigest()
   ```

   El valor esperado se recalcula exactamente igual que el código bajo test (`documento_service.py:272-274`). La aserción nunca puede fallar; debe usarse un valor literal pre-calculado e independiente.

4. **Aserción vacía/siempre verdadera.** `test_models_documento.py:13`:

   ```python
   assert not doc.is_processed or isinstance(doc.is_processed, bool)
   ```

   `is_processed` es un campo `bool` de Pydantic con default `False`; la aserción pasa siempre por construcción y no verifica nada.

5. **Un test, varios comportamientos.** `test_normalize_and_checksum_and_build_reference` mezcla tres comportamientos sin relación (normalización, checksum, referencia en memoria); `test_validate_uploaded_pdf_basic` mezcla tres ramas de validación. Un fallo no identifica qué comportamiento se rompió, y no se puede ver un ciclo red→green por comportamiento.

6. **Hack de import que enmascara el problema.** `test_services_documento_service.py:12-25` usa un `try/except` con carga por `importlib` "por si el paquete no está disponible", en lugar de corregir el import. Los otros dos archivos no tienen ese fallback y fallan directo en Linux.

7. **Duplicación de fixtures.** `FakeDB` está definida dos veces: en `test/conftest.py:10-20` y de nuevo en `test_repositories_documento_repository.py:10-18`. Los fixtures `fake_db`, `repo` y `tmp_pdf_bytes` del conftest quedan sin usar.

### 2.5 Proceso CI

`.github/workflows/ci.yml` ejecuta `python -m pytest -q` en `ubuntu-latest` (Linux) con Python 3.13. Dado el error de import de la sección 2.1, el job `test` **está roto desde el commit `523e6bd` (2026-07-20)** y nadie lo corrigió al arreglar el casing en `14b15cf` (2026-07-23). El umbral de "suite verde" que exige TDD no se cumple ni siquiera como guardián del merge.

---

## 3. Evaluación por criterio

| # | Criterio | ¿Cumple? | Evidencia |
|---|----------|:--------:|-----------|
| C1 | Red antes que green | **No** | La implementación completa precedió a los tests (commits `6b963df`/`be70e81`/`4a6cbb7` → `b68e449`). No hay rastro de tests fallando primero. |
| C2 | Una slice a la vez | **No** | Todos los tests se agregaron de una vez en `b68e449` junto a una reescritura de 298 líneas del servicio (slice horizontal, no vertical). |
| C3 | Tests en seams públicos | **No** | Los 5 tests verifican métodos privados (`_serialize`, `_deserialize`, `_next_document_id`, `_normalize_original_filename`, `_calculate_checksum`, `_build_memory_reference`, `_validate_uploaded_pdf`). |
| C4 | Sin anti-patrones | **No** | Tautología del checksum (2.4.3), aserción vacía (2.4.4), multi-comportamiento por test (2.4.5), alias de producción "for older tests" (2.4.2). |
| C5 | Suite verde y reproducible | **No** | `ModuleNotFoundError: No module named 'app.repositories'` en Linux; CI roto desde 2026-07-20. Solo pasa en Windows por case-insensitivity. |
| C6 | Cobertura de caminos críticos | **No** | Sin tests de `create_document` (validaciones, duplicados), CRUD completo, `extract_text`, ni de la capa API (`App/api/`, `App/utils/`). 5 tests / ~824 líneas. |

**Resultado: 0 de 6 criterios cumplidos.**

---

## 4. Fortalezas (lo que sí está bien)

- Hay una suite pytest estructurada (`test/`, `pytest.ini` con `testpaths`, convención `test_*.py`).
- Los tests usan fakes/mocks (`FakeDB`, `MagicMock`) sin depender de MongoDB real; el aislamiento de infraestructura es correcto.
- El CI existe y ejecuta los tests en cada push/PR, y `requirements-dev.txt` incluye pytest, pytest-cov, pytest-mock, mongomock.
- Los nombres de archivo siguen la convención por capa (`test_models_*`, `test_repositories_*`, `test_services_*`).

---

## 5. Riesgos derivados

- Refactorizar `DocumentService` o `DocumentRepository` romperá la suite aunque el comportamiento no cambie (acoplamiento a internals).
- Bugs en los flujos principales (duplicados por checksum, validación de tamaño, extracción de texto) no serían detectados por tests.
- El CI rojo normaliza el "verde no obligatorio": ningún PR puede usar la suite como red de seguridad hoy.
- La tautología del checksum da falsa confianza: si `_calculate_checksum` cambiara de algoritmo, el test seguiría en verde.

---

## 6. Plan de acción recomendado (hacia TDD)

1. **Reparar la suite primero (deuda crítica).** Cambiar los imports de `test/` a `App.` (mayúscula) en `test/conftest.py:7`, `test/test_models_documento.py:4`, `test/test_repositories_documento_repository.py:6-7` y eliminar el hack de `importlib` de `test/test_services_documento_service.py:12-25`. Verificar `python -m pytest -q` en Linux. Mover los tests al CI como condición de merge.

2. **Acordar los seams públicos antes de reescribir tests.** Propuesta de seams:
   - `DocumentService.create_document(name, filename, bytes)`: nombre vacío → error; extensión no `.pdf` → error; tamaño 0 o > `MAX_PDF_SIZE_BYTES` → error; firma `%PDF-` inválida → error; checksum duplicado → error; éxito → `DocumentResponse` con texto extraído y `is_processed=True`.
   - `DocumentService.get_document`, `get_all_documents`, `update_document`, `delete_document`, `extract_text`.
   - Endpoints FastAPI: `POST /documents`, `GET /documents`, `GET/PUT/DELETE /documents/{id}`, `POST /documents/{id}/extract` (via `TestClient`).

3. **Reescribir los tests en slices verticales** (un test → una implementación mínima), eliminando los tests de métodos privados y el alias `_next_document_id` de producción (`documento_repository.py:129-134`) junto con su test.

4. **Usar valores esperados independientes.** Para el checksum, un literal pre-calculado de un vector conocido (ej. SHA-256 de `"abc"` = `ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad`), no recomputado con `hashlib` en el test.

5. **Un comportamiento por test** (nombres tipo `test_create_document_rejects_empty_name`), siguiendo el formato de especificación: "user can X / system rejects Y".

6. **Agregar cobertura al CI.** `pytest-cov` ya está en `requirements-dev.txt` pero no se usa; agregar `--cov=App --cov-report=term-missing` con umbral (p. ej. ≥ 80 % en servicios y repositorios) para que la cobertura no siga cayendo.

7. **Documentar los seams acordados** en el repo (p. ej. en `TESTS.md` o `CONTEXT.md`) para que todo el equipo teste los mismos límites públicos.

---

## 7. Conclusión

El proyecto tiene la *infraestructura* de testing (pytest, CI, fakes) pero no la *práctica* de TDD: los tests llegaron después del código, en un solo lote, contra métodos privados, con aserciones que no pueden fallar, y hoy ni siquiera se ejecutan en el entorno de CI. Para cumplir con TDD se requiere (a) reparar los imports y volver la suite verde en Linux, (b) acordar los seams públicos, y (c) reescribir los tests en ciclos red → green por comportamiento, eliminando el acoplamiento a internals y las tautologías.
