"""Script pour insérer des données de test (seed) dans la base de données."""

import asyncio
import logging
from decimal import Decimal
from execution.tools.db_manager import DatabaseManager
from execution.models.database import DataAdministration, KilometresParcourus

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

async def seed():
    """Insère des données de test."""
    logger.info("🌱 Seeding de la base de données...")
    
    db = DatabaseManager()
    
    try:
        async with db.async_session_maker() as session:
            # 2. Données pour Facturation Client (Exemple: Apple, 2026)
            facture_apple = DataAdministration(
                id_data_administration="facturation_client_apple_2026",
                annee=2026,
                nom_client="Apple",
                adresse_client="1 Apple Park Way, Cupertino, CA 95014, USA",
                email_client="billing@apple.com",
                produit="Développement Python & IA",
                prix_unitaire=Decimal("1500.00"),
                tva="20%",
                paiement="Virement bancaire sous 30 jours",
                email_entreprise="finance@masasu.fr",
                nom_entreprise="Ma SASU",
                adresse_entreprise="1 Rue de l'Example, 75001 Paris",
                devise="EUR"
            )

            facture_laito = DataAdministration(
                id_data_administration="facturation_client_laito_2026",
                annee=2026,
                nom_client="Laito",
                adresse_client="42 Avenue du Lait, 75010 Paris",
                email_client="compta@laito.fr",
                produit="Livraison de Lait",
                prix_unitaire=Decimal("20.00"),
                tva="20%",
                paiement="Virement",
                email_entreprise="finance@masasu.fr",
                nom_entreprise="Ma SASU",
                adresse_entreprise="1 Rue de l'Example, 75001 Paris",
                devise="EUR"
            )
            
            # 3. Données pour Quittance de Loyer (2026)
            quittance_2026 = DataAdministration(
                id_data_administration="quittance_loyer_1",
                annee=2026,
                nom_professionnel="Nacim Rabia",
                adresse_professionnel="15 Rue de la Paix, 75002 Paris",
                nom_entreprise="Locataire Dupont",
                adresse_entreprise="10 Rue du Commerce, 69002 Lyon",
                montant_loyer=Decimal("850.00"),
                email_professionnel_1="nacim@example.com",
                email_entreprise="contact@location.fr",
                devise="EUR"
            )
            
            # 4. Données pour Charges Locatives (2025)
            charges_2025 = DataAdministration(
                id_data_administration="charge_locative_1",
                annee=2025,
                nom_entreprise="Locataire Dupont",
                charges={
                    "eau": 150,
                    "electricite": 300,
                    "chauffage": 450,
                    "entretien": 100
                },
                email_entreprise="contact@location.fr"
            )
            
            # 5. Données pour Frais Kilométriques (2026)
            frais_km_2026 = DataAdministration(
                id_data_administration="frai_kilometrique_1",
                annee=2026,
                nom_client_mission="Alteca",
                adresse_client_mission="45 Quai Charles de Gaulle, 69006 Lyon",
                trajet_client_mission=Decimal("460.00"),
                puissance_fiscal=5,
                email_entreprise="contact@masasu.fr"
            )
            
            # 6. Suivi des kilomètres (Mock)
            km_suivi = KilometresParcourus(
                mois=1,
                annee=2026,
                total_kilometres_parcourus=Decimal("1250.0")
            )
            
            # Ajouter tout à la session
            session.add_all([
                facture_apple, 
                facture_laito,
                quittance_2026, 
                charges_2025, 
                frais_km_2026, 
                km_suivi
            ])
            
            await session.commit()
            logger.info("✅ Données de test insérées avec succès !")

    except Exception as e:
        logger.error(f"❌ Erreur lors du seeding: {e}")
        raise
    finally:
        await db.close()

if __name__ == "__main__":
    asyncio.run(seed())