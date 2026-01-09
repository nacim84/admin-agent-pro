"""Bot Telegram pour l'agent administratif."""

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from execution.agents.invoice_agent import InvoiceAgent
from execution.agents.base_admin_agent import AdminAgentState
from execution.tools.telegram_helpers import (
    send_document_with_preview,
    parse_command_args,
    format_error_message,
    format_success_message,
    build_help_text,
    validate_user_access,
    send_typing_action,
)
from execution.tools.db_manager import DatabaseManager
from execution.core.config import get_settings
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class AdminBot:
    """Bot Telegram pour automatisation administrative."""

    def __init__(self):
        """Initialise le bot avec la configuration."""
        self.settings = get_settings()
        self.db = DatabaseManager()

        # Créer l'application
        self.app = Application.builder().token(self.settings.telegram_bot_token).build()

        # Enregistrer les commandes
        self._register_handlers()

        logger.info("✅ Bot initialisé")

    def _register_handlers(self) -> None:
        """Enregistre tous les handlers de commandes."""
        # Commandes générales
        self.app.add_handler(CommandHandler("start", self.cmd_start))
        self.app.add_handler(CommandHandler("help", self.cmd_help))
        self.app.add_handler(CommandHandler("stats", self.cmd_stats))

        # Commandes de génération de documents
        self.app.add_handler(CommandHandler("facture", self.cmd_invoice))
        self.app.add_handler(CommandHandler("devis", self.cmd_quote))
        self.app.add_handler(CommandHandler("frais_km", self.cmd_mileage))
        self.app.add_handler(CommandHandler("quittance", self.cmd_rent_receipt))
        self.app.add_handler(CommandHandler("charges", self.cmd_rental_charges))

        # Handler pour les messages non reconnus
        self.app.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_unknown)
        )

        logger.info("✅ Handlers enregistrés")

    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Commande /start - Message de bienvenue."""
        user_id = update.effective_user.id

        if not validate_user_access(user_id, self.settings.telegram_admin_users):
            await update.message.reply_text(
                "❌ **Accès non autorisé**\n\n"
                "Vous n'êtes pas autorisé à utiliser ce bot.",
                parse_mode="Markdown",
            )
            return

        welcome_text = f"""
👋 **Bienvenue sur Admin Agent Pro !**

Je suis votre assistant administratif automatisé.

Je peux générer pour vous:
• 📄 Factures
• 📝 Devis
• 🚗 Notes de frais kilométriques
• 🏠 Quittances de loyer
• 💰 Décomptes de charges

Utilisez `/help` pour voir toutes les commandes disponibles.

