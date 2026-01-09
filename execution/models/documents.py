"""Modèles Pydantic pour les documents administratifs."""

from pydantic import BaseModel, Field, field_validator
from datetime import date
from decimal import Decimal
from typing import Literal, Optional


class InvoiceItem(BaseModel):
    """Item d'une facture ou d'un devis."""

    description: str = Field(..., min_length=1, description="Description de l'article")
    quantity: Decimal = Field(..., gt=0, description="Quantité")
    unit_price: Decimal = Field(..., ge=0, description="Prix unitaire HT")
    vat_rate: Decimal = Field(default=Decimal("0.20"), ge=0, le=1, description="Taux de TVA")

    @property
    def total_ht(self) -> Decimal:
        """Calcule le total HT."""
        return self.quantity * self.unit_price

    @property
    def vat_amount(self) -> Decimal:
        """Calcule le montant de TVA."""
        return self.total_ht * self.vat_rate

    @property
    def total_ttc(self) -> Decimal:
        """Calcule le total TTC."""
        return self.total_ht + self.vat_amount


class Invoice(BaseModel):
    """Modèle de facture."""

    invoice_number: str = Field(..., description="Numéro de facture (ex: 2024-0001)")
    invoice_date: date = Field(..., description="Date de facturation")
    due_date: date = Field(..., description="Date d'échéance")

    # Client info
    client_name: str = Field(..., min_length=1, description="Nom du client")
    client_address: str = Field(..., min_length=1, description="Adresse du client")
    client_siret: Optional[str] = Field(default=None, description="SIRET du client (optionnel)")

    # Items
    items: list[InvoiceItem] = Field(..., min_items=1, description="Liste des articles")

    # Additional info
    payment_conditions: str = Field(
        default="Paiement à 30 jours",
        description="Conditions de paiement"
    )
    notes: Optional[str] = Field(default=None, description="Notes additionnelles")

    @field_validator("client_siret")
    @classmethod
    def validate_siret(cls, v: Optional[str]) -> Optional[str]:
        """Valide le format du SIRET (14 chiffres)."""
        if v is not None:
            # Enlever les espaces
            v = v.replace(" ", "")
            if not v.isdigit() or len(v) != 14:
                raise ValueError("Le SIRET doit contenir exactement 14 chiffres")
        return v

    @field_validator("due_date")
    @classmethod
    def validate_due_date(cls, v: date, info) -> date:
        """Vérifie que la date d'échéance est après la date de facturation."""
        if "invoice_date" in info.data and v < info.data["invoice_date"]:
            raise ValueError("La date d'échéance doit être postérieure à la date de facturation")
        return v

    @property
    def total_ht(self) -> Decimal:
        """Calcule le total HT de la facture."""
        return sum(item.total_ht for item in self.items)

    @property
    def total_vat(self) -> Decimal:
        """Calcule le total de TVA."""
        return sum(item.vat_amount for item in self.items)

    @property
    def total_ttc(self) -> Decimal:
        """Calcule le total TTC de la facture."""
        return sum(item.total_ttc for item in self.items)


class Quote(BaseModel):
    """Modèle de devis."""

    quote_number: str = Field(..., description="Numéro de devis (ex: DEV-2024-0001)")
    quote_date: date = Field(..., description="Date du devis")
    validity_days: int = Field(default=30, gt=0, description="Validité en jours")

    # Client info
    client_name: str = Field(..., min_length=1, description="Nom du client")
    client_address: str = Field(..., min_length=1, description="Adresse du client")
    client_siret: Optional[str] = Field(default=None, description="SIRET du client (optionnel)")

    # Items
    items: list[InvoiceItem] = Field(..., min_items=1, description="Liste des articles")

    # Additional info
    notes: Optional[str] = Field(default=None, description="Notes additionnelles")

    @field_validator("client_siret")
    @classmethod
    def validate_siret(cls, v: Optional[str]) -> Optional[str]:
        """Valide le format du SIRET."""
        if v is not None:
            v = v.replace(" ", "")
            if not v.isdigit() or len(v) != 14:
                raise ValueError("Le SIRET doit contenir exactement 14 chiffres")
        return v

    @property
    def valid_until(self) -> date:
        """Calcule la date de validité."""
        from datetime import timedelta
        return self.quote_date + timedelta(days=self.validity_days)

    @property
    def total_ht(self) -> Decimal:
        """Calcule le total HT du devis."""
        return sum(item.total_ht for item in self.items)

    @property
    def total_vat(self) -> Decimal:
        """Calcule le total de TVA."""
        return sum(item.vat_amount for item in self.items)

    @property
    def total_ttc(self) -> Decimal:
        """Calcule le total TTC du devis."""
        return sum(item.total_ttc for item in self.items)


