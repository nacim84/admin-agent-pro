"""Agent spécialisé dans la génération de quittances de loyer."""

from datetime import date
from decimal import Decimal
from execution.agents.base_admin_agent import BaseAdminAgent, AdminAgentState, get_company_info
from execution.models.documents import RentReceipt
from execution.models.database import DocumentType
from execution.prompts.rent_receipt_prompts import RENT_RECEIPT_EXTRACTION_SYSTEM_PROMPT


class RentReceiptAgent(BaseAdminAgent):
    """Agent pour générer des quittances de loyer."""

    def get_system_prompt(self) -> str:
        return RENT_RECEIPT_EXTRACTION_SYSTEM_PROMPT

    async def validate_input(self, state: AdminAgentState) -> AdminAgentState:
        """
        Valide et enrichit les données de quittance.

        Enrichissements automatiques:
        - Numéro de quittance (si absent) : format QUIT-YYYY-NNNN
        - Date de paiement (si absente) : aujourd'hui
        - Moyen de paiement par défaut : virement
        - Adresse bien loué (si absente) : copie adresse locataire
        
        Args:
            state: État avec input_data contenant les données brutes

        Returns:
            État avec validated_data ou error
        """
        try:
            data = state["input_data"].copy()
            self.logger.info(f"Validation quittance pour user {state['user_id']}")

            current_year = date.today().year

            # 1. Période
            if "period_year" not in data or not data["period_year"]:
                data["period_year"] = current_year
            
            if "period_month" not in data or not data["period_month"]:
                # Par défaut mois précédent si on est au début du mois, sinon mois courant
                # Simple approximation: mois courant
                data["period_month"] = date.today().month

            # 2. Générer numéro de quittance
            if "receipt_number" not in data or not data["receipt_number"]:
                data["receipt_number"] = await self.db.get_next_rent_receipt_number(data["period_year"])
                self.logger.info(f"Numéro de quittance généré: {data['receipt_number']}")

            # 3. Date paiement par défaut = aujourd'hui
            if "payment_date" not in data or not data["payment_date"]:
                data["payment_date"] = date.today()

            if isinstance(data["payment_date"], str):
                data["payment_date"] = date.fromisoformat(data["payment_date"])

            # 4. Adresses
            if not data.get("tenant_name"):
                raise ValueError("Le nom du locataire est requis")
            
            if not data.get("tenant_address"):
                raise ValueError("L'adresse du locataire est requise")
                
            if not data.get("property_address"):
                # Si pas d'adresse du bien, on suppose que c'est l'adresse du locataire
                data["property_address"] = data["tenant_address"]

            # 5. Montants
            if "rent_amount" not in data:
                raise ValueError("Le montant du loyer est requis")
                
            if "charges_amount" not in data:
                data["charges_amount"] = 0

            # 6. Créer l'objet RentReceipt validé
            receipt = RentReceipt(
                receipt_number=data["receipt_number"],
                period_month=int(data["period_month"]),
                period_year=int(data["period_year"]),
                tenant_name=data["tenant_name"],
                tenant_address=data["tenant_address"],
                property_address=data["property_address"],
                rent_amount=Decimal(str(data["rent_amount"])),
                charges_amount=Decimal(str(data["charges_amount"])),
                payment_date=data["payment_date"],
                payment_method=data.get("payment_method", "virement")
            )

            # 7. Convertir en dict pour stockage
            state["validated_data"] = receipt.model_dump(mode="json")

            self.logger.info(
                f"✅ Quittance validée: {receipt.receipt_number} - "
                f"Total: {float(receipt.total_amount):.2f}€"
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
        Génère le PDF de la quittance.

        Args:
            state: État avec validated_data

        Returns:
            État avec pdf_path ou error
        """
        if state.get("error"):
            return state

        try:
            self.logger.info("Génération du PDF de quittance...")

            receipt = RentReceipt(**state["validated_data"])
            company_info = get_company_info()

            pdf_path = self.pdf_gen.generate_rent_receipt_pdf(receipt, company_info)

            state["pdf_path"] = pdf_path
            self.logger.info(f"✅ PDF généré: {pdf_path}")

            return state

        except Exception as e:
            state["error"] = f"Erreur génération PDF: {str(e)}"
            self.logger.error(f"PDF generation failed: {e}", exc_info=True)
            return state

    async def save_to_db(self, state: AdminAgentState) -> AdminAgentState:
        """
        Sauvegarde la quittance en base.

        Args:
            state: État avec validated_data et pdf_path

        Returns:
            État avec db_record_id ou error
        """
        if state.get("error"):
            return state

        try:
            self.logger.info("Sauvegarde de la quittance en base...")

            receipt = RentReceipt(**state["validated_data"])

            doc = await self.db.save_document(
                doc_type=DocumentType.RENT_RECEIPT,
                doc_number=receipt.receipt_number,
                data=state["validated_data"],
                pdf_path=str(state["pdf_path"]) if state["pdf_path"] else None,
                user_id=state["user_id"],
            )

            state["db_record_id"] = doc.id
            self.logger.info(f"✅ Quittance sauvegardée en base (ID: {doc.id})")

            return state

        except Exception as e:
            state["error"] = f"Erreur sauvegarde DB: {str(e)}"
            self.logger.error(f"DB save failed: {e}", exc_info=True)
            return state
