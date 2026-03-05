# app.py
# Streamlit app: Canada Land Transfer Tax (LTT) / Property Transfer Tax (PTT)
# Notes:
# - This is a best-effort calculator for common provincial/municipal rules.
# - It does NOT include all niche rebates/exemptions (e.g., rural, special programs, certain municipal rebates).
# - Values and brackets can change; verify with provincial guidance for final closing numbers.

import streamlit as st
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

st.set_page_config(page_title="Canada Land Transfer Tax Calculator", page_icon="🏠", layout="centered")

# -----------------------------
# Helpers / Core tax engine
# -----------------------------

@dataclass
class Bracket:
    up_to: Optional[float]  # None means no upper limit
    rate: float            # e.g., 0.01 for 1%

def calc_progressive_tax(amount: float, brackets: List[Bracket]) -> float:
    """Compute progressive tax for amount using ordered brackets."""
    if amount <= 0:
        return 0.0

    tax = 0.0
    prev_cap = 0.0

    for b in brackets:
        cap = b.up_to if b.up_to is not None else amount
        if amount <= prev_cap:
            break

        taxable = min(amount, cap) - prev_cap
        if taxable > 0:
            tax += taxable * b.rate

        prev_cap = cap

    return tax

def money(x: float) -> str:
    return f"${x:,.2f}"

# -----------------------------
# Province definitions (best-effort / common rules)
# -----------------------------
PROVINCES = [
    "Alberta",
    "British Columbia",
    "Manitoba",
    "New Brunswick",
    "Newfoundland and Labrador",
    "Northwest Territories",
    "Nova Scotia",
    "Nunavut",
    "Ontario",
    "Prince Edward Island",
    "Quebec",
    "Saskatchewan",
    "Yukon",
]

def ltt_ontario(purchase_price: float) -> float:
    # Ontario land transfer tax (common brackets)
    brackets = [
        Bracket(55_000, 0.005),
        Bracket(250_000, 0.01),
        Bracket(400_000, 0.015),
        Bracket(2_000_000, 0.02),
        Bracket(None, 0.025),
    ]
    return calc_progressive_tax(purchase_price, brackets)

def ltt_toronto_municipal(purchase_price: float) -> float:
    # City of Toronto Municipal Land Transfer Tax uses same bracket rates as Ontario (commonly applied)
    # This is in addition to Ontario LTT.
    return ltt_ontario(purchase_price)

def ptt_bc(purchase_price: float) -> float:
    # BC Property Transfer Tax (general)
    # 1% on first $200k, 2% on $200k–$2M, 3% on $2M–$3M, 5% on over $3M
    brackets = [
        Bracket(200_000, 0.01),
        Bracket(2_000_000, 0.02),
        Bracket(3_000_000, 0.03),
        Bracket(None, 0.05),
    ]
    return calc_progressive_tax(purchase_price, brackets)

def ptt_bc_additional_foreign_buyer(purchase_price: float, is_foreign: bool) -> float:
    # Additional Property Transfer Tax (foreign buyers) varies and is region-specific in reality.
    # We provide an optional generic add-on at 20% of purchase price as a placeholder toggle.
    # You can remove/adjust this section if you don't want it.
    return purchase_price * 0.20 if is_foreign else 0.0

def ltt_mb(purchase_price: float) -> float:
    # Manitoba Land Transfer Tax (common schedule)
    # 0% up to 30k
    # 0.5% 30k–90k
    # 1.0% 90k–150k
    # 1.5% 150k–200k
    # 2.0% 200k–? (commonly applied above 200k)
    brackets = [
        Bracket(30_000, 0.0),
        Bracket(90_000, 0.005),
        Bracket(150_000, 0.01),
        Bracket(200_000, 0.015),
        Bracket(None, 0.02),
    ]
    return calc_progressive_tax(purchase_price, brackets)

def ltt_nb(purchase_price: float) -> float:
    # New Brunswick Real Property Transfer Tax is often described as 1% of assessed value (commonly purchase price).
    return purchase_price * 0.01

