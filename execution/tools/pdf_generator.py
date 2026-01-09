"""Générateur de documents PDF avec ReportLab."""

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from pathlib import Path
from datetime import datetime
from decimal import Decimal
from execution.models.documents import Invoice, Quote, MileageRecord, RentReceipt, RentalCharges
import logging

logger = logging.getLogger(__name__)


class PDFGenerator:
    """Générateur de documents PDF professionnels."""

    def __init__(self, output_dir: Path):
        """
        Initialise le générateur.

        Args:
            output_dir: Répertoire de sortie pour les PDFs
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.width, self.height = A4

    def generate_invoice_pdf(self, invoice: Invoice, company_info: dict) -> Path:
        """
        Génère un PDF de facture conforme aux normes françaises.

        Args:
            invoice: Objet Invoice avec les données
            company_info: Informations de l'entreprise émettrice

        Returns:
            Path vers le PDF généré
        """
        filename = f"facture_{invoice.invoice_number.replace('/', '-')}_{datetime.now().strftime('%Y%m%d')}.pdf"
        filepath = self.output_dir / filename

        c = canvas.Canvas(str(filepath), pagesize=A4)

        # En-tête entreprise
        y = self.height - 2*cm
        c.setFont("Helvetica-Bold", 16)
        c.drawString(2*cm, y, company_info["name"])

        y -= 0.6*cm
        c.setFont("Helvetica", 10)
        c.drawString(2*cm, y, company_info["address"])

        y -= 0.5*cm
        c.drawString(2*cm, y, f"SIRET: {company_info['siret']}")

        y -= 0.5*cm
        c.drawString(2*cm, y, f"N° TVA: {company_info['tva']}")

        # Titre FACTURE
        y -= 2*cm
        c.setFont("Helvetica-Bold", 24)
        c.drawString(2*cm, y, "FACTURE")

        c.setFont("Helvetica-Bold", 12)
        c.drawString(2*cm, y - 0.7*cm, f"N° {invoice.invoice_number}")

        # Informations client (à droite)
        y_client = self.height - 2*cm
        c.setFont("Helvetica-Bold", 11)
        c.drawString(12*cm, y_client, "Client:")

        y_client -= 0.6*cm
        c.setFont("Helvetica", 10)
        c.drawString(12*cm, y_client, invoice.client_name)

        y_client -= 0.5*cm
        # Gérer les adresses multi-lignes
        address_lines = invoice.client_address.split(",")
        for line in address_lines:
            c.drawString(12*cm, y_client, line.strip())
            y_client -= 0.5*cm

        if invoice.client_siret:
            c.drawString(12*cm, y_client, f"SIRET: {invoice.client_siret}")

        # Dates
        y -= 2*cm
        c.setFont("Helvetica", 10)
        c.drawString(2*cm, y, f"Date d'émission: {invoice.invoice_date.strftime('%d/%m/%Y')}")

        y -= 0.6*cm
        c.drawString(2*cm, y, f"Date d'échéance: {invoice.due_date.strftime('%d/%m/%Y')}")

        # Tableau des items
        y -= 1.5*cm

        # En-têtes du tableau
        c.setFont("Helvetica-Bold", 10)
        headers_y = y
        c.drawString(2*cm, headers_y, "Description")
        c.drawString(10*cm, headers_y, "Qté")
        c.drawString(12*cm, headers_y, "P.U. HT")
        c.drawString(14.5*cm, headers_y, "Total HT")
        c.drawString(17.5*cm, headers_y, "TVA")

        # Ligne de séparation
        y -= 0.3*cm
        c.line(2*cm, y, 19*cm, y)

        # Items
        y -= 0.7*cm
        c.setFont("Helvetica", 9)

        for item in invoice.items:
            # Description (tronquer si trop long)
            desc = item.description[:50]
            c.drawString(2*cm, y, desc)
            c.drawString(10*cm, y, str(item.quantity))
            c.drawString(12*cm, y, f"{float(item.unit_price):.2f} €")
            c.drawString(14.5*cm, y, f"{float(item.total_ht):.2f} €")
            c.drawString(17.5*cm, y, f"{float(item.vat_rate*100):.0f}%")
            y -= 0.6*cm

        # Ligne de séparation avant totaux
        y -= 0.5*cm
        c.line(12*cm, y, 19*cm, y)

        # Totaux
        y -= 0.7*cm
        c.setFont("Helvetica-Bold", 11)
        c.drawString(13*cm, y, "Total HT:")
        c.drawString(17*cm, y, f"{float(invoice.total_ht):.2f} €")

        y -= 0.7*cm
        c.drawString(13*cm, y, "TVA:")
        c.drawString(17*cm, y, f"{float(invoice.total_vat):.2f} €")

        y -= 0.7*cm
        c.setFont("Helvetica-Bold", 13)
        c.drawString(13*cm, y, "Total TTC:")
        c.drawString(17*cm, y, f"{float(invoice.total_ttc):.2f} €")

        # Conditions de paiement
        y -= 2*cm
        c.setFont("Helvetica", 9)
        c.drawString(2*cm, y, f"Conditions de paiement: {invoice.payment_conditions}")

        # Notes additionnelles
        if invoice.notes:
            y -= 1*cm
            c.drawString(2*cm, y, "Notes:")
            y -= 0.5*cm
            c.setFont("Helvetica", 8)
            # Gérer les notes multi-lignes
            notes_lines = invoice.notes.split("\n")
            for line in notes_lines[:3]:  # Limiter à 3 lignes
                c.drawString(2*cm, y, line)
                y -= 0.4*cm

        # Pied de page
        c.setFont("Helvetica", 7)
        c.drawCentredString(self.width / 2, 2*cm, company_info["name"])
        c.drawCentredString(self.width / 2, 1.6*cm, f"SIRET: {company_info['siret']} - TVA: {company_info['tva']}")

        c.save()
        logger.info(f"✅ Facture PDF générée: {filepath}")
        return filepath

    def generate_quote_pdf(self, quote: Quote, company_info: dict) -> Path:
        """Génère un PDF de devis (similaire à la facture)."""
        filename = f"devis_{quote.quote_number.replace('/', '-')}_{datetime.now().strftime('%Y%m%d')}.pdf"
        filepath = self.output_dir / filename

        c = canvas.Canvas(str(filepath), pagesize=A4)

        # En-tête (identique à facture)
        y = self.height - 2*cm
        c.setFont("Helvetica-Bold", 16)
        c.drawString(2*cm, y, company_info["name"])

        y -= 0.6*cm
        c.setFont("Helvetica", 10)
        c.drawString(2*cm, y, company_info["address"])

        y -= 0.5*cm
        c.drawString(2*cm, y, f"SIRET: {company_info['siret']}")

        # Titre DEVIS
        y -= 2*cm
        c.setFont("Helvetica-Bold", 24)
        c.drawString(2*cm, y, "DEVIS")

        c.setFont("Helvetica-Bold", 12)
        c.drawString(2*cm, y - 0.7*cm, f"N° {quote.quote_number}")

        # Client
        y_client = self.height - 2*cm
        c.setFont("Helvetica-Bold", 11)
        c.drawString(12*cm, y_client, "Client:")

        y_client -= 0.6*cm
        c.setFont("Helvetica", 10)
        c.drawString(12*cm, y_client, quote.client_name)

        y_client -= 0.5*cm
        address_lines = quote.client_address.split(",")
        for line in address_lines:
            c.drawString(12*cm, y_client, line.strip())
            y_client -= 0.5*cm

        # Dates
        y -= 2*cm
        c.setFont("Helvetica", 10)
        c.drawString(2*cm, y, f"Date: {quote.quote_date.strftime('%d/%m/%Y')}")

        y -= 0.6*cm
        c.drawString(2*cm, y, f"Valable jusqu'au: {quote.valid_until.strftime('%d/%m/%Y')}")

        # Tableau items (même logique que facture)
        y -= 1.5*cm
        c.setFont("Helvetica-Bold", 10)
        c.drawString(2*cm, y, "Description")
        c.drawString(10*cm, y, "Qté")
        c.drawString(12*cm, y, "P.U. HT")
        c.drawString(14.5*cm, y, "Total HT")

        y -= 0.3*cm
        c.line(2*cm, y, 19*cm, y)

        y -= 0.7*cm
        c.setFont("Helvetica", 9)

        for item in quote.items:
            desc = item.description[:50]
            c.drawString(2*cm, y, desc)
            c.drawString(10*cm, y, str(item.quantity))
            c.drawString(12*cm, y, f"{float(item.unit_price):.2f} €")
            c.drawString(14.5*cm, y, f"{float(item.total_ht):.2f} €")
            y -= 0.6*cm

        # Totaux
        y -= 0.5*cm
        c.line(12*cm, y, 19*cm, y)

        y -= 0.7*cm
        c.setFont("Helvetica-Bold", 11)
        c.drawString(13*cm, y, "Total HT:")
        c.drawString(17*cm, y, f"{float(quote.total_ht):.2f} €")

        y -= 0.7*cm
        c.drawString(13*cm, y, "TVA:")
        c.drawString(17*cm, y, f"{float(quote.total_vat):.2f} €")

        y -= 0.7*cm
        c.setFont("Helvetica-Bold", 13)
        c.drawString(13*cm, y, "Total TTC:")
        c.drawString(17*cm, y, f"{float(quote.total_ttc):.2f} €")

        # Note de validité
        y -= 2*cm
        c.setFont("Helvetica-Oblique", 9)
        c.drawString(2*cm, y, f"Ce devis est valable {quote.validity_days} jours à compter de sa date d'émission.")

        c.save()
        logger.info(f"✅ Devis PDF généré: {filepath}")
        return filepath

    def generate_mileage_pdf(
        self,
        records: list[MileageRecord],
        company_info: dict,
        period_label: str = "Note de frais kilométriques"
    ) -> Path:
        """Génère un PDF de note de frais kilométriques."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"frais_km_{timestamp}.pdf"
        filepath = self.output_dir / filename

        c = canvas.Canvas(str(filepath), pagesize=A4)

        # En-tête
        y = self.height - 2*cm
        c.setFont("Helvetica-Bold", 18)
        c.drawString(2*cm, y, period_label)

        y -= 1*cm
        c.setFont("Helvetica", 10)
        c.drawString(2*cm, y, f"Émis par: {company_info['name']}")

        y -= 0.5*cm
        c.drawString(2*cm, y, f"Date: {datetime.now().strftime('%d/%m/%Y')}")

        # Tableau
        y -= 1.5*cm
        c.setFont("Helvetica-Bold", 9)
        c.drawString(2*cm, y, "Date")
        c.drawString(4*cm, y, "Trajet")
        c.drawString(11*cm, y, "Distance")
        c.drawString(13.5*cm, y, "Véhicule")
        c.drawString(15.5*cm, y, "Tarif/km")
        c.drawString(17.5*cm, y, "Montant")

        y -= 0.3*cm
        c.line(2*cm, y, 19*cm, y)

        y -= 0.7*cm
        c.setFont("Helvetica", 8)

        total = Decimal("0")

        for record in records:
            c.drawString(2*cm, y, record.travel_date.strftime('%d/%m/%Y'))
            trajet = f"{record.start_location} → {record.end_location}"[:30]
            c.drawString(4*cm, y, trajet)
            c.drawString(11*cm, y, f"{float(record.distance_km):.1f} km")
            c.drawString(13.5*cm, y, record.vehicle_type)
            c.drawString(15.5*cm, y, f"{float(record.rate_per_km):.3f} €")
            c.drawString(17.5*cm, y, f"{float(record.total_amount):.2f} €")

            total += record.total_amount
            y -= 0.5*cm

        # Total
        y -= 0.5*cm
        c.line(15*cm, y, 19*cm, y)

        y -= 0.7*cm
        c.setFont("Helvetica-Bold", 11)
        c.drawString(15*cm, y, "TOTAL:")
        c.drawString(17.5*cm, y, f"{float(total):.2f} €")

        c.save()
        logger.info(f"✅ Note de frais PDF générée: {filepath}")
        return filepath

    def generate_rent_receipt_pdf(self, receipt: RentReceipt, company_info: dict) -> Path:
        """Génère un PDF de quittance de loyer."""
        filename = f"quittance_{receipt.receipt_number.replace('/', '-')}.pdf"
        filepath = self.output_dir / filename

        c = canvas.Canvas(str(filepath), pagesize=A4)

        # Titre
        y = self.height - 3*cm
        c.setFont("Helvetica-Bold", 20)
        c.drawCentredString(self.width / 2, y, "QUITTANCE DE LOYER")

        # Propriétaire
        y -= 2*cm
        c.setFont("Helvetica-Bold", 11)
        c.drawString(2*cm, y, "Propriétaire:")

        y -= 0.6*cm
        c.setFont("Helvetica", 10)
        c.drawString(2*cm, y, company_info["name"])

        y -= 0.5*cm
        c.drawString(2*cm, y, company_info["address"])

        # Locataire
        y -= 1.5*cm
        c.setFont("Helvetica-Bold", 11)
        c.drawString(2*cm, y, "Locataire:")

        y -= 0.6*cm
        c.setFont("Helvetica", 10)
        c.drawString(2*cm, y, receipt.tenant_name)

        y -= 0.5*cm
        c.drawString(2*cm, y, receipt.tenant_address)

        # Bien loué
        y -= 1.5*cm
        c.setFont("Helvetica-Bold", 11)
        c.drawString(2*cm, y, "Bien loué:")

        y -= 0.6*cm
        c.setFont("Helvetica", 10)
        c.drawString(2*cm, y, receipt.property_address)

        # Période et paiement
        y -= 1.5*cm
        c.setFont("Helvetica", 10)
        c.drawString(2*cm, y, f"Période: {receipt.period_str}")

        y -= 0.6*cm
        c.drawString(2*cm, y, f"Date de paiement: {receipt.payment_date.strftime('%d/%m/%Y')}")

        y -= 0.6*cm
        c.drawString(2*cm, y, f"Moyen de paiement: {receipt.payment_method}")

        # Détail des montants
        y -= 2*cm
        c.setFont("Helvetica-Bold", 11)
        c.drawString(10*cm, y, "Loyer:")
        c.drawString(16*cm, y, f"{float(receipt.rent_amount):.2f} €")

        y -= 0.7*cm
        c.drawString(10*cm, y, "Charges:")
        c.drawString(16*cm, y, f"{float(receipt.charges_amount):.2f} €")

        y -= 0.5*cm
        c.line(10*cm, y, 18*cm, y)

        y -= 0.7*cm
        c.setFont("Helvetica-Bold", 13)
        c.drawString(10*cm, y, "TOTAL:")
        c.drawString(16*cm, y, f"{float(receipt.total_amount):.2f} €")

        # Certification
        y -= 2*cm
        c.setFont("Helvetica-Oblique", 9)
        text = "Je soussigné(e), certifie avoir reçu la somme indiquée ci-dessus au titre du loyer et des charges pour la période mentionnée."
        c.drawString(2*cm, y, text)

        # Signature
        y -= 2*cm
        c.setFont("Helvetica", 10)
        c.drawString(12*cm, y, "Fait le:")
        c.drawString(14.5*cm, y, datetime.now().strftime('%d/%m/%Y'))

        y -= 1*cm
        c.drawString(12*cm, y, "Signature:")

        c.save()
        logger.info(f"✅ Quittance de loyer PDF générée: {filepath}")
        return filepath
