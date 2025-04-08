from fastapi import FastAPI
from tasks import process_uploaded_file

app = FastAPI()

@app.post("/process/{document_id}")
async def process_document(document_id: str):
    """
    Procesa el documento dado su ID: particiona en chunks, embebe y actualiza la base de datos.
    """
    try:
        # Llamamos directamente a la función del worker
        process_uploaded_file(document_id)
        return {"message": f"Documento {document_id} procesado correctamente."}
    except Exception as e:
        return {"error": str(e)}