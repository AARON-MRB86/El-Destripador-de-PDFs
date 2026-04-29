"""
from App.domain import documento

class DocumentoService:
    def __init__(self, documento: documento.Documento):
        self.documento = documento

    def procesar_pdf(self):
        # Implementar lógica para extraer texto del PDF y procesarlo
            texto = self.extraer_texto(self.documento.file)
            checksum = self.calcular_checksum()
            return texto, checksum

    def validar_duplicados(self, otros_documentos):
        # Implementar lógica para validar si el documento es un duplicado de otros documentos
        pass
"""
from App.domain import documento
from pypdf import PdfReader                     # Librería para leer PDFs
import hashlib                                  # Librería para generar el checksum (hash)
from io import BytesIO                          # Permite tratar bytes como si fuera un archivo en memoria


"""
primero defino la función para que resiva el pdf y luego lo guardo.
En la funcion "procesar_pdf" lo que hace es pocesesar el documento extrallendo el texto 
que contiene y lo transforma en binario luego generamos un checksum para evitar archivos duplicados
"""
# Clase que contiene la lógica principal 
class DocumentoService:

    
    def __init__(self, documento: documento.Documento):           # Constructor: recibe un Documento
        self.documento = documento                                # guardamos el documento para usarlo después

    def procesar_pdf(self):
        texto = self.extraer_texto(self.documento.file)           # Extraemos el texto del PDF
        checksum = self.calcular_checksum(self.documento.file)    # Generamos el checksum del archivo
        return texto, checksum                                    # Devolvemos ambos resultados

    def extraer_texto(self, file_bytes):                          # Función para extraer texto del PDF
        reader = PdfReader(BytesIO(file_bytes))                   # PdfReader espera un archivo
        texto = ""                                                # acumulador de texto
        for pagina in reader.pages:                               # Recorremos cada página del PDF
            texto += pagina.extract_text() or ""                  # Extraemos texto de la página 
            # si no hay texto (None), usamos "" para evitar errores
        return texto                                              # Devolvemos todo el texto concatenado

    def calcular_checksum(self, file_bytes):                      # Función para generar checksum (huella única del archivo)
        hash_obj = hashlib.sha256()                               # Creamos un objeto hash usando SHA-256        
        hash_obj.update(file_bytes)                               # Le pasamos el contenido del archivo
        return hash_obj.hexdigest()                               # Generamos el hash final en formato texto (hexadecimal)