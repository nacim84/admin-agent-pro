# Directive : Note de Frais Kilométriques

## Objectif

Générer une note de frais kilométriques conforme au barème fiscal français pour déduire les frais de déplacement professionnels.

## Contexte

Les travailleurs indépendants peuvent déduire leurs frais de déplacement selon le barème kilométrique officiel publié chaque année par l'administration fiscale.

## Entrées Requises

### Par Déplacement
- **Date** : Date du déplacement
- **Lieu de départ** : Ville/adresse de départ
- **Lieu d'arrivée** : Ville/adresse d'arrivée
- **Distance** : Distance en kilomètres
- **Motif** : Raison du déplacement (RDV client, formation, etc.)
- **Type de véhicule** : voiture, moto, ou scooter
- **Puissance fiscale** : Chevaux fiscaux du véhicule

### Enrichissements Automatiques
- **Tarif au km** : Calculé selon le barème fiscal en fonction du type de véhicule et de la puissance
- **Montant total** : distance × tarif

## Barème Kilométrique 2024 (Simplifié)

### Voitures
- ≤ 3 CV : 0.529 €/km
- 4-5 CV : 0.606 €/km
- 6-7 CV : 0.636 €/km
- 8+ CV : 0.665 €/km

### Motos
- ≤ 2 CV : 0.395 €/km
- 3+ CV : 0.468 €/km

### Scooters
- 0.315 €/km

## Outils d'Exécution

1. **`execution/models/documents.py::MileageRecord`**
   - Calcul automatique du `rate_per_km` selon véhicule
   - Calcul du `total_amount`

2. **`execution/tools/pdf_generator.py::generate_mileage_pdf(records, company_info, period_label)`**
   - Tableau avec tous les déplacements
   - Total général

3. **`execution/tools/db_manager.py::save_document(...)`**

## Agent

**`execution/agents/mileage_agent.py::MileageAgent`** (à implémenter)

## Sortie

- PDF dans `.tmp/documents/frais_km_YYYYMMDD_HHMMSS.pdf`
- Enregistrement en base type `MILEAGE`

## Validation

- Distance > 0 km
- Puissance fiscale entre 1 et 20 CV
- Date valide
- Type de véhicule dans la liste autorisée

## Cas Limites

### Multiple Déplacements
L'agent doit supporter la génération d'une note pour plusieurs déplacements sur une période (semaine, mois).

### Barème Variable
Le barème change chaque année. Idéalement, il faudrait :
- Stocker les barèmes par année
- Appliquer le barème correspondant à la date du déplacement

## Conformité Fiscale

- Le barème officiel doit être respecté
- Justificatifs de déplacement recommandés (tickets péage, etc.)
- Ne pas dépasser 40 000 km/an pour bénéficier du barème

## Exemples

```
/frais_km date=2024-01-15 depart="Paris" arrivee="Lyon" km=465 motif="Rendez-vous client ACME Corp" vehicule=voiture cv=5
```

---

**Statut** : 🚧 Agent à implémenter
