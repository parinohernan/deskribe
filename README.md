# deskribe
deskribe is a ia pryect to read images and get jsonfile


📌 1. Configuración Inicial del Proyecto (Entorno Virtual y Estructura)
Objetivo: Crear una base sólida y organizada.

1.1. Instalar Python y Herramientas
Asegúrate de tener Python 3.9+ (recomendado para compatibilidad con librerías de IA).

Instala pip (gestor de paquetes de Python) y venv (para entornos virtuales).

1.2. Crear Estructura de Carpetas
text
/proyecto_ia
│
├── /app                  # Código principal
│   ├── /models           # Modelos de datos (Pydantic)
│   ├── /services         # Lógica de negocio (procesamiento IA)
│   ├── /routes           # Endpoints de la API
│   ├── main.py           # Punto de entrada
│
├── /tests                # Pruebas automatizadas
├── requirements.txt      # Dependencias
├── .env                  # Variables de entorno
├── Dockerfile            # Configuración para Docker
└── README.md             # Documentación
1.3. Crear y Activar Entorno Virtual
bash
python -m venv venv               # Crear entorno
source venv/bin/activate          # Linux/Mac
venv\Scripts\activate             # Windows
📌 2. Instalar Dependencias
Objetivo: Gestionar librerías de forma limpia.

2.1. Crear requirements.txt
txt
fastapi==0.95.2
uvicorn==0.22.0
python-multipart==0.0.6
pillow==10.0.0
torch==2.0.1
transformers==4.30.0
donut-python==1.0.0
python-dotenv==1.0.0
2.2. Instalar Dependencias
bash
pip install -r requirements.txt
📌 3. Crear el Backend con FastAPI
Objetivo: Construir una API REST bien estructurada.

3.1. Definir Modelos de Datos (app/models/document.py)
python
from pydantic import BaseModel
from typing import Optional, List

class ProcessingParams(BaseModel):
    expected_vendor: Optional[str] = None
    document_type: str  # "invoice" o "price_list"
    language: str = "es"

class Article(BaseModel):
    name: str
    price: float
    category: Optional[str] = None

class ProcessedDocument(BaseModel):
    vendor: str
    articles: List[Article]
3.2. Crear Servicio de IA (app/services/ai_processor.py)
python
from donut import DonutModel
import torch
from PIL import Image

class DocumentProcessor:
    def __init__(self):
        self.model = DonutModel.from_pretrained(
            "naver-clova-ix/donut-base-finetuned-cord-v2"
        )
        if torch.cuda.is_available():
            self.model.half().to("cuda")

    def process_image(self, image_path: str, params: dict):
        image = Image.open(image_path)
        output = self.model.inference(
            image=image,
            prompt=f"<s_{params['document_type']}>"
        )
        return self._format_output(output)

    def _format_output(self, raw_output: dict) -> dict:
        # Lógica para convertir la salida del modelo en tu estructura deseada
        return {
            "vendor": "empresa1",  # Ejemplo (debes adaptarlo)
            "articles": [{
                "name": "pinza pelacables",
                "price": 3998,
                "category": "electricidad"
            }]
        }
3.3. Crear Endpoints (app/routes/document.py)
python
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.models.document import ProcessingParams, ProcessedDocument
from app.services.ai_processor import DocumentProcessor
import tempfile
import os

router = APIRouter()
processor = DocumentProcessor()

@router.post("/process", response_model=ProcessedDocument)
async def process_document(
    params: ProcessingParams,
    file: UploadFile = File(...)
):
    try:
        # Guardar imagen temporalmente
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        # Procesar con IA
        result = processor.process_image(tmp_path, params.dict())
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)  # Limpieza
3.4. Punto de Entrada (app/main.py)
python
from fastapi import FastAPI
from app.routes.document import router as document_router

app = FastAPI(title="Procesador de Facturas con IA")

app.include_router(document_router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
📌 4. Ejecutar y Probar la API
4.1. Iniciar el Servidor
bash
uvicorn app.main:app --reload
--reload: Recarga automática al hacer cambios (solo desarrollo).

4.2. Probar con curl o Postman
bash
curl -X POST "http://localhost:8000/api/v1/process" \
  -H "accept: application/json" \
  -F "file=@factura.png" \
  -F "params={\"document_type\":\"invoice\"};type=application/json"
📌 5. Despliegue Básico con Docker
Objetivo: Empaquetar la aplicación para producción.

5.1. Crear Dockerfile
dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
5.2. Construir y Ejecutar
bash
docker build -t invoice-processor .
docker run -p 8000:8000 invoice-processor
📌 6. Buenas Prácticas Adicionales
Variables de Entorno: Usa python-dotenv para configuraciones sensibles.

Logging: Registra eventos importantes (logging module).

Pruebas Unitarias: Usa pytest para probar tu lógica.

Documentación: FastAPI genera automáticamente docs en /docs y /redoc.

