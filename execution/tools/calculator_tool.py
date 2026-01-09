"""Tool for financial calculations."""

from typing import Dict, Any, Optional
from decimal import Decimal, ROUND_HALF_UP
from langchain_core.tools import BaseTool
import logging

logger = logging.getLogger(__name__)

class CalculatorTool(BaseTool):
    name: str = "calculator"
    description: str = """
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

    def _run(self, operation: str, **kwargs) -> Dict[str, float]:
        """Execute calculation synchronously."""
        try:
            if operation == "facture_totals":
                return self._calc_facture_totals(**kwargs)
            elif operation == "charges_totals":
                return self._calc_charges_totals(**kwargs)
            else:
                raise ValueError(f"Unknown operation: {operation}")
        except Exception as e:
            logger.error(f"Calculation error: {e}")
            raise

    async def _arun(self, operation: str, **kwargs) -> Dict[str, float]:
        """Execute calculation asynchronously (wraps synchronous execution)."""
        return self._run(operation, **kwargs)

    def _calc_facture_totals(
        self,
        prix_unitaire: float,
        quantite: float,
        tva_pourcent: float = 20.0
    ) -> Dict[str, float]:
        """Calculate invoice totals with Decimal precision."""
        pu = Decimal(str(prix_unitaire))
        qty = Decimal(str(quantite))
        tva = Decimal(str(tva_pourcent))

        total_ht = (pu * qty).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        montant_tva = (total_ht * tva / Decimal("100")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        total_ttc = (total_ht + montant_tva).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        return {
            "total_ht": float(total_ht),
            "montant_tva": float(montant_tva),
            "total_ttc": float(total_ttc)
        }

    def _calc_charges_totals(
        self,
        items: list[Dict[str, Any]]
    ) -> Dict[str, float]:
        """
        Calculate total for multiple charge items.
        Each item: {"description": str, "amount": float}
        """
        total_ht = Decimal("0.00")
        for item in items:
            amount = Decimal(str(item.get("amount", 0)))
            total_ht += amount

        total_ht = total_ht.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        
        # Charges locatives usually don't have separate VAT calculation here
        # but let's return a consistent structure
        return {
            "total_ht": float(total_ht),
            "montant_tva": 0.0,
            "total_ttc": float(total_ht)
        }
