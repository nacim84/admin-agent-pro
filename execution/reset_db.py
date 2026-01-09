import asyncio
from execution.tools.db_manager import DatabaseManager
from execution.seed_db import seed

async def main():
    db = DatabaseManager()
    print("🗑️ Suppression de toutes les tables...")
    await db.drop_all()
    print("🏗️ Initialisation du nouveau schéma...")
    await db.init_db()
    await db.close()
    
    print("🌱 Insertion des données de test...")
    await seed()
    print("✨ Base de données réinitialisée !")

if __name__ == "__main__":
    asyncio.run(main())