class MileageRecord(BaseModel):
    """Modèle de note de frais kilométriques."""

    travel_date: date = Field(..., description="Date du déplacement")
    start_location: str = Field(..., min_length=1, description="Lieu de départ")
    end_location: str = Field(..., min_length=1, description="Lieu d'arrivée")
    distance_km: Decimal = Field(..., gt=0, description="Distance en kilomètres")
    purpose: str = Field(..., min_length=1, description="Motif du déplacement")
    vehicle_type: Literal["voiture", "moto", "scooter"] = Field(
        default="voiture",
        description="Type de véhicule"
    )
    fiscal_power: int = Field(..., gt=0, le=20, description="Puissance fiscale (chevaux)")

    @property
    def rate_per_km(self) -> Decimal:
        """
        Calcule le tarif au km selon le barème fiscal 2024.
        Simplifié pour cet exemple - à adapter selon le barème officiel.
        """
        if self.vehicle_type == "voiture":
            if self.fiscal_power <= 3:
                return Decimal("0.529")
            elif self.fiscal_power <= 5:
                return Decimal("0.606")
            elif self.fiscal_power <= 7:
                return Decimal("0.636")
            else:
                return Decimal("0.665")
        elif self.vehicle_type == "moto":
            if self.fiscal_power <= 2:
                return Decimal("0.395")
            else:
                return Decimal("0.468")
        else:  # scooter
            return Decimal("0.315")

    @property
    def total_amount(self) -> Decimal:
        """Calcule le montant total des frais."""
        return self.distance_km * self.rate_per_km


class RentReceipt(BaseModel):
    """Modèle de quittance de loyer."""

    receipt_number: str = Field(..., description="Numéro de quittance")
    period_month: int = Field(..., ge=1, le=12, description="Mois de la période (1-12)")
    period_year: int = Field(..., ge=2000, description="Année de la période")

    # Tenant info
    tenant_name: str = Field(..., min_length=1, description="Nom du locataire")
    tenant_address: str = Field(..., min_length=1, description="Adresse du locataire")

    # Property info
    property_address: str = Field(..., min_length=1, description="Adresse du bien loué")

    # Amounts
    rent_amount: Decimal = Field(..., gt=0, description="Montant du loyer")
    charges_amount: Decimal = Field(default=Decimal("0"), ge=0, description="Montant des charges")

    # Payment info
    payment_date: date = Field(..., description="Date du paiement")
    payment_method: Literal["virement", "chèque", "espèces", "prélèvement"] = Field(
        default="virement",
        description="Moyen de paiement"
    )

    @property
    def total_amount(self) -> Decimal:
        """Calcule le montant total (loyer + charges)."""
        return self.rent_amount + self.charges_amount

    @property
    def period_str(self) -> str:
        """Retourne la période au format texte."""
        months = [
            "Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
            "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"
        ]
        return f"{months[self.period_month - 1]} {self.period_year}"


class ChargeItem(BaseModel):
    """Item de charge locative."""

    label: str = Field(..., min_length=1, description="Libellé de la charge")
    amount: Decimal = Field(..., ge=0, description="Montant de la charge")


class RentalCharges(BaseModel):
    """Modèle de décompte de charges locatives."""

    period_start: date = Field(..., description="Début de la période")
    period_end: date = Field(..., description="Fin de la période")

    # Tenant info
    tenant_name: str = Field(..., min_length=1, description="Nom du locataire")

    # Property info
    property_address: str = Field(..., min_length=1, description="Adresse du bien")

    # Charges
    charges: list[ChargeItem] = Field(..., min_items=1, description="Liste des charges")

    @field_validator("period_end")
    @classmethod
    def validate_period(cls, v: date, info) -> date:
        """Vérifie que la fin de période est après le début."""
        if "period_start" in info.data and v <= info.data["period_start"]:
            raise ValueError("La fin de période doit être postérieure au début")
        return v

    @property
    def total_charges(self) -> Decimal:
        """Calcule le total des charges."""
        return sum(charge.amount for charge in self.charges)
