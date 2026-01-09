# Admin Agent Pro

**Agent IA d'automatisation administrative pour entreprises unipersonnelles (SASU, EURL)**

Ce projet est un système intelligent basé sur LangGraph qui automatise la génération de documents administratifs (factures, devis, notes de frais, quittances de loyer, etc.) via une interface Telegram intuitive.

Construit sur une architecture à trois couches qui sépare le raisonnement probabiliste des LLM de l'exécution déterministe du code pour une fiabilité maximale.

## 🔊 LLM Provider : OpenRouter

Ce projet est maintenant configuré pour utiliser **OpenRouter** comme fournisseur de LLM. Cela offre :
- **Flexibilité** : Accès à une multitude de modèles (Gemini, Claude, GPT, Mistral, etc.) via une API unique.
- **Éviter les Quotas Google** : Ne plus être limité par les quotas spécifiques de Gemini.
- **Stabilité** : Utilisation de `langchain-openai` pour une compatibilité standard.

Pour utiliser OpenRouter :
1.  Ajoutez votre clé API dans `.env` :
    ```env
    OPENROUTER_API_KEY=sk-or-v1-votre-clé-api
    OPENROUTER_MODEL=google/gemini-2.0-flash-001  # ou un autre modèle supporté
    ```
2.  Votre bot utilisera automatiquement votre clé OpenRouter.

## 🧠 Mémoire Conversationnelle

Le bot intègre désormais une **mémoire conversationnelle** persistante grâce à une base de données (`chat_history`). Vos conversations sont enregistrées, permettant à l'assistant de comprendre le contexte des échanges et de répondre de manière plus pertinente.

## 🏗 L'Architecture à 3 Couches

Pour maximiser la fiabilité, ce système sépare les responsabilités :

1.  **Couche 1 : Directive (Le "Quoi")**
    *   Située dans `directives/`.
    *   Procédures Opérationnelles Standard (SOP) en Markdown.
    *   Définit les objectifs, les entrées/sorties et les outils à utiliser.

2.  **Couche 2 : Orchestration (La Décision)**
    *   C'est l'Agent (LLM via OpenRouter).
    *   Lit les directives, sélectionne les outils d'exécution, gère les erreurs et met à jour les instructions en fonction des apprentissages.
    *   **Utilise l'historique des conversations** pour une meilleure compréhension contextuelle.

3.  **Couche 3 : Exécution (Le "Comment")**
    *   Située dans `execution/`.
    *   Scripts Python déterministes.
    *   Gère les appels API, le traitement de données et les interactions système de manière fiable et testable.

## 📂 Structure du Projet

```text
.
├── directives/                  # Instructions et SOPs (Markdown)
│   ├── TECHNICAL_SPECS.md       # Spécifications techniques complètes
│   ├── mcp-servers-guide.md     # Guide d'implémentation MCP
│   └── workflow_*.md            # SOPs de workflows spécifiques
├── execution/                   # Scripts Python (Outils déterministes)
│   ├── core/                    # Configuration et utilitaires
│   ├── agents/                  # Implémentations d'agents
│   ├── workflows/               # Orchestration de workflows
│   ├── tools/                   # Outils réutilisables
│   └── mcp_servers/             # Serveurs MCP personnalisés
├── tests/                       # Tests unitaires et d'intégration
├── .tmp/                        # Fichiers intermédiaires (non commités)
├── .env                         # Variables d'environnement et clés API
├── pyproject.toml               # Configuration UV et dépendances
├── .python-version              # Version Python (3.12+)
├── AGENTS.md                    # Instructions système pour l'Agent
└── README.md                    # Documentation du projet
```

## ✨ Fonctionnalités

### Actuellement Disponibles
- 💬 **Interface Conversationnelle** - Interagissez naturellement avec le bot.
- 📄 **Génération de factures** (PDF) - Conformes aux normes françaises avec numérotation séquentielle.
- 🤖 **Interface Telegram** - Commandes textuelles simples et intuitives.
- 🗄️ **Historique PostgreSQL** - Conversations persistantes et accès aux documents.
- 📊 **Statistiques** - Suivi des documents générés.
- 🌐 **OpenRouter** : Flexibilité LLM et évite les quotas Google.
- 📝 **Génération de devis** (PDF)
- 🚗 **Notes de frais kilométriques** (Barème fiscal)
- 🏠 **Quittances de loyer**
- 💰 **Décomptes de charges locatives**

