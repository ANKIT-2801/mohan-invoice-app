from typing import List, Dict

def compute_line_amount(qty: float, rate: float) -> float:
    qty = float(qty or 0)
    rate = float(rate or 0)
    return round(qty * rate, 2)

def compute_totals(items: List[Dict], cgst_rate: float, sgst_rate: float) -> Dict:
    subtotal = 0.0
    total_qty = 0.0

    for it in items:
        qty = float(it.get("qty", 0) or 0)
        rate = float(it.get("rate", 0) or 0)
        amt = compute_line_amount(qty, rate)
        subtotal += amt
        total_qty += qty

    cgst = round(subtotal * float(cgst_rate or 0), 2)
    sgst = round(subtotal * float(sgst_rate or 0), 2)
    total = round(subtotal + cgst + sgst, 2)

    return {
        "subtotal": round(subtotal, 2),
        "cgst": cgst,
        "sgst": sgst,
        "total": total,
        "total_qty": round(total_qty, 2),
    }
