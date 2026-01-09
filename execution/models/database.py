"""Modèles de base de données SQLAlchemy."""

from sqlalchemy.orm import DeclarativeBase

from sqlalchemy import Column, Integer, String, Date, JSON, ForeignKey, DateTime, Enum, Text, BigInteger, Numeric

from sqlalchemy.dialects.postgresql import JSONB

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





class DataAdministration(Base):

    """Table de configuration et données métier (migrée de N8n)."""

    __tablename__ = "data_administration"



    id_data_administration = Column(String(255), primary_key=True)

    annee = Column(Integer, nullable=False)

    

    # Identité électronique

    email_professionnel_1 = Column(String(255), nullable=True)

    email_professionnel_2 = Column(String(255), nullable=True)

    email_entreprise = Column(String(255), nullable=True)

    email_client = Column(String(255), nullable=True)

    

    devise = Column(String(10), nullable=True)

    nom_professionnel = Column(String(255), nullable=True)

    

    # 1. Quittance de loyer

    nom_entreprise = Column(String(255), nullable=True)

    adresse_entreprise = Column(String(255), nullable=True)

    adresse_professionnel = Column(String(255), nullable=True)

    montant_loyer = Column(Numeric(10, 2), nullable=True)

    

    # 2. Facturation client

    nom_client = Column(String(255), nullable=True)

    adresse_client = Column(Text, nullable=True)

    produit = Column(String(255), nullable=True)

    prix_unitaire = Column(Numeric(10, 2), nullable=True)

    tva = Column(String(10), nullable=True)

    paiement = Column(Text, nullable=True)

    

    # 3. Charge locative

    charges = Column(JSONB, nullable=True)

    

    # 4. Frais kilométriques

    adresse_client_mission = Column(Text, nullable=True)

    nom_client_mission = Column(String(255), nullable=True)

    trajet_client_mission = Column(Numeric(5, 2), nullable=True)

    puissance_fiscal = Column(Integer, nullable=True)





class KilometresParcourus(Base):

    """Table du suivi des kilomètres parcourus."""

    __tablename__ = "kilometres_parcourus"



    mois = Column(Integer, primary_key=True)

    annee = Column(Integer, primary_key=True)

    total_kilometres_parcourus = Column(Numeric(10, 1), nullable=True)





class ChatHistory(Base):
    """Table de l'historique des conversations."""
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(BigInteger, index=True)
    role = Column(String)  # "user" ou "assistant"
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

