"""Modèles de base de données SQLAlchemy."""

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, Integer, String, Date, JSON, ForeignKey, DateTime, Enum, Text, BigInteger
from datetime import datetime
import enum


class Base(DeclarativeBase):
    pass


class DocumentType(enum.Enum):
    """Types de documents supportés."""

    INVOICE = "invoice"
    QUOTE = "quote"
    MILEAGE = "mileage"
    RENT_RECEIPT = "rent_receipt"
    RENTAL_CHARGES = "rental_charges"


class Document(Base):
    """Table des documents générés."""
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    document_type = Column(Enum(DocumentType), index=True)
    document_number = Column(String, unique=True, index=True)
    user_id = Column(BigInteger, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Stockage des données structurées (JSON)
    data = Column(JSON)
    
    # Chemin du fichier PDF généré
    pdf_path = Column(String, nullable=True)
    
    # ID du fichier Telegram (pour renvoi rapide)
    telegram_file_id = Column(String, nullable=True)


class ChatHistory(Base):
    """Table de l'historique des conversations."""
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(BigInteger, index=True)
    role = Column(String)  # "user" ou "assistant"
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