## 🚀 Principes de Fonctionnement

*   **Priorité aux Outils :** Toujours vérifier si un script existe dans `execution/` avant d'en créer un nouveau.
*   **Auto-réparation (Self-healing) :** En cas d'erreur, l'agent analyse la stack trace, corrige le script d'exécution et met à jour la directive correspondante pour éviter la récurrence du problème.
*   **Directives Vivantes :** Les documents dans `directives/` évoluent avec le temps pour inclure les limites d'API découvertes, les cas limites et les meilleures approches.
*   **Fiabilité Déterministe :** En déportant la complexité vers du code (Layer 3), on garantit un taux de réussite bien plus élevé qu'en laissant le LLM manipuler les données directement.

## 🛠 Installation et Usage

### Prérequis

- **Python 3.12+**
- **PostgreSQL 14+**
- **Bot Telegram** (créer via @BotFather sur Telegram)
- **UV** (gestionnaire de paquets Astral)

### Installation

#### 1. Installer UV (si pas déjà installé)

```bash
# Linux/Mac
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

#### 2. Cloner le projet

```bash
git clone https://github.com/votreusername/admin-agent-pro.git
cd admin-agent-pro
```

#### 3. Installer les dépendances

```bash
uv sync
```

#### 4. Configurer PostgreSQL

```bash
# Créer la base de données
createdb admin_agent

# Ou avec psql
psql -U postgres
CREATE DATABASE admin_agent;
\q
```

#### 5. Créer un bot Telegram

1.  Ouvrir Telegram et chercher **@BotFather**
2.  Envoyer `/newbot`
3.  Suivre les instructions
4.  Récupérer le token (format: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)
5.  Récupérer votre user_id Telegram (via @userinfobot)

#### 6. Configurer l'environnement

```bash
# Copier le fichier d'exemple
cp .env.example .env

# Éditer .env avec vos informations
nano .env  # ou code .env
```

Remplir les variables :
- `POSTGRES_*` : Informations de connexion PostgreSQL
- `TELEGRAM_BOT_TOKEN` : Token de votre bot
- **`OPENROUTER_API_KEY`** : Votre clé API OpenRouter (indispensable pour le LLM)
- **`OPENROUTER_MODEL`** : Modèle LLM à utiliser (ex: `google/gemini-2.0-flash-001`, `openai/gpt-4o-mini`)
- `TELEGRAM_ADMIN_USERS` : Liste de vos user_id Telegram autorisés (ex: `[5032994206]`)
- `COMPANY_*` : Informations de votre entreprise (SIRET, adresse, etc.)

#### 7. Initialiser la base de données

```bash
# Assurez-vous que PostgreSQL est démarré
uv run python execution/init_db.py
```

**Vérifier que l'initialisation a réussi** :
```bash
# Devrait afficher des messages de succès et création de tables
psql -U admin -d admin_agent -c "\dt"
# Doit montrer les tables 'documents' et 'chat_history'
```

#### 8. **✅ CHECKLIST AVANT DE LANCER LE BOT**

**Avant d'exécuter `run_bot.py`, vérifiez que TOUTES ces conditions sont remplies** :

##### 8.1. Vérifier PostgreSQL
```bash
# Linux
sudo service postgresql status

# Mac
brew services list | grep postgresql

# Windows
# Vérifier dans Services (services.msc) que PostgreSQL est démarré
```

##### 8.2. Vérifier la connexion à la base
```bash
# Tester la connexion avec les credentials de votre .env
psql -U admin -d admin_agent

