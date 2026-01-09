"""Agent spécialisé dans la génération de devis."""

from datetime import date, timedelta
from decimal import Decimal
from execution.agents.base_admin_agent import BaseAdminAgent, AdminAgentState, get_company_info
from execution.models.documents import Quote, InvoiceItem
from execution.models.database import DocumentType
from execution.prompts.quote_prompts import QUOTE_EXTRACTION_SYSTEM_PROMPT


class QuoteAgent(BaseAdminAgent):
    """Agent pour générer des devis conformes."""

    def get_system_prompt(self) -> str:
        return QUOTE_EXTRACTION_SYSTEM_PROMPT

    async def validate_input(self, state: AdminAgentState) -> AdminAgentState:
        """
        Valide et enrichit les données de devis.

        Enrichissements automatiques:
        - Numéro de devis (si absent) : format DEV-YYYY-NNNN
        - Date de devis (si absente) : aujourd'hui
        - Validité (si absente) : 30 jours
        
        Args:
            state: État avec input_data contenant les données brutes

        Returns:
            État avec validated_data ou error
        """
        try:
            data = state["input_data"].copy()
            self.logger.info(f"Validation des données de devis pour user {state['user_id']}")

            # 1. Génère numéro de devis si absent
            if "quote_number" not in data or not data["quote_number"]:
                year = date.today().year
                data["quote_number"] = await self.db.get_next_quote_number(year)
                self.logger.info(f"Numéro de devis généré: {data['quote_number']}")

            # 2. Date par défaut = aujourd'hui
            if "quote_date" not in data or not data["quote_date"]:
                data["quote_date"] = date.today()

            # Convertir string en date si nécessaire
            if isinstance(data["quote_date"], str):
                data["quote_date"] = date.fromisoformat(data["quote_date"])

            # 3. Validité par défaut = 30 jours
            if "validity_days" not in data or not data["validity_days"]:
                data["validity_days"] = 30
            else:
                data["validity_days"] = int(data["validity_days"])

            # 4. Vérifier les informations client
            if not data.get("client_name"):
                raise ValueError("Le nom du client est requis")

            if not data.get("client_address"):
                raise ValueError("L'adresse du client est requise")

            # 5. Construire les items
            if "items" not in data or not data["items"]:
                raise ValueError("Au moins un article est requis")

            items = []
            for item_data in data["items"]:
                items.append(
                    InvoiceItem(
                        description=item_data["description"],
                        quantity=Decimal(str(item_data.get("quantity", 1))),
                        unit_price=Decimal(str(item_data["unit_price"])),
                        vat_rate=Decimal(str(item_data.get("vat_rate", "0.20"))),
                    )
                )

            # 6. Créer l'objet Quote validé avec Pydantic
            quote = Quote(
                quote_number=data["quote_number"],
                quote_date=data["quote_date"],
                validity_days=data["validity_days"],
                client_name=data["client_name"],
                client_address=data["client_address"],
                client_siret=data.get("client_siret"),
                items=items,
                notes=data.get("notes"),
            )

            # 7. Convertir en dict pour stockage
            state["validated_data"] = quote.model_dump(mode="json")

            self.logger.info(
                f"✅ Devis validé: {quote.quote_number} - "
                f"Total TTC: {float(quote.total_ttc):.2f}€"
            )
            return state

        except ValueError as e:
            state["error"] = f"Erreur de validation: {str(e)}"
            self.logger.error(f"Validation failed: {e}")
            return state

        except Exception as e:
            state["error"] = f"Erreur inattendue lors de la validation: {str(e)}"
            self.logger.error(f"Unexpected error: {e}", exc_info=True)
            return state

    async def generate_pdf(self, state: AdminAgentState) -> AdminAgentState:
        """
        Génère le PDF du devis.

        Args:
            state: État avec validated_data

        Returns:
            État avec pdf_path ou error
        """
        if state.get("error"):
            return state

        try:
            self.logger.info("Génération du PDF de devis...")

            # Recréer l'objet Quote depuis validated_data
            quote = Quote(**state["validated_data"])

            # Récupérer les infos de l'entreprise
            company_info = get_company_info()

            # Générer le PDF
            pdf_path = self.pdf_gen.generate_quote_pdf(quote, company_info)

            state["pdf_path"] = pdf_path
            self.logger.info(f"✅ PDF généré: {pdf_path}")

            return state

        except Exception as e:
            state["error"] = f"Erreur génération PDF: {str(e)}"
            self.logger.error(f"PDF generation failed: {e}", exc_info=True)
            return state

    async def save_to_db(self, state: AdminAgentState) -> AdminAgentState:
        """
        Sauvegarde le devis en base de données.

        Args:
            state: État avec validated_data et pdf_path

        Returns:
            État avec db_record_id ou error
        """
        if state.get("error"):
            return state

        try:
            self.logger.info("Sauvegarde du devis en base...")

            quote = Quote(**state["validated_data"])

            doc = await self.db.save_document(
                doc_type=DocumentType.QUOTE,
                doc_number=quote.quote_number,
                data=state["validated_data"],
                pdf_path=str(state["pdf_path"]) if state["pdf_path"] else None,
                user_id=state["user_id"],
            )

            state["db_record_id"] = doc.id
            self.logger.info(f"✅ Devis sauvegardé en base (ID: {doc.id})")

            return state

        except Exception as e:
            state["error"] = f"Erreur sauvegarde DB: {str(e)}"
            self.logger.error(f"DB save failed: {e}", exc_info=True)
            return state
