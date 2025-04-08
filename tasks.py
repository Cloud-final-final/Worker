# tasks.py

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Document  # Tu modelo de base de datos
import nltk
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuraciones
DATABASE_URL = os.getenv("DATABASE_URL")
NFS_MOUNT_PATH = os.getenv("NFS_MOUNT_PATH")
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# Inicializar SQLAlchemy
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

# Inicializar modelo de embeddings (ligero)
model = SentenceTransformer(EMBEDDING_MODEL_NAME)

# Descargar punkt tokenizer (esto lo haces UNA VEZ manualmente antes)
# nltk.download('punkt')  # Ya no lo dejes aquí para no depender de internet en producción

def process_uploaded_file(document_id):
    db = SessionLocal()

    try:
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            print(f"Documento {document_id} no encontrado.")
            return

        file_folder = document.file_path
        original_file = os.path.join(file_folder, document.filename)

        with open(original_file, "r", encoding="utf-8") as f:
            text = f.read()

        chunks = nltk.tokenize.sent_tokenize(text)
        embeddings = model.encode(chunks).tolist()

        # Guardar embeddings en la base de datos
        document.embeddings = embeddings
        db.commit()

        # Guardar chunks como archivos
        for i, chunk in enumerate(chunks):
            chunk_filename = f"chunk_{i}.txt"
            chunk_path = os.path.join(file_folder, chunk_filename)
            with open(chunk_path, "w", encoding="utf-8") as cf:
                cf.write(chunk)

        print(f"Documento {document.filename} procesado exitosamente.")

    except Exception as e:
        print(f"Error procesando documento: {e}")
    finally:
        db.close()