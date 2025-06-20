from fastapi import FastAPI
from app.routes.document import router as document_router

app = FastAPI(title="Procesador de Facturas con IA")

app.include_router(document_router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 