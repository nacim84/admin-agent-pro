"""Script de lancement du bot Telegram Admin Agent Pro."""

import sys
from pathlib import Path

# Ajouter le répertoire racine au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent))

from execution.telegram_bot import AdminBot


if __name__ == "__main__":
    print("=" * 50)
    print("🤖 Admin Agent Pro - Bot Telegram")
    print("=" * 50)
    print()

    # Initialiser la base de données
    import asyncio
    from execution.init_db import main as init_db_main
    
    print("🔄 Vérification de la base de données...")
    try:
        asyncio.run(init_db_main())
    except Exception as e:
        print(f"❌ Erreur critique lors de l'initialisation de la DB: {e}")
        sys.exit(1)

    bot = AdminBot()
    bot.run()
