"""Agent spécialisé dans la gestion des frais kilométriques."""

from datetime import date
from decimal import Decimal
from execution.agents.base_admin_agent import BaseAdminAgent, AdminAgentState, get_company_info
from execution.models.documents import MileageRecord
from execution.models.database import DocumentType
from execution.prompts.mileage_prompts import MILEAGE_EXTRACTION_SYSTEM_PROMPT


class MileageAgent(BaseAdminAgent):
    """Agent pour générer des notes de frais kilométriques."""

    def get_system_prompt(self) -> str:
        return MILEAGE_EXTRACTION_SYSTEM_PROMPT

    async def validate_input(self, state: AdminAgentState) -> AdminAgentState:
        """
        Valide et enrichit les données de frais kilométriques.
        
        Args:
            state: État avec input_data contenant une liste de trajets dans "trips"

        Returns:
            État avec validated_data contenant la liste des MileageRecord validés et le numéro de document
        """
        try:
            data = state["input_data"].copy()
            self.logger.info(f"Validation des frais kilométriques pour user {state['user_id']}")

            # Vérifier si on a une liste de trajets
            raw_trips = data.get("trips", [])
            if not raw_trips:
                # Si input_data est plat (un seul trajet), on le met dans une liste
                if "distance_km" in data:
                    raw_trips = [data]
                else:
                    raise ValueError("Aucun trajet trouvé dans la demande")

            validated_records = []
            
            for trip in raw_trips:
                # 1. Date par défaut = aujourd'hui
                if "travel_date" not in trip or not trip["travel_date"]:
                    trip["travel_date"] = date.today()
                
                if isinstance(trip["travel_date"], str):
                    trip["travel_date"] = date.fromisoformat(trip["travel_date"])

                # 2. Type de véhicule par défaut
                if "vehicle_type" not in trip or not trip["vehicle_type"]:
                    trip["vehicle_type"] = "voiture"

                # 3. Puissance fiscale obligatoire pour voiture/moto
                if trip["vehicle_type"] in ["voiture", "moto"]:
                    if "fiscal_power" not in trip or not trip["fiscal_power"]:
                         # Tenter d'inférer ou erreur
                         raise ValueError(f"Puissance fiscale manquante pour {trip['vehicle_type']}")
                    trip["fiscal_power"] = int(trip["fiscal_power"])
                else:
                    # Scooter ou autre : on met une valeur par défaut valide (ex: 1) pour satisfaire le modèle
                    # car le modèle Pydantic exige fiscal_power > 0
                    if "fiscal_power" not in trip:
                        trip["fiscal_power"] = 1

                # 4. Créer l'objet MileageRecord
                record = MileageRecord(
                    travel_date=trip["travel_date"],
                    start_location=trip["start_location"],
                    end_location=trip["end_location"],
                    distance_km=Decimal(str(trip["distance_km"])),
                    purpose=trip["purpose"],
                    vehicle_type=trip["vehicle_type"],
                    fiscal_power=trip["fiscal_power"]
                )
                validated_records.append(record)

            if not validated_records:
                raise ValueError("Aucun trajet valide identifié")

            # 5. Générer le numéro de document pour le rapport
            year = date.today().year
            doc_number = await self.db.get_next_mileage_number(year)

            # 6. Préparer les données validées pour le state
            # On stocke les records sérialisés et le numéro de document
            state["validated_data"] = {
                "document_number": doc_number,
                "records": [rec.model_dump(mode="json") for rec in validated_records],
                "total_amount": float(sum(rec.total_amount for rec in validated_records))
            }

            self.logger.info(
                f"✅ Note de frais validée: {doc_number} - "
                f"{len(validated_records)} trajets - Total: {state['validated_data']['total_amount']:.2f}€"
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
        Génère le PDF de la note de frais.

        Args:
            state: État avec validated_data

        Returns:
            État avec pdf_path ou error
        """
        if state.get("error"):
            return state

        try:
            self.logger.info("Génération du PDF de frais kilométriques...")

            data = state["validated_data"]
            records = [MileageRecord(**rec) for rec in data["records"]]
            doc_number = data["document_number"]

            # Récupérer les infos de l'entreprise
            company_info = get_company_info()

            # Générer le PDF
            # Note: generate_mileage_pdf dans pdf_generator ne prend pas encore doc_number en paramètre explicite
            # mais génère un filename basé sur timestamp.
            # On pourrait améliorer cela, mais pour l'instant on utilise la méthode existante.
            pdf_path = self.pdf_gen.generate_mileage_pdf(
                records=records, 
                company_info=company_info,
                period_label=f"Note de Frais #{doc_number}"
            )

            state["pdf_path"] = pdf_path
            self.logger.info(f"✅ PDF généré: {pdf_path}")

            return state

        except Exception as e:
            state["error"] = f"Erreur génération PDF: {str(e)}"
            self.logger.error(f"PDF generation failed: {e}", exc_info=True)
            return state

    async def save_to_db(self, state: AdminAgentState) -> AdminAgentState:
        """
        Sauvegarde la note de frais en base de données.

        Args:
            state: État avec validated_data et pdf_path

        Returns:
            État avec db_record_id ou error
        """
        if state.get("error"):
            return state

        try:
            self.logger.info("Sauvegarde de la note de frais en base...")

            data = state["validated_data"]
            doc_number = data["document_number"]

            doc = await self.db.save_document(
                doc_type=DocumentType.MILEAGE,
                doc_number=doc_number,
                data=data, # On sauvegarde tout le json (records + total)
                pdf_path=str(state["pdf_path"]) if state["pdf_path"] else None,
                user_id=state["user_id"],
            )

            state["db_record_id"] = doc.id
            self.logger.info(f"✅ Note de frais sauvegardée en base (ID: {doc.id})")

            return state

        except Exception as e:
            state["error"] = f"Erreur sauvegarde DB: {str(e)}"
            self.logger.error(f"DB save failed: {e}", exc_info=True)
            return state
