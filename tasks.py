import os
import shutil
import nltk
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Document  # Tu modelo de base de datos

# Cargar variables de entorno
from dotenv import load_dotenv
load_dotenv()

import tensorflow as tf
import tensorflow_hub as hub
import tensorflow_text  # Import necesario aunque no lo uses directamente

# Configuraciones
DATABASE_URL = os.getenv("DATABASE_URL")
NFS_MOUNT_PATH = os.getenv("NFS_MOUNT_PATH")

# Inicializar SQLAlchemy
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

# Inicializar modelo de embeddings (Universal Sentence Encoder)
embed = hub.load("https://tfhub.dev/google/universal-sentence-encoder/4")

# Descargar tokenizer
nltk.download('punkt')

def process_uploaded_file(document_id):
    db = SessionLocal()

    try:
        # Buscar el documento
        document = db.query(Document).filter(Document.id == document_id).first()

        if not document:
            print(f"Documento {document_id} no encontrado.")
            return

        file_folder = document.file_path
        original_file = os.path.join(file_folder, document.filename)

        # Leer archivo
        with open(original_file, "r", encoding="utf-8") as f:
            text = f.read()

        # Partir en chunks
        chunks = nltk.tokenize.sent_tokenize(text)

        # Obtener embeddings usando USE
        embeddings_tensor = embed(chunks)
        embeddings = embeddings_tensor.numpy().tolist()

        # Guardar cada chunk como archivo .txt
        for i, chunk in enumerate(chunks):
            chunk_filename = f"chunk_{i}.txt"
            chunk_path = os.path.join(file_folder, chunk_filename)

            with open(chunk_path, "w", encoding="utf-8") as cf:
                cf.write(chunk)

        # Actualizar embeddings en la base de datos
        document.embeddings = embeddings
        db.commit()

        print(f"Procesado documento {document.filename} correctamente.")

    except Exception as e:
        print(f"Error procesando documento: {e}")

    finally:
        db.close()