def ltt_nl(purchase_price: float) -> float:
    # Newfoundland & Labrador: Registration of Deeds/Conveyance fees can vary.
    # As a simple proxy, many calculators treat it as ~0.4% (varies by municipality/registry).
    # Set to 0.4% default; allow user override.
    return purchase_price * 0.004

def ltt_nst(purchase_price: float) -> float:
    # Nova Scotia: Deed transfer tax is municipal and varies (often ~1%–1.5%).
    # We require a user-provided municipal rate.
    return 0.0  # computed via custom rate input in UI

def ptt_pei(purchase_price: float) -> float:
    # PEI: Real Property Transfer Tax is generally 1% of the greater of consideration or assessed value.
    return purchase_price * 0.01

def ltt_qc(purchase_price: float) -> float:
    # Quebec "Welcome Tax" (Taxe de bienvenue) commonly:
    # 0.5% on first $52,800
    # 1.0% on $52,800–$264,000
    # 1.5% on $264,000–$527,900
    # 2.0% on remainder
    # Thresholds are indexed annually; these are commonly used base figures.
    brackets = [
        Bracket(52_800, 0.005),
        Bracket(264_000, 0.01),
        Bracket(527_900, 0.015),
        Bracket(None, 0.02),
    ]
    return calc_progressive_tax(purchase_price, brackets)

def ltt_sk(purchase_price: float) -> float:
    # Saskatchewan: no general land transfer tax; there are land titles fees.
    # We'll return 0 and show note.
    return 0.0

def ltt_ab(purchase_price: float) -> float:
    # Alberta: no land transfer tax; there are land titles fees.
    return 0.0

def ltt_territories(purchase_price: float) -> float:
    # Territories generally do not have an LTT like ON/QC/BC; there may be registry fees.
    return 0.0

# Some provinces that require a "sale price" in special cases (e.g., flipping/speculation taxes) exist,
# but they are not standard LTT and are policy-specific. We'll treat "sale price" as optional and only
# use it when user selects an "additional tax module" below (optional).

# -----------------------------
# UI
# -----------------------------

st.title("🏠 Canada Land Transfer Tax Calculator")
st.caption("Estimate land transfer tax / property transfer tax by province (and Toronto municipal LTT where applicable).")

col1, col2 = st.columns(2)
with col1:
    province = st.selectbox("Province / Territory", PROVINCES, index=PROVINCES.index("Ontario"))
with col2:
    city = st.text_input("City (optional)", placeholder="e.g., Toronto, Vancouver, Halifax")

purchase_price = st.number_input(
    "Purchase price (CAD)",
    min_value=0.0,
    value=750_000.0,
    step=10_000.0,
    format="%.2f",
)

st.divider()

# Optional fields
with st.expander("Optional details (rebates / municipal rates / special cases)"):
    is_first_time_buyer = st.checkbox("First-time home buyer (common ON/Toronto/QC/BC rebates not fully implemented)", value=False)
    # Nova Scotia municipal deed transfer rate input
    ns_rate = st.number_input(
        "Nova Scotia municipal deed transfer tax rate (if applicable, enter %)",
        min_value=0.0,
        max_value=5.0,
        value=1.5,
        step=0.1,
        format="%.2f",
        help="Nova Scotia deed transfer tax is set by municipality. Enter the local rate (commonly 1%–1.5%).",
    )

    # Newfoundland override (since it varies)
    nl_rate = st.number_input(
        "Newfoundland & Labrador conveyance proxy rate (enter % if you want to override)",
        min_value=0.0,
        max_value=2.0,
        value=0.40,
        step=0.05,
        format="%.2f",
        help="This is a simplified proxy. Actual fees can vary.",
    )

    # Optional “sale price” for additional modules (e.g., if you later add flipping/speculation logic)
    include_sale_price = st.checkbox("Include sale price (only needed for certain special taxes you may add later)", value=False)
    sale_price = None
    if include_sale_price:
        sale_price = st.number_input(
            "Sale price (CAD)",
            min_value=0.0,
            value=800_000.0,
            step=10_000.0,
            format="%.2f",
        )

    # Optional BC foreign buyer toggle placeholder
    bc_foreign = st.checkbox("BC: Foreign buyer additional property transfer tax (placeholder toggle)", value=False)

