"""Agent spécialisé dans le décompte de charges locatives."""

from datetime import date
from decimal import Decimal
from execution.agents.base_admin_agent import BaseAdminAgent, AdminAgentState, get_company_info
from execution.models.documents import RentalCharges, ChargeItem
from execution.models.database import DocumentType
from execution.prompts.rental_charges_prompts import RENTAL_CHARGES_EXTRACTION_SYSTEM_PROMPT


class RentalChargesAgent(BaseAdminAgent):
    """Agent pour générer des décomptes de charges locatives."""

    def get_system_prompt(self) -> str:
        return RENTAL_CHARGES_EXTRACTION_SYSTEM_PROMPT

    async def validate_input(self, state: AdminAgentState) -> AdminAgentState:
        """
        Valide et enrichit les données de décompte de charges.

        Enrichissements automatiques:
        - Dates (validation format)
        - Provisions (défaut 0)
        - Numéro de document
        
        Args:
            state: État avec input_data contenant les données brutes

        Returns:
            État avec validated_data ou error
        """
        try:
            data = state["input_data"].copy()
            self.logger.info(f"Validation charges locatives pour user {state['user_id']}")

            # 1. Dates
            if "period_start" not in data or not data["period_start"]:
                raise ValueError("Date de début requise")
            if "period_end" not in data or not data["period_end"]:
                raise ValueError("Date de fin requise")

            if isinstance(data["period_start"], str):
                data["period_start"] = date.fromisoformat(data["period_start"])
            if isinstance(data["period_end"], str):
                data["period_end"] = date.fromisoformat(data["period_end"])

            # 2. Infos de base
            if not data.get("tenant_name"):
                raise ValueError("Le nom du locataire est requis")
            
            if not data.get("property_address"):
                raise ValueError("L'adresse du bien est requise")

            # 3. Charges
            if "charges" not in data or not data["charges"]:
                raise ValueError("La liste des charges est requise")

            charge_items = []
            for item in data["charges"]:
                charge_items.append(
                    ChargeItem(
                        label=item["label"],
                        amount=Decimal(str(item["amount"]))
                    )
                )

            # 4. Provisions
            if "provisions_amount" not in data:
                data["provisions_amount"] = 0

            # 5. Créer l'objet validé
            charges_doc = RentalCharges(
                period_start=data["period_start"],
                period_end=data["period_end"],
                tenant_name=data["tenant_name"],
                property_address=data["property_address"],
                charges=charge_items,
                provisions_amount=Decimal(str(data["provisions_amount"]))
            )

            # 6. Générer numéro de document
            year = data["period_end"].year
            doc_number = await self.db.get_next_rental_charges_number(year)

            # 7. Convertir en dict pour stockage (avec numéro)
            validated_data = charges_doc.model_dump(mode="json")
            validated_data["document_number"] = doc_number
            state["validated_data"] = validated_data

            self.logger.info(
                f"✅ Décompte validé: {doc_number} - "
                f"Régul: {float(charges_doc.regularization_amount):.2f}€"
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
        """Génère le PDF."""
        if state.get("error"):
            return state

        try:
            self.logger.info("Génération du PDF de charges...")

            # Pour le PDF generator, on a besoin de l'objet RentalCharges
            # Le doc_number est dans validated_data mais pas dans le modèle RentalCharges (ce n'est pas un champ du modèle pour l'instant)
            # Mais generate_rental_charges_pdf n'utilise pas le numéro dans le contenu visible (juste nom de fichier)
            
            charges = RentalCharges(**state["validated_data"])
            company_info = get_company_info()

            pdf_path = self.pdf_gen.generate_rental_charges_pdf(charges, company_info)

            state["pdf_path"] = pdf_path
            self.logger.info(f"✅ PDF généré: {pdf_path}")

            return state

        except Exception as e:
            state["error"] = f"Erreur génération PDF: {str(e)}"
            self.logger.error(f"PDF generation failed: {e}", exc_info=True)
            return state

    async def save_to_db(self, state: AdminAgentState) -> AdminAgentState:
        """Sauvegarde en base."""
        if state.get("error"):
            return state

        try:
            self.logger.info("Sauvegarde du décompte en base...")

            doc_number = state["validated_data"]["document_number"]

            doc = await self.db.save_document(
                doc_type=DocumentType.RENTAL_CHARGES,
                doc_number=doc_number,
                data=state["validated_data"],
                pdf_path=str(state["pdf_path"]) if state["pdf_path"] else None,
                user_id=state["user_id"],
            )

            state["db_record_id"] = doc.id
            self.logger.info(f"✅ Décompte sauvegardé en base (ID: {doc.id})")

            return state

        except Exception as e:
            state["error"] = f"Erreur sauvegarde DB: {str(e)}"
            self.logger.error(f"DB save failed: {e}", exc_info=True)
            return state
