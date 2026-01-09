# Admin Agent Pro

**Agent IA d'automatisation administrative pour entreprises unipersonnelles (SASU, EURL)**

Ce projet est un système intelligent basé sur LangGraph qui automatise la génération de documents administratifs (factures, devis, notes de frais, quittances de loyer, etc.) via une interface Telegram intuitive.

Construit sur une architecture à trois couches qui sépare le raisonnement probabiliste des LLM de l'exécution déterministe du code pour une fiabilité maximale.

## 🏗 L'Architecture à 3 Couches

Pour maximiser la fiabilité, ce système sépare les responsabilités :

1.  **Couche 1 : Directive (Le "Quoi")**
    *   Située dans `directives/`.
    *   Procédures Opérationnelles Standard (SOP) en Markdown.
    *   Définit les objectifs, les entrées/sorties et les outils à utiliser.

2.  **Couche 2 : Orchestration (La Décision)**
    *   C'est l'Agent (LLM).
    *   Lit les directives, sélectionne les outils d'exécution, gère les erreurs et met à jour les instructions en fonction des apprentissages.

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
- 📄 **Génération de factures** (PDF) - Conformes aux normes françaises avec numérotation séquentielle
- 🤖 **Interface Telegram** - Commandes textuelles simples et intuitives
- 🗄️ **Historique PostgreSQL** - Stockage et recherche de tous les documents générés
- 📊 **Statistiques** - Suivi des documents générés par type

### En Développement (🚧)
- 📝 **Génération de devis** (PDF)
- 🚗 **Notes de frais kilométriques** - Barème fiscal français
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

1. Ouvrir Telegram et chercher **@BotFather**
2. Envoyer `/newbot`
3. Suivre les instructions
4. Récupérer le token (format: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)
5. Récupérer votre user_id Telegram (via @userinfobot)

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
- `TELEGRAM_ADMIN_USERS` : Liste de vos user_id Telegram autorisés
- `COMPANY_*` : Informations de votre entreprise (SIRET, adresse, etc.)
- `ANTHROPIC_API_KEY` : Clé API Anthropic (pour futures fonctionnalités IA)

#### 7. Initialiser la base de données

```bash
uv run python execution/init_db.py
```

#### 8. Lancer le bot

```bash
uv run python run_bot.py
```

Vous devriez voir :
```
🤖 Démarrage du bot Telegram...
📱 Bot configuré pour: Votre Entreprise
```

#### 9. Tester sur Telegram

Ouvrez Telegram, trouvez votre bot et envoyez :
```
/start
```

### Utilisation

#### Commandes Telegram Disponibles

**Génération de facture :**
```
/facture client="ACME Corp" montant=1500 description="Développement site web" adresse="1 rue Example, 75001 Paris"
```

**Voir les statistiques :**
```
/stats
```

**Aide :**
```
/help
```

#### Paramètres des Commandes

**Pour `/facture`** :
- `client` (requis) : Nom du client
- `montant` (requis) : Montant HT en euros
- `description` (optionnel) : Description de la prestation
- `adresse` (optionnel) : Adresse du client
- `siret` (optionnel) : SIRET du client (14 chiffres)
- `conditions` (optionnel) : Conditions de paiement
- `notes` (optionnel) : Notes additionnelles

### Développement

#### Ajouter des dépendances

```bash
# Dépendance de production
uv add nom-du-package

# Dépendance de développement
uv add --dev pytest
```

#### Lancer les tests

```bash
uv run pytest
```

#### Linting

```bash
uv run ruff check .
```

## 📚 Documentation

### Guides Techniques

- **[Spécifications Techniques](directives/TECHNICAL_SPECS.md)** : Stack technique complète, frameworks agentiques (LangGraph, CrewAI, AutoGen, etc.), patterns et best practices
- **[Guide MCP Servers](directives/mcp-servers-guide.md)** : Implémentation de serveurs Model Context Protocol pour étendre les capacités des agents
- **[Instructions Agent](AGENTS.md)** : Directives système pour l'orchestration par les LLMs

### Stack Technique Principal

- **Python 3.12** avec **UV** (Astral) pour gestion de dépendances
- **Frameworks Agentiques** : LangGraph, CrewAI, LlamaIndex, Pydantic AI
- **LLM Providers** : Anthropic Claude, OpenAI, LiteLLM (abstraction unifiée)
- **MCP** : Model Context Protocol pour intégrations externes
- **Infrastructure** : FastAPI, Redis, PostgreSQL, Celery
- **Observabilité** : Structlog, LangFuse, Prometheus

### Frameworks Recommandés par Use Case

| Use Case | Framework |
|----------|-----------|
| Workflows complexes stateful | **LangGraph** |
| Équipes d'agents collaboratifs | **CrewAI** |
| RAG et knowledge bases | **LlamaIndex** |
| Type-safety et validation stricte | **Pydantic AI** |

---

## 🎯 Stack Technique

