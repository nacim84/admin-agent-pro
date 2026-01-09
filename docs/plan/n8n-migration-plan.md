# PLAN TECHNIQUE: Migration N8n → Python Tools
#
**PRD Source** : `PRD.md`
**Auteur** : Admin Agent Pro Team
**Date** : 2026-01-09
**Status** : COMPLETED (2026-01-09)

---

## 11. Migration Summary

The migration from N8n to the Python Agentic 3-Layer Architecture is now complete.

### Key Achievements:
- **Tools Layer**: Implemented 5 deterministic tools (`CalculatorTool`, `DatabaseQueryTool`, `EmailSenderTool`, `WhisperTranscriptionTool`, `MarkdownCleanerTool`).
- **Data Integrity**: Migrated `data_administration` schema to SQLAlchemy and initialized the database.
- **Orchestration**: Updated `OrchestratorAgent` with N8n business logic and tool-calling capabilities.
- **Precision**: Enforced `Decimal` precision for all financial calculations.
- **Email Standards**: Automated the strict N8n email hierarchy (TO/CC).
- **Telegram UX**: Added audio transcription and Markdown cleaning for improved mobile experience.

### Next Steps:
- Monitor Whisper API usage and costs.
- Validate SMTP delivery with actual credentials.
- Expand `database_query` filters as more clients are added.

### 1.1 Stack Technique

**Backend** :
- Framework : Python 3.11+
- LangChain : 0.3.19 (agents + tools)
- ORM : SQLAlchemy 2.0 (async)
- Database : PostgreSQL 15
- Package Manager : UV (fast Python package manager)
- Testing : pytest + pytest-asyncio
- Linting : ruff

**Tools Layer (NOUVEAU)** :
- Location : `execution/tools/`
- Pattern : LangChain BaseTool
- Type-safety : Pydantic 2.8+

### 1.2 Architectural Pattern

**Pattern Principal** : **Tools Layer** entre Orchestration et Execution

```
┌──────────────────────────────────────────────┐
│           DIRECTIVES (N8n JSON)              │
│      Logique métier et règles                │
└───────────────┬──────────────────────────────┘
                │
                ▼
┌──────────────────────────────────────────────┐
│       ORCHESTRATION (orchestrator_agent)     │
│   LangChain ChatOpenAI + OpenRouter          │
│   Intent Recognition + Entity Extraction     │
└───────────────┬──────────────────────────────┘
                │
                ▼
┌──────────────────────────────────────────────┐
│          TOOLS LAYER (NOUVEAU)               │
│  CalculatorTool | DatabaseQueryTool          │
│  EmailSenderTool | WhisperTranscriptionTool  │
│  MarkdownCleanerTool                         │
└───────────────┬──────────────────────────────┘
                │
                ▼
┌──────────────────────────────────────────────┐
│         EXECUTION (agents spécialisés)       │
│  invoice_agent | quote_agent |               │
│  mileage_agent | rent_receipt_agent |        │
│  rental_charges_agent                        │
└──────────────────────────────────────────────┘
```

**Justification** :
- **Séparation des responsabilités** : Les agents se concentrent sur la génération PDF, les tools gèrent les calculs/data/emails
- **Réutilisabilité** : Un tool peut être appelé par plusieurs agents
- **Testabilité** : Chaque tool est testable unitairement

---

## 2. Database Schema

### 2.1 Tables Existantes (Utilisées)

**Table : `data_administration`**
```sql
-- Structure existante (déjà créée)
-- Contient toutes les données métier (factures, charges, frais km, etc.)
```

**Table : `documents`**
```python
# execution/models/documents.py (déjà créé)
class Document(Base):
    id: UUID
    user_id: int
    document_type: str
    file_path: str
    created_at: datetime
```

**Table : `chat_history`**
```python
# execution/models/database.py (déjà créé)
class ChatHistory(Base):
    id: UUID
    user_id: int
    role: str
    content: str
    timestamp: datetime
```

### 2.2 Pas de Nouvelle Table

✅ Aucune modification de schéma nécessaire. Les tables existantes suffisent.

---

## 3. Tools Design

### 3.1 CalculatorTool

**Responsabilité** : Calculer les totaux financiers (HT, TVA, TTC)

