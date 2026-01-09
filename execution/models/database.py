"""Modèles de base de données SQLAlchemy."""

from sqlalchemy import Column, String, Integer, DateTime, Enum, JSON, Index
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum


Base = declarative_base()


class DocumentType(enum.Enum):
    """Types de documents supportés."""

    INVOICE = "invoice"
    QUOTE = "quote"
    MILEAGE = "mileage"
    RENT_RECEIPT = "rent_receipt"
    RENTAL_CHARGES = "rental_charges"


class Document(Base):
    """
    Table principale pour stocker tous les documents générés.

    Stocke les données sous forme JSON pour flexibilité,
    avec des colonnes indexées pour les recherches rapides.
    """

    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    document_type = Column(Enum(DocumentType), nullable=False, index=True)
    document_number = Column(String(100), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.now, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)

    # Données du document (modèle Pydantic sérialisé en JSON)
    data = Column(JSON, nullable=False)

    # Fichiers générés
    pdf_path = Column(String(500), nullable=True)
    telegram_file_id = Column(String(200), nullable=True)

    # Utilisateur
    user_id = Column(Integer, nullable=False, index=True)

    def __repr__(self) -> str:
        """Représentation textuelle."""
        return (
            f"<Document(id={self.id}, type={self.document_type.value}, "
            f"number={self.document_number}, user={self.user_id})>"
        )


# Créer des index composites pour optimiser les requêtes
Index("idx_user_type", Document.user_id, Document.document_type)
Index("idx_user_created", Document.user_id, Document.created_at.desc())
