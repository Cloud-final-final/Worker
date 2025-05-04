import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Document, Base
import nltk
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from google.cloud import storage
import tempfile

# Descargar recursos NLTK
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('omw-1.4')

# Cargar variables de entorno
load_dotenv()

# Configuraciones
DATABASE_URL = os.getenv("DATABASE_URL")
GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
EMBEDDING_MODEL_NAME = os.getenv(
    "EMBEDDING_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2")

# Inicializar SQLAlchemy
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

# Move this line HERE - after engine is initialized
Base.metadata.create_all(bind=engine)

# Inicializar cliente de GCS
storage_client = storage.Client()
bucket = storage_client.bucket(GCS_BUCKET_NAME)

# Inicializar modelo de embeddings
model = SentenceTransformer(EMBEDDING_MODEL_NAME)


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

        # Crear archivo temporal
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            # Descargar contenido al archivo temporal
            blob.download_to_filename(temp_file.name)

            # Leer el archivo
            with open(temp_file.name, "r", encoding="utf-8") as f:
                text = f.read()

        # Eliminar archivo temporal
        os.unlink(temp_file.name)

        # Procesar el texto
        chunks = nltk.tokenize.sent_tokenize(text)
        embeddings = model.encode(chunks).tolist()

        # Guardar embeddings en la base de datos
        document.embeddings = embeddings
        db.commit()

        # Guardar chunks como archivos en GCS
        for i, chunk in enumerate(chunks):
            chunk_filename = f"{document.file_path}/chunks/chunk_{i}.txt"
            chunk_blob = bucket.blob(chunk_filename)
            chunk_blob.upload_from_string(chunk)

        print(f"Documento {document.filename} procesado exitosamente.")

    except Exception as e:
        print(f"Error procesando documento: {e}")
    finally:
        db.close()
