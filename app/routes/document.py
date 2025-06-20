from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from app.models.document import ProcessingParams, ProcessedDocument
from app.services.ai_processor import DocumentProcessor
import tempfile
import os
import json

router = APIRouter()
processor = DocumentProcessor()

@router.post("/process", response_model=ProcessedDocument)
async def process_document(
    file: UploadFile = File(...),
    params: str = Form(...)
):
    try:
        # Parsear los parámetros JSON
        try:
            params_dict = json.loads(params)
            processing_params = ProcessingParams(**params_dict)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON in params")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid params: {str(e)}")

        # Guardar imagen temporalmente
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        # Procesar con IA
        result = processor.process_image(tmp_path, processing_params.dict())
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)  # Limpieza 