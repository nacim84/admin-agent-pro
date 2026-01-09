"""Script d'initialisation de la base de données."""

import asyncio
import logging
from execution.tools.db_manager import DatabaseManager

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


async def main():
    """Initialise les tables de la base de données."""
    logger.info("🚀 Initialisation de la base de données...")

    db = DatabaseManager()

    try:
        await db.init_db()
        logger.info("✅ Base de données initialisée avec succès !")
        logger.info("📋 Tables créées: documents")

    except Exception as e:
        logger.error(f"❌ Erreur lors de l'initialisation: {e}")
        raise

    finally:
        await db.close()


if __name__ == "__main__":
    asyncio.run(main())