### Backend
- **Python 3.12** avec type hints strict
- **LangGraph** pour l'orchestration d'agents
- **Pydantic** pour validation des données
- **SQLAlchemy + asyncpg** pour PostgreSQL asynchrone
- **ReportLab** pour génération de PDF

### Bot & Interface
- **python-telegram-bot** pour l'interface Telegram
- Parsing intelligent des commandes textuelles
- Support des arguments avec guillemets

### Base de Données
- **PostgreSQL** pour stockage persistant
- Index composites pour performances
- Stockage JSON pour flexibilité

### Observabilité
- **Structlog** pour logging structuré
- Métriques par type de document
- Trace complète des workflows

## 📊 État du Projet

### ✅ Implémenté
- [x] Architecture 3 couches (Directive/Orchestration/Exécution)
- [x] Agent de génération de factures avec LangGraph
- [x] Générateur PDF professionnel
- [x] Base de données PostgreSQL avec historique
- [x] Bot Telegram fonctionnel
- [x] Commandes: `/start`, `/help`, `/stats`, `/facture`
- [x] Validation Pydantic stricte
- [x] Conformité légale française (SIRET, TVA, mentions obligatoires)
- [x] Documentation complète (directives + README)

### 🚧 En Cours
- [ ] Agent de génération de devis
- [ ] Agent de frais kilométriques
- [ ] Agent de quittances de loyer
- [ ] Agent de charges locatives
- [ ] Tests unitaires et d'intégration
- [ ] Menus interactifs Telegram (InlineKeyboard)
- [ ] Notifications automatiques

### 🔮 Roadmap Future
- [ ] Support multi-items pour factures
- [ ] Gestion des acomptes et soldes
- [ ] Factures d'avoir (remboursements)
- [ ] Export vers logiciels comptables
- [ ] Relances automatiques de paiement
- [ ] API REST pour intégrations tierces
- [ ] Dashboard web de visualisation
- [ ] Support des signatures électroniques
- [ ] Intégration Stripe pour paiements
- [ ] MCP servers pour intégrations externes

## 🔒 Sécurité

- ✅ Liste blanche d'utilisateurs Telegram (TELEGRAM_ADMIN_USERS)
- ✅ Validation stricte de toutes les entrées utilisateur
- ✅ Pas d'exécution de code arbitraire
- ✅ Secrets dans .env (exclus de Git)
- ✅ Connexions PostgreSQL sécurisées
- ⚠️ **TODO**: Chiffrement des données sensibles en base
- ⚠️ **TODO**: Rate limiting sur les commandes
- ⚠️ **TODO**: Audit logs des actions critiques

## 📝 Conformité Légale (France)

Ce système génère des documents conformes à la législation française :

- ✅ Numérotation séquentielle des factures (obligation légale)
- ✅ Mentions obligatoires (SIRET, TVA, adresses)
- ✅ Taux de TVA français (20%, 10%, 5.5%, 0%)
- ✅ Format des dates françaises (JJ/MM/AAAA)
- ✅ Conditions de paiement
- ✅ Conservation des justificatifs (base de données)

**Note** : Ce système est un outil d'aide à la gestion administrative. Il est recommandé de faire valider les documents par un expert-comptable, surtout pour les premières utilisations.

## 🐛 Dépannage

### Le bot ne répond pas
1. Vérifier que le token Telegram est correct dans `.env`
2. Vérifier que votre user_id est dans TELEGRAM_ADMIN_USERS
3. Vérifier les logs du bot pour les erreurs

### Erreur de connexion PostgreSQL
```bash
# Vérifier que PostgreSQL est démarré
sudo service postgresql status  # Linux
brew services list  # Mac

# Vérifier les credentials dans .env
psql -U admin -d admin_agent  # Tester la connexion
```

### Erreur "ModuleNotFoundError"
```bash
# Réinstaller les dépendances
uv sync
```

### PDF mal formé
1. Vérifier les informations d'entreprise dans `.env`
2. Vérifier les logs pour les erreurs ReportLab
3. Ouvrir un issue avec le PDF en exemple

## 🤝 Contribution

Les contributions sont les bienvenues !

1. Fork le projet
2. Créer une branche (`git checkout -b feature/ma-feature`)
3. Commit les changements (`git commit -m 'Ajout de ma feature'`)
4. Push vers la branche (`git push origin feature/ma-feature`)
5. Ouvrir une Pull Request

**Guidelines** :
- Suivre les conventions de code (Ruff)
- Ajouter des tests pour les nouvelles fonctionnalités
- Mettre à jour la documentation
- Ajouter/mettre à jour les directives dans `directives/`

## 📄 Licence

MIT

## 🙏 Remerciements

- [LangGraph](https://github.com/langchain-ai/langgraph) pour l'orchestration d'agents
- [python-telegram-bot](https://python-telegram-bot.org/) pour l'interface Telegram
- [ReportLab](https://www.reportlab.com/) pour la génération de PDF
- [Astral (UV)](https://astral.sh/) pour le gestionnaire de paquets ultra-rapide

---

**Créé avec ❤️ pour les entrepreneurs français**