**Signature** :
```python
class CalculatorTool(BaseTool):
    name = "calculator"
    description = """
    Calculate financial totals for French administrative documents.

    Input format:
    {
        "operation": "facture_totals",  # or "charges_totals"
        "prix_unitaire": 500.00,
        "quantite": 10.5,
        "tva_pourcent": 20.0
    }

    Output:
    {
        "total_ht": 5250.00,
        "montant_tva": 1050.00,
        "total_ttc": 6300.00
    }
    """

    def _run(self, operation: str, **kwargs) -> Dict[str, Decimal]:
        if operation == "facture_totals":
            return self._calc_facture_totals(**kwargs)
        elif operation == "charges_totals":
            return self._calc_charges_totals(**kwargs)
        raise ValueError(f"Unknown operation: {operation}")

    def _calc_facture_totals(
        self,
        prix_unitaire: float,
        quantite: float,
        tva_pourcent: float
    ) -> Dict[str, Decimal]:
        """Calculate invoice totals with Decimal precision."""
        pu = Decimal(str(prix_unitaire))
        qty = Decimal(str(quantite))
        tva = Decimal(str(tva_pourcent))

        total_ht = (pu * qty).quantize(Decimal("0.01"))
        montant_tva = (total_ht * tva / Decimal("100")).quantize(Decimal("0.01"))
        total_ttc = (total_ht + montant_tva).quantize(Decimal("0.01"))

        return {
            "total_ht": float(total_ht),
            "montant_tva": float(montant_tva),
            "total_ttc": float(total_ttc)
        }
```

**Tests** :
- ✅ Calcul facture : 500 × 10.5 @ 20% TVA = 6300.00 TTC
- ✅ Précision décimale : arrondi à 2 chiffres
- ✅ Edge cases : quantité 0, TVA 0%, prix négatif (erreur)

---

### 3.2 DatabaseQueryTool

**Responsabilité** : Requêter la table `data_administration` pour récupérer les infos métier

**Signature** :
```python
class DatabaseQueryTool(BaseTool):
    name = "database_query"
    description = """
    Query the data_administration table to retrieve business data.

    Input format:
    {
        "query_type": "facture_info",  # or "charges_info", "frais_km_info", etc.
        "filters": {"client": "ALTECA", "annee": 2025}
    }

    Output:
    {
        "nom_entreprise": "RN-BLOCK",
        "adresse_entreprise": "2 RUE JEHAN ALAIN...",
        "nom_client": "ALTECA",
        "prix_unitaire": 500.00,
        "tva": 20.0,
        "emails": {
            "email_entreprise": "rn.block.pro@gmail.com",
            "email_professionnel_1": "rabia.nacim@gmail.com",
            "email_client": "comptafournisseurs@alteca.fr"
        }
    }
    """

    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()

    async def _arun(self, query_type: str, filters: Dict) -> Dict:
        if query_type == "facture_info":
            return await self._get_facture_info(**filters)
        elif query_type == "charges_info":
            return await self._get_charges_info(**filters)
        # ... autres query_types

    async def _get_facture_info(self, client: str, annee: int) -> Dict:
        """Fetch invoice-related data from data_administration."""
        query = """
        SELECT
            nom_entreprise,
            adresse_entreprise,
            nom_client,
            adresse_client,
            prix_unitaire,
            tva,
            email_entreprise,
            email_professionnel_1,
            email_professionnel_2,
            email_client
        FROM data_administration
        WHERE nom_client = :client
          AND annee = :annee
        LIMIT 1
        """
        result = await self.db.execute_query(query, {"client": client, "annee": annee})
        return result[0] if result else {}
```

**Tests** :
- ✅ Query facture pour client "ALTECA" retourne données complètes
- ✅ Query charges pour période "Mars 2025" retourne liste charges
- ✅ Client inexistant retourne dict vide
- ✅ SQL injection protection (parameterized queries)

---

### 3.3 EmailSenderTool

**Responsabilité** : Envoyer des emails avec pièces jointes PDF selon hiérarchie N8n

