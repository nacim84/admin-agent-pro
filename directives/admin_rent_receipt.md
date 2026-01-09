# Directive : Quittance de Loyer

## Objectif

Générer une quittance de loyer pour attester du paiement du loyer et des charges par un locataire.

## Contexte Légal

En France, le propriétaire-bailleur doit fournir gratuitement une quittance de loyer au locataire qui en fait la demande (article 21 de la loi du 6 juillet 1989).

## Entrées Requises

### Obligatoires
- **Période** : Mois (1-12) et année du loyer
- **Nom du locataire** : Nom complet
- **Adresse du locataire** : Adresse de résidence
- **Adresse du bien loué** : Adresse du logement concerné
- **Montant du loyer** : Loyer hors charges
- **Montant des charges** : Charges locatives
- **Date de paiement** : Date effective du paiement
- **Moyen de paiement** : virement, chèque, espèces, prélèvement

### Optionnelles
- **Numéro de quittance** : Auto-généré (QUIT-YYYY-NNNN)

## Outils d'Exécution

1. **`execution/models/documents.py::RentReceipt`**
   - Calcul `total_amount` = loyer + charges
   - Formatage `period_str` : "Janvier 2024"

2. **`execution/tools/pdf_generator.py::generate_rent_receipt_pdf(receipt, company_info)`**

3. **`execution/tools/db_manager.py::save_document(...)`**

## Agent

**`execution/agents/rent_receipt_agent.py::RentReceiptAgent`** (à implémenter)

## Sortie

- PDF dans `.tmp/documents/quittance_QUIT-YYYY-NNNN.pdf`
- Enregistrement en base type `RENT_RECEIPT`

## Contenu de la Quittance

1. **Titre** : "QUITTANCE DE LOYER"
2. **Identité du bailleur** : Nom, adresse
3. **Identité du locataire** : Nom, adresse
4. **Bien concerné** : Adresse complète
5. **Période** : Mois et année
6. **Détail des montants** :
   - Loyer
   - Charges
   - Total
7. **Paiement** : Date et moyen
8. **Certification** : Texte attestant de la réception du paiement
9. **Date et signature** (automatique)

## Validation

- Période : mois entre 1 et 12, année >= 2000
- Montants >= 0
- Date de paiement valide
- Moyen de paiement dans la liste autorisée

## Mentions Légales

La quittance doit mentionner :
- "Je soussigné(e) certifie avoir reçu la somme de X€ au titre du loyer..."
- Montants séparés loyer/charges
- Période concernée clairement indiquée

## Exemples

```
/quittance locataire="Dupont Jean" loyer=800 charges=150 mois=1 annee=2024 date=2024-01-05 paiement=virement adresse_locataire="5 rue Victor Hugo, 75015 Paris" adresse_bien="5 rue Victor Hugo, Apt 301, 75015 Paris"
```

---

**Statut** : 🚧 Agent à implémenter
