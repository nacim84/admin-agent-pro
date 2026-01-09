"""Tool for querying business data from PostgreSQL."""

from typing import Dict, Any, Optional, List
from langchain_core.tools import BaseTool
from sqlalchemy import select
from execution.models.database import DataAdministration, KilometresParcourus
from execution.tools.db_manager import DatabaseManager
import logging

logger = logging.getLogger(__name__)

class DatabaseQueryTool(BaseTool):
    name: str = "database_query"
    description: str = """
    Query the data_administration table to retrieve business data.

    Input format:
    {
        "query_type": "facture_info",  # or "charges_info", "frais_km_info", "quittance_info"
        "filters": {"client": "ALTECA", "annee": 2025}
    }

    Output contains all relevant fields for the requested document type.
    """

    def _run(self, query_type: str, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Synchronous run not implemented for this async-heavy tool."""
        raise NotImplementedError("Use _arun for DatabaseQueryTool")

    async def _arun(self, query_type: str, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute query asynchronously."""
        try:
            db = DatabaseManager()
            if query_type == "facture_info":
                return await self._get_facture_info(db, **filters)
            elif query_type == "charges_info":
                return await self._get_charges_info(db, **filters)
            elif query_type == "frais_km_info":
                return await self._get_frais_km_info(db, **filters)
            elif query_type == "quittance_info":
                return await self._get_quittance_info(db, **filters)
            else:
                raise ValueError(f"Unknown query_type: {query_type}")
        except Exception as e:
            logger.error(f"Database query error: {e}")
            return {"error": str(e)}
        finally:
            await db.close()

    async def _get_facture_info(self, db: DatabaseManager, client: str, annee: int) -> Dict[str, Any]:
        """Fetch invoice-related data."""
        async with db.async_session_maker() as session:
            stmt = select(DataAdministration).where(
                DataAdministration.nom_client == client,
                DataAdministration.annee == annee,
                DataAdministration.id_data_administration == 'facturation_client_1'
            ).limit(1)
            result = await session.execute(stmt)
            obj = result.scalar_one_or_none()
            return self._to_dict(obj)

    async def _get_charges_info(self, db: DatabaseManager, annee: int) -> Dict[str, Any]:
        """Fetch rental charges data."""
        async with db.async_session_maker() as session:
            stmt = select(DataAdministration).where(
                DataAdministration.annee == annee,
                DataAdministration.id_data_administration == 'charge_locative_1'
            ).limit(1)
            result = await session.execute(stmt)
            obj = result.scalar_one_or_none()
            return self._to_dict(obj)

    async def _get_frais_km_info(self, db: DatabaseManager, annee: int) -> Dict[str, Any]:
        """Fetch mileage-related data."""
        async with db.async_session_maker() as session:
            stmt = select(DataAdministration).where(
                DataAdministration.annee == annee,
                DataAdministration.id_data_administration == 'frai_kilometrique_1'
            ).limit(1)
            result = await session.execute(stmt)
            obj = result.scalar_one_or_none()
            return self._to_dict(obj)

    async def _get_quittance_info(self, db: DatabaseManager, annee: int) -> Dict[str, Any]:
        """Fetch rent receipt data."""
        async with db.async_session_maker() as session:
            stmt = select(DataAdministration).where(
                DataAdministration.annee == annee,
                DataAdministration.id_data_administration == 'quittance_loyer_1'
            ).limit(1)
            result = await session.execute(stmt)
            obj = result.scalar_one_or_none()
            return self._to_dict(obj)

    def _to_dict(self, obj: Any) -> Dict[str, Any]:
        """Convert SQLAlchemy object to dict."""
        if not obj:
            return {}
        
        # Simple conversion for DataAdministration
        return {
            "id_data_administration": obj.id_data_administration,
            "annee": obj.annee,
            "email_professionnel_1": obj.email_professionnel_1,
            "email_professionnel_2": obj.email_professionnel_2,
            "email_entreprise": obj.email_entreprise,
            "email_client": obj.email_client,
            "devise": obj.devise,
            "nom_professionnel": obj.nom_professionnel,
            "nom_entreprise": obj.nom_entreprise,
            "adresse_entreprise": obj.adresse_entreprise,
            "adresse_professionnel": obj.adresse_professionnel,
            "montant_loyer": obj.montant_loyer,
            "nom_client": obj.nom_client,
            "adresse_client": obj.adresse_client,
            "produit": obj.produit,
            "prix_unitaire": obj.prix_unitaire,
            "tva": obj.tva,
            "paiement": obj.paiement,
            "charges": obj.charges,
            "adresse_client_mission": obj.adresse_client_mission,
            "nom_client_mission": obj.nom_client_mission,
            "trajet_client_mission": obj.trajet_client_mission,
            "puissance_fiscal": obj.puissance_fiscal,
        }
