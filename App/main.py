from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles

from App.api.Routes.document import router as documents_router
from App.config.settings import settings
from App.services import DocumentService
from App.utils.database import ensure_indexes, get_database

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    docs_url=settings.api_docs_url,
    redoc_url=settings.api_redoc_url,
    openapi_url=settings.api_openapi_url,
)

app.include_router(documents_router, prefix=settings.api_v1_prefix)
app.mount("/static", StaticFiles(directory="App/static"), name="static")

HOME_PAGE = """
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Extractor de PDF</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 0; padding: 0; background: #f4f7fb; color: #1f2937; }
    .page { max-width: 960px; margin: 0 auto; padding: 24px; }
    h1 { margin-bottom: 8px; }
    .card { background: #ffffff; border-radius: 12px; box-shadow: 0 5px 18px rgba(15, 23, 42, 0.08); padding: 20px; margin-bottom: 24px; }
    label { display: block; margin-bottom: 12px; }
    input[type=text], input[type=file] { width: 100%; padding: 10px 12px; border: 1px solid #cbd5e1; border-radius: 8px; }
    button { cursor: pointer; border: none; background: #0f62fe; color: white; padding: 12px 18px; border-radius: 8px; font-weight: 600; }
    button.secondary { background: #64748b; }
    .message { margin: 16px 0; padding: 14px 16px; border-radius: 10px; background: #e2f0ff; color: #0f172a; }
    .doc-item { border: 1px solid #e2e8f0; border-radius: 10px; padding: 14px; margin-bottom: 12px; }
    .doc-actions { margin-top: 10px; }
    .doc-actions button { margin-right: 8px; margin-bottom: 8px; }
    pre { white-space: pre-wrap; word-break: break-word; background: #f8fafc; padding: 14px; border-radius: 10px; border: 1px solid #e2e8f0; max-height: 360px; overflow: auto; }
    .small { color: #475569; font-size: 0.95rem; }
    .top-line { display: flex; flex-wrap: wrap; justify-content: space-between; gap: 12px; align-items: center; }
  </style>
</head>
<body>
  <div class="page">
    <div class="card">
      <div class="top-line">
        <div>
          <h1>Extractor de PDF</h1>
          <p class="small">Sube un PDF y la app guardará el documento, extraerá el texto y lo mostrará aquí mismo.</p>
        </div>
        <div>
          <a href="/docs" style="text-decoration:none;"><button class="secondary">Abrir documentación /api</button></a>
        </div>
      </div>
      <div style="text-align:center; margin: 18px 0;">
        <img src="/static/images/WhatsApp%20Image%202026-05-11%20at%204.21.17%20PM.jpeg" alt="Banner de PDF" style="max-width: 100%; height: auto; border-radius: 12px; box-shadow: 0 8px 18px rgba(15, 23, 42, 0.1);" />
      </div>
      <form id="uploadForm">
        <label>
          Nombre del documento
          <input type="text" id="name" placeholder="Ej: Contrato" required />
        </label>
        <label>
          Archivo PDF
          <input type="file" id="file" accept="application/pdf" required />
        </label>
        <button type="submit">Subir PDF</button>
      </form>
      <div id="message" class="message" style="display:none"></div>
    </div>

    <div class="card">
      <div class="top-line">
        <div>
          <h2>Documentos guardados</h2>
          <p class="small">Se muestran los archivos que cargaste y su texto extraído.</p>
        </div>
        <button class="secondary" onclick="loadDocuments()">Actualizar lista</button>
      </div>
      <div id="documents"></div>
    </div>
  </div>

  <script>
    const apiPrefix = "/api/v1/documents";
    const messageEl = document.getElementById("message");
    const documentsEl = document.getElementById("documents");
    const uploadForm = document.getElementById("uploadForm");

    function showMessage(text, success = true) {
      messageEl.style.display = "block";
      messageEl.style.background = success ? "#e2f0ff" : "#fee2e2";
      messageEl.style.color = success ? "#0f172a" : "#b91c1c";
      messageEl.textContent = text;
      setTimeout(() => { messageEl.style.display = "none"; }, 6000);
    }

    async function loadDocuments() {
      try {
        const response = await fetch(apiPrefix + "?skip=0&limit=50");
        const documents = await response.json();
        if (!response.ok) {
          throw new Error(documents.detail || "No se pudo leer los documentos");
        }
        renderDocuments(documents);
      } catch (error) {
        showMessage(error.message || "Error cargando documentos", false);
      }
    }

    function renderDocuments(documents) {
      if (!documents.length) {
        documentsEl.innerHTML = "<p>No hay documentos cargados aún.</p>";
        return;
      }
      documentsEl.innerHTML = documents.map(doc => `
        <div class="doc-item">
          <strong>${doc.name}</strong> <span class="small">(ID ${doc.id})</span>
          <div class="small">Archivo: ${doc.original_filename} · ${doc.file_size} bytes</div>
          <div class="small">Procesado: ${doc.is_processed ? "sí" : "no"}</div>
          <div class="doc-actions">
            <button onclick="viewText(${doc.id})">Ver texto</button>
            <button onclick="downloadText(${doc.id})">Descargar .txt</button>
            <button class="secondary" onclick="deleteDocument(${doc.id})">Eliminar</button>
          </div>
          <div id="text-${doc.id}" style="display:none; margin-top:12px;"></div>
        </div>
      `).join("");
    }

    async function uploadPdf(event) {
      event.preventDefault();
      const name = document.getElementById("name").value.trim();
      const fileInput = document.getElementById("file");
      if (!name || fileInput.files.length === 0) {
        showMessage("Por favor completa el nombre y selecciona un PDF.", false);
        return;
      }
      const formData = new FormData();
      formData.append("name", name);
      formData.append("file", fileInput.files[0]);
      try {
        const response = await fetch(apiPrefix, { method: "POST", body: formData });
        const result = await response.json();
        if (!response.ok) {
          throw new Error(result.detail || "No se pudo subir el PDF.");
        }
        showMessage(`PDF subido: ${result.original_filename}`);
        uploadForm.reset();
        loadDocuments();
      } catch (error) {
        showMessage(error.message || "Error subiendo el PDF.", false);
      }
    }

    async function viewText(id) {
      try {
        const response = await fetch(`${apiPrefix}/${id}`);
        const doc = await response.json();
        if (!response.ok) {
          throw new Error(doc.detail || "No se pudo obtener el documento.");
        }
        const target = document.getElementById(`text-${id}`);
        target.style.display = "block";
        target.innerHTML = doc.extracted_text ? `<pre>${escapeHtml(doc.extracted_text)}</pre>` : "<p>No hay texto extraído.</p>";
      } catch (error) {
        showMessage(error.message || "Error al leer el texto.", false);
      }
    }

    async function downloadText(id) {
      try {
        const response = await fetch(`${apiPrefix}/${id}`);
        const doc = await response.json();
        if (!response.ok) {
          throw new Error(doc.detail || "No se pudo obtener el documento.");
        }
        if (!doc.extracted_text) {
          showMessage("El documento no tiene texto extraído.", false);
          return;
        }
        const blob = new Blob([doc.extracted_text], { type: "text/plain;charset=utf-8" });
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = `documento-${doc.id}.txt`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
      } catch (error) {
        showMessage(error.message || "Error descargando el archivo.", false);
      }
    }

    async function deleteDocument(id) {
      if (!confirm("¿Seguro que quieres eliminar este documento?")) {
        return;
      }
      try {
        const response = await fetch(`${apiPrefix}/${id}`, { method: "DELETE" });
        if (!response.ok) {
          const data = await response.json();
          throw new Error(data.detail || "No se pudo eliminar el documento.");
        }
        showMessage("Documento eliminado.");
        loadDocuments();
      } catch (error) {
        showMessage(error.message || "Error eliminando el documento.", false);
      }
    }

    function escapeHtml(str) {
      return str
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/\"/g, "&quot;")
        .replace(/'/g, "&#039;");
    }

    uploadForm.addEventListener("submit", uploadPdf);
    loadDocuments();
  </script>
</body>
</html>
"""

@app.on_event("startup")
async def startup_event() -> None:
    ensure_indexes()

@app.get("/", response_class=HTMLResponse)
async def home() -> HTMLResponse:
    return HTMLResponse(content=HOME_PAGE)

@app.get("/api/v1/documents/{doc_id}/download", response_class=PlainTextResponse)
async def download_document_text(doc_id: int) -> PlainTextResponse:
    db = get_database()
    service = DocumentService(db)
    document = service.get_document(doc_id)
    if not document:
        raise HTTPException(status_code=404, detail="Documento no encontrado")
    if not document.extracted_text:
        raise HTTPException(status_code=400, detail="El documento no tiene texto extraído")
    return PlainTextResponse(
        document.extracted_text,
        media_type="text/plain; charset=utf-8",
        headers={"Content-Disposition": f"attachment; filename=pdf-extract-{doc_id}.txt"},
    )

