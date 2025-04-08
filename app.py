from fastapi import FastAPI
from tasks import process_uploaded_file
from pydantic import BaseModel

class DocumentIDRequest(BaseModel):
    document_id: str

app = FastAPI()

@app.post("/process")
def process_file(data: DocumentIDRequest):
    process_uploaded_file(data.document_id)
    return {"message": f"Procesado documento {data.document_id}"}