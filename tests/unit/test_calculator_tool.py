import pytest
from execution.tools.calculator_tool import CalculatorTool
from decimal import Decimal

def test_facture_totals_basic():
    tool = CalculatorTool()
    result = tool._run(
        operation="facture_totals",
        prix_unitaire=500.0,
        quantite=10.5,
        tva_pourcent=20.0
    )
    assert result["total_ht"] == 5250.0
    assert result["montant_tva"] == 1050.0
    assert result["total_ttc"] == 6300.0

def test_facture_totals_rounding():
    tool = CalculatorTool()
    # 33.33 * 3 = 99.99
    # TVA 20% = 19.998 -> 20.00
    # TTC = 119.99
    result = tool._run(
        operation="facture_totals",
        prix_unitaire=33.33,
        quantite=3.0,
        tva_pourcent=20.0
    )
    assert result["total_ht"] == 99.99
    assert result["montant_tva"] == 20.00
    assert result["total_ttc"] == 119.99

def test_facture_totals_zero_tva():
    tool = CalculatorTool()
    result = tool._run(
        operation="facture_totals",
        prix_unitaire=100.0,
        quantite=1.0,
        tva_pourcent=0.0
    )
    assert result["total_ht"] == 100.0
    assert result["montant_tva"] == 0.0
    assert result["total_ttc"] == 100.0

def test_charges_totals_basic():
    tool = CalculatorTool()
    items = [
        {"description": "Eau", "amount": 50.5},
        {"description": "Électricité", "amount": 120.3},
        {"description": "Ordures", "amount": 30.0}
    ]
    result = tool._run(
        operation="charges_totals",
        items=items
    )
    assert result["total_ht"] == 200.8
    assert result["total_ttc"] == 200.8

def test_calculator_invalid_operation():
    tool = CalculatorTool()
    with pytest.raises(ValueError, match="Unknown operation"):
        tool._run(operation="invalid")

@pytest.mark.asyncio
async def test_calculator_async():
    tool = CalculatorTool()
    result = await tool._arun(
        operation="facture_totals",
        prix_unitaire=100.0,
        quantite=2.0,
        tva_pourcent=20.0
    )
    assert result["total_ht"] == 200.0
    assert result["montant_tva"] == 40.0
    assert result["total_ttc"] == 240.0
