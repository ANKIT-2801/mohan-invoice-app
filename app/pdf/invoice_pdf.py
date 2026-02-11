from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm

from app.pdf.styles import FONT_BOLD, FONT_NORMAL

def money(x: float) -> str:
    return f"{x:,.2f}"

def generate_invoice_pdf(payload: dict) -> bytes:
    """
    Creates an A4 PDF invoice. Layout is clean and stable; you can refine to match Invoice Draft 3 later.
    """
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    W, H = A4

    x = 14 * mm
    y = H - 14 * mm

    company = payload["company"]
    inv = payload["invoice"]
    customer = payload["customer"]
    items = payload["items"]
    totals = payload["totals"]

    # Header
    c.setFont(FONT_BOLD, 16)
    c.drawCentredString(W / 2, y, "INVOICE")
    y -= 8 * mm

    c.setFont(FONT_BOLD, 20)
    c.drawCentredString(W / 2, y, company["company_name"])
    y -= 7 * mm

    c.setFont(FONT_NORMAL, 9)
    c.drawCentredString(W / 2, y, company["office_address"])
    y -= 5 * mm

    left = x
    right = W - x

    # Company details line
    c.setFont(FONT_NORMAL, 9)
    c.drawString(left, y, f"GSTIN: {company['gstin']}    UDYOG AADHAR: {company['udyog_aadhar']}")
    c.drawRightString(right, y, f"EMAIL: {company['email']}    MOBILE: {', '.join(company['phones'])}")
    y -= 6 * mm

    # Invoice meta box
    c.setFont(FONT_BOLD, 10)
    c.drawString(left, y, f"INVOICE NO: {inv['invoice_no']}")
    c.drawCentredString(W / 2, y, f"DATE: {inv['date']}")
    c.drawRightString(right, y, f"SALE TYPE: {inv['sale_type']}")
    y -= 6 * mm

    c.line(left, y, right, y)
    y -= 6 * mm

    # Consignee details
    c.setFont(FONT_BOLD, 10)
    c.drawString(left, y, "CONSIGNEE DETAILS")
    y -= 5 * mm

    c.setFont(FONT_NORMAL, 10)
    c.drawString(left, y, f"Name: {customer['name']}")
    y -= 5 * mm
    c.drawString(left, y, f"GSTIN: {customer['gstin']}")
    y -= 5 * mm
    c.drawString(left, y, f"Address: {customer['address']}")
    y -= 7 * mm

    # Items table header
    table_top = y
    c.setFont(FONT_BOLD, 9)

    cols = [
        ("ART NO", 18*mm),
        ("PRODUCT DETAILS", 70*mm),
        ("HSN", 25*mm),
        ("QTY", 18*mm),
        ("RATE", 20*mm),
        ("AMOUNT", 26*mm),
    ]

    cx = left
    c.rect(left, y - 72*mm, right - left, 72*mm, stroke=1, fill=0)

    header_y = y - 5*mm
    for title, w in cols:
        c.drawString(cx + 2*mm, header_y, title)
        cx += w

    # Column vertical lines
    cx = left
    for _, w in cols[:-1]:
        cx += w
        c.line(cx, y, cx, y - 72*mm)

    # Rows
    c.setFont(FONT_NORMAL, 9)
    row_y = y - 10*mm
    row_h = 6*mm

    for it in items[:10]:  # keep simple for prototype
        c.drawString(left + 2*mm, row_y, str(it.get("art_no", "")))
        c.drawString(left + 20*mm, row_y, str(it.get("product", ""))[:40])
        c.drawString(left + 92*mm, row_y, str(it.get("hsn", "")))
        c.drawRightString(left + 110*mm, row_y, str(it.get("qty", "")))
        c.drawRightString(left + 130*mm, row_y, money(float(it.get("rate", 0) or 0)))
        c.drawRightString(right - 2*mm, row_y, money(float(it.get("amount", 0) or 0)))
        row_y -= row_h

    y = y - 76*mm

    # Totals area
    c.setFont(FONT_BOLD, 10)
    c.drawRightString(right - 2*mm, y, f"SUBTOTAL: {money(totals['subtotal'])}")
    y -= 5*mm
    c.setFont(FONT_NORMAL, 10)
    c.drawRightString(right - 2*mm, y, f"CGST: {money(totals['cgst'])}")
    y -= 5*mm
    c.drawRightString(right - 2*mm, y, f"SGST: {money(totals['sgst'])}")
    y -= 6*mm
    c.setFont(FONT_BOLD, 11)
    c.drawRightString(right - 2*mm, y, f"TOTAL: {money(totals['total'])}")
    y -= 8*mm

    # Bank details + signature
    c.setFont(FONT_BOLD, 10)
    c.drawString(left, y, "Bank:")
    c.setFont(FONT_NORMAL, 9)
    y -= 5*mm
    c.drawString(left, y, company["bank_name"])
    y -= 4.5*mm
    c.drawString(left, y, f"Address: {company['bank_address']}")
    y -= 4.5*mm
    c.drawString(left, y, f"A/C No: {company['account_no']}")
    y -= 4.5*mm
    c.drawString(left, y, f"A/C Name: {company['account_name']}")
    y -= 4.5*mm
    c.drawString(left, y, f"IFSC Code: {company['ifsc']}")
    y -= 10*mm

    c.setFont(FONT_BOLD, 10)
    c.drawRightString(right, y + 15*mm, f"FOR {company['company_name']}")
    c.setFont(FONT_NORMAL, 10)
    c.drawRightString(right, y, "SIGNATURE")

    c.showPage()
    c.save()

    return buf.getvalue()
