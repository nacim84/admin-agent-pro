# Directive : Génération de Facture

## Objectif

Générer une facture PDF conforme aux normes comptables françaises pour une entreprise unipersonnelle (SASU, EURL).

## Entrées Requises

### Obligatoires
- **Nom du client** : Nom complet de l'entreprise ou du particulier
- **Adresse du client** : Adresse postale complète
- **Montant HT** : Montant hors taxes de la prestation
- **Description** : Description de la prestation ou du produit

### Optionnelles (avec valeurs par défaut)
- **Numéro de facture** : Auto-généré au format YYYY-NNNN (ex: 2024-0001)
- **Date d'émission** : Date du jour si non fournie
- **Date d'échéance** : Date d'émission + 30 jours par défaut
- **SIRET client** : Numéro SIRET du client (14 chiffres)
- **Taux de TVA** : 20% par défaut (autres: 10%, 5.5%, 0%)
- **Conditions de paiement** : "Paiement à 30 jours" par défaut
- **Notes** : Notes additionnelles à afficher sur la facture

## Outils d'Exécution

### Couche 3 (Exécution Déterministe)

1. **`execution/tools/db_manager.py::get_next_invoice_number(year)`**
   - Génère le prochain numéro de facture séquentiel
   - Format: YYYY-NNNN (ex: 2024-0001, 2024-0002, etc.)
   - Assure l'unicité et la continuité des numéros

2. **`execution/tools/pdf_generator.py::generate_invoice_pdf(invoice, company_info)`**
   - Génère un PDF professionnel avec ReportLab
   - Inclut : en-tête entreprise, infos client, tableau items, totaux HT/TVA/TTC
   - Sortie dans `.tmp/documents/`

3. **`execution/tools/db_manager.py::save_document(doc_type, doc_number, data, pdf_path, user_id)`**
   - Enregistre le document en base PostgreSQL
   - Stocke les données JSON + chemin PDF
   - Permet recherche et historique

### Couche 2 (Orchestration LangGraph)

**Agent** : `execution/agents/invoice_agent.py::InvoiceAgent`

**Workflow LangGraph** :
```
validate_input → generate_pdf → save_to_db → END
```

Chaque nœud peut produire une erreur qui arrête le workflow.

## Sortie

1. **PDF généré** : Fichier dans `.tmp/documents/facture_YYYY-NNNN_YYYYMMDD.pdf`
2. **Enregistrement en base** : Document sauvegardé dans table `documents`
3. **Envoi Telegram** : PDF envoyé au demandeur avec message de confirmation

## Règles de Validation

### SIRET Client
- Si fourni, doit contenir exactement 14 chiffres
- Les espaces sont automatiquement supprimés
- Erreur si format invalide

### Dates
- Date d'échéance doit être postérieure à la date d'émission
- Conversion automatique string → date si nécessaire

### Items
- Au moins un item requis
- Quantité > 0
- Prix unitaire >= 0
- Taux TVA entre 0 et 1 (ex: 0.20 pour 20%)

### Numéro de Facture
- Vérification d'unicité en base
- Séquence continue par année
- Ne jamais ré-utiliser un numéro existant

## Cas Limites et Gestion d'Erreurs

### Limite Rate API
N/A - Pas d'API externe

### Données Incomplètes
- Enrichir automatiquement avec valeurs par défaut
- Erreur seulement si données obligatoires manquantes

### Erreur Génération PDF
- Logger l'erreur complète avec stack trace
- Retourner message d'erreur clair à l'utilisateur
- Ne pas créer d'enregistrement en base si PDF échoue

### Erreur Base de Données
- Rollback automatique via SQLAlchemy
- PDF reste accessible localement
- Possibilité de réessayer la sauvegarde

## Conformité Légale Française

### Mentions Obligatoires sur la Facture
- ✅ Numéro séquentiel unique
- ✅ Date d'émission et d'échéance
- ✅ Identité du fournisseur (nom, adresse, SIRET, TVA)
- ✅ Identité du client (nom, adresse)
- ✅ Description détaillée des prestations
- ✅ Montants HT, TVA, TTC
- ✅ Conditions de paiement

### Taux de TVA en Vigueur (2024)
- **20%** : Taux normal (par défaut)
- **10%** : Taux intermédiaire (restauration, transports, etc.)
- **5.5%** : Taux réduit (alimentation, énergie, etc.)
- **0%** : Exonération (export, services intracommunautaires)

## Améliorations Futures

1. **Multi-items avancés** : Support de plusieurs lignes avec différents taux TVA
2. **Acomptes** : Gestion des factures d'acompte et solde
3. **Avoirs** : Génération de factures d'avoir (remboursements)
4. **Exports comptables** : Export vers logiciels comptables (QuickBooks, Sage, etc.)
5. **Relances automatiques** : Envoi automatique de relances pour factures impayées

## Exemples d'Utilisation

### Via Telegram

**Simple** :
```
/facture client="ACME Corp" montant=1500 description="Développement site web"
```

**Complet** :
```
/facture client="ACME Corp" montant=2500 description="Prestation consulting" adresse="10 rue de la Paix, 75002 Paris" siret="12345678901234" conditions="Paiement à réception"
```

### Via Code Python

```python
from execution.agents.invoice_agent import InvoiceAgent

state = {
    "user_id": 123456789,
    "request_type": "invoice",
    "input_data": {
        "client_name": "ACME Corp",
        "client_address": "10 rue de la Paix, 75002 Paris",
        "items": [{
            "description": "Développement application mobile",
            "quantity": 1,
            "unit_price": 5000,
            "vat_rate": 0.20
        }]
    },
    "validated_data": None,
    "pdf_path": None,
    "db_record_id": None,
    "error": None
}

agent = InvoiceAgent()
result = await agent.execute(state)

if result["error"]:
    print(f"Erreur: {result['error']}")
else:
    print(f"Facture générée: {result['pdf_path']}")
    print(f"ID base: {result['db_record_id']}")
```

## Logs et Monitoring

### Logs à Produire
- ✅ Début de validation
- ✅ Numéro généré
- ✅ Validation réussie avec totaux
- ✅ PDF généré avec chemin
- ✅ Sauvegarde DB réussie avec ID
- ❌ Toutes les erreurs avec stack trace

### Métriques à Suivre
- Nombre de factures générées par jour/semaine/mois
- Montant total facturé
- Temps moyen de génération
- Taux d'erreur

---

**Dernière mise à jour** : 2024-01-09
**Auteur** : Admin Agent Pro Team
