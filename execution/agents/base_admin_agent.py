"""Agent de base pour tous les agents administratifs."""

from abc import ABC, abstractmethod
from typing import Any, TypedDict
from pathlib import Path
from langgraph.graph import StateGraph, END
from execution.tools.pdf_generator import PDFGenerator
from execution.tools.db_manager import DatabaseManager
from execution.core.config import get_settings
import logging

logger = logging.getLogger(__name__)


class AdminAgentState(TypedDict):
    """État partagé entre les nœuds du graph LangGraph."""

    user_id: int
    request_type: str
    input_data: dict[str, Any]
    validated_data: dict[str, Any] | None
    pdf_path: Path | None
    db_record_id: int | None
    error: str | None


class BaseAdminAgent(ABC):
    """Classe de base pour tous les agents administratifs."""

    def __init__(self):
        """Initialise l'agent avec les outils nécessaires."""
        self.settings = get_settings()
        self.pdf_gen = PDFGenerator(Path(self.settings.tmp_dir) / "documents")
        self.db = DatabaseManager()
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    async def validate_input(self, state: AdminAgentState) -> AdminAgentState:
        """
        Valide et enrichit les données d'entrée.

        Cette méthode doit:
        1. Vérifier que toutes les données requises sont présentes
        2. Enrichir les données avec des valeurs par défaut si nécessaire
        3. Créer un modèle Pydantic validé
        4. Mettre à jour state["validated_data"] avec le dict du modèle

        Args:
            state: État actuel du workflow

        Returns:
            État mis à jour avec validated_data ou error
        """
        pass

    @abstractmethod
    async def generate_pdf(self, state: AdminAgentState) -> AdminAgentState:
        """
        Génère le PDF du document.

        Cette méthode doit:
        1. Vérifier qu'il n'y a pas d'erreur
        2. Recréer le modèle Pydantic depuis validated_data
        3. Appeler la méthode appropriée du PDF generator
        4. Mettre à jour state["pdf_path"]

        Args:
            state: État actuel du workflow

        Returns:
            État mis à jour avec pdf_path ou error
        """
        pass

    async def save_to_db(self, state: AdminAgentState) -> AdminAgentState:
        """
        Enregistre le document en base de données.

        Méthode commune à tous les agents.

        Args:
            state: État actuel du workflow

        Returns:
            État mis à jour avec db_record_id ou error
        """
        if state.get("error"):
            return state

        try:
            # Cette méthode sera implémentée par les agents concrets
            # car elle nécessite de connaître le type de document
            self.logger.info(f"Sauvegarde en base pour user {state['user_id']}")
            return state

        except Exception as e:
            self.logger.error(f"Erreur sauvegarde DB: {e}", exc_info=True)
            state["error"] = f"Erreur sauvegarde DB: {str(e)}"
            return state

    def build_graph(self) -> StateGraph:
        """
        Construit le graph LangGraph pour ce type d'agent.

        Le workflow standard est:
        1. Validation des entrées
        2. Génération du PDF
        3. Sauvegarde en base de données

        Returns:
            Graph LangGraph compilé
        """
        workflow = StateGraph(AdminAgentState)

        # Ajouter les nœuds
        workflow.add_node("validate", self.validate_input)
        workflow.add_node("generate", self.generate_pdf)
        workflow.add_node("save", self.save_to_db)

        # Définir le flux
        workflow.set_entry_point("validate")
        workflow.add_edge("validate", "generate")
        workflow.add_edge("generate", "save")
        workflow.add_edge("save", END)

        return workflow.compile()

    async def execute(self, state: AdminAgentState) -> AdminAgentState:
        """
        Exécute le workflow complet de l'agent.

        Args:
            state: État initial

        Returns:
            État final après exécution
        """
        try:
            self.logger.info(f"Démarrage agent {self.__class__.__name__} pour user {state['user_id']}")

            # Construire et exécuter le graph
            graph = self.build_graph()
            result = await graph.ainvoke(state)

            if result.get("error"):
                self.logger.error(f"Agent terminé avec erreur: {result['error']}")
            else:
                self.logger.info(f"Agent terminé avec succès. PDF: {result.get('pdf_path')}")

            return result

        except Exception as e:
            self.logger.error(f"Erreur critique dans l'agent: {e}", exc_info=True)
            state["error"] = f"Erreur critique: {str(e)}"
            return state


def get_company_info() -> dict[str, str]:
    """
    Récupère les informations de l'entreprise depuis la configuration.

    Returns:
        Dictionnaire avec les infos de l'entreprise
    """
    settings = get_settings()
    return {
        "name": settings.company_name,
        "address": settings.company_address,
        "siret": settings.company_siret,
        "tva": settings.company_tva_number,
    }
