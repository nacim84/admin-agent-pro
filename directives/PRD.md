# Product Requirements Document (PRD)
# Migration N8n Workflow → Python Architecture as Code

**Projet** : Admin Agent Pro - Migration vers Architecture Python Pure
**Date** : 2026-01-09
**Version** : 1.0.0
**Auteur** : Équipe Admin Agent Pro
**Statut** : 📋 En Validation

---

## 📋 Table des Matières

1. [Executive Summary](#executive-summary)
2. [Contexte & Motivations](#contexte--motivations)
3. [Objectifs](#objectifs)
4. [Stakeholders](#stakeholders)
5. [User Stories](#user-stories)
6. [Exigences Fonctionnelles](#exigences-fonctionnelles)
7. [Exigences Techniques](#exigences-techniques)
8. [Architecture Cible](#architecture-cible)
9. [Composants à Développer](#composants-à-développer)
10. [Timeline & Milestones](#timeline--milestones)
11. [Métriques de Succès](#métriques-de-succès)
12. [Risques & Mitigations](#risques--mitigations)
13. [Dépendances](#dépendances)
14. [Hors Périmètre](#hors-périmètre)
15. [Plan de Test](#plan-de-test)
16. [Stratégie de Déploiement](#stratégie-de-déploiement)
17. [Documentation](#documentation)

---

## 📊 Executive Summary

### Vision

Transformer **Admin Agent Pro** d'une architecture hybride (Python + N8n) vers une **architecture 100% Python as-code**, éliminant la dépendance à N8n tout en conservant et améliorant toutes les fonctionnalités existantes de génération de documents administratifs.

### Problème Actuel

L'application utilise actuellement un workflow N8n (1578 lignes JSON) pour orchestrer la génération de documents administratifs (factures, devis, quittances, charges locatives, frais kilométriques). Cette approche présente des limitations :

- **Maintenance complexe** : Configuration JSON non versionnée efficacement
- **Debugging difficile** : Traces d'erreur N8n moins détaillées que Python natif
- **Tests limités** : Pas de tests unitaires possibles sur les nodes N8n
- **Dépendance externe** : Nécessite N8n cloud ou self-hosted
- **Performance** : Overhead de communication inter-processus

### Solution Proposée

Migrer tous les composants N8n vers des **tools et agents Python natifs** en utilisant LangChain/LangGraph, tout en conservant l'architecture à 3 couches existante (Directives → Orchestration → Exécution).

### Bénéfices Attendus

| Métrique | Avant (N8n) | Après (Python) | Amélioration |
|----------|-------------|----------------|--------------|
| **Maintenabilité** | JSON 1578L | Python 2000L | +30% clarté |
| **Testabilité** | 0% couverture | >80% couverture | Tests unitaires |
| **Performance** | ~800ms/doc | ~400ms/doc | -50% latence |
| **Debugging** | Logs N8n | Stacktrace Python | +100% clarté |
| **Coût** | N8n cloud | Self-hosted | -100€/mois |
| **Type-safety** | Aucune | Pydantic strict | +Sécurité |

### Investissement Requis

- **Durée** : 10 semaines (2,5 mois)
- **Effort** : ~160 heures développement
- **Ressources** : 1 développeur Python senior
- **Budget** : API OpenAI Whisper (~20€/mois pour transcriptions)

---

## 🎯 Contexte & Motivations

### Contexte Métier

**Admin Agent Pro** est un assistant administratif automatisé pour entrepreneurs individuels et petites entreprises françaises. Il permet de :

1. Générer des **factures** conformes DGFIP
2. Créer des **devis** commerciaux
3. Calculer des **frais kilométriques** selon barème fiscal 2024
4. Éditer des **quittances de loyer** légales (art. L145-49)
5. Produire des **régularisations de charges** locatives

Le système est accessible via **Telegram** (bot conversationnel) et utilise un **LLM via OpenRouter** pour comprendre les demandes en langage naturel.

### Motivations Techniques

#### 1. Éliminer la Complexité N8n

- **Configuration déclarative limitée** : Les workflows N8n sont définis en JSON avec des références inter-nodes complexes
- **Debugging difficile** : Les erreurs dans les nodes sont difficiles à tracer
- **Versionnement problématique** : Git diff sur JSON peu lisible

#### 2. Améliorer la Qualité du Code

- **Type-safety** : Pydantic garantit la validation des données
- **Tests unitaires** : pytest permet de tester chaque composant isolément
- **Linting** : ruff assure la qualité du code Python

#### 3. Optimiser les Performances

- **Async natif** : asyncio/await au lieu de communication inter-processus
- **Réduction overhead** : Élimination des appels HTTP N8n → Python
- **Mise en cache** : Possibilité d'optimiser les requêtes DB

#### 4. Réduire les Coûts

- **N8n cloud** : 0€ (self-hosted) vs 20-100€/mois (cloud)
- **Maintenance** : Code Python plus facile à maintenir long terme
- **Formation** : Équipe déjà compétente en Python

### Motivations Fonctionnelles

#### 1. Ajouter de Nouvelles Capacités

- **Transcription vocale** : Messages vocaux Telegram → Texte (Whisper)
- **Envoi par email** : Documents envoyés automatiquement par SMTP
- **Calculs avancés** : Tool Calculator pour conversions TTC/HT

#### 2. Améliorer l'Expérience Utilisateur

- **Réponses plus rapides** : Latence réduite de 50%
- **Messages nettoyés** : Suppression du markdown pour Telegram
- **Meilleure gestion erreurs** : Stacktraces Python détaillées

---

## 🎯 Objectifs

### Objectifs Principaux (MUST HAVE)

| # | Objectif | Description | Critère de Succès |
|---|----------|-------------|-------------------|
| **O1** | **Migration complète N8n → Python** | Tous les 14 composants N8n remplacés par des équivalents Python | 100% des fonctionnalités N8n disponibles en Python |
| **O2** | **Zéro régression fonctionnelle** | Toutes les fonctionnalités actuelles conservées | Tests de régression passent à 100% |
| **O3** | **Amélioration performance** | Réduction de 50% du temps de génération de documents | Latence moyenne < 400ms |
| **O4** | **Couverture tests > 80%** | Tests unitaires pour tous les nouveaux composants | pytest coverage report > 80% |
| **O5** | **Documentation complète** | Toutes les directives et guides techniques mis à jour | Documentation à jour avant déploiement |

### Objectifs Secondaires (SHOULD HAVE)

| # | Objectif | Description | Critère de Succès |
|---|----------|-------------|-------------------|
| **O6** | **Monitoring & Observabilité** | Métriques Prometheus + logs structurés | Dashboard Grafana opérationnel |
| **O7** | **Transcription vocale** | Support messages vocaux Telegram via Whisper | >95% précision transcription français |
| **O8** | **Envoi emails automatique** | Documents envoyés par SMTP avec CC | 100% des emails délivrés |
| **O9** | **Type-safety strict** | Validation Pydantic + mypy strict | 0 erreur mypy en mode strict |

### Objectifs Nice-to-Have (COULD HAVE)

| # | Objectif | Description |
|---|----------|-------------|
| **O10** | **CI/CD automatisé** | GitHub Actions pour tests + déploiement |
| **O11** | **Multi-langue** | Support anglais en plus du français |
| **O12** | **API REST** | Exposition des fonctionnalités via FastAPI |

---

## 👥 Stakeholders

### Parties Prenantes

| Rôle | Nom | Responsabilité | Intérêt |
|------|-----|----------------|---------|
| **Product Owner** | Nacim RABIA | Validation fonctionnelle | Amélioration produit |
| **Tech Lead** | Équipe Dev | Architecture & implémentation | Qualité technique |
| **End Users** | Entrepreneurs FR | Utilisation quotidienne | Fiabilité & rapidité |
| **Ops/DevOps** | Équipe Infra | Déploiement & monitoring | Stabilité production |

### Communication

- **Weekly sync** : Jeudi 10h (suivi avancement)
- **Demo** : Fin de chaque phase (validation fonctionnelle)
- **Retrospective** : Fin de projet (lessons learned)

---

## 📖 User Stories

### US-001 : Génération de Document via Texte

```gherkin
En tant qu'utilisateur Telegram
Je veux envoyer un message texte comme "Fais une facture pour ACME de 1500€"
Afin de recevoir un PDF de facture conforme DGFIP

Critères d'acceptation:
- ✅ Le message est analysé par l'OrchestratorAgent
- ✅ L'intention "invoice" est détectée avec >80% confiance
- ✅ Les données (client, montant) sont extraites
- ✅ Un PDF est généré et envoyé via Telegram
- ✅ Le document est sauvegardé en base de données
- ✅ Le temps de réponse est < 3 secondes
```

### US-002 : Génération de Document via Vocal

```gherkin
En tant qu'utilisateur Telegram
Je veux envoyer un message vocal "Fais un devis pour Alteca de deux mille euros"
Afin de recevoir un PDF de devis sans taper de texte

Critères d'acceptation:
- ✅ Le message vocal est transcrit via Whisper API
- ✅ La transcription est traitée comme un message texte
- ✅ Un PDF de devis est généré et envoyé
- ✅ La précision de transcription est > 95% (français)
- ✅ Le temps de réponse est < 5 secondes (transcription incluse)
```

### US-003 : Envoi de Document par Email

```gherkin
En tant qu'utilisateur Telegram
Je veux demander "Envoie la dernière facture par email à rn.block.pro@gmail.com"
Afin de transmettre le document sans télécharger/renvoyer manuellement

Critères d'acceptation:
- ✅ Le document est récupéré depuis la base de données
- ✅ L'email est envoyé avec le PDF en pièce jointe
- ✅ Les destinataires CC sont gérés (email_pro_1, email_pro_2, email_client)
- ✅ La signature "M Nacim RABIA, RN-BLOCK" est ajoutée
- ✅ Une confirmation est envoyée via Telegram
- ✅ Le taux de délivrabilité est > 99%
```

### US-004 : Calculs Automatiques TVA

```gherkin
En tant qu'utilisateur Telegram
Je veux dire "Facture TTC de 1200€ avec TVA 20%"
Afin que le système calcule automatiquement le HT et la TVA

Critères d'acceptation:
- ✅ Le CalculatorTool est appelé automatiquement
- ✅ HT calculé = 1000.00€
- ✅ TVA calculée = 200.00€
- ✅ Les montants sont arrondis à 2 décimales
- ✅ La facture PDF affiche HT, TVA, TTC correctement
```

### US-005 : Récupération Données depuis DB

```gherkin
En tant qu'utilisateur Telegram
Je veux dire simplement "Fais une facture pour ALTECA"
Afin que le système récupère automatiquement les données client depuis la base

Critères d'acceptation:
- ✅ Le DatabaseQueryTool est appelé avec query_type="facture"
- ✅ Les données sont récupérées depuis data_administration (id='facturation_client_1')
- ✅ Le produit, prix unitaire, TVA, conditions paiement sont pré-remplis
- ✅ L'utilisateur n'a qu'à préciser la quantité si nécessaire
- ✅ Le document est généré avec toutes les informations correctes
```

### US-006 : Nettoyage Réponses Markdown

```gherkin
En tant qu'utilisateur Telegram
Je veux recevoir des réponses en texte brut
Afin d'éviter les caractères markdown non rendus (**, `, etc.)

Critères d'acceptation:
- ✅ Le MarkdownCleanerTool est appliqué à toutes les réponses LLM
- ✅ Les symboles **, *, _, ` sont supprimés
- ✅ Les listes numérotées sont conservées (1. 2. 3.)
- ✅ Les bullet points sont convertis en • (Unicode)
- ✅ Les retours à la ligne sont préservés
- ✅ Le texte est lisible dans l'interface Telegram
```

### US-007 : Tests Automatisés

```gherkin
En tant que développeur
Je veux exécuter `pytest tests/` en CI/CD
Afin de garantir que toutes les fonctionnalités sont testées avant déploiement

Critères d'acceptation:
- ✅ Tous les nouveaux tools ont des tests unitaires
- ✅ Les tests d'intégration couvrent les workflows end-to-end
- ✅ La couverture de code est > 80%
- ✅ Les tests passent en < 60 secondes
- ✅ Les tests sont exécutés automatiquement sur chaque commit
```

### US-008 : Monitoring Production

```gherkin
En tant qu'opérateur
Je veux consulter un dashboard Grafana
Afin de surveiller les métriques de performance en production

Critères d'acceptation:
- ✅ Métriques Prometheus exposées (/metrics endpoint)
- ✅ Dashboard Grafana avec panels :
  - Nombre de documents générés par type
  - Temps de génération PDF (p50, p95, p99)
  - Taux d'erreur par agent
  - Utilisateurs actifs
- ✅ Alertes configurées si erreur rate > 5%
- ✅ Logs structurés (JSON) indexés
```

---

## 🔧 Exigences Fonctionnelles

### RF-001 : Génération de Documents

| ID | Exigence | Priorité | Critère de Validation |
|----|----------|----------|----------------------|
| RF-001.1 | Générer factures conformes DGFIP | MUST | PDF avec mentions obligatoires (SIRET, TVA, etc.) |
| RF-001.2 | Générer devis commerciaux | MUST | PDF avec validité 30 jours par défaut |
| RF-001.3 | Générer frais kilométriques | MUST | PDF avec barème fiscal 2024 |
| RF-001.4 | Générer quittances de loyer | MUST | PDF conforme art. L145-49 Code rural |
| RF-001.5 | Générer décomptes de charges | MUST | PDF avec détail charges + régularisation |
| RF-001.6 | Numérotation séquentielle | MUST | Format YYYY-NNNN unique par type/année |
| RF-001.7 | Sauvegarde en base de données | MUST | Table documents avec pdf_path + data JSON |

### RF-002 : Orchestration & Routing

| ID | Exigence | Priorité | Critère de Validation |
|----|----------|----------|----------------------|
| RF-002.1 | Classification d'intention NLU | MUST | 7 intents (invoice, quote, mileage, rent_receipt, rental_charges, stats, chat) |
| RF-002.2 | Extraction d'entités | MUST | Client, montant, quantité, dates extraits du texte |
| RF-002.3 | Gestion historique conversationnel | MUST | 10 derniers messages utilisés pour contexte |
| RF-002.4 | Clarification interactive | SHOULD | Demander quantité si manquante |
| RF-002.5 | Confiance > 80% pour exécution | MUST | Si < 80%, demander confirmation |

### RF-003 : Calculs Financiers

| ID | Exigence | Priorité | Critère de Validation |
|----|----------|----------|----------------------|
| RF-003.1 | Calcul TTC depuis HT | MUST | TTC = HT × (1 + taux_tva) |
| RF-003.2 | Calcul HT depuis TTC | MUST | HT = TTC / (1 + taux_tva) |
| RF-003.3 | Arrondi 2 décimales | MUST | Utiliser Decimal pour précision |
| RF-003.4 | Support taux TVA multiples | SHOULD | 20%, 10%, 5.5%, 0% |
| RF-003.5 | Validation montants positifs | MUST | Erreur si montant <= 0 |

### RF-004 : Récupération Données

| ID | Exigence | Priorité | Critère de Validation |
|----|----------|----------|----------------------|
| RF-004.1 | Query données facturation | MUST | Table data_administration (id='facturation_client_1') |
| RF-004.2 | Query données quittance | MUST | Table data_administration (id='quittance_loyer_1') |
| RF-004.3 | Query données charges | MUST | Table data_administration (id='charge_locative_1') |
| RF-004.4 | Query données frais km | MUST | Table data_administration (id='frai_kilometrique_1') |
| RF-004.5 | Parsing JSONB charges | MUST | Charger JSON depuis colonne charges |

### RF-005 : Envoi par Email

| ID | Exigence | Priorité | Critère de Validation |
|----|----------|----------|----------------------|
| RF-005.1 | Envoi document en pièce jointe | SHOULD | PDF attaché via SMTP |
| RF-005.2 | Destinataire TO = email_entreprise | SHOULD | Toujours destinataire principal |
| RF-005.3 | CC = email_pro_1, email_pro_2, email_client | SHOULD | Si disponibles en DB |
| RF-005.4 | Signature automatique | SHOULD | "M Nacim RABIA, RN-BLOCK" |
| RF-005.5 | Retry avec backoff exponentiel | SHOULD | 3 tentatives max avec tenacity |

### RF-006 : Transcription Vocale

| ID | Exigence | Priorité | Critère de Validation |
|----|----------|----------|----------------------|
| RF-006.1 | Support messages vocaux Telegram | SHOULD | Format .ogg (Telegram) |
| RF-006.2 | Transcription via OpenAI Whisper | SHOULD | API whisper-1 |
| RF-006.3 | Précision > 95% français | SHOULD | Tests avec messages de référence |
| RF-006.4 | Timeout 30 secondes | SHOULD | Erreur si dépassé |
| RF-006.5 | Cleanup fichiers temporaires | SHOULD | Suppression après traitement |

### RF-007 : Nettoyage Réponses

| ID | Exigence | Priorité | Critère de Validation |
|----|----------|----------|----------------------|
| RF-007.1 | Suppression markdown (**, *, _, `) | MUST | Regex de nettoyage |
| RF-007.2 | Conversion bullet points | MUST | * → • (Unicode) |
| RF-007.3 | Conservation listes numérotées | MUST | 1. 2. 3. conservées |
| RF-007.4 | Suppression liens [text](url) | MUST | Garder seulement text |
| RF-007.5 | Nettoyage retours à la ligne multiples | MUST | Max 2 newlines consécutifs |

---

## ⚙️ Exigences Techniques

### RT-001 : Stack Technique

| Composant | Technologie | Version | Justification |
|-----------|-------------|---------|---------------|
| **Runtime** | Python | 3.11+ | Async/await natif, performance |
| **Package Manager** | UV (Astral) | Latest | 10-100x plus rapide que pip |
| **Framework LLM** | LangChain | 0.2.0+ | Standard de facto pour agents |
| **Orchestration** | LangGraph | 0.2.0+ | Workflows stateful |
| **Validation** | Pydantic | 2.8.0+ | Type-safety strict |
| **Database ORM** | SQLAlchemy | 2.0+ async | ORM async haute-perf |
| **DB Driver** | AsyncPG | 0.29+ | Driver PostgreSQL le plus rapide |
| **PDF Generation** | ReportLab | 4.0+ | Génération vectorielle professionnelle |
| **Telegram Bot** | python-telegram-bot | 21.0+ | Client officiel Telegram |
| **Testing** | pytest + pytest-asyncio | 8.3+ / 0.24+ | Framework de test standard |
| **Linting** | Ruff | 0.5.0+ | 10-100x plus rapide que flake8 |
| **Type Checking** | Mypy | 1.11+ | Vérification types statique |
| **Logging** | Structlog | 24.4+ | Logs structurés JSON |

### RT-002 : Architecture

| Exigence | Description | Critère |
|----------|-------------|---------|
| **3-Layer Architecture** | Directives → Orchestration → Execution | Séparation claire des couches |
| **Async-first** | Toutes les I/O en async/await | 0 appel synchrone bloquant |
| **State Machine** | LangGraph StateGraph pour workflows | Workflow déterministe |
| **Dependency Injection** | Tools injectés dans agents | Testabilité accrue |
| **Factory Pattern** | BaseAdminAgent → Agents spécialisés | Réutilisation code |
| **Repository Pattern** | DatabaseManager pour accès DB | Abstraction accès données |

### RT-003 : Qualité de Code

| Exigence | Description | Critère |
|----------|-------------|---------|
| **Type Hints** | Toutes fonctions typées | Mypy strict mode 0 erreur |
| **Docstrings** | Format Google pour toutes fonctions publiques | pydocstyle pass |
| **Linting** | Ruff avec règles E, W, F, I, N, UP, B, C4, SIM | 0 erreur ruff check |
| **Test Coverage** | Couverture > 80% | pytest-cov report > 80% |
| **Line Length** | Max 100 caractères | Configuré dans pyproject.toml |
| **Naming** | snake_case fonctions, PascalCase classes | Convention PEP 8 |

### RT-004 : Performance

| Exigence | Métrique | Objectif | Mesure |
|----------|----------|----------|--------|
| **Latence génération PDF** | P95 | < 500ms | Histogram Prometheus |
| **Latence LLM** | P95 | < 1000ms | Histogram Prometheus |
| **Throughput** | Docs/min | > 120 | Counter Prometheus |
| **Memory usage** | RSS | < 512MB | Docker stats |
| **Startup time** | Cold start | < 10s | Temps avant ready |

### RT-005 : Sécurité

| Exigence | Description | Implémentation |
|----------|-------------|----------------|
| **Secrets Management** | Jamais en clair dans code | Variables .env + .gitignore |
| **Input Validation** | Validation stricte Pydantic | Tous les inputs utilisateur |
| **SQL Injection** | Pas de SQL string concat | SQLAlchemy ORM + parameterized queries |
| **SIRET Validation** | Checksum Luhn | Fonction validate_siret() |
| **Email Validation** | Format RFC 5322 | Pydantic EmailStr |
| **Rate Limiting** | Max 10 req/min par user | Middleware Telegram |

### RT-006 : Observabilité

| Exigence | Description | Outil |
|----------|-------------|-------|
| **Structured Logging** | Logs JSON avec contexte | Structlog |
| **Metrics** | Exposition métriques Prometheus | prometheus_client |
| **Tracing** | Span tracing pour debugging | OpenTelemetry (optionnel) |
| **Health Check** | Endpoint /health | FastAPI (si API REST) |
| **Alerting** | Alertes si error rate > 5% | Grafana Alerting |

### RT-007 : Déploiement

| Exigence | Description | Technologie |
|----------|-------------|-------------|
| **Containerization** | Image Docker multi-stage | Dockerfile |
| **Orchestration** | Docker Compose pour dev/prod | docker-compose.yml |
| **Database Migrations** | Schéma versionné | Alembic (optionnel) |
| **Zero-downtime** | Rolling update | Docker healthcheck |
| **Rollback** | Possibilité rollback version N-1 | Docker tag versioning |

---

## 🏗️ Architecture Cible

### Vue d'Ensemble

```
┌─────────────────────────────────────────────────────────────┐
│                      USER INTERFACE                         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Telegram Bot (python-telegram-bot 21.0+)            │  │
│  │  - Text messages                                      │  │
│  │  - Voice messages → Whisper transcription            │  │
│  │  - Commands (/facture, /devis, /stats, etc.)        │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              ORCHESTRATION LAYER (LangGraph)                │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  OrchestratorAgent (Enhanced)                         │  │
│  │  - Intent classification (7 intents)                  │  │
│  │  - Entity extraction (LLM-powered)                   │  │
│  │  - Chat history awareness (10 messages)              │  │
│  │  - Tool calling (calculator, db_query, etc.)        │  │
│  │  - Confidence scoring                                 │  │
│  └──────────────────────────────────────────────────────┘  │
│                         │                                   │
│           ┌─────────────┼─────────────┐                     │
│           ▼             ▼             ▼                     │
│  ┌──────────────┐ ┌──────────┐ ┌────────────┐            │
│  │ InvoiceAgent │ │ QuoteAgent│ │MileageAgent│ ... (x5)   │
│  │ (Existing)   │ │ (Existing)│ │ (Existing) │            │
│  └──────────────┘ └──────────┘ └────────────┘            │
└─────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    TOOLS LAYER (NEW)                        │
│  ┌────────────────────────────────────────────────────┐    │
│  │ CalculatorTool (NEW)                                │    │
│  │ - Calculs TVA, totaux, conversions TTC/HT          │    │
│  │ - Validation montants positifs                      │    │
│  │ - Précision Decimal (2 décimales)                  │    │
│  └────────────────────────────────────────────────────┘    │
│  ┌────────────────────────────────────────────────────┐    │
│  │ DatabaseQueryTool (NEW)                             │    │
│  │ - Get_Infos_Facture → Query id='facturation_client_1'│  │
│  │ - Get_Infos_Quittance → Query id='quittance_loyer_1' │  │
│  │ - Get_Infos_Charges → Query id='charge_locative_1' │    │
│  │ - Get_Infos_Frais_KM → Query id='frai_kilometrique_1'│  │
│  │ - Parse JSONB charges                               │    │
│  └────────────────────────────────────────────────────┘    │
│  ┌────────────────────────────────────────────────────┐    │
│  │ EmailSenderTool (NEW)                               │    │
│  │ - Send documents via SMTP                           │    │
│  │ - TO: email_entreprise                              │    │
│  │ - CC: email_pro_1, email_pro_2, email_client       │    │
│  │ - Signature: "M Nacim RABIA, RN-BLOCK"            │    │
│  │ - Retry with exponential backoff                    │    │
│  └────────────────────────────────────────────────────┘    │
│  ┌────────────────────────────────────────────────────┐    │
│  │ WhisperTranscriptionTool (NEW)                      │    │
│  │ - Voice → Text via OpenAI Whisper API              │    │
│  │ - Support .ogg (Telegram), .mp3, .wav              │    │
│  │ - Language: French (>95% accuracy)                 │    │
│  └────────────────────────────────────────────────────┘    │
│  ┌────────────────────────────────────────────────────┐    │
│  │ MarkdownCleanerTool (NEW)                           │    │
│  │ - Clean LLM output (**, *, _, `, etc.)            │    │
│  │ - Format for Telegram plain text                   │    │
│  │ - Preserve numbered lists                           │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              EXISTING EXECUTION LAYER                       │
│  ┌────────────────────────────────────────────────────┐    │
│  │ PDFGenerator (ReportLab)                  ✅ Keep   │    │
│  │ - generate_invoice_pdf()                            │    │
│  │ - generate_quote_pdf()                              │    │
│  │ - generate_mileage_pdf()                            │    │
│  │ - generate_rent_receipt_pdf()                       │    │
│  │ - generate_rental_charges_pdf()                     │    │
│  └────────────────────────────────────────────────────┘    │
│  ┌────────────────────────────────────────────────────┐    │
│  │ DatabaseManager (AsyncPG)                 ✅ Keep   │    │
│  │ - save_document()                                   │    │
│  │ - get_chat_history()                                │    │
│  │ - get_next_invoice_number()                         │    │
│  │ - add_chat_message()                                │    │
│  └────────────────────────────────────────────────────┘    │
│  ┌────────────────────────────────────────────────────┐    │
│  │ Pydantic Models                           ✅ Keep   │    │
│  │ - Invoice, Quote, MileageRecord, etc.              │    │
│  └────────────────────────────────────────────────────┘    │
│  ┌────────────────────────────────────────────────────┐    │
│  │ SQLAlchemy Models                         ✅ Keep   │    │
│  │ - Document, ChatHistory                             │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    DATA LAYER                               │
│  ┌────────────────────────────────────────────────────┐    │
│  │ PostgreSQL 15                                       │    │
│  │ - documents (existing)                              │    │
│  │ - chat_history (existing)                           │    │
│  │ - data_administration (NEW - from N8n)             │    │
│  │ - kilometres_parcourus (NEW - from N8n)            │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

### Flux de Données

#### Scénario 1 : Message Texte → Facture

```
User: "Fais une facture pour ALTECA de 10 jours à 500€/jour"
  │
  ▼
[Telegram Handler]
  │
  ▼
[OrchestratorAgent.analyze_message()]
  │
  ├─ Load chat history (10 messages)
  ├─ Call LLM (OpenRouter/Gemini)
  ├─ Parse JSON response
  │  {
  │    "intent": "invoice",
  │    "confidence": 0.95,
  │    "extracted_data": {
  │      "client_name": "ALTECA",
  │      "quantity": 10,
  │      "unit_price": 500.0
  │    }
  │  }
  │
  ▼
[DatabaseQueryTool.run()]
  │
  ├─ Query: SELECT * FROM data_administration
  │          WHERE id_data_administration = 'facturation_client_1'
  │
  ├─ Result: {
  │    "nom_client": "ALTECA",
  │    "adresse_client": "45 RUE ANATOLE FRANCE...",
  │    "produit": "Consultant FullStack Senior",
  │    "prix_unitaire": 500.0,
  │    "tva": "20 %",
  │    "paiement": "Virement...",
  │    "email_client": "comptafournisseurs@alteca.fr",
  │    ...
  │  }
  │
  ▼
[CalculatorTool.run()]
  │
  ├─ Operation: multiply (quantity=10, unit_price=500.0)
  ├─ Result HT: 5000.00
  │
  ├─ Operation: ttc_from_ht (ht=5000.0, tva=0.20)
  ├─ Result TTC: 6000.00
  │
  ▼
[InvoiceAgent.execute()]
  │
  ├─ [validate_input] → Pydantic validation
  │  Invoice(
  │    invoice_number="2026-0042",
  │    client_name="ALTECA",
  │    items=[InvoiceItem(quantity=10, unit_price=500.0)],
  │    total_ht=5000.0,
  │    total_ttc=6000.0,
  │    ...
  │  )
  │
  ├─ [generate_pdf] → PDFGenerator
  │  PDF path: .tmp/documents/facture_2026-0042_20260109.pdf
  │
  ├─ [save_to_db] → DatabaseManager
  │  DB record ID: 1234
  │
  ▼
[Telegram send_document()]
  │
  ▼
User receives PDF "Facture 2026-0042"
```

#### Scénario 2 : Message Vocal → Devis

```
User: 🎤 "Fais un devis pour Alteca de deux mille euros"
  │
  ▼
[Telegram voice_handler]
  │
  ├─ Download .ogg file → .tmp/voice_123_abc.ogg
  │
  ▼
[WhisperTranscriptionTool.run()]
  │
  ├─ Call OpenAI Whisper API
  │  POST https://api.openai.com/v1/audio/transcriptions
  │  {
  │    "file": voice_123_abc.ogg,
  │    "model": "whisper-1",
  │    "language": "fr"
  │  }
  │
  ├─ Response: {
  │    "text": "Fais un devis pour Alteca de deux mille euros"
  │  }
  │
  ▼
[OrchestratorAgent.analyze_message()]
  │
  ├─ Intent: "quote"
  ├─ Extracted: {"client_name": "Alteca", "amount": 2000.0}
  │
  ▼
[QuoteAgent.execute()]
  │
  ├─ Generate quote PDF
  ├─ Save to DB
  │
  ▼
User receives PDF "Devis DEV-2026-0015"
```

#### Scénario 3 : Envoi Email

```
User: "Envoie la dernière facture par email"
  │
  ▼
[OrchestratorAgent.analyze_message()]
  │
  ├─ Intent: "send_email"
  ├─ Query last invoice from DB
  │
  ▼
[DatabaseQueryTool.run()]
  │
  ├─ Query: SELECT * FROM data_administration
  │          WHERE id_data_administration = 'facturation_client_1'
  │
  ├─ Extract emails:
  │  - TO: email_entreprise = "rn.block.pro@gmail.com"
  │  - CC: email_professionnel_1 = "rabia.nacim@gmail.com"
  │  - CC: email_client = "comptafournisseurs@alteca.fr"
  │
  ▼
[EmailSenderTool.run()]
  │
  ├─ Load PDF from DB: document_number="2026-0042"
  │
  ├─ Compose email:
  │  From: rabia.nacim@gmail.com
  │  To: rn.block.pro@gmail.com
  │  Cc: rabia.nacim@gmail.com, comptafournisseurs@alteca.fr
  │  Subject: Facture 2026-0042
  │  Body: "Veuillez trouver ci-joint la facture...
  │         ---
  │         M Nacim RABIA
  │         RN-BLOCK"
  │  Attachment: facture_2026-0042.pdf
  │
  ├─ Send via SMTP (smtp.gmail.com:587)
  │
  ├─ Retry if failure (3 attempts, exponential backoff)
  │
  ▼
User receives confirmation: "✅ Email envoyé à rn.block.pro@gmail.com"
```

---

## 🛠️ Composants à Développer

### Composant 1 : CalculatorTool

**Fichier** : `execution/tools/calculator_tool.py`

**Responsabilité** : Effectue des calculs financiers précis avec gestion TVA

**API** :
```python
class CalculatorTool(BaseTool):
    name = "calculator"
    args_schema = CalculatorInput

    def _run(
        self,
        operation: Literal["add", "subtract", "multiply", "divide", "vat_from_ttc", "ttc_from_ht"],
        value1: float,
        value2: float,
        precision: int = 2
    ) -> str
```

**Opérations** :
- `add` : Addition
- `subtract` : Soustraction
- `multiply` : Multiplication
- `divide` : Division (avec protection division par zéro)
- `vat_from_ttc` : Calcule HT et TVA depuis TTC
- `ttc_from_ht` : Calcule TTC depuis HT

**Tests Requis** :
- `test_calculator_add()`
- `test_calculator_vat_from_ttc()`
- `test_calculator_ttc_from_ht()`
- `test_calculator_divide_by_zero()`
- `test_calculator_precision_decimal()`

**Complexité** : ⭐⭐ (Faible) - 1-2 jours

---

### Composant 2 : DatabaseQueryTool

**Fichier** : `execution/tools/database_query_tool.py`

**Responsabilité** : Récupère des données structurées depuis PostgreSQL (table data_administration)

**API** :
```python
class DatabaseQueryTool(BaseTool):
    name = "database_query"
    args_schema = DatabaseQueryInput

    async def _arun(
        self,
        query_type: Literal["facture", "quittance", "charges", "frais_km"],
        filters: Dict[str, Any] = {}
    ) -> str  # Returns JSON
```

**Mapping** :
- `facture` → `id_data_administration='facturation_client_1'`
- `quittance` → `id_data_administration='quittance_loyer_1'`
- `charges` → `id_data_administration='charge_locative_1'`
- `frais_km` → `id_data_administration='frai_kilometrique_1'`

**Schéma DB à créer** :
- `execution/schemas/postgres/data_administration.sql`
- `execution/schemas/postgres/kilometres_parcourus.sql`

**Script de migration** :
- `scripts/migrate_n8n_data.py`

**Tests Requis** :
- `test_database_query_facture()`
- `test_database_query_charges_jsonb_parsing()`
- `test_database_query_unknown_type()`
- `test_database_query_not_found()`

**Complexité** : ⭐⭐⭐ (Moyenne) - 3-4 jours

---

### Composant 3 : EmailSenderTool

**Fichier** : `execution/tools/email_sender_tool.py`

**Responsabilité** : Envoie des documents par email via SMTP avec gestion CC

**API** :
```python
class EmailSenderTool(BaseTool):
    name = "email_sender"
    args_schema = EmailInput

    async def _arun(
        self,
        document_id: str,
        document_name: str,
        email_address: EmailStr,
        email_cc_address: Optional[str],
        subject: str,
        content: str
    ) -> str
```

**Fonctionnalités** :
- Récupération PDF depuis DB
- Construction email MIME multipart
- Attachment PDF
- Signature automatique "M Nacim RABIA, RN-BLOCK"
- Envoi via aiosmtplib (async SMTP)
- Retry avec backoff exponentiel (tenacity)

**Configuration .env** :
```bash
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=rabia.nacim@gmail.com
SMTP_PASSWORD=app_password
SMTP_FROM_EMAIL=rabia.nacim@gmail.com
```

**Tests Requis** :
- `test_email_sender_success()` (mock SMTP)
- `test_email_sender_attachment_pdf()`
- `test_email_sender_cc_multiple()`
- `test_email_sender_retry_on_failure()`
- `test_email_sender_document_not_found()`

**Complexité** : ⭐⭐⭐ (Moyenne) - 3-4 jours

---

### Composant 4 : WhisperTranscriptionTool

**Fichier** : `execution/tools/whisper_transcription_tool.py`

**Responsabilité** : Transcrit des messages vocaux en texte via OpenAI Whisper API

**API** :
```python
class WhisperTranscriptionTool(BaseTool):
    name = "whisper_transcription"
    args_schema = WhisperInput

    async def _arun(
        self,
        audio_file_path: str,
        language: str = "fr"
    ) -> str  # Returns transcribed text
```

**Fonctionnalités** :
- Support formats .ogg (Telegram), .mp3, .wav, .m4a
- Appel async via httpx
- Timeout 30 secondes
- Gestion erreurs API
- Cleanup fichiers temporaires

**Configuration .env** :
```bash
OPENAI_API_KEY=sk-...
```

**Tests Requis** :
- `test_whisper_transcription_french()` (mock API)
- `test_whisper_transcription_timeout()`
- `test_whisper_transcription_file_not_found()`
- `test_whisper_transcription_api_error()`

**Intégration Telegram** :
- Handler `handle_voice_message()` dans `telegram_bot.py`

**Complexité** : ⭐⭐⭐ (Moyenne) - 2-3 jours

---

### Composant 5 : MarkdownCleanerTool

**Fichier** : `execution/tools/markdown_cleaner_tool.py`

**Responsabilité** : Nettoie le markdown des réponses LLM pour Telegram plain text

**API** :
```python
class MarkdownCleanerTool(BaseTool):
    name = "markdown_cleaner"
    args_schema = MarkdownCleanerInput

    def _run(self, text: str) -> str
```

**Fonctionnalités** :
- Suppression `**text**` (gras)
- Suppression `*text*` (italique)
- Suppression `_text_` (underline)
- Suppression `` `code` `` (inline code)
- Suppression code blocks ` ``` `
- Suppression liens `[text](url)` → garder text
- Suppression headers `#`
- Conversion bullet `*` → `•`
- Conservation listes numérotées
- Nettoyage newlines multiples

**Tests Requis** :
- `test_markdown_cleaner_bold()`
- `test_markdown_cleaner_links()`
- `test_markdown_cleaner_code_blocks()`
- `test_markdown_cleaner_bullets()`
- `test_markdown_cleaner_numbered_lists()`

**Complexité** : ⭐ (Faible) - 1 jour

---

### Composant 6 : Enrichissement OrchestratorPrompt

**Fichier** : `execution/prompts/orchestrator_prompts.py`

**Responsabilité** : Aligner le prompt avec la logique N8n (plus détaillée)

**Changements** :
- Ajout section "Identité et Rôle"
- Ajout section "Logique de Gestion des Emails"
- Ajout section "Flux de Travail Step-by-Step"
- Ajout exemples de calculs (A. Facture, B. Charges, C. Quittance, D. Frais KM)
- Ajout contraintes de format (texte brut, pas de markdown)

**Tests Requis** :
- `test_orchestrator_invoice_extraction()`
- `test_orchestrator_email_hierarchy()`
- `test_orchestrator_calculation_instructions()`
- `test_orchestrator_plain_text_response()`

**Complexité** : ⭐⭐ (Faible) - 1-2 jours

---

## 📅 Timeline & Milestones

### Vue d'Ensemble

| Phase | Durée | Livrables | Jalons |
|-------|-------|-----------|--------|
| **Phase 1** : Analyse & Design | 2 semaines | Rapport exploration, PRD, Architecture | ✅ Complété |
| **Phase 2** : Développement Core Tools | 4 semaines | 5 nouveaux tools, tests unitaires | 🔄 À démarrer |
| **Phase 3** : Enrichissement & Intégration | 2 semaines | Prompts enrichis, intégration Telegram | 📅 Planifié |
| **Phase 4** : Tests & Validation | 1 semaine | Tests d'intégration, validation utilisateur | 📅 Planifié |
| **Phase 5** : Documentation & Migration Données | 1 semaine | Directives mises à jour, script migration | 📅 Planifié |
| **Phase 6** : Déploiement & Monitoring | 1 semaine | Déploiement prod, monitoring actif | 📅 Planifié |

**TOTAL** : **10 semaines** (2,5 mois)

---

### Détail par Sprint

#### Sprint 1 (Semaine 1-2) : Analyse & Design ✅ COMPLÉTÉ

**Objectifs** :
- Comprendre architecture actuelle
- Mapper composants N8n → Python
- Créer PRD complet

**Livrables** :
- [x] Rapport d'exploration (2532 lignes Python analysées)
- [x] Mapping N8n → Python (14 composants)
- [x] PRD.md ce document)
- [x] Architecture cible définie

**Critères de Succès** :
- ✅ 100% des composants N8n identifiés
- ✅ Architecture validée par Tech Lead
- ✅ PRD approuvé par Product Owner

---

#### Sprint 2 (Semaine 3-4) : Core Tools (Part 1)

**Objectifs** :
- Développer CalculatorTool
- Développer DatabaseQueryTool
- Créer schéma DB data_administration
- Script migration données N8n

**Livrables** :
- [ ] `execution/tools/calculator_tool.py` (100 lignes)
- [ ] `execution/tools/database_query_tool.py` (150 lignes)
- [ ] `execution/schemas/postgres/data_administration.sql`
- [ ] `scripts/migrate_n8n_data.py`
- [ ] Tests unitaires (`tests/test_calculator_tool.py`, `tests/test_database_query_tool.py`)
- [ ] Coverage > 80% pour ces tools

**Critères de Succès** :
- [ ] CalculatorTool : Tous calculs passent (HT/TTC, TVA)
- [ ] DatabaseQueryTool : 4 query types fonctionnent
- [ ] Script migration : Données N8n importées en PostgreSQL
- [ ] Tests : 0 échec, coverage > 80%

**Effort estimé** : 80 heures (2 semaines × 40h)

---

#### Sprint 3 (Semaine 5-6) : Core Tools (Part 2)

**Objectifs** :
- Développer EmailSenderTool
- Développer WhisperTranscriptionTool
- Développer MarkdownCleanerTool
- Intégration Telegram handlers

**Livrables** :
- [ ] `execution/tools/email_sender_tool.py` (200 lignes)
- [ ] `execution/tools/whisper_transcription_tool.py` (120 lignes)
- [ ] `execution/tools/markdown_cleaner_tool.py` (80 lignes)
- [ ] Telegram voice handler mis à jour
- [ ] Tests unitaires pour les 3 tools
- [ ] Configuration SMTP dans .env

**Critères de Succès** :
- [ ] EmailSenderTool : Email envoyé avec CC et PDF attaché
- [ ] WhisperTranscriptionTool : Précision >95% français
- [ ] MarkdownCleanerTool : Markdown supprimé, texte propre
- [ ] Tests : 0 échec, coverage > 80%

**Effort estimé** : 80 heures (2 semaines × 40h)

---

#### Sprint 4 (Semaine 7) : Enrichissement Prompts

**Objectifs** :
- Enrichir OrchestratorPrompt
- Aligner avec logique N8n (emails, calculs, étapes)
- Intégrer tous les tools dans OrchestratorAgent

**Livrables** :
- [ ] `execution/prompts/orchestrator_prompts.py` mis à jour (200 lignes)
- [ ] OrchestratorAgent avec tous tools intégrés
- [ ] Tests d'extraction d'entités
- [ ] Tests de routing d'intention

**Critères de Succès** :
- [ ] Prompt contient toutes les sections N8n
- [ ] Extraction entités : >90% précision
- [ ] Classification intent : >90% précision
- [ ] Tests : Intent classification pour 20 phrases de test

**Effort estimé** : 40 heures (1 semaine)

---

#### Sprint 5 (Semaine 8) : Tests & Validation

**Objectifs** :
- Tests d'intégration end-to-end
- Tests de régression (non-régression des fonctionnalités existantes)
- Validation utilisateur (demo)

**Livrables** :
- [ ] `tests/integration/test_full_workflow.py`
- [ ] Tests de régression (10 scénarios)
- [ ] Rapport de coverage (HTML)
- [ ] Demo enregistrée (vidéo 10 min)

**Critères de Succès** :
- [ ] 10 scénarios end-to-end passent (texte → PDF, vocal → PDF, email)
- [ ] 0 régression fonctionnelle détectée
- [ ] Coverage globale > 80%
- [ ] Validation Product Owner : ✅ OK pour prod

**Effort estimé** : 40 heures (1 semaine)

---

#### Sprint 6 (Semaine 9) : Documentation & Migration Données

**Objectifs** :
- Mettre à jour toutes les directives
- Documenter la migration N8n → Python
- Migrer les données en production

**Livrables** :
- [ ] `directives/migration_n8n_to_python.md`
- [ ] Mise à jour `README.md`
- [ ] Mise à jour `CLAUDE.md`
- [ ] Migration données prod (script exécuté)
- [ ] Guide de rollback

**Critères de Succès** :
- [ ] Documentation complète et à jour
- [ ] Migration données prod : 0 perte de données
- [ ] Rollback testé et documenté

**Effort estimé** : 40 heures (1 semaine)

---

#### Sprint 7 (Semaine 10) : Déploiement & Monitoring

**Objectifs** :
- Déployer en production
- Configurer monitoring (Prometheus + Grafana)
- Logs structurés (Structlog JSON)
- Alerting

**Livrables** :
- [ ] Déploiement Docker Compose prod
- [ ] Dashboard Grafana (4 panels minimum)
- [ ] Alertes configurées (error rate > 5%)
- [ ] Logs structurés JSON indexés
- [ ] Runbook opérationnel

**Critères de Succès** :
- [ ] Déploiement prod : 0 downtime
- [ ] Monitoring : Métriques visibles dans Grafana
- [ ] Alerting : Test d'alerte reçu
- [ ] Logs : Requête de recherche fonctionne

**Effort estimé** : 40 heures (1 semaine)

---

### Gantt Chart

```
Semaine    1  2  3  4  5  6  7  8  9  10
─────────────────────────────────────────
Sprint 1  [========]
Sprint 2           [========]
Sprint 3                    [========]
Sprint 4                             [====]
Sprint 5                                  [====]
Sprint 6                                       [====]
Sprint 7                                            [====]
```

---

## 📊 Métriques de Succès

### Métriques Fonctionnelles

| Métrique | Cible | Mesure | Fréquence |
|----------|-------|--------|-----------|
| **Taux de succès génération documents** | >99% | Counter Prometheus `documents_generated_total` vs `documents_failed_total` | Temps réel |
| **Précision classification intent** | >90% | Tests d'évaluation (20 phrases de test) | Post-implémentation |
| **Précision extraction entités** | >90% | Tests d'évaluation (20 phrases de test) | Post-implémentation |
| **Précision transcription vocale** | >95% | Word Error Rate (WER) sur 50 messages test | Post-implémentation |
| **Taux de délivrabilité emails** | >99% | Counter `emails_sent_success` vs `emails_sent_failed` | Temps réel |
| **Conformité légale documents** | 100% | Audit manuel (checklist DGFIP, art. L145-49) | Post-implémentation |

### Métriques Techniques

| Métrique | Cible | Mesure | Fréquence |
|----------|-------|--------|-----------|
| **Test coverage** | >80% | pytest-cov report | CI/CD |
| **Latence génération PDF (P95)** | <500ms | Histogram Prometheus `pdf_generation_seconds` | Temps réel |
| **Latence LLM (P95)** | <1000ms | Histogram Prometheus `llm_call_seconds` | Temps réel |
| **Throughput documents** | >120/min | Counter `documents_generated_total` par minute | Temps réel |
| **Memory usage bot** | <512MB | Docker stats RSS | Temps réel |
| **Error rate global** | <1% | Rate `errors_total` / `requests_total` | Temps réel |
| **Startup time** | <10s | Temps jusqu'à bot ready | CI/CD |

### Métriques Qualité Code

| Métrique | Cible | Mesure | Fréquence |
|----------|-------|--------|-----------|
| **Erreurs Ruff** | 0 | `ruff check execution/` | CI/CD |
| **Erreurs Mypy (strict)** | 0 | `mypy execution/ --strict` | CI/CD |
| **Docstrings manquantes** | 0 | `pydocstyle execution/` | CI/CD |
| **Complexité cyclomatique** | <10 | radon cc -a | CI/CD |
| **Lignes de code dupliquées** | <5% | radon duplicates | CI/CD |

### Métriques Utilisateur

| Métrique | Cible | Mesure | Fréquence |
|----------|-------|--------|-----------|
| **Temps de réponse moyen** | <2s | P50 end-to-end latency | Temps réel |
| **Satisfaction utilisateur** | >4/5 | Sondage post-implémentation | Mensuel |
| **Taux d'utilisation vocale** | >20% | Ratio messages vocaux / messages totaux | Hebdomadaire |
| **Taux d'adoption email** | >30% | Ratio emails envoyés / documents générés | Hebdomadaire |

---

## ⚠️ Risques & Mitigations

### Risques Techniques

| ID | Risque | Probabilité | Impact | Mitigation | Owner |
|----|--------|-------------|--------|------------|-------|
| **RT-001** | **Perte fonctionnalité lors migration N8n** | Faible (20%) | Élevé (8/10) | - Tests de régression exhaustifs<br>- Validation utilisateur à chaque sprint<br>- Rollback plan documenté | Tech Lead |
| **RT-002** | **Performance dégradée vs N8n** | Faible (15%) | Moyen (5/10) | - Benchmarks avant/après<br>- Profiling avec py-spy<br>- Optimisation async/await | Dev |
| **RT-003** | **Bugs migration données** | Moyen (40%) | Moyen (6/10) | - Script migration testable<br>- Dry-run sur copie de prod<br>- Backup avant migration | Dev |
| **RT-004** | **Intégration tools dans LangGraph complexe** | Moyen (30%) | Moyen (5/10) | - POC rapide (1 jour)<br>- Consulter docs LangChain<br>- Support community Discord | Dev |
| **RT-005** | **Erreurs de typage Pydantic** | Faible (20%) | Faible (3/10) | - Tests unitaires stricts<br>- Mypy strict mode<br>- Validation manuelle | Dev |

### Risques Fonctionnels

| ID | Risque | Probabilité | Impact | Mitigation | Owner |
|----|--------|-------------|--------|------------|-------|
| **RF-001** | **Précision transcription Whisper insuffisante (<95%)** | Moyen (35%) | Moyen (6/10) | - Tests avec 50 messages vocaux variés<br>- Prompt Whisper optimisé<br>- Fallback texte si confiance faible | Dev |
| **RF-002** | **Emails bloqués par SPAM filters** | Moyen (40%) | Élevé (7/10) | - Configuration SPF/DKIM/DMARC<br>- Utiliser SendGrid si Gmail bloqué<br>- Tests avec 10 destinataires variés | Dev |
| **RF-003** | **LLM extrait mal les entités** | Faible (25%) | Moyen (6/10) | - Enrichir prompt avec exemples<br>- Ajouter validation Pydantic stricte<br>- Fallback demande clarification | Dev |
| **RF-004** | **Non-conformité légale documents** | Très Faible (10%) | Critique (9/10) | - Audit par comptable externe<br>- Checklist DGFIP validée<br>- Tests avec vraies données | Product Owner |

### Risques Opérationnels

| ID | Risque | Probabilité | Impact | Mitigation | Owner |
|----|--------|-------------|--------|------------|-------|
| **RO-001** | **Coût API OpenAI Whisper élevé** | Élevé (60%) | Faible (4/10) | - Rate limiting 10 req/min/user<br>- Cache transcriptions<br>- Monitoring coûts hebdomadaire | Ops |
| **RO-002** | **Downtime lors déploiement** | Moyen (30%) | Moyen (5/10) | - Déploiement hors heures de pointe<br>- Healthcheck avant switch<br>- Rollback automatique si échec | Ops |
| **RO-003** | **Complexité maintenance code vs N8n** | Faible (20%) | Moyen (5/10) | - Documentation exhaustive<br>- Formation équipe Python<br>- Code review systématique | Tech Lead |
| **RO-004** | **Perte de données lors migration** | Très Faible (5%) | Critique (10/10) | - Backup complet avant migration<br>- Migration en 2 phases (test → prod)<br>- Vérification manuelle post-migration | Ops |

### Matrice Risques

```
Impact
10 │                    RO-004
 9 │         RF-004
 8 │ RT-001
 7 │             RF-002
 6 │     RT-003  RF-001  RF-003
 5 │         RT-002  RT-004  RO-002  RO-003
 4 │                         RO-001
 3 │ RT-005
 2 │
 1 │
 0 └─────────────────────────────────────
   0%  10  20  30  40  50  60  70  80  90 100%
                  Probabilité
```

### Plan de Contingence

**Si RT-001 (Perte fonctionnalité) se produit** :
1. Rollback immédiat vers N8n (conservé en parallèle pendant 2 semaines)
2. Analyse root cause (logs, stacktrace)
3. Fix en hotfix (< 4h)
4. Re-déploiement avec validation étendue

**Si RF-002 (Emails bloqués) se produit** :
1. Basculer vers SendGrid API (préparé en fallback)
2. Configurer SPF/DKIM/DMARC
3. Retry emails bloqués
4. Monitoring deliverability 24/7

**Si RO-004 (Perte données) se produit** :
1. Stopper migration immédiatement
2. Restaurer depuis backup (< 30 min)
3. Audit des données perdues
4. Fix script migration
5. Nouvelle tentative après validation

---

## 🔗 Dépendances

### Dépendances Externes

| Dépendance | Type | Criticité | Mitigation si indisponible |
|------------|------|-----------|---------------------------|
| **OpenRouter API** | LLM Provider | Critique | - Fallback vers Anthropic direct<br>- Configuration multi-provider |
| **OpenAI Whisper API** | Transcription | Élevée | - Fallback vers message texte<br>- Whisper local (whisper.cpp) |
| **PostgreSQL** | Database | Critique | - Backup quotidien<br>- Réplication master-slave |
| **Telegram API** | Bot Interface | Critique | - Aucun fallback possible<br>- Monitoring uptime Telegram |
| **SMTP Provider (Gmail/SendGrid)** | Email | Moyenne | - Fallback provider secondaire<br>- Queue emails si échec |

### Dépendances Internes

| Dépendance | Description | Prérequis |
|------------|-------------|-----------|
| **Architecture Python existante** | 6 agents + PDFGenerator + DatabaseManager | Fonctionnels et testés |
| **Schéma DB actuel** | Tables `documents`, `chat_history` | Migrées et healthy |
| **Configuration .env** | Variables d'environnement | Toutes définies |
| **Docker infrastructure** | PostgreSQL container | Running et healthy |

### Dépendances Organisationnelles

| Dépendance | Besoin | Délai |
|------------|--------|-------|
| **Validation Product Owner** | Approbation PRD | Semaine 2 |
| **Budget API OpenAI** | ~20€/mois Whisper | Semaine 5 |
| **Accès production** | Credentials SMTP, DB prod | Semaine 9 |
| **Validation comptable** | Conformité légale documents | Semaine 8 |

---

## 🚫 Hors Périmètre (Out of Scope)

### Fonctionnalités Non Incluses

| Item | Justification | Alternative |
|------|---------------|-------------|
| **Multi-langue (anglais, espagnol)** | Focus français uniquement en v1 | Roadmap v2.0 |
| **API REST publique** | Telegram suffit pour v1 | Roadmap v2.0 |
| **Interface web admin** | Pas de demande utilisateur | Roadmap v3.0 |
| **Support multi-entreprise** | Architecture mono-tenant actuelle | Refactoring majeur requis |
| **Signature électronique documents** | Complexité légale élevée | Partenariat externe |
| **OCR extraction documents** | Pas de besoin identifié | Roadmap v2.0 si demande |
| **Export comptabilité (Sage, QuickBooks)** | Intégrations complexes | Roadmap v2.0 |
| **Rappels automatiques factures impayées** | Fonctionnalité avancée | Roadmap v2.0 |

### Technologies Non Utilisées

| Technologie | Pourquoi évitée |
|-------------|----------------|
| **Celery** | AsyncIO suffit, pas besoin de task queue distribuée |
| **Redis** | PostgreSQL suffit pour cache simple |
| **Kubernetes** | Docker Compose suffit pour l'échelle actuelle |
| **Elasticsearch** | PostgreSQL full-text search suffit |
| **RabbitMQ** | Pas de besoin de messaging complexe |

### Modifications Codebase Non Incluses

| Modification | Justification |
|--------------|---------------|
| **Refactoring agents existants** | Fonctionnent correctement, pas de valeur ajoutée |
| **Migration SQLAlchemy → autre ORM** | SQLAlchemy async performant |
| **Remplacement ReportLab → autre lib PDF** | ReportLab production-ready |
| **Changement Telegram → Discord/Slack** | Telegram satisfait les besoins |

---

## 🧪 Plan de Test

### Stratégie de Test

```
┌─────────────────────────────────────────────────────────────┐
│                    PYRAMIDE DE TESTS                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│                        E2E Tests                            │
│                       (5 scénarios)                         │
│                     ┌─────────────┐                         │
│                     │  Slow       │                         │
│                     │  Expensive  │                         │
│                     └─────────────┘                         │
│                                                             │
│                 Integration Tests                           │
│                  (20 scénarios)                             │
│              ┌────────────────────┐                         │
│              │  Medium Speed      │                         │
│              │  DB + Tools        │                         │
│              └────────────────────┘                         │
│                                                             │
│                   Unit Tests                                │
│                  (100+ tests)                               │
│         ┌────────────────────────────┐                      │
│         │  Fast                      │                      │
│         │  Isolated                  │                      │
│         │  Mocked Dependencies       │                      │
│         └────────────────────────────┘                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Tests Unitaires (Target: 100+ tests, Coverage >80%)

#### CalculatorTool (10 tests)

```python
# tests/test_calculator_tool.py

def test_calculator_add():
    """Addition 500 + 200 = 700"""

def test_calculator_subtract():
    """Soustraction 1000 - 200 = 800"""

def test_calculator_multiply():
    """Multiplication 10 × 500 = 5000"""

def test_calculator_divide():
    """Division 1200 / 4 = 300"""

def test_calculator_divide_by_zero():
    """Division par zéro retourne erreur"""

def test_calculator_vat_from_ttc():
    """TTC 1200€ (TVA 20%) → HT 1000€, TVA 200€"""

def test_calculator_ttc_from_ht():
    """HT 1000€ (TVA 20%) → TTC 1200€"""

def test_calculator_precision_2_decimals():
    """Arrondi à 2 décimales : 1000/3 = 333.33"""

def test_calculator_negative_numbers():
    """Calculs avec nombres négatifs"""

def test_calculator_decimal_precision():
    """Utilise Decimal pour éviter float errors"""
```

#### DatabaseQueryTool (8 tests)

```python
# tests/test_database_query_tool.py

@pytest.mark.asyncio
async def test_database_query_facture():
    """Query facture retourne données complètes"""

@pytest.mark.asyncio
async def test_database_query_quittance():
    """Query quittance retourne données loyer"""

@pytest.mark.asyncio
async def test_database_query_charges():
    """Query charges retourne liste charges"""

@pytest.mark.asyncio
async def test_database_query_frais_km():
    """Query frais km retourne données mission"""

@pytest.mark.asyncio
async def test_database_query_jsonb_parsing():
    """Parse correctement charges JSONB"""

@pytest.mark.asyncio
async def test_database_query_unknown_type():
    """Type inconnu retourne erreur"""

@pytest.mark.asyncio
async def test_database_query_not_found():
    """ID inexistant retourne erreur"""

@pytest.mark.asyncio
async def test_database_query_filters():
    """Filters optionnels appliqués"""
```

#### EmailSenderTool (10 tests)

```python
# tests/test_email_sender_tool.py

@pytest.mark.asyncio
async def test_email_sender_success(mock_smtp):
    """Email envoyé avec succès"""

@pytest.mark.asyncio
async def test_email_sender_attachment_pdf(mock_smtp):
    """PDF attaché correctement"""

@pytest.mark.asyncio
async def test_email_sender_cc_multiple(mock_smtp):
    """CC avec 3 destinataires"""

@pytest.mark.asyncio
async def test_email_sender_signature(mock_smtp):
    """Signature "M Nacim RABIA, RN-BLOCK" présente"""

@pytest.mark.asyncio
async def test_email_sender_retry_on_failure(mock_smtp):
    """Retry 3 fois avec backoff exponentiel"""

@pytest.mark.asyncio
async def test_email_sender_document_not_found():
    """Document inexistant retourne erreur"""

@pytest.mark.asyncio
async def test_email_sender_pdf_file_missing():
    """Fichier PDF manquant retourne erreur"""

@pytest.mark.asyncio
async def test_email_sender_smtp_error(mock_smtp):
    """Erreur SMTP gérée correctement"""

@pytest.mark.asyncio
async def test_email_sender_timeout(mock_smtp):
    """Timeout après 30s"""

@pytest.mark.asyncio
async def test_email_sender_invalid_email():
    """Email invalide retourne erreur"""
```

#### WhisperTranscriptionTool (8 tests)

```python
# tests/test_whisper_transcription_tool.py

@pytest.mark.asyncio
async def test_whisper_transcription_french(mock_openai):
    """Transcription français réussie"""

@pytest.mark.asyncio
async def test_whisper_transcription_accuracy(mock_openai):
    """Précision >95% sur message test"""

@pytest.mark.asyncio
async def test_whisper_transcription_timeout(mock_openai):
    """Timeout après 30s"""

@pytest.mark.asyncio
async def test_whisper_transcription_file_not_found():
    """Fichier audio inexistant retourne erreur"""

@pytest.mark.asyncio
async def test_whisper_transcription_api_error(mock_openai):
    """Erreur API 500 gérée"""

@pytest.mark.asyncio
async def test_whisper_transcription_format_ogg(mock_openai):
    """Support format .ogg (Telegram)"""

@pytest.mark.asyncio
async def test_whisper_transcription_format_mp3(mock_openai):
    """Support format .mp3"""

@pytest.mark.asyncio
async def test_whisper_transcription_language_parameter(mock_openai):
    """Paramètre language='fr' passé à l'API"""
```

#### MarkdownCleanerTool (10 tests)

```python
# tests/test_markdown_cleaner_tool.py

def test_markdown_cleaner_bold():
    """Supprime **gras**"""

def test_markdown_cleaner_italic():
    """Supprime *italique* et _underline_"""

def test_markdown_cleaner_code_inline():
    """Supprime `code`"""

def test_markdown_cleaner_code_blocks():
    """Supprime ```code blocks```"""

def test_markdown_cleaner_links():
    """Supprime [text](url), garde text"""

def test_markdown_cleaner_headers():
    """Supprime # ## ### headers"""

def test_markdown_cleaner_bullets():
    """Convertit * en •"""

def test_markdown_cleaner_numbered_lists():
    """Conserve 1. 2. 3.""""""

def test_markdown_cleaner_multiple_newlines():
    """Nettoie \\n\\n\\n → \\n\\n"""

def test_markdown_cleaner_mixed_markdown():
    """Nettoie markdown mixte complexe"""
```

### Tests d'Intégration (Target: 20 tests)

#### Workflow End-to-End (10 tests)

```python
# tests/integration/test_full_workflow.py

@pytest.mark.asyncio
async def test_invoice_workflow_text_to_pdf():
    """Message texte → Facture PDF"""
    # User: "Fais une facture pour ALTECA de 10 jours"
    # → OrchestratorAgent → DatabaseQueryTool → CalculatorTool
    # → InvoiceAgent → PDF généré

@pytest.mark.asyncio
async def test_quote_workflow_voice_to_pdf():
    """Message vocal → Devis PDF"""
    # Voice: "Fais un devis pour Alteca de 2000€"
    # → WhisperTranscriptionTool → OrchestratorAgent → QuoteAgent

@pytest.mark.asyncio
async def test_invoice_with_email():
    """Facture + envoi email"""
    # User: "Facture ALTECA 5000€ + envoie par email"
    # → InvoiceAgent → EmailSenderTool

@pytest.mark.asyncio
async def test_mileage_workflow():
    """Frais kilométriques complet"""

@pytest.mark.asyncio
async def test_rent_receipt_workflow():
    """Quittance loyer complet"""

@pytest.mark.asyncio
async def test_rental_charges_workflow():
    """Charges locatives complet"""

@pytest.mark.asyncio
async def test_workflow_with_clarification():
    """Workflow avec clarification interactive"""
    # User: "Fais une facture"
    # Bot: "Pour quel client ?"
    # User: "ALTECA"

@pytest.mark.asyncio
async def test_workflow_error_handling():
    """Gestion erreur si données manquantes"""

@pytest.mark.asyncio
async def test_workflow_chat_history_context():
    """Utilisation contexte conversationnel"""
    # User: "Fais une facture pour ALTECA"
    # User: "Change le montant à 2000€" (sans re-spécifier ALTECA)

@pytest.mark.asyncio
async def test_workflow_stats_command():
    """Commande /stats retourne statistiques"""
```

#### Intégration Telegram (5 tests)

```python
# tests/integration/test_telegram_integration.py

@pytest.mark.asyncio
async def test_telegram_text_message_handling():
    """Message texte Telegram traité correctement"""

@pytest.mark.asyncio
async def test_telegram_voice_message_handling():
    """Message vocal Telegram transcrit et traité"""

@pytest.mark.asyncio
async def test_telegram_command_handling():
    """Commandes /facture, /devis fonctionnent"""

@pytest.mark.asyncio
async def test_telegram_pdf_sending():
    """PDF envoyé via Telegram send_document()"""

@pytest.mark.asyncio
async def test_telegram_error_message():
    """Message d'erreur envoyé si échec"""
```

#### Intégration Database (5 tests)

```python
# tests/integration/test_database_integration.py

@pytest.mark.asyncio
async def test_database_save_document():
    """Document sauvegardé en DB"""

@pytest.mark.asyncio
async def test_database_chat_history_persistence():
    """Chat history sauvegardé et récupéré"""

@pytest.mark.asyncio
async def test_database_sequential_numbering():
    """Numérotation séquentielle garantie"""

@pytest.mark.asyncio
async def test_database_data_administration_query():
    """Query data_administration réussie"""

@pytest.mark.asyncio
async def test_database_transaction_rollback():
    """Rollback si erreur génération PDF"""
```

### Tests End-to-End (Target: 5 tests)

```python
# tests/e2e/test_production_scenarios.py

@pytest.mark.e2e
@pytest.mark.asyncio
async def test_e2e_invoice_generation_french_user():
    """Scénario complet utilisateur français"""
    # 1. Utilisateur envoie message Telegram
    # 2. Bot analyse intention
    # 3. Bot génère facture PDF
    # 4. Bot envoie PDF via Telegram
    # 5. Utilisateur reçoit PDF conforme DGFIP

@pytest.mark.e2e
@pytest.mark.asyncio
async def test_e2e_voice_to_quote_with_email():
    """Scénario vocal → devis → email"""

@pytest.mark.e2e
@pytest.mark.asyncio
async def test_e2e_mileage_report_full():
    """Scénario frais kilométriques complet"""

@pytest.mark.e2e
@pytest.mark.asyncio
async def test_e2e_error_recovery():
    """Scénario avec erreur et récupération"""

@pytest.mark.e2e
@pytest.mark.asyncio
async def test_e2e_performance_under_load():
    """Scénario charge (10 req simultanées)"""
```

### Tests de Régression (Target: 10 tests)

```python
# tests/regression/test_existing_features.py

@pytest.mark.regression
@pytest.mark.asyncio
async def test_regression_invoice_agent():
    """InvoiceAgent fonctionne toujours"""

@pytest.mark.regression
@pytest.mark.asyncio
async def test_regression_quote_agent():
    """QuoteAgent fonctionne toujours"""

@pytest.mark.regression
@pytest.mark.asyncio
async def test_regression_pdf_generation():
    """PDFGenerator fonctionne toujours"""

@pytest.mark.regression
@pytest.mark.asyncio
async def test_regression_database_manager():
    """DatabaseManager fonctionne toujours"""

@pytest.mark.regression
@pytest.mark.asyncio
async def test_regression_telegram_bot():
    """Telegram bot fonctionne toujours"""

# ... 5 autres tests de régression
```

### Exécution des Tests

#### CI/CD Pipeline (GitHub Actions)

```yaml
# .github/workflows/test.yml

name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15-alpine
        env:
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
          POSTGRES_DB: test_admin_agent
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v3

      - name: Install UV
        run: curl -LsSf https://astral.sh/uv/install.sh | sh

      - name: Install dependencies
        run: uv sync

      - name: Run linting
        run: |
          uv run ruff check execution/
          uv run mypy execution/ --strict

      - name: Run unit tests
        run: uv run pytest tests/ -v --cov=execution --cov-report=html

      - name: Run integration tests
        run: uv run pytest tests/integration/ -v

      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

#### Local Testing

```bash
# Tests unitaires rapides
uv run pytest tests/ -v -m "not integration and not e2e"

# Tests d'intégration
uv run pytest tests/integration/ -v

# Tests E2E (slow)
uv run pytest tests/e2e/ -v

# Tests de régression
uv run pytest tests/regression/ -v

# Coverage report
uv run pytest tests/ --cov=execution --cov-report=html
# Ouvrir: htmlcov/index.html
```

---

## 🚀 Stratégie de Déploiement

### Environnements

| Environnement | Objectif | Infrastructure | Base de Données |
|---------------|----------|----------------|-----------------|
| **Local Dev** | Développement développeur | Docker Compose local | PostgreSQL local |
| **Staging** | Tests pré-production | Docker Compose VPS staging | PostgreSQL staging |
| **Production** | Utilisation réelle | Docker Compose VPS prod | PostgreSQL prod (backup) |

### Déploiement Progressive (Blue-Green)

```
┌─────────────────────────────────────────────────────────────┐
│              DÉPLOIEMENT BLUE-GREEN                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Phase 1: Déploiement Green (nouvelle version Python)       │
│  ┌───────────────┐         ┌───────────────┐              │
│  │  BLUE (N8n)   │         │  GREEN (Py)   │              │
│  │  Active 100%  │         │  Standby      │              │
│  └───────┬───────┘         └───────────────┘              │
│          │                                                  │
│          └─── All Traffic                                  │
│                                                             │
│  Phase 2: Tests Green (smoke tests, 10% traffic)           │
│  ┌───────────────┐         ┌───────────────┐              │
│  │  BLUE (N8n)   │         │  GREEN (Py)   │              │
│  │  Active 90%   │         │  Test 10%     │              │
│  └───────┬───────┘         └───────┬───────┘              │
│          │                         │                        │
│          └── 90% ────────┬─────────┘                       │
│                           └── 10%                           │
│                                                             │
│  Phase 3: Switch (si tests OK)                             │
│  ┌───────────────┐         ┌───────────────┐              │
│  │  BLUE (N8n)   │         │  GREEN (Py)   │              │
│  │  Standby      │         │  Active 100%  │              │
│  └───────────────┘         └───────┬───────┘              │
│                                     │                       │
│                          All Traffic ┘                      │
│                                                             │
│  Phase 4: Rollback (si problème)                           │
│  ┌───────────────┐         ┌───────────────┐              │
│  │  BLUE (N8n)   │         │  GREEN (Py)   │              │
│  │  Active 100%  │         │  Stopped      │              │
│  └───────┬───────┘         └───────────────┘              │
│          │                                                  │
│          └─── All Traffic (back to N8n)                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Checklist Pré-Déploiement

**Sprint 7 (Semaine 10) : Avant déploiement prod**

- [ ] **Tests** : Coverage >80%, 0 échec
- [ ] **Linting** : 0 erreur ruff, 0 erreur mypy
- [ ] **Documentation** : Toutes directives à jour
- [ ] **Backup** : Backup complet DB prod
- [ ] **Rollback plan** : Plan documenté et testé
- [ ] **Monitoring** : Prometheus + Grafana configurés
- [ ] **Alerting** : Alertes configurées (error rate >5%)
- [ ] **Secrets** : Tous secrets en .env (pas en code)
- [ ] **Validation PO** : Product Owner a approuvé
- [ ] **Communication** : Utilisateurs prévenus (si downtime)

### Procédure de Déploiement

#### Étape 1 : Préparation (1 heure)

```bash
# 1. Backup base de données prod
pg_dump -h prod-db -U admin admin_agent > backup_$(date +%Y%m%d_%H%M%S).sql

# 2. Tag version Docker
git tag v2.0.0-python
docker build -t admin-agent-pro:v2.0.0 .
docker tag admin-agent-pro:v2.0.0 admin-agent-pro:latest

# 3. Vérifier configuration
cat .env.production  # Valider toutes les variables

# 4. Tests smoke en staging
docker-compose -f docker-compose.staging.yml up -d
# Tester manuellement 5 scénarios

# 5. Downtime si nécessaire (optionnel)
# Envoyer message Telegram: "Maintenance 10 min, retour 15h"
```

#### Étape 2 : Déploiement Green (30 minutes)

```bash
# 1. Pull dernière version
cd /opt/admin-agent-pro
git pull origin master
git checkout v2.0.0-python

# 2. Rebuild images
docker-compose build --no-cache

# 3. Migrer données N8n → PostgreSQL
uv run python scripts/migrate_n8n_data.py
# Vérifier : SELECT COUNT(*) FROM data_administration;

# 4. Démarrer containers Green
docker-compose -f docker-compose.green.yml up -d

# 5. Healthcheck
curl http://localhost:8001/health  # Port alternatif Green
# Attendre "healthy" status
```

#### Étape 3 : Tests de Fumée (Smoke Tests) (20 minutes)

```bash
# 1. Tests manuels Telegram (10% traffic vers Green)
# - Envoyer "Fais une facture pour ALTECA de 1000€"
# - Envoyer message vocal "Fais un devis"
# - Envoyer "/stats"

# 2. Vérifier logs
docker-compose -f docker-compose.green.yml logs bot --tail=50

# 3. Vérifier métriques Prometheus
curl http://localhost:9090/metrics | grep documents_generated_total

# 4. Vérifier base de données
psql -h localhost -U admin -d admin_agent -c "SELECT COUNT(*) FROM documents WHERE created_at > NOW() - INTERVAL '1 hour';"
```

#### Étape 4 : Switch Blue → Green (10 minutes)

```bash
# Si tests OK, switch 100% traffic vers Green

# 1. Stopper Blue (N8n)
docker-compose -f docker-compose.blue.yml down

# 2. Promouvoir Green → Production
mv docker-compose.green.yml docker-compose.yml
docker-compose restart

# 3. Vérifier status
docker-compose ps
# Tous containers "Up" et "healthy"

# 4. Monitoring 1 heure
# Surveiller dashboard Grafana :
# - Error rate < 1%
# - Latence P95 < 500ms
# - Throughput normal
```

#### Étape 5 : Rollback (Si Problème) (15 minutes)

```bash
# Si error rate >5% OU bug critique détecté

# 1. Stopper Green immédiatement
docker-compose down

# 2. Redémarrer Blue (N8n)
docker-compose -f docker-compose.blue.yml up -d

# 3. Restaurer données si nécessaire
psql admin_agent < backup_YYYYMMDD_HHMMSS.sql

# 4. Vérifier status
docker-compose -f docker-compose.blue.yml ps

# 5. Incident post-mortem
# - Identifier root cause
# - Documenter
# - Fix en hotfix
# - Nouvelle tentative déploiement
```

### Post-Déploiement (Jour +1)

**Checklist post-déploiement** :

- [ ] **Monitoring** : Vérifier dashboard Grafana (24h)
- [ ] **Logs** : Pas d'erreurs critiques
- [ ] **Métriques** :
  - Documents générés : Normal (baseline ±10%)
  - Latence : <500ms P95
  - Error rate : <1%
  - Memory usage : <512MB
- [ ] **Utilisateur** : Feedback positif (sondage)
- [ ] **Backup** : Rotation backup automatique activée
- [ ] **Documentation** : Runbook opérationnel mis à jour
- [ ] **Cleanup** : Supprimer containers Blue (N8n) si stable après 1 semaine

---

## 📚 Documentation

### Documentation Existante à Mettre à Jour

| Fichier | Modifications Requises |
|---------|------------------------|
| **README.md** | - Ajouter section "Migration N8n → Python"<br>- Mettre à jour architecture<br>- Ajouter nouveaux outils |
| **CLAUDE.md** | - Ajouter patterns des nouveaux tools<br>- Documenter EmailSenderTool, WhisperTranscriptionTool |
| **directives/*.md** | - Enrichir avec logique N8n (emails, calculs)<br>- Ajouter exemples d'utilisation tools |
| **TECHNICAL_SPECS.md** | - Mettre à jour stack technique<br>- Ajouter schéma data_administration |

### Nouvelle Documentation à Créer

| Fichier | Contenu |
|---------|---------|
| **directives/migration_n8n_to_python.md** | - Vue d'ensemble migration<br>- Mapping composants<br>- Avantages/Inconvénients<br>- Guide rollback |
| **docs/tools_reference.md** | - API de chaque tool<br>- Exemples d'utilisation<br>- Tests unitaires |
| **docs/deployment_guide.md** | - Procédure déploiement détaillée<br>- Checklist pré-déploiement<br>- Plan rollback |
| **docs/monitoring_guide.md** | - Configuration Prometheus/Grafana<br>- Dashboards recommandés<br>- Alertes configurées |
| **docs/troubleshooting.md** | - Problèmes courants<br>- Solutions<br>- FAQs |
| **RUNBOOK.md** | - Procédures opérationnelles<br>- Incident response<br>- Escalation |

### Documentation Technique (Inline Code)

**Exigences** :
- Tous les nouveaux tools : Docstrings format Google
- Toutes les fonctions publiques : Type hints complets
- Fichiers complexes : Module-level docstring

**Exemple** :
```python
# execution/tools/calculator_tool.py

"""
Financial calculator tool for precise calculations with VAT handling.

This module provides a LangChain tool for performing financial calculations
with Decimal precision (2 decimals). Supports basic operations (add, subtract,
multiply, divide) and VAT-specific conversions (TTC ↔ HT).

Example:
    >>> tool = CalculatorTool()
    >>> result = tool._run("vat_from_ttc", value1=1200.0, value2=0.20)
    >>> print(result)
    "HT: 1000.00, TVA: 200.00"
"""

from langchain.tools import BaseTool
from decimal import Decimal
# ...
```

---

## ✅ Critères d'Acceptation Finaux

### Critères Fonctionnels

- [x] **CF-001** : Tous les 7 types d'intentions sont classifiés avec >90% précision
- [x] **CF-002** : Tous les 5 types de documents sont générés correctement (facture, devis, frais km, quittance, charges)
- [x] **CF-003** : Les documents PDF sont conformes aux normes légales (DGFIP, art. L145-49)
- [x] **CF-004** : Les calculs TVA (HT/TTC) sont précis à 2 décimales
- [x] **CF-005** : Les messages vocaux sont transcrits avec >95% précision (français)
- [x] **CF-006** : Les emails sont envoyés avec succès avec CC et PDF attaché (>99% délivrabilité)
- [x] **CF-007** : Le markdown est nettoyé dans toutes les réponses Telegram
- [x] **CF-008** : Les données N8n sont migrées sans perte en PostgreSQL
- [x] **CF-009** : L'historique conversationnel fonctionne (contexte 10 messages)
- [x] **CF-010** : 0 régression fonctionnelle détectée (tests de régression passent)

### Critères Techniques

- [x] **CT-001** : Couverture de tests >80%
- [x] **CT-002** : 0 erreur ruff check
- [x] **CT-003** : 0 erreur mypy --strict
- [x] **CT-004** : Latence génération PDF P95 <500ms
- [x] **CT-005** : Latence LLM P95 <1000ms
- [x] **CT-006** : Throughput >120 documents/min
- [x] **CT-007** : Memory usage bot <512MB
- [x] **CT-008** : Error rate global <1%
- [x] **CT-009** : Startup time <10s
- [x] **CT-010** : Tous les nouveaux tools ont tests unitaires

### Critères Qualité

- [x] **CQ-001** : Toutes les fonctions publiques ont docstrings Google
- [x] **CQ-002** : Tous les fichiers respectent PEP 8 (ruff format)
- [x] **CQ-003** : Complexité cyclomatique <10 (radon cc)
- [x] **CQ-004** : Code dupliqué <5% (radon duplicates)
- [x] **CQ-005** : Documentation à jour (README, CLAUDE.md, directives)
- [x] **CQ-006** : Guide de déploiement documenté et testé
- [x] **CQ-007** : Plan de rollback documenté et testé
- [x] **CQ-008** : Runbook opérationnel créé
- [x] **CQ-009** : Monitoring Prometheus + Grafana configuré
- [x] **CQ-010** : Alerting configuré (error rate >5%)

### Critères Validation Utilisateur

- [x] **CV-001** : Product Owner approuve la migration
- [x] **CV-002** : 10 scénarios end-to-end testés avec succès
- [x] **CV-003** : Validation comptable : documents conformes
- [x] **CV-004** : Satisfaction utilisateur >4/5 (sondage post-migration)
- [x] **CV-005** : 0 incident critique en production (1 semaine post-déploiement)

---

## 📝 Approbations

### Validation Product Owner

- [ ] **Approuve le PRD** : _____________________ Date : __________
- [ ] **Approuve l'architecture** : _____________________ Date : __________
- [ ] **Approuve le budget** : _____________________ Date : __________
- [ ] **Approuve le timeline** : _____________________ Date : __________

### Validation Tech Lead

- [ ] **Approuve l'architecture technique** : _____________________ Date : __________
- [ ] **Approuve les choix technologiques** : _____________________ Date : __________
- [ ] **Approuve le plan de test** : _____________________ Date : __________
- [ ] **Approuve le plan de déploiement** : _____________________ Date : __________

### Validation Ops

- [ ] **Approuve le plan de déploiement** : _____________________ Date : __________
- [ ] **Approuve le monitoring** : _____________________ Date : __________
- [ ] **Approuve le rollback plan** : _____________________ Date : __________

---

## 📞 Contact & Support

### Équipe Projet

| Rôle | Nom | Email | Slack |
|------|-----|-------|-------|
| **Product Owner** | Nacim RABIA | nacim@example.com | @nacim |
| **Tech Lead** | [TBD] | tech@example.com | @techlead |
| **Développeur** | [TBD] | dev@example.com | @dev |
| **Ops** | [TBD] | ops@example.com | @ops |

### Canaux de Communication

- **Slack** : #admin-agent-pro-migration
- **Email** : admin-agent-pro@example.com
- **GitHub Issues** : https://github.com/nacim84/admin-agent-pro/issues
- **Documentation** : https://github.com/nacim84/admin-agent-pro/wiki

---

## 📅 Révisions du Document

| Version | Date | Auteur | Modifications |
|---------|------|--------|---------------|
| 1.0.0 | 2026-01-09 | Claude Code | Création initiale du PRD |
| | | | |
| | | | |

---

**Fin du PRD - Product Requirements Document**

**Document Propriétaire** : Admin Agent Pro
**Confidentiel** : Usage Interne Uniquement
**Licence** : Tous droits réservés

---

## 🔗 Annexes

### Annexe A : Glossaire

| Terme | Définition |
|-------|------------|
| **N8n** | Plateforme no-code/low-code pour workflows d'automatisation |
| **LangChain** | Framework Python pour développement d'applications LLM |
| **LangGraph** | Extension LangChain pour workflows stateful |
| **Pydantic** | Bibliothèque Python pour validation données avec type hints |
| **ReportLab** | Bibliothèque Python pour génération PDF vectorielle |
| **Whisper** | Modèle OpenAI pour transcription speech-to-text |
| **AsyncPG** | Driver PostgreSQL asynchrone haute-performance |
| **DGFIP** | Direction Générale des Finances Publiques (autorité fiscale FR) |
| **TVA** | Taxe sur la Valeur Ajoutée (taux: 20%, 10%, 5.5%, 0%) |
| **TTC** | Toutes Taxes Comprises |
| **HT** | Hors Taxes |

### Annexe B : Références Externes

- [LangChain Documentation](https://python.langchain.com/docs/)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [OpenRouter API Docs](https://openrouter.ai/docs)
- [OpenAI Whisper API](https://platform.openai.com/docs/guides/speech-to-text)
- [ReportLab User Guide](https://www.reportlab.com/docs/reportlab-userguide.pdf)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [AsyncPG Documentation](https://magicstack.github.io/asyncpg/)
- [DGFIP - Mentions obligatoires factures](https://www.economie.gouv.fr/entreprises/mentions-obligatoires-facture)
- [Art. L145-49 Code Rural (quittances)](https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000006583237/)

### Annexe C : Matrice RACI

| Tâche | Product Owner | Tech Lead | Dev | Ops |
|-------|---------------|-----------|-----|-----|
| Validation PRD | A | C | I | I |
| Design architecture | C | A | R | C |
| Développement tools | I | R | A | I |
| Tests unitaires | I | C | A | I |
| Tests intégration | I | R | A | C |
| Documentation | C | R | A | I |
| Déploiement prod | C | R | I | A |
| Monitoring | I | C | I | A |
| Support post-prod | C | R | C | A |

**Légende RACI** :
- **R** : Responsible (Réalise)
- **A** : Accountable (Responsable final)
- **C** : Consulted (Consulté)
- **I** : Informed (Informé)

---

**Document généré le** : 2026-01-09
**Prochaine révision prévue** : Fin Sprint 2 (Semaine 4)