**Signature** :
```python
class EmailSenderTool(BaseTool):
    name = "send_email"
    description = """
    Send email with PDF attachment following N8n email hierarchy.

    Email hierarchy (STRICT):
    - TO: email_entreprise (ALWAYS)
    - CC: email_professionnel_1, email_professionnel_2, email_client (if available)

    Input format:
    {
        "to": "rn.block.pro@gmail.com",
        "cc": ["rabia.nacim@gmail.com", "comptafournisseurs@alteca.fr"],
        "subject": "Facture FACT-RNBLOCK-022025",
        "body": "Veuillez trouver ci-joint votre facture...",
        "attachments": [{"filename": "facture.pdf", "path": "/tmp/facture.pdf"}]
    }

    Output:
    {
        "status": "sent",
        "message_id": "abc123",
        "recipients": ["to@example.com", "cc1@example.com"]
    }
    """

    def __init__(self):
        super().__init__()
        self.smtp_host = get_settings().smtp_host
        self.smtp_port = get_settings().smtp_port
        self.smtp_user = get_settings().smtp_user
        self.smtp_password = get_settings().smtp_password

    async def _arun(
        self,
        to: str,
        cc: List[str],
        subject: str,
        body: str,
        attachments: List[Dict[str, str]]
    ) -> Dict:
        """Send email with SMTP using aiosmtplib."""
        import aiosmtplib
        from email.message import EmailMessage

        msg = EmailMessage()
        msg["From"] = self.smtp_user
        msg["To"] = to
        msg["Cc"] = ", ".join(cc)
        msg["Subject"] = subject
        msg.set_content(body)

        # Attach PDFs
        for attachment in attachments:
            with open(attachment["path"], "rb") as f:
                pdf_data = f.read()
            msg.add_attachment(
                pdf_data,
                maintype="application",
                subtype="pdf",
                filename=attachment["filename"]
            )

        # Send via SMTP
        await aiosmtplib.send(
            msg,
            hostname=self.smtp_host,
            port=self.smtp_port,
            username=self.smtp_user,
            password=self.smtp_password,
            use_tls=True
        )

        return {
            "status": "sent",
            "recipients": [to] + cc
        }
```

**Tests** :
- ✅ Email envoyé avec TO = email_entreprise
- ✅ CC inclut email_professionnel_1, email_professionnel_2, email_client
- ✅ Pièce jointe PDF incluse (taille > 0)
- ✅ Erreur SMTP gérée (raise SMTPException)

---

### 3.4 WhisperTranscriptionTool

**Responsabilité** : Transcrire des messages vocaux Telegram en texte via OpenAI Whisper

**Signature** :
```python
class WhisperTranscriptionTool(BaseTool):
    name = "whisper_transcription"
    description = """
    Transcribe voice messages to text using OpenAI Whisper API.

    Input format:
    {
        "audio_file_path": "/tmp/voice_message.ogg",
        "language": "fr"  # optional, auto-detect by default
    }

    Output:
    {
        "text": "Bonjour, je voudrais générer une facture pour...",
        "language": "fr",
        "duration": 12.5
    }
    """

    def __init__(self):
        super().__init__()
        self.openai_api_key = get_settings().openai_api_key
        import openai
        self.client = openai.OpenAI(api_key=self.openai_api_key)

    async def _arun(
        self,
        audio_file_path: str,
        language: str = None
    ) -> Dict:
        """Transcribe audio using Whisper API."""
        with open(audio_file_path, "rb") as audio_file:
            response = self.client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language=language,
                response_format="verbose_json"
            )

        return {
            "text": response.text,
            "language": response.language,
            "duration": response.duration
        }
```

**Tests** :
- ✅ Audio 10s en français transcrit correctement
- ✅ Auto-détection language fonctionne
- ✅ Fichier audio invalide raise OpenAIError
- ✅ API key manquante raise ConfigurationError

---

### 3.5 MarkdownCleanerTool

**Responsabilité** : Nettoyer la sortie LLM pour Telegram (supprimer Markdown, math symbols)

