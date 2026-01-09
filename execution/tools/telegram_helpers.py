"""Fonctions utilitaires pour l'interaction Telegram."""

from telegram import Update
from telegram.ext import ContextTypes
from pathlib import Path
import re
import logging

logger = logging.getLogger(__name__)


async def send_document_with_preview(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    pdf_path: Path,
    caption: str,
) -> str | None:
    """
    Envoie un document PDF à l'utilisateur via Telegram.

    Args:
        update: Objet Update de Telegram
        context: Contexte Telegram
        pdf_path: Chemin vers le fichier PDF
        caption: Légende du message

    Returns:
        file_id du document envoyé, ou None en cas d'erreur
    """
    try:
        with open(pdf_path, "rb") as pdf_file:
            message = await update.message.reply_document(
                document=pdf_file,
                filename=pdf_path.name,
                caption=caption,
            )
            logger.info(f"Document envoyé: {pdf_path.name}")
            return message.document.file_id if message.document else None

    except FileNotFoundError:
        logger.error(f"Fichier PDF introuvable: {pdf_path}")
        await update.message.reply_text(f"❌ Erreur: fichier {pdf_path.name} introuvable")
        return None

    except Exception as e:
        logger.error(f"Erreur lors de l'envoi du document: {e}", exc_info=True)
        await update.message.reply_text("❌ Erreur lors de l'envoi du document")
        return None


def parse_command_args(message_text: str) -> dict[str, str]:
    """
    Parse les arguments d'une commande Telegram.

    Format supportés:
    - clé=valeur
    - clé="valeur avec espaces"
    - clé='valeur avec espaces'

    Exemples:
    >>> parse_command_args('/facture client="ACME Corp" montant=1500')
    {'client': 'ACME Corp', 'montant': '1500'}

    >>> parse_command_args("/devis client='ClientXYZ' montant=3000 description='Audit SEO'")
    {'client': 'ClientXYZ', 'montant': '3000', 'description': 'Audit SEO'}

    Args:
        message_text: Texte complet du message (avec la commande)

    Returns:
        Dictionnaire des arguments parsés
    """
    # Enlever la commande (/facture, /devis, etc.)
    parts = message_text.split(maxsplit=1)
    if len(parts) < 2:
        return {}

    args_text = parts[1]

    # Regex pour matcher key=value, key="value avec espaces", key='value'
    pattern = r'(\w+)=(?:"([^"]*)"|\'([^\']*)\'|(\S+))'
    matches = re.findall(pattern, args_text)

    args = {}
    for match in matches:
        key = match[0]
        # La valeur peut être dans l'un des 3 groupes (guillemets doubles, simples, ou sans)
        value = match[1] or match[2] or match[3]
        args[key] = value

    logger.debug(f"Arguments parsés: {args}")
    return args


def format_error_message(error: str) -> str:
    """
    Formate un message d'erreur pour Telegram.

    Args:
        error: Message d'erreur brut

    Returns:
        Message d'erreur formaté avec emoji
    """
    return f"❌ **Erreur**\n\n{error}"


def format_success_message(doc_type: str, doc_number: str, total: str | None = None) -> str:
    """
    Formate un message de succès pour Telegram.

    Args:
        doc_type: Type de document (facture, devis, etc.)
        doc_number: Numéro du document
        total: Montant total (optionnel)

    Returns:
        Message de succès formaté avec emojis
    """
    emoji_map = {
        "facture": "📄",
        "devis": "📝",
        "frais": "🚗",
        "quittance": "🏠",
    }

    emoji = emoji_map.get(doc_type, "📋")

    message = f"{emoji} **{doc_type.capitalize()} générée avec succès !**\n\n"
    message += f"Numéro: `{doc_number}`"

    if total:
        message += f"\nMontant: **{total}**"

    return message


def build_help_text() -> str:
    """
    Construit le texte d'aide complet avec toutes les commandes.

    Returns:
        Texte d'aide formaté en Markdown
    """
    return """
📋 **Commandes Disponibles**

**Facturation:**
• `/facture` - Générer une facture
• `/devis` - Générer un devis

**Frais:**
• `/frais_km` - Note de frais kilométriques

**Immobilier:**
• `/quittance` - Quittance de loyer
• `/charges` - Décompte de charges locatives

**Autres:**
• `/help` - Afficher cette aide
• `/stats` - Voir vos statistiques

**Exemples d'utilisation:**

*Facture:*
```
/facture client="ACME Corp" montant=1500 description="Développement site web" adresse="1 rue Example, 75001 Paris"
```

*Devis:*
```
/devis client="ClientXYZ" montant=3000 description="Audit SEO"
```

*Frais kilométriques:*
```
/frais_km date=2024-01-15 depart="Paris" arrivee="Lyon" km=465 motif="Rendez-vous client"
```

*Quittance de loyer:*
```
/quittance locataire="Dupont Jean" loyer=800 charges=150 mois=1 annee=2024
```

**Format des arguments:**
- Utilisez `clé=valeur` pour les arguments
- Mettez les valeurs avec espaces entre guillemets: `clé="ma valeur"`
- Les montants sont en euros (sans le symbole €)
"""


def validate_user_access(user_id: int, allowed_users: list[int]) -> bool:
    """
    Vérifie si un utilisateur est autorisé à utiliser le bot.

    Args:
        user_id: ID Telegram de l'utilisateur
        allowed_users: Liste des IDs autorisés

    Returns:
        True si l'utilisateur est autorisé
    """
    is_allowed = user_id in allowed_users
    if not is_allowed:
        logger.warning(f"Accès refusé pour user_id: {user_id}")
    return is_allowed


async def send_typing_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Envoie une action "en train de taper" pour indiquer que le bot travaille.

    Args:
        update: Objet Update de Telegram
        context: Contexte Telegram
    """
    try:
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id,
            action="typing"
        )
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi de l'action typing: {e}")
