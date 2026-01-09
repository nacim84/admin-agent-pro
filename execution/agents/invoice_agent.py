"""Agent spécialisé dans la génération de factures."""

from datetime import date, timedelta
from decimal import Decimal
from execution.agents.base_admin_agent import BaseAdminAgent, AdminAgentState, get_company_info
from execution.models.documents import Invoice, InvoiceItem
from execution.models.database import DocumentType


class InvoiceAgent(BaseAdminAgent):
    """Agent pour générer des factures conformes aux normes françaises."""

    async def validate_input(self, state: AdminAgentState) -> AdminAgentState:
        """
        Valide et enrichit les données de facture.

        Enrichissements automatiques:
        - Numéro de facture (si absent) : format YYYY-NNNN
        - Date de facturation (si absente) : aujourd'hui
        - Date d'échéance (si absente) : date + 30 jours
        - Conditions de paiement : défaut "Paiement à 30 jours"

        Args:
            state: État avec input_data contenant les données brutes

        Returns:
            État avec validated_data ou error
        """
        try:
            data = state["input_data"].copy()
            self.logger.info(f"Validation des données de facture pour user {state['user_id']}")

            # 1. Génère numéro de facture si absent
            if "invoice_number" not in data or not data["invoice_number"]:
                year = date.today().year
                data["invoice_number"] = await self.db.get_next_invoice_number(year)
                self.logger.info(f"Numéro de facture généré: {data['invoice_number']}")

            # 2. Date par défaut = aujourd'hui
            if "invoice_date" not in data or not data["invoice_date"]:
                data["invoice_date"] = date.today()

            # Convertir string en date si nécessaire
            if isinstance(data["invoice_date"], str):
                data["invoice_date"] = date.fromisoformat(data["invoice_date"])

            # 3. Échéance = date + 30 jours par défaut
            if "due_date" not in data or not data["due_date"]:
                data["due_date"] = data["invoice_date"] + timedelta(days=30)

            if isinstance(data["due_date"], str):
                data["due_date"] = date.fromisoformat(data["due_date"])

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

            # 6. Créer l'objet Invoice validé avec Pydantic
            invoice = Invoice(
                invoice_number=data["invoice_number"],
                invoice_date=data["invoice_date"],
                due_date=data["due_date"],
                client_name=data["client_name"],
                client_address=data["client_address"],
                client_siret=data.get("client_siret"),
                items=items,
                payment_conditions=data.get(
                    "payment_conditions", "Paiement à 30 jours"
                ),
                notes=data.get("notes"),
            )

            # 7. Convertir en dict pour stockage
            state["validated_data"] = invoice.model_dump(mode="json")

            self.logger.info(
                f"✅ Facture validée: {invoice.invoice_number} - "
                f"Total TTC: {float(invoice.total_ttc):.2f}€"
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
        Génère le PDF de la facture.

        Args:
            state: État avec validated_data

        Returns:
            État avec pdf_path ou error
        """
        if state.get("error"):
            return state

        try:
            self.logger.info("Génération du PDF de facture...")

            # Recréer l'objet Invoice depuis validated_data
            invoice = Invoice(**state["validated_data"])

            # Récupérer les infos de l'entreprise
            company_info = get_company_info()

            # Générer le PDF
            pdf_path = self.pdf_gen.generate_invoice_pdf(invoice, company_info)

            state["pdf_path"] = pdf_path
            self.logger.info(f"✅ PDF généré: {pdf_path}")

            return state

        except Exception as e:
            state["error"] = f"Erreur génération PDF: {str(e)}"
            self.logger.error(f"PDF generation failed: {e}", exc_info=True)
            return state

    async def save_to_db(self, state: AdminAgentState) -> AdminAgentState:
        """
        Sauvegarde la facture en base de données.

        Args:
            state: État avec validated_data et pdf_path

        Returns:
            État avec db_record_id ou error
        """
        if state.get("error"):
            return state

        try:
            self.logger.info("Sauvegarde de la facture en base...")

            invoice = Invoice(**state["validated_data"])

            doc = await self.db.save_document(
                doc_type=DocumentType.INVOICE,
                doc_number=invoice.invoice_number,
                data=state["validated_data"],
                pdf_path=str(state["pdf_path"]) if state["pdf_path"] else None,
                user_id=state["user_id"],
            )

            state["db_record_id"] = doc.id
            self.logger.info(f"✅ Facture sauvegardée en base (ID: {doc.id})")

            return state

        except Exception as e:
            state["error"] = f"Erreur sauvegarde DB: {str(e)}"
            self.logger.error(f"DB save failed: {e}", exc_info=True)
            return state