# -----------------------------
# Calculation routing
# -----------------------------
province_tax = 0.0
municipal_tax = 0.0
notes: List[str] = []

if province == "Ontario":
    province_tax = ltt_ontario(purchase_price)
    if city.strip().lower() == "toronto":
        municipal_tax = ltt_toronto_municipal(purchase_price)
        notes.append("Toronto Municipal Land Transfer Tax is added on top of Ontario LTT (same bracket structure in this calculator).")
    else:
        notes.append("Ontario LTT calculated using common provincial brackets.")
    if is_first_time_buyer:
        notes.append("First-time buyer rebates are not applied in this version (add if needed).")

elif province == "British Columbia":
    province_tax = ptt_bc(purchase_price)
    if bc_foreign:
        municipal_tax += ptt_bc_additional_foreign_buyer(purchase_price, True)
        notes.append("BC foreign buyer additional tax toggle is a placeholder (rates/areas vary).")
    notes.append("BC PTT calculated using common brackets (1% / 2% / 3% / 5%).")
    if is_first_time_buyer:
        notes.append("First-time buyer exemptions are not applied in this version (add if needed).")

elif province == "Manitoba":
    province_tax = ltt_mb(purchase_price)
    notes.append("Manitoba LTT calculated using common bracket schedule (0%–2%).")

elif province == "Quebec":
    province_tax = ltt_qc(purchase_price)
    notes.append("Quebec Welcome Tax estimated with commonly used thresholds (indexed annually in reality).")
    if is_first_time_buyer:
        notes.append("Any municipal/provincial programs or rebates are not applied in this version.")

elif province == "New Brunswick":
    province_tax = ltt_nb(purchase_price)
    notes.append("NB Real Property Transfer Tax estimated as 1% of purchase price (assessed value may apply).")

elif province == "Prince Edward Island":
    province_tax = ptt_pei(purchase_price)
    notes.append("PEI Real Property Transfer Tax estimated as 1% of purchase price (greater of consideration/assessed value may apply).")

elif province == "Nova Scotia":
    # municipal deed transfer tax varies
    province_tax = purchase_price * (ns_rate / 100.0)
    notes.append("Nova Scotia deed transfer tax varies by municipality; using the rate you entered.")

elif province == "Newfoundland and Labrador":
    province_tax = purchase_price * (nl_rate / 100.0)
    notes.append("NL fees vary; using a simplified proxy rate (overrideable).")

elif province in ["Alberta", "Saskatchewan", "Yukon", "Northwest Territories", "Nunavut"]:
    province_tax = 0.0
    notes.append("This calculator returns $0 for LTT/PTT here because these jurisdictions typically use land title/registration fees instead of an LTT.")

total_tax = province_tax + municipal_tax

# -----------------------------
# Output
# -----------------------------
st.subheader("Estimated Taxes")

c1, c2, c3 = st.columns(3)
c1.metric("Province / Territory tax", money(province_tax))
c2.metric("Municipal / additional tax", money(municipal_tax))
c3.metric("Total estimated", money(total_tax))

st.divider()

st.subheader("Breakdown (progressive where applicable)")
if province in ["Ontario", "British Columbia", "Manitoba", "Quebec"]:
    st.write("Progressive bracket calculation applied.")
else:
    st.write("Flat-rate estimate or jurisdictional note applied.")

if sale_price is not None:
    st.info(
        f"Sale price captured: {money(sale_price)}. "
        "No sale-price-based taxes are calculated yet. If you want flipping/speculation modules, tell me which province/program."
    )

if notes:
    st.subheader("Notes")
    for n in notes:
        st.write(f"• {n}")

st.divider()

with st.expander("Developer notes / how to extend"):
    st.markdown(
        """
**How to extend this app**
- Add province-specific rebates (e.g., Ontario first-time buyer rebate, Toronto rebate, BC exemptions, etc.).
- Add municipal deed transfer rate lookup tables (e.g., Nova Scotia municipalities).
- Add special taxes (e.g., anti-flipping rules, speculation/vacancy taxes) if you specify the exact program you want.

**Run**
```bash
pip install streamlit
streamlit run app.py