# Si ça marche, vous êtes connecté. Tapez \q pour quitter
# Si erreur "FATAL: password authentication failed" → vérifier POSTGRES_PASSWORD dans .env
# Si erreur "FATAL: database "admin_agent" does not exist" → createdb admin_agent
```

##### 8.3. Vérifier le fichier .env
```bash
# Afficher les clés (sans les secrets)
cat .env | grep -v 'KEY\|PASSWORD\|TOKEN'
```
Vérifier que TOUTES ces variables sont remplies et valides :
- `POSTGRES_*`
- `TELEGRAM_BOT_TOKEN`
- **`OPENROUTER_API_KEY`** (Indispensable)
- **`OPENROUTER_MODEL`** (Ex: `google/gemini-2.0-flash-001`)
- `TELEGRAM_ADMIN_USERS` (Format `[ID1,ID2]`)
- `COMPANY_*`

##### 8.4. Vérifier votre Telegram user_id
```bash
# 1. Dans Telegram, /start avec @userinfobot
# 2. Noter votre Id (ex: 5032994206)
# 3. Vérifier qu'il est bien dans TELEGRAM_ADMIN_USERS dans .env
#    Format: TELEGRAM_ADMIN_USERS=[5032994206]
```

##### 8.5. Vérifier les dépendances Python
```bash
uv pip list | grep -E "telegram|langgraph|reportlab|pydantic|sqlalchemy|langchain-openai|langchain-core"
# Si incomplet, réinstaller : uv sync
```

##### 8.6. Vérifier la structure des dossiers
```bash
ls -la execution/agents/
ls -la execution/prompts/
ls -la .tmp/
```

#### 9. Lancer le bot

```bash
uv run python run_bot.py
```

**✅ Sortie attendue (succès)** :
```
...
INFO - 🤖 Démarrage du bot Telegram...
INFO - 📱 Bot configuré pour: Ma SASU
INFO - 👥 Admins autorisés: [5032994206]
...
INFO - Application started
```

#### 10. Tester sur Telegram

Envoyez un message en langage naturel, par exemple :
`"Fais une facture pour Client XYZ de 1200€ pour la prestation A"`

**✅ Comportement attendu :**
Le bot analyse la demande, extrait les infos, génère le document et le renvoie.

Si vous rencontrez des erreurs de quota API ou de modèle indisponible, vérifiez votre clé OpenRouter et le modèle choisi dans `.env`.

---

## 🐛 Dépannage

### Erreur LLM (`RESOURCE_EXHAUSTED`, `NOT_FOUND`, etc.)
1.  Vérifier `OPENROUTER_API_KEY` dans `.env`.
2.  Vérifier le modèle choisi dans `.env` (`OPENROUTER_MODEL`). Assurez-vous qu'il est supporté par OpenRouter et votre clé.
3.  Si vous utilisez un modèle gratuit, vérifiez les quotas sur votre compte OpenRouter. Passez à un modèle payant si nécessaire.
4.  Si le modèle est introuvable, vérifiez son nom exact sur le site d'OpenRouter.

### Erreur `AttributeError: 'AdminBot' object has no attribute 'cmd_rent_receipt'` (ou similaire)
1.  Vérifier les modifications récentes dans `execution/telegram_bot.py` et `execution/agents/__init__.py`. Assurez-vous que tous les agents sont correctement importés et que les méthodes sont bien définies.
2.  Effectuer un `docker-compose up -d --build --force-recreate` pour recharger le code.

### Erreur `NameError: name 'BigInteger' is not defined`
1.  Vérifier l'importation de `BigInteger` depuis `sqlalchemy` dans `execution/models/database.py`.

---

## 🤝 Contribution

Les contributions sont les bienvenues !

1.  Fork le projet
2.  Créer une branche (`git checkout -b feature/ma-feature`)
3.  Commit les changements (`git commit -m 'Ajout de ma feature'`)
4.  Push vers la branche (`git push origin feature/ma-feature`)
5.  Ouvrir une Pull Request

**Guidelines** :
- Suivre les conventions de code (Ruff)
- Ajouter des tests pour les nouvelles fonctionnalités
- Mettre à jour la documentation
- Ajouter/mettre à jour les directives dans `directives/`

## 📄 Licence

MIT

## 🙏 Remerciements

- [LangChain](https://github.com/langchain-ai/langchain) pour le framework IA
- [OpenRouter](https://openrouter.ai/) pour l'accès LLM flexible
- [python-telegram-bot](https://python-telegram-bot.org/) pour l'interface Telegram
- [ReportLab](https://www.reportlab.com/) pour la génération de PDF
- [SQLAlchemy](https://www.sqlalchemy.org/) pour l'ORM et la DB
- [Astral (UV)](https://astral.sh/) pour le gestionnaire de paquets ultra-rapide

---

**Créé avec ❤️ pour les entrepreneurs français**