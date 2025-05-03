from sqlalchemy import Column, String, ForeignKey, Text, JSON
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    username = Column(String, primary_key=True, index=True)
    hashed_password = Column(String)

    documents = relationship("Document", back_populates="owner")


class Document(Base):
    __tablename__ = "documents"
    id = Column(String, primary_key=True, index=True)
    owner_username = Column(String, ForeignKey("users.username"))
    filename = Column(String)
    # Ahora esto será la ruta en GCS (ej: "documentos/usuario1/archivo.txt")
    file_path = Column(Text)
    embeddings = Column(JSON)

    owner = relationship("User", back_populates="documents")