**Configuration actuelle:**
Entreprise: {self.settings.company_name}
SIRET: {self.settings.company_siret}
"""
        await update.message.reply_text(welcome_text, parse_mode="Markdown")

    async def cmd_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Commande /help - Affiche l'aide."""
        user_id = update.effective_user.id

        if not validate_user_access(user_id, self.settings.telegram_admin_users):
            await update.message.reply_text("❌ Accès non autorisé.")
            return

        help_text = build_help_text()
        await update.message.reply_text(help_text, parse_mode="Markdown")

    async def cmd_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Commande /stats - Affiche les statistiques de l'utilisateur."""
        user_id = update.effective_user.id

        if not validate_user_access(user_id, self.settings.telegram_admin_users):
            await update.message.reply_text("❌ Accès non autorisé.")
            return

        await send_typing_action(update, context)

        try:
            counts = await self.db.get_document_count_by_type(user_id)

            if not counts:
                await update.message.reply_text(
                    "📊 Vous n'avez encore généré aucun document."
                )
                return

            stats_text = "📊 **Vos Statistiques**\n\n"
            emoji_map = {
                "invoice": "📄",
                "quote": "📝",
                "mileage": "🚗",
                "rent_receipt": "🏠",
                "rental_charges": "💰",
            }

            for doc_type, count in counts.items():
                emoji = emoji_map.get(doc_type, "📋")
                stats_text += f"{emoji} {doc_type.replace('_', ' ').title()}: **{count}**\n"

            total = sum(counts.values())
            stats_text += f"\n**Total: {total} documents**"

            await update.message.reply_text(stats_text, parse_mode="Markdown")

        except Exception as e:
            logger.error(f"Erreur stats: {e}", exc_info=True)
            await update.message.reply_text("❌ Erreur lors de la récupération des statistiques")

    async def cmd_invoice(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Commande /facture - Génère une facture."""
        user_id = update.effective_user.id

        if not validate_user_access(user_id, self.settings.telegram_admin_users):
            await update.message.reply_text("❌ Accès non autorisé.")
            return

        # Parser les arguments
        args = parse_command_args(update.message.text)

        if not args.get("client") or not args.get("montant"):
            await update.message.reply_text(
                "❌ **Arguments manquants**\n\n"
                "Usage:\n"
                "`/facture client=\"Nom Client\" montant=1500 description=\"Service\"`\n\n"
                "Arguments requis:\n"
                "• `client` - Nom du client\n"
                "• `montant` - Montant HT\n\n"
                "Arguments optionnels:\n"
                "• `description` - Description de la prestation\n"
                "• `adresse` - Adresse du client\n"
                "• `siret` - SIRET du client",
                parse_mode="Markdown",
            )
            return

        await send_typing_action(update, context)
        await update.message.reply_text("⏳ Génération de la facture en cours...")

        try:
            # Préparer l'état initial
            state: AdminAgentState = {
                "user_id": user_id,
                "request_type": "invoice",
                "input_data": {
                    "client_name": args["client"],
                    "client_address": args.get("adresse", "Adresse non fournie"),
                    "client_siret": args.get("siret"),
                    "items": [
                        {
                            "description": args.get("description", "Prestation"),
                            "quantity": 1,
                            "unit_price": float(args["montant"]),
                            "vat_rate": 0.20,
                        }
                    ],
                    "payment_conditions": args.get("conditions", "Paiement à 30 jours"),
                    "notes": args.get("notes"),
                },
                "validated_data": None,
                "pdf_path": None,
                "db_record_id": None,
                "error": None,
            }

            # Exécuter l'agent
            agent = InvoiceAgent()
            result = await agent.execute(state)

            # Gérer le résultat
            if result.get("error"):
                error_msg = format_error_message(result["error"])
                await update.message.reply_text(error_msg, parse_mode="Markdown")
                return

            # Envoyer le PDF
            from execution.models.documents import Invoice

            invoice = Invoice(**result["validated_data"])
            success_msg = format_success_message(
                "facture",
                invoice.invoice_number,
                f"{float(invoice.total_ttc):.2f}€",
            )

            await send_document_with_preview(
                update, context, result["pdf_path"], success_msg
            )

        except Exception as e:
            logger.error(f"Erreur facture: {e}", exc_info=True)
            await update.message.reply_text(
                f"❌ Erreur lors de la génération: {str(e)}"
            )

    async def cmd_quote(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Commande /devis - Génère un devis."""
        user_id = update.effective_user.id

        if not validate_user_access(user_id, self.settings.telegram_admin_users):
            await update.message.reply_text("❌ Accès non autorisé.")
            return

        await update.message.reply_text(
            "🚧 La génération de devis sera bientôt disponible !\n\n"
            "L'agent pour les devis est en cours d'implémentation."
        )

    async def cmd_mileage(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Commande /frais_km - Génère une note de frais kilométriques."""
        user_id = update.effective_user.id

        if not validate_user_access(user_id, self.settings.telegram_admin_users):
            await update.message.reply_text("❌ Accès non autorisé.")
            return

        await update.message.reply_text(
            "🚧 Les notes de frais kilométriques seront bientôt disponibles !\n\n"
            "L'agent est en cours d'implémentation."
        )

    async def cmd_rent_receipt(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Commande /quittance - Génère une quittance de loyer."""
        user_id = update.effective_user.id

        if not validate_user_access(user_id, self.settings.telegram_admin_users):
            await update.message.reply_text("❌ Accès non autorisé.")
            return

        await update.message.reply_text(
            "🚧 Les quittances de loyer seront bientôt disponibles !\n\n"
            "L'agent est en cours d'implémentation."
        )

    async def cmd_rental_charges(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Commande /charges - Génère un décompte de charges."""
        user_id = update.effective_user.id

        if not validate_user_access(user_id, self.settings.telegram_admin_users):
            await update.message.reply_text("❌ Accès non autorisé.")
            return

        await update.message.reply_text(
            "🚧 Les décomptes de charges seront bientôt disponibles !\n\n"
            "L'agent est en cours d'implémentation."
        )

    async def handle_unknown(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Gère les messages non reconnus."""
        await update.message.reply_text(
            "❓ Je n'ai pas compris votre message.\n\n"
            "Utilisez `/help` pour voir les commandes disponibles."
        )

    def run(self) -> None:
        """Lance le bot en mode polling."""
        logger.info("🤖 Démarrage du bot Telegram...")
        logger.info(f"📱 Bot configuré pour: {self.settings.company_name}")

        try:
            self.app.run_polling(allowed_updates=Update.ALL_TYPES)
        except KeyboardInterrupt:
            logger.info("👋 Arrêt du bot...")
        except Exception as e:
            logger.error(f"❌ Erreur fatale: {e}", exc_info=True)
            raise


if __name__ == "__main__":
    bot = AdminBot()
    bot.run()
