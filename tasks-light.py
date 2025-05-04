import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Document, Base
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from dotenv import load_dotenv
from google.cloud import storage
import tempfile
import numpy as np
import json

# Configuramos NLTK para usar solo lo esencial
nltk.download('punkt', quiet=True)

# Cargar variables de entorno
load_dotenv()

# Configuraciones
DATABASE_URL = os.getenv("DATABASE_URL")
GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

# Inicializar SQLAlchemy
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base.metadata.create_all(bind=engine)

# Inicializar cliente de GCS
storage_client = storage.Client()
bucket = storage_client.bucket(GCS_BUCKET_NAME)

# Vectorizador TF-IDF más ligero que reemplaza a sentence-transformers
vectorizer = TfidfVectorizer(max_features=100)


def process_uploaded_file(document_id):
    db = SessionLocal()

    try:
        document = db.query(Document).filter(
            Document.id == document_id).first()
        if not document:
            print(f"Documento {document_id} no encontrado.")
            return

        # Obtener blob de GCS
        blob = bucket.blob(document.file_path)

        # Leer directamente de GCS sin archivo temporal
        text = blob.download_as_text()

        # Procesar el texto - versión simplificada
        chunks = nltk.tokenize.sent_tokenize(text)

        # Generar embeddings simplificados usando TF-IDF
        if chunks:
            # Vectorización TF-IDF (mucho más rápida que modelos neuronales)
            tfidf_matrix = vectorizer.fit_transform(chunks)
            # Convertir a lista para almacenar en JSON
            simple_embeddings = [
                list(vec) for vec in tfidf_matrix.toarray()
            ]
        else:
            simple_embeddings = []

        # Guardar embeddings en la base de datos
        document.embeddings = simple_embeddings
        db.commit()

        # Guardar chunks como archivos en GCS
        base_path = "/".join(document.file_path.split("/")[:-1])
        chunk_folder = f"{base_path}/chunks"

        for i, chunk in enumerate(chunks):
            chunk_filename = f"{chunk_folder}/chunk_{i}.txt"
            chunk_blob = bucket.blob(chunk_filename)
            chunk_blob.upload_from_string(chunk)

        print(f"Documento {document.filename} procesado exitosamente.")

    except Exception as e:
        print(f"Error procesando documento: {e}")
    finally:
        db.close()
