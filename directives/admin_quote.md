# Directive : Génération de Devis

## Objectif

Générer un devis PDF pour proposer une prestation ou un produit à un client potentiel.

## Différences avec la Facture

- Numéro au format DEV-YYYY-NNNN (ex: DEV-2024-0001)
- Pas de date d'échéance mais une date de validité
- Validité par défaut : 30 jours
- Pas d'obligation de paiement

## Entrées Requises

### Obligatoires
- **Nom du client** : Nom de l'entreprise ou du particulier
- **Adresse du client** : Adresse postale complète
- **Montant HT** : Montant hors taxes
- **Description** : Description de la prestation

### Optionnelles
- **Numéro de devis** : Auto-généré (DEV-YYYY-NNNN)
- **Date d'émission** : Date du jour
- **Validité** : 30 jours par défaut
- **SIRET client** : Optionnel
- **Notes** : Conditions particulières

## Outils d'Exécution

1. **`execution/tools/db_manager.py::get_next_quote_number(year)`**
2. **`execution/tools/pdf_generator.py::generate_quote_pdf(quote, company_info)`**
3. **`execution/tools/db_manager.py::save_document(...)`**

## Agent

**`execution/agents/quote_agent.py::QuoteAgent`** (à implémenter)

## Sortie

- PDF dans `.tmp/documents/devis_DEV-YYYY-NNNN_YYYYMMDD.pdf`
- Enregistrement en base type `QUOTE`
- Envoi via Telegram

## Validation

Identique à la facture, sauf :
- Validation de la durée de validité (> 0 jours)
- Calcul automatique de la date limite : date_emission + validité

## Conformité

Un devis n'a pas les mêmes obligations légales qu'une facture, mais doit contenir :
- Coordonnées complètes du prestataire
- Description précise des prestations
- Prix TTC
- Durée de validité

## Exemples

```
/devis client="ACME Corp" montant=3000 description="Audit SEO complet" validite=45
```

---

**Statut** : 🚧 Agent à implémenter
