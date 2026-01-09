# Directive : Décompte de Charges Locatives

## Objectif

Générer un décompte annuel de charges locatives pour régulariser les charges payées par le locataire durant l'année écoulée.

## Contexte Légal

Le propriétaire doit communiquer au locataire, au moins une fois par an, le décompte des charges locatives (article 23 de la loi du 6 juillet 1989). Ce décompte doit être envoyé dans le mois qui suit la réception des comptes de la copropriété.

## Entrées Requises

### Obligatoires
- **Période** : Date de début et date de fin (ex: 01/01/2023 au 31/12/2023)
- **Nom du locataire** : Nom complet
- **Adresse du bien** : Adresse du logement
- **Liste des charges** : Tableau avec libellé et montant
  - Exemple : Eau, Électricité parties communes, Entretien ascenseur, Ordures ménagères, etc.

## Structure d'une Charge

Chaque charge contient :
- **Libellé** : Description (ex: "Eau froide", "Entretien espaces verts")
- **Montant** : Montant en euros

## Calcul

- **Provisions versées** : Total des charges payées dans les loyers sur la période
- **Charges réelles** : Total des charges effectivement engagées
- **Régularisation** : Différence (solde à payer ou à rembourser)

## Outils d'Exécution

1. **`execution/models/documents.py::ChargeItem`**
   - Modèle pour une charge individuelle

2. **`execution/models/documents.py::RentalCharges`**
   - Calcul `total_charges` (somme de toutes les charges)
   - Validation période

3. **`execution/tools/pdf_generator.py::generate_rental_charges_pdf(...)`** (à implémenter)

4. **`execution/tools/db_manager.py::save_document(...)`**

## Agent

**`execution/agents/rental_charges_agent.py::RentalChargesAgent`** (à implémenter)

## Sortie

- PDF dans `.tmp/documents/charges_YYYYMMDD.pdf`
- Enregistrement en base type `RENTAL_CHARGES`

## Contenu du Décompte

1. **Titre** : "DÉCOMPTE DE CHARGES LOCATIVES"
2. **Période** : Du XX/XX/XXXX au XX/XX/XXXX
3. **Identité du bailleur**
4. **Identité du locataire**
5. **Bien concerné**
6. **Tableau des charges** :
   - Colonne 1 : Libellé
   - Colonne 2 : Montant
7. **Total des charges réelles**
8. **Provisions versées**
9. **Régularisation** : Solde à payer ou à rembourser
10. **Pièces justificatives** : Mention de la disponibilité des justificatifs

## Validation

- Date de fin > Date de début
- Au moins une charge dans la liste
- Tous les montants >= 0
- Période cohérente (max 2 ans)

## Charges Récupérables

Liste non exhaustive des charges récupérables (Décret n°87-713) :
- Eau froide et chaude
- Chauffage collectif
- Électricité parties communes
- Entretien ascenseur
- Entretien espaces verts
- Ordures ménagères
- Entretien de la chaudière
- Produits d'entretien
- Gardiennage/concierge (quote-part)

## Exemples

```
/charges locataire="Dupont Jean" debut=2023-01-01 fin=2023-12-31 adresse="5 rue Victor Hugo, Apt 301, 75015 Paris" charges='[{"libelle":"Eau","montant":250},{"libelle":"Électricité communes","montant":180},{"libelle":"Entretien ascenseur","montant":120}]' provisions=600
```

## Notes

- Le propriétaire doit conserver les justificatifs pendant 5 ans
- Le locataire peut demander à consulter les justificatifs
- En cas de solde créditeur, le bailleur doit rembourser ou déduire du loyer suivant

---

**Statut** : 🚧 Agent à implémenter
