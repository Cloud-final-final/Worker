from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from tasks import process_uploaded_file

app = FastAPI()

class ProcessRequest(BaseModel):
    document_id: str

@app.post("/process")
async def process_document(request: ProcessRequest):
    try:
        process_uploaded_file(request.document_id)
        return {"message": f"Processing started for document {request.document_id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))