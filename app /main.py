import streamlit as st
from datetime import date
from app.utils.helpers import load_json
from app.utils.calculations import compute_line_amount, compute_totals
from app.pdf.invoice_pdf import generate_invoice_pdf

st.set_page_config(page_title="Mohan Invoice", layout="wide")

# Load config/data
company = load_json("app/data/company_profile.json")
customers = load_json("app/data/sample_customers.json") or []
products = load_json("app/data/sample_products.json") or []

# Session init
if "items" not in st.session_state:
    st.session_state.items = [
        {"art_no": "", "product": "", "hsn": "", "qty": 1, "rate": 0, "amount": 0}
    ]

st.title("Invoice Generator (Prototype)")

# Top actions
colA, colB, colC = st.columns([1,1,2])
with colA:
    if st.button("New Invoice", use_container_width=True):
        st.session_state.items = [{"art_no": "", "product": "", "hsn": "", "qty": 1, "rate": 0, "amount": 0}]
        st.success("Started a new invoice.")
with colB:
    st.caption("Prototype build")

st.divider()

# Invoice meta
m1, m2, m3, m4 = st.columns([1,1,1,1])
with m1:
    invoice_no = st.text_input("Invoice No", value="597")
with m2:
    inv_date = st.date_input("Date", value=date.today())
with m3:
    sale_type = st.selectbox("Sale Type", ["STATE SALE", "INTERSTATE SALE"])
with m4:
    state_code = st.text_input("State Code", value=company.get("state_code", "27"))

st.divider()

# Customer select + auto fill
cust_names = [c["name"] for c in customers] if customers else []
selected_name = st.selectbox("Customer (Consignee Name)", options=cust_names if cust_names else ["(No customers loaded)"])
cust = next((c for c in customers if c["name"] == selected_name), {"name": "", "gstin": "", "address": ""})

c1, c2, c3 = st.columns([1,1,2])
with c1:
    cust_name = st.text_input("Name", value=cust.get("name",""))
with c2:
    cust_gstin = st.text_input("GSTIN", value=cust.get("gstin",""))
with c3:
    cust_address = st.text_input("Address", value=cust.get("address",""))

st.divider()

st.subheader("Items")

# Add/remove row controls
r1, r2, r3 = st.columns([1,1,6])
with r1:
    if st.button("Add item"):
        st.session_state.items.append({"art_no": "", "product": "", "hsn": "", "qty": 1, "rate": 0, "amount": 0})
with r2:
    if st.button("Remove last") and len(st.session_state.items) > 1:
        st.session_state.items.pop()

# Items editor
prod_names = [p["name"] for p in products]

for idx, it in enumerate(st.session_state.items):
    cols = st.columns([1,3,1,1,1,1])
    with cols[0]:
        it["art_no"] = st.text_input(f"Art No #{idx+1}", value=it.get("art_no",""), key=f"art_{idx}")
    with cols[1]:
        if prod_names:
            chosen = st.selectbox(f"Product #{idx+1}", options=[""] + prod_names, index=0 if it.get("product","") == "" else (prod_names.index(it["product"])+1 if it["product"] in prod_names else 0), key=f"prod_{idx}")
            it["product"] = chosen
            # auto-fill HSN + rate when selecting product
            if chosen:
                p = next((x for x in products if x["name"] == chosen), None)
                if p:
                    it["hsn"] = p.get("hsn", it.get("hsn",""))
                    if float(it.get("rate", 0) or 0) == 0:
                        it["rate"] = p.get("default_rate", 0)
        else:
            it["product"] = st.text_input(f"Product #{idx+1}", value=it.get("product",""), key=f"prod_txt_{idx}")
    with cols[2]:
        it["hsn"] = st.text_input(f"HSN #{idx+1}", value=it.get("hsn",""), key=f"hsn_{idx}")
    with cols[3]:
        it["qty"] = st.number_input(f"Qty #{idx+1}", min_value=0.0, step=1.0, value=float(it.get("qty", 1) or 1), key=f"qty_{idx}")
    with cols[4]:
        it["rate"] = st.number_input(f"Rate #{idx+1}", min_value=0.0, step=1.0, value=float(it.get("rate", 0) or 0), key=f"rate_{idx}")
    with cols[5]:
        it["amount"] = compute_line_amount(it["qty"], it["rate"])
        st.text_input(f"Amount #{idx+1}", value=str(it["amount"]), disabled=True, key=f"amt_{idx}")

st.divider()

# Tax rates
t1, t2, t3 = st.columns([1,1,2])
with t1:
    cgst_rate = st.number_input("CGST rate", min_value=0.0, max_value=1.0, step=0.01, value=float(company.get("default_cgst_rate", 0.06)))
with t2:
    sgst_rate = st.number_input("SGST rate", min_value=0.0, max_value=1.0, step=0.01, value=float(company.get("default_sgst_rate", 0.06)))

totals = compute_totals(st.session_state.items, cgst_rate=cgst_rate, sgst_rate=sgst_rate)

s1, s2, s3, s4 = st.columns([1,1,1,1])
s1.metric("Subtotal", f"{totals['subtotal']:.2f}")
s2.metric("CGST", f"{totals['cgst']:.2f}")
s3.metric("SGST", f"{totals['sgst']:.2f}")
s4.metric("Total", f"{totals['total']:.2f}")

st.divider()

# Generate PDF
generate = st.button("Generate Invoice (A4 PDF)", type="primary", use_container_width=True)

if generate:
    payload = {
        "company": company,
        "invoice": {
            "invoice_no": invoice_no,
            "date": inv_date.strftime("%d-%m-%Y"),
            "sale_type": sale_type,
            "state_code": state_code,
        },
        "customer": {
            "name": cust_name,
            "gstin": cust_gstin,
            "address": cust_address,
        },
        "items": st.session_state.items,
        "totals": totals,
    }

    pdf_bytes = generate_invoice_pdf(payload)

    st.success("Invoice generated.")
    st.download_button(
        label="Download PDF",
        data=pdf_bytes,
        file_name=f"invoice_{invoice_no}.pdf",
        mime="application/pdf",
        use_container_width=True
    )

    # Preview inside Streamlit
    st.subheader("Preview")
    st.pdf(pdf_bytes) if hasattr(st, "pdf") else st.write("Preview not supported in this Streamlit version.")