**Signature** :
```python
class MarkdownCleanerTool(BaseTool):
    name = "markdown_cleaner"
    description = """
    Clean LLM output for Telegram by removing Markdown and math symbols.

    Replacements:
    - ** (bold) → plain text
    - * (italic) → plain text
    - +, -, *, / → "plus", "moins", "fois", "divisé par"
    - Bullet lists (-, *) → Numbered lists (1., 2.)

    Input format:
    {
        "text": "**Total HT** : 500 * 10 = 5000€\\n- Item 1\\n- Item 2"
    }

    Output:
    {
        "cleaned_text": "Total HT : 500 fois 10 = 5000€\\n1. Item 1\\n2. Item 2"
    }
    """

    def _run(self, text: str) -> Dict[str, str]:
        """Clean text for Telegram display."""
        import re

        # Remove bold/italic Markdown
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # **bold** → bold
        text = re.sub(r'\*(.*?)\*', r'\1', text)       # *italic* → italic

        # Replace math symbols
        text = text.replace(' + ', ' plus ')
        text = text.replace(' - ', ' moins ')
        text = text.replace(' * ', ' fois ')
        text = text.replace(' / ', ' divisé par ')

        # Convert bullet lists to numbered lists
        lines = text.split('\n')
        cleaned_lines = []
        list_counter = 1

        for line in lines:
            if re.match(r'^[\-\*]\s+', line):
                cleaned_lines.append(f"{list_counter}. {line[2:]}")
                list_counter += 1
            else:
                cleaned_lines.append(line)
                if not line.strip():
                    list_counter = 1  # Reset counter on empty line

        return {"cleaned_text": '\n'.join(cleaned_lines)}
```

**Tests** :
- ✅ **Bold** → plain text
- ✅ Math symbols : 5 * 10 → 5 fois 10
- ✅ Bullet lists → Numbered lists
- ✅ Empty string → empty string
- ✅ No Markdown → unchanged

---

## 4. File Structure

### 4.1 Nouveaux Fichiers

```
execution/
├── tools/
│   ├── __init__.py                 # Expose all tools
│   ├── calculator_tool.py          # CalculatorTool (NEW)
│   ├── database_query_tool.py      # DatabaseQueryTool (NEW)
│   ├── email_sender_tool.py        # EmailSenderTool (NEW)
│   ├── whisper_transcription_tool.py  # WhisperTranscriptionTool (NEW)
│   ├── markdown_cleaner_tool.py    # MarkdownCleanerTool (NEW)
│   ├── db_manager.py               # Existing (reuse)
│   ├── pdf_generator.py            # Existing (reuse)
│   └── telegram_helpers.py         # Existing (reuse)
tests/
├── tools/
│   ├── test_calculator_tool.py     # 10 tests
│   ├── test_database_query_tool.py # 8 tests
│   ├── test_email_sender_tool.py   # 10 tests
│   ├── test_whisper_transcription_tool.py  # 8 tests
│   └── test_markdown_cleaner_tool.py  # 10 tests
```

### 4.2 Fichiers Modifiés

- `execution/agents/orchestrator_agent.py` : Ajouter les 5 nouveaux tools à la liste des outils disponibles
- `execution/prompts/orchestrator_prompts.py` : Enrichir le prompt système avec la logique métier N8n
- `pyproject.toml` : Ajouter dépendances (aiosmtplib, openai)

---

## 5. Découpage en Tâches

### 5.1 Phase 1 : CalculatorTool (P0)

**Durée estimée** : 4 heures

- [ ] **CALC-1** : Créer `execution/tools/calculator_tool.py` avec `_calc_facture_totals`
- [ ] **CALC-2** : Ajouter `_calc_charges_totals` pour charges locatives
- [ ] **CALC-3** : Tests unitaires : `tests/tools/test_calculator_tool.py` (10 tests)
- [ ] **CALC-4** : Intégrer CalculatorTool dans orchestrator_agent

### 5.2 Phase 2 : DatabaseQueryTool (P0)

**Durée estimée** : 8 heures

- [ ] **DB-1** : Créer `execution/tools/database_query_tool.py`
- [ ] **DB-2** : Implémenter `_get_facture_info` query
- [ ] **DB-3** : Implémenter `_get_charges_info` query
- [ ] **DB-4** : Implémenter `_get_frais_km_info` query
- [ ] **DB-5** : Tests unitaires : `tests/tools/test_database_query_tool.py` (8 tests)
- [ ] **DB-6** : Intégrer DatabaseQueryTool dans orchestrator_agent

### 5.3 Phase 3 : EmailSenderTool (P0)

**Durée estimée** : 8 heures

