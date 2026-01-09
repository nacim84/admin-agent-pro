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

    bot = AdminBot()
    bot.run()
