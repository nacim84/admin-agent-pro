"""Gestionnaire de base de données PostgreSQL."""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select, func, desc
from execution.models.database import Base, Document, DocumentType, ChatHistory
from execution.core.config import get_settings
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Gestionnaire centralisé pour les opérations de base de données."""

    def __init__(self):
        """Initialise le gestionnaire avec la configuration."""
        settings = get_settings()

        # Construire l'URL de connexion PostgreSQL
        db_url = (
            f"postgresql+asyncpg://{settings.postgres_user}:{settings.postgres_password}"
            f"@{settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}"
        )

        # Créer l'engine async
        self.engine = create_async_engine(
            db_url,
            echo=settings.debug,  # Log SQL si debug activé
            pool_size=5,
            max_overflow=10,
        )

        # Créer le session maker
        self.async_session_maker = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    async def init_db(self) -> None:
        """Crée toutes les tables si elles n'existent pas."""
        try:
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("✅ Tables de base de données initialisées")
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'initialisation de la base: {e}")
            raise

    async def drop_all(self) -> None:
        """Supprime toutes les tables (ATTENTION : destructif !)."""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        logger.warning("⚠️  Toutes les tables ont été supprimées")

    async def save_document(
        self,
        doc_type: DocumentType,
        doc_number: str,
        data: dict,
        pdf_path: Optional[str],
        user_id: int,
        telegram_file_id: Optional[str] = None,
    ) -> Document:
        """
        Enregistre un nouveau document en base.

        Args:
            doc_type: Type de document
            doc_number: Numéro unique du document
            data: Données du document (dict du modèle Pydantic)
            pdf_path: Chemin vers le PDF généré
            user_id: ID Telegram de l'utilisateur
            telegram_file_id: ID du fichier sur Telegram (optionnel)

        Returns:
            Document: L'objet Document créé

        Raises:
            Exception: Si une erreur se produit lors de la sauvegarde
        """
        try:
            async with self.async_session_maker() as session:
                document = Document(
                    document_type=doc_type,
                    document_number=doc_number,
                    data=data,
                    pdf_path=pdf_path,
                    user_id=user_id,
                    telegram_file_id=telegram_file_id,
                )

                session.add(document)
                await session.commit()
                await session.refresh(document)

                logger.info(
                    f"✅ Document sauvegardé: {doc_type.value} #{doc_number} "
                    f"(ID: {document.id})"
                )
                return document

        except Exception as e:
            logger.error(f"❌ Erreur lors de la sauvegarde du document: {e}")
            raise

    async def get_document_by_number(self, doc_number: str) -> Optional[Document]:
        """Récupère un document par son numéro."""
        async with self.async_session_maker() as session:
            result = await session.execute(
                select(Document).where(Document.document_number == doc_number)
            )
            return result.scalar_one_or_none()

    async def get_documents_by_user(
        self,
        user_id: int,
        doc_type: Optional[DocumentType] = None,
        limit: int = 50,
    ) -> list[Document]:
        """
        Récupère les documents d'un utilisateur.

        Args:
            user_id: ID Telegram de l'utilisateur
            doc_type: Filtrer par type de document (optionnel)
            limit: Nombre maximum de résultats

        Returns:
            Liste des documents
        """
        async with self.async_session_maker() as session:
            query = select(Document).where(Document.user_id == user_id)

            if doc_type:
                query = query.where(Document.document_type == doc_type)

            query = query.order_by(Document.created_at.desc()).limit(limit)

            result = await session.execute(query)
            return list(result.scalars().all())

    async def get_next_invoice_number(self, year: int) -> str:
        """
        Génère le prochain numéro de facture pour l'année donnée.

        Format: YYYY-NNNN (ex: 2024-0001)

        Args:
            year: Année pour la facture

        Returns:
            Numéro de facture au format YYYY-NNNN
        """
        async with self.async_session_maker() as session:
            # Chercher la dernière facture de l'année
            result = await session.execute(
                select(Document.document_number)
                .where(Document.document_type == DocumentType.INVOICE)
                .where(Document.document_number.like(f"{year}-%"))
                .order_by(Document.document_number.desc())
                .limit(1)
            )

            last_number = result.scalar_one_or_none()

            if last_number:
                # Extraire le numéro séquentiel et incrémenter
                seq = int(last_number.split("-")[1]) + 1
            else:
                # Première facture de l'année
                seq = 1

            return f"{year}-{seq:04d}"

    async def get_next_quote_number(self, year: int) -> str:
        """
        Génère le prochain numéro de devis pour l'année donnée.

        Format: DEV-YYYY-NNNN (ex: DEV-2024-0001)
        """
        async with self.async_session_maker() as session:
            result = await session.execute(
                select(Document.document_number)
                .where(Document.document_type == DocumentType.QUOTE)
                .where(Document.document_number.like(f"DEV-{year}-%"))
                .order_by(Document.document_number.desc())
                .limit(1)
            )

            last_number = result.scalar_one_or_none()

            if last_number:
                seq = int(last_number.split("-")[2]) + 1
            else:
                seq = 1

            return f"DEV-{year}-{seq:04d}"

    async def get_next_mileage_number(self, year: int) -> str:
        """
        Génère le prochain numéro de note de frais pour l'année donnée.

        Format: KM-YYYY-NNNN (ex: KM-2024-0001)
        """
        async with self.async_session_maker() as session:
            result = await session.execute(
                select(Document.document_number)
                .where(Document.document_type == DocumentType.MILEAGE)
                .where(Document.document_number.like(f"KM-{year}-%"))
                .order_by(Document.document_number.desc())
                .limit(1)
            )

            last_number = result.scalar_one_or_none()

            if last_number:
                seq = int(last_number.split("-")[2]) + 1
            else:
                seq = 1

            return f"KM-{year}-{seq:04d}"

    async def get_next_rent_receipt_number(self, year: int) -> str:
        """
        Génère le prochain numéro de quittance pour l'année donnée.

        Format: QUIT-YYYY-NNNN (ex: QUIT-2024-0001)
        """
        async with self.async_session_maker() as session:
            result = await session.execute(
                select(Document.document_number)
                .where(Document.document_type == DocumentType.RENT_RECEIPT)
                .where(Document.document_number.like(f"QUIT-{year}-%"))
                .order_by(Document.document_number.desc())
                .limit(1)
            )

            last_number = result.scalar_one_or_none()

            if last_number:
                seq = int(last_number.split("-")[2]) + 1
            else:
                seq = 1

            return f"QUIT-{year}-{seq:04d}"

    async def get_next_rental_charges_number(self, year: int) -> str:
        """
        Génère le prochain numéro de régularisation pour l'année donnée.

        Format: REGUL-YYYY-NNNN (ex: REGUL-2024-0001)
        """
        async with self.async_session_maker() as session:
            result = await session.execute(
                select(Document.document_number)
                .where(Document.document_type == DocumentType.RENTAL_CHARGES)
                .where(Document.document_number.like(f"REGUL-{year}-%"))
                .order_by(Document.document_number.desc())
                .limit(1)
            )

            last_number = result.scalar_one_or_none()

            if last_number:
                seq = int(last_number.split("-")[2]) + 1
            else:
                seq = 1

            return f"REGUL-{year}-{seq:04d}"

    async def add_chat_message(self, user_id: int, role: str, content: str) -> None:
        """Ajoute un message à l'historique."""
        try:
            async with self.async_session_maker() as session:
                message = ChatHistory(
                    user_id=user_id,
                    role=role,
                    content=content
                )
                session.add(message)
                await session.commit()
        except Exception as e:
            logger.error(f"❌ Erreur sauvegarde chat: {e}")

    async def get_chat_history(self, user_id: int, limit: int = 10) -> list[dict]:
        """
        Récupère l'historique récent pour un utilisateur.
        Retourne une liste de dicts ordonnée du plus ancien au plus récent.
        """
        async with self.async_session_maker() as session:
            # Récupérer les X derniers messages (descendant)
            result = await session.execute(
                select(ChatHistory)
                .where(ChatHistory.user_id == user_id)
                .order_by(desc(ChatHistory.created_at))
                .limit(limit)
            )
            messages = result.scalars().all()
            
            # Remettre dans l'ordre chronologique (ancien -> récent)
            return [
                {"role": msg.role, "content": msg.content}
                for msg in reversed(messages)
            ]

    async def get_document_count_by_type(self, user_id: int) -> dict[str, int]:
        """Retourne le nombre de documents par type pour un utilisateur."""
        async with self.async_session_maker() as session:
            result = await session.execute(
                select(Document.document_type, func.count(Document.id))
                .where(Document.user_id == user_id)
                .group_by(Document.document_type)
            )

            counts = {doc_type.value: count for doc_type, count in result.all()}
            return counts

    async def close(self) -> None:
        """Ferme proprement les connexions."""
        await self.engine.dispose()
        logger.info("🔌 Connexions base de données fermées")