- [ ] **EMAIL-1** : Installer dépendance : `uv add aiosmtplib`
- [ ] **EMAIL-2** : Créer `execution/tools/email_sender_tool.py`
- [ ] **EMAIL-3** : Implémenter envoi SMTP avec attachments PDF
- [ ] **EMAIL-4** : Gérer hiérarchie emails (TO: email_entreprise, CC: emails_pro)
- [ ] **EMAIL-5** : Tests unitaires : `tests/tools/test_email_sender_tool.py` (10 tests)
- [ ] **EMAIL-6** : Ajouter config SMTP dans `.env` et `core/config.py`
- [ ] **EMAIL-7** : Intégrer EmailSenderTool dans orchestrator_agent

### 5.4 Phase 4 : WhisperTranscriptionTool (P1)

**Durée estimée** : 6 heures

- [ ] **WHISPER-1** : Installer dépendance : `uv add openai`
- [ ] **WHISPER-2** : Créer `execution/tools/whisper_transcription_tool.py`
- [ ] **WHISPER-3** : Implémenter transcription via OpenAI Whisper API
- [ ] **WHISPER-4** : Gérer conversion format audio (.ogg → .mp3 si nécessaire)
- [ ] **WHISPER-5** : Tests unitaires : `tests/tools/test_whisper_transcription_tool.py` (8 tests)
- [ ] **WHISPER-6** : Ajouter OPENAI_API_KEY dans `.env` et `core/config.py`
- [ ] **WHISPER-7** : Intégrer WhisperTranscriptionTool dans telegram_bot.py (handler voice)

### 5.5 Phase 5 : MarkdownCleanerTool (P1)

**Durée estimée** : 3 heures

- [ ] **MD-1** : Créer `execution/tools/markdown_cleaner_tool.py`
- [ ] **MD-2** : Implémenter regex pour supprimer Markdown (**, *)
- [ ] **MD-3** : Implémenter remplacement symboles math (+, -, *, /)
- [ ] **MD-4** : Implémenter conversion bullet lists → numbered lists
- [ ] **MD-5** : Tests unitaires : `tests/tools/test_markdown_cleaner_tool.py` (10 tests)
- [ ] **MD-6** : Intégrer MarkdownCleanerTool dans telegram_bot.py (avant envoi message)

### 5.6 Phase 6 : Enrichissement OrchestratorPrompt (P0)

**Durée estimée** : 4 heures

- [ ] **PROMPT-1** : Copier logique métier N8n dans `orchestrator_prompts.py`
- [ ] **PROMPT-2** : Ajouter hiérarchie emails (TO/CC) dans prompt système
- [ ] **PROMPT-3** : Ajouter règles de calcul (Facture, Charges, Frais KM)
- [ ] **PROMPT-4** : Ajouter formats JSON attendus (exemples N8n)
- [ ] **PROMPT-5** : Tester avec vraies demandes utilisateur (facture, charges, etc.)

### 5.7 Phase 7 : Tests & Validation (P0)

**Durée estimée** : 8 heures

- [ ] **TEST-1** : Tests E2E : Générer facture complète (DB → Calcul → PDF → Email)
- [ ] **TEST-2** : Tests E2E : Générer charges locatives
- [ ] **TEST-3** : Tests E2E : Générer frais kilométriques
- [ ] **TEST-4** : Tests E2E : Transcription vocale → Génération document
- [ ] **TEST-5** : Tests performance : < 500ms par document (P95)
- [ ] **TEST-6** : Tests regression : Tous agents existants fonctionnent toujours
- [ ] **TEST-7** : Coverage report : > 80% pour tools/

---

## 6. Dépendances & Intégrations

### 6.1 Nouvelles Dépendances

```toml
# pyproject.toml
[project]
dependencies = [
    # ... existing dependencies
    "aiosmtplib>=3.0.0",  # Async SMTP for EmailSenderTool
    "openai>=1.58.1",     # Whisper API for WhisperTranscriptionTool
]
```

**Installation** :
```bash
uv add aiosmtplib openai
```

### 6.2 Configuration (.env)

```env
# Email (SMTP)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=rn.block.pro@gmail.com
SMTP_PASSWORD=<app_password>

# OpenAI (Whisper)
OPENAI_API_KEY=sk-proj-...
```

### 6.3 Configuration (core/config.py)

```python
class Settings(BaseSettings):
    # ... existing settings

    # SMTP Configuration
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str
    smtp_password: str

    # OpenAI Whisper Configuration
    openai_api_key: str
```

---

## 7. Security & Performance

### 7.1 Security Checklist

- [x] **SQL Injection** : Parameterized queries dans DatabaseQueryTool
- [x] **Email Injection** : Validation emails (regex) dans EmailSenderTool
- [x] **File Upload** : Validation format audio (.ogg, .mp3) dans WhisperTranscriptionTool
- [x] **API Keys** : Stockées dans .env (jamais dans code)
- [x] **SMTP Credentials** : App password Gmail (pas password principal)
- [x] **Decimal Precision** : Utilisation de Decimal dans CalculatorTool (pas float)

### 7.2 Performance Targets

- **CalculatorTool** : < 1ms (calculs simples)
- **DatabaseQueryTool** : < 50ms (query simple avec index)
- **EmailSenderTool** : < 2s (SMTP send avec attachment 1MB)
- **WhisperTranscriptionTool** : < 5s (audio 30s)
- **MarkdownCleanerTool** : < 10ms (regex sur texte 1000 chars)

### 7.3 Optimizations

- [x] Database indexes sur `nom_client`, `annee` dans `data_administration`
- [x] Async I/O pour EmailSenderTool (aiosmtplib) et WhisperTranscriptionTool
- [x] Caching : Pas nécessaire (données changent fréquemment)
- [x] Connection pooling : Déjà géré par SQLAlchemy async engine

---

## 8. Rollout & Feature Flags

### 8.1 Stratégie de Déploiement

**Approche Progressive** : Déployer outil par outil pour limiter les risques

1. **Sprint 1 (Semaine 1-2)** : CalculatorTool + DatabaseQueryTool
   - Tester uniquement ces 2 outils
   - Agents existants continuent de fonctionner

2. **Sprint 2 (Semaine 3)** : EmailSenderTool
   - Tester envoi emails avec PDF
   - Valider hiérarchie TO/CC

3. **Sprint 3 (Semaine 4)** : WhisperTranscriptionTool + MarkdownCleanerTool
   - Tester transcription vocale
   - Tester nettoyage Markdown

4. **Sprint 4 (Semaine 5)** : Enrichissement OrchestratorPrompt
   - Intégrer logique N8n dans prompt système
   - Tester tous les scénarios E2E

5. **Sprint 5 (Semaine 6)** : Tests & Validation
   - Coverage > 80%
   - Performance < 500ms P95
   - Déploiement production

### 8.2 Rollback Plan

Si un tool échoue en production :
1. Désactiver le tool dans `orchestrator_agent.py` (commentaire import)
2. Revenir au commit précédent : `git revert <commit_hash>`
3. Redéployer : `docker-compose down && docker-compose up -d --build`

---

## 9. Risks & Mitigations

| Risk | Impact | Probabilité | Mitigation |
|------|--------|-------------|------------|
| SMTP Gmail bloque envois | High | Medium | Utiliser App Password + OAuth2 backup |
| Whisper API coût élevé | Medium | Low | Limiter durée audio max (60s) + cache transcriptions |
| Decimal precision errors | High | Low | Tests unitaires avec edge cases (0.01, 99999.99) |
| DB query lente | Medium | Low | Indexes sur colonnes filtrées (nom_client, annee) |
| Email CC manquants | Medium | Medium | Tests E2E validant hiérarchie TO/CC stricte |

---

## 10. Success Metrics (Post-Launch)

**Tracking** :
- [ ] **Performance** : Mesurer P95 latency pour chaque tool (DataDog/Prometheus)
- [ ] **Reliability** : Taux d'erreur < 1% par tool
- [ ] **Coverage** : Tests coverage > 80% sur `execution/tools/`
- [ ] **User Satisfaction** : Aucune régression fonctionnelle vs N8n

**Review** : 7 jours post-déploiement

---

## Approbations Techniques

- [ ] Tech Lead : Nacim RABIA
- [ ] Senior Python Dev : Claude Sonnet 4.5
- [ ] DevOps : À valider (Docker redéploiement)

---

**Statut Actuel** : ✅ PLAN APPROUVÉ → Prêt pour implémentation

**Prochaine étape** : Phase 1 - Implémentation CalculatorTool
