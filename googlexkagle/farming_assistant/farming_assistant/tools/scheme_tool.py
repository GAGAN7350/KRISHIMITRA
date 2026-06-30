"""
Government Scheme knowledge base for Indian farmers.

Covers the major agricultural welfare schemes:
  - PM-KISAN  (income support ₹6,000/year)
  - PMFBY     (crop insurance)
  - PM-KUSUM  (solar pump subsidies)
  - PMKSY     (micro irrigation / drip & sprinkler)
  - KCC       (Kisan Credit Card — subsidised crop loans)
  - PM-KMY    (pension scheme for small & marginal farmers)
"""

from __future__ import annotations

# ─────────────────────────────────────────────────────────────
# KNOWLEDGE BASE
# ─────────────────────────────────────────────────────────────

SCHEMES: dict[str, dict] = {
    "pm-kisan": {
        "full_name": "Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)",
        "objective": "Direct income support of ₹6,000 per year in 3 equal installments of ₹2,000 each to landholding farmer families.",
        "eligibility": [
            "Must be a landholding farmer family (husband, wife, and minor children).",
            "Land must be in the name of the farmer (or jointly owned with spouse).",
            "e-KYC (Aadhaar OTP or biometric) must be completed.",
            "Bank account must be Aadhaar-seeded.",
            "Income Tax payers, constitutional post-holders, and government employees are NOT eligible.",
        ],
        "benefit": "₹6,000 per year (₹2,000 × 3 installments) via Direct Benefit Transfer (DBT) to Aadhaar-linked bank account.",
        "how_to_apply": [
            "Visit https://pmkisan.gov.in/ and click 'Farmers Corner → New Farmer Registration'.",
            "Alternatively visit the nearest CSC (Common Service Centre) or Village Level Entrepreneur (VLE) with Aadhaar card and land documents.",
            "Complete e-KYC online or at the nearest CSC.",
        ],
        "helpline": "155261 (Toll-free, 24×7)",
        "portal": "https://pmkisan.gov.in/",
        "keywords": ["pm kisan", "kisan samman", "samman nidhi", "6000", "2000", "income support", "installment"],
    },
    "pmfby": {
        "full_name": "Pradhan Mantri Fasal Bima Yojana (PMFBY)",
        "objective": "Affordable crop insurance to protect farmers against losses from natural calamities, pests, and diseases.",
        "eligibility": [
            "All farmers — loanee and non-loanee — growing notified crops in notified areas.",
            "Sharecroppers and tenant farmers are also eligible.",
            "For loanee farmers: automatically enrolled via bank when taking KCC / crop loan.",
            "For non-loanee farmers: must enrol voluntarily through bank / CSC / PMFBY portal before the cut-off date.",
        ],
        "benefit": (
            "Insurance coverage for the entire crop cycle — pre-sowing to post-harvest losses. "
            "Premium rates: 2% for Kharif crops, 1.5% for Rabi crops, 5% for commercial / horticultural crops. "
            "Remaining premium is shared equally by Central and State Government."
        ),
        "how_to_apply": [
            "Visit https://pmfby.gov.in/ for online enrollment.",
            "Contact nearest bank branch, CSC, or insurance company representative.",
            "For loanee farmers: automatically covered — verify with your bank.",
            "Enrol BEFORE the cut-off date (usually 2 weeks before the sowing season ends).",
        ],
        "helpline": "14447 (Toll-free, 9 AM – 6 PM, Mon–Sat)",
        "portal": "https://pmfby.gov.in/",
        "keywords": ["pmfby", "fasal bima", "crop insurance", "insurance", "natural disaster", "flood", "drought coverage"],
    },
    "pm-kusum": {
        "full_name": "Pradhan Mantri Kisan Urja Suraksha evam Utthan Mahabhiyan (PM-KUSUM)",
        "objective": "Provide solar-powered irrigation pumps and enable farmers to sell surplus solar power to DISCOMs.",
        "eligibility": [
            "Individual farmers, groups of farmers, Panchayats, Farmer Producer Organisations (FPOs), Water User Associations.",
            "Land required for Component A (solar plants): minimum 1 acre per MW.",
            "Component B (standalone solar pumps): farmers with no grid-connected pumps.",
            "Component C (solarisation of grid-connected pumps): farmers with existing pumps.",
        ],
        "benefit": (
            "Component A: Sell solar power at fixed tariff (₹3–3.5/unit) to DISCOM — passive income for 25 years.\n"
            "Component B: 60–70% subsidy on standalone solar pump (min 500W to 7.5 HP capacity).\n"
            "Component C: 30–40% subsidy to solarise existing grid-connected agriculture pumps."
        ),
        "how_to_apply": [
            "Apply through your State DISCOM (electricity distribution company) or State Renewable Energy Development Agency (REDA).",
            "Karnataka: KREDL (www.kredlinfo.in)",
            "Maharashtra: MEDA (www.mahaurja.com)",
            "General portal: https://pmkusum.mnre.gov.in/",
        ],
        "helpline": "1800-180-3333 (MNRE Toll-free)",
        "portal": "https://pmkusum.mnre.gov.in/",
        "keywords": ["pm kusum", "kusum", "solar pump", "solar energy", "bijli", "urja", "DISCOM", "renewable"],
    },
    "pmksy": {
        "full_name": "Pradhan Mantri Krishi Sinchayee Yojana (PMKSY)",
        "objective": "Expand irrigation coverage and improve water-use efficiency ('Har Khet Ko Pani, More Crop Per Drop').",
        "eligibility": [
            "All farmers who own or lease agricultural land.",
            "Priority to small and marginal farmers for subsidy under Per Drop More Crop component.",
            "Land must be in a district covered under PMKSY (most of India is covered).",
        ],
        "benefit": (
            "55% subsidy on micro-irrigation (drip / sprinkler) equipment for small & marginal farmers.\n"
            "45% subsidy for other farmers.\n"
            "Includes subsidy on pipes, filters, emitters, and installation costs."
        ),
        "how_to_apply": [
            "Apply online through your State Agriculture Department portal.",
            "Karnataka: https://raitamitra.karnataka.gov.in/",
            "Maharashtra: https://mahadbt.maharashtra.gov.in/",
            "Visit your nearest District Agriculture Office with land records and bank details.",
        ],
        "helpline": "Contact State Agriculture Department helpline.",
        "portal": "https://pmksy.gov.in/",
        "keywords": ["pmksy", "drip irrigation", "sprinkler", "micro irrigation", "water", "sinchayee", "har khet ko pani"],
    },
    "kcc": {
        "full_name": "Kisan Credit Card (KCC)",
        "objective": "Provide short-term formal credit to farmers for cultivation expenses, post-harvest needs, and allied activities.",
        "eligibility": [
            "All farmers — individual, joint borrowers, tenant farmers, sharecroppers.",
            "Self-help groups (SHGs) of farmers.",
            "No minimum land holding requirement.",
            "Age: 18–75 years (with co-borrower if above 60).",
        ],
        "benefit": (
            "Credit limit based on land holding, crop, and scale of finance — typically ₹1–3 lakh for small farmers.\n"
            "Interest rate: 7% per annum (effectively 4% with 3% interest subvention for prompt repayment).\n"
            "Revolving credit — can draw and repay multiple times within the year.\n"
            "Also covers crop insurance (PMFBY) and personal accident insurance."
        ),
        "how_to_apply": [
            "Visit any nationalised bank, cooperative bank, or Regional Rural Bank (RRB) branch.",
            "Carry: Aadhaar card, land ownership documents / lease agreement, passport photo.",
            "You can also apply at NABARD-affiliated cooperative credit societies.",
        ],
        "helpline": "NABARD helpline: 1800-200-0102 (Toll-free)",
        "portal": "https://www.nabard.org/",
        "keywords": ["kcc", "kisan credit", "credit card", "loan", "farming loan", "crop loan", "udhar", "bank"],
    },
    "pm-kmy": {
        "full_name": "Pradhan Mantri Kisan Maandhan Yojana (PM-KMY)",
        "objective": "Voluntary contributory pension scheme providing ₹3,000/month after age 60 to small and marginal farmers.",
        "eligibility": [
            "Small and marginal farmers with land holding up to 2 hectares.",
            "Age: 18–40 years at enrollment (benefit received after age 60).",
            "Not a beneficiary of any other pension scheme (NPS, ESIC, EPFO).",
            "Not an income tax payer.",
        ],
        "benefit": (
            "Monthly pension of ₹3,000 after 60 years of age.\n"
            "Government matches the farmer's monthly contribution 1:1.\n"
            "Contribution ranges from ₹55/month (if joining at 18) to ₹200/month (if joining at 40).\n"
            "Spouse is also eligible to join separately."
        ),
        "how_to_apply": [
            "Visit your nearest CSC (Common Service Centre) with Aadhaar card, bank passbook, and a savings bank account.",
            "Or apply online at https://maandhan.in/",
        ],
        "helpline": "1800-267-6888 (Toll-free)",
        "portal": "https://maandhan.in/",
        "keywords": ["pm kmy", "kmy", "pension", "maandhan", "retirement", "old age", "3000 per month"],
    },
}

# State-specific notes for Karnataka (since the demo farmer is from Karnataka)
STATE_NOTES: dict[str, str] = {
    "karnataka": (
        "Karnataka-specific: Register on Raitha Mitra portal (https://raitamitra.karnataka.gov.in/) for "
        "state agriculture subsidies. PM-KISAN status can be checked at any Raitha Samparka Kendra (RSK). "
        "Helpline: 1800-425-1553 (Dept. of Agriculture, Karnataka — Toll-free)."
    ),
    "maharashtra": (
        "Maharashtra-specific: Apply for state schemes at https://mahadbt.maharashtra.gov.in/. "
        "The DBT portal covers many state-level subsidies alongside central schemes."
    ),
    "andhra pradesh": (
        "Andhra Pradesh-specific: AP Rythu Bharosa (state income support) is in addition to PM-KISAN. "
        "Visit www.apagrisnet.gov.in for state scheme details."
    ),
    "telangana": (
        "Telangana-specific: TS Rythu Bandhu (₹5,000/acre/season) is separate from PM-KISAN. "
        "Visit agriculture.telangana.gov.in for scheme details."
    ),
}


# ─────────────────────────────────────────────────────────────
# TOOL FUNCTIONS
# ─────────────────────────────────────────────────────────────

def get_scheme_info(scheme_name: str) -> dict:
    """
    Returns detailed information about a government agricultural scheme.

    Args:
        scheme_name: Name of the scheme (e.g., 'PM-KISAN', 'PMFBY', 'KCC',
                     'PM-KUSUM', 'PMKSY', 'PM-KMY').

    Returns:
        A dictionary with keys: full_name, objective, eligibility (list),
        benefit (str), how_to_apply (list), helpline, portal.
        Returns a fallback message if the scheme is not found.
    """
    key = scheme_name.lower().replace(" ", "-").replace("_", "-")

    # Try direct match
    if key in SCHEMES:
        return SCHEMES[key]

    # Try keyword search across all schemes
    scheme_lower = scheme_name.lower()
    for scheme_key, scheme_data in SCHEMES.items():
        for kw in scheme_data.get("keywords", []):
            if kw in scheme_lower or scheme_lower in kw:
                return scheme_data

    return {
        "full_name": scheme_name,
        "error": (
            f"Scheme '{scheme_name}' not found in our database. "
            f"Available schemes: PM-KISAN, PMFBY, PM-KUSUM, PMKSY, KCC, PM-KMY. "
            f"For other state-specific schemes, contact your District Agriculture Office "
            f"or call Kisan Call Centre: 1800-180-1551 (Toll-free, 6 AM – 10 PM)."
        ),
    }


def list_all_schemes() -> dict:
    """
    Returns a summary list of all available government agricultural schemes.

    Returns:
        A dictionary with a list of scheme summaries.
    """
    summaries = []
    for key, data in SCHEMES.items():
        summaries.append({
            "scheme_id": key,
            "name": data["full_name"],
            "one_line": data["objective"][:120] + "..." if len(data["objective"]) > 120 else data["objective"],
            "portal": data.get("portal", ""),
        })
    return {
        "total_schemes": len(summaries),
        "schemes": summaries,
        "kisan_call_centre": "1800-180-1551 (Toll-free, 6 AM – 10 PM, all days)",
    }


def check_scheme_eligibility(
    scheme_name: str,
    land_holding_hectares: float,
    state: str = "",
    is_income_tax_payer: bool = False,
    farmer_age: int = 0,
) -> str:
    """
    Evaluates a farmer's likely eligibility for a government scheme based on key parameters.

    Args:
        scheme_name: Name of the scheme to check (e.g., 'PM-KISAN', 'PMFBY').
        land_holding_hectares: Farmer's land holding in hectares (e.g., 1.5 for 1.5 ha).
        state: Farmer's state (e.g., 'Karnataka', 'Maharashtra'). Optional.
        is_income_tax_payer: True if the farmer pays income tax. Affects PM-KISAN eligibility.
        farmer_age: Farmer's age in years. Used for PM-KMY pension scheme check.

    Returns:
        A plain text eligibility assessment with recommendations.
    """
    scheme_data = get_scheme_info(scheme_name)
    if "error" in scheme_data:
        return scheme_data["error"]

    scheme_key = scheme_name.lower().replace(" ", "-")

    lines = [f"📋 Eligibility check for: {scheme_data['full_name']}", ""]

    if scheme_key == "pm-kisan":
        if is_income_tax_payer:
            lines.append("❌ You are likely NOT eligible — income tax payers are excluded from PM-KISAN.")
        elif land_holding_hectares <= 0:
            lines.append("❌ PM-KISAN requires registered land ownership. Tenant farmers are NOT eligible.")
        else:
            lines.append("✅ You appear ELIGIBLE for PM-KISAN.")
            lines.append(f"   → Land holding ({land_holding_hectares:.2f} ha) — good, any size qualifies.")
            lines.append("   → Ensure your Aadhaar is linked to your bank account and e-KYC is done.")
            lines.append("   → Apply at: https://pmkisan.gov.in/ or your nearest CSC.")

    elif scheme_key == "pm-kmy":
        if land_holding_hectares > 2.0:
            lines.append(f"❌ PM-KMY is for small & marginal farmers (≤2 ha). Your land ({land_holding_hectares:.2f} ha) exceeds the limit.")
        elif farmer_age > 0 and (farmer_age < 18 or farmer_age > 40):
            lines.append(f"❌ PM-KMY enrollment is for age 18–40 only. Your age ({farmer_age}) is outside this range.")
        elif is_income_tax_payer:
            lines.append("❌ Income tax payers are NOT eligible for PM-KMY.")
        else:
            lines.append("✅ You appear ELIGIBLE for PM-KMY pension scheme.")
            if farmer_age > 0:
                monthly_contrib = max(55, min(200, int(55 + (farmer_age - 18) * 5.3)))
                lines.append(f"   → Estimated monthly contribution at age {farmer_age}: ₹{monthly_contrib}/month")
            lines.append("   → Apply at any CSC with Aadhaar and bank passbook.")

    elif scheme_key == "kcc":
        lines.append("✅ All farmers (including tenant farmers and sharecroppers) are eligible for KCC.")
        lines.append("   → Visit your nearest bank or cooperative bank with Aadhaar + land/lease documents.")
        lines.append(f"   → Effective interest rate: 4% per annum (after 3% government subvention) for prompt repayers.")

    elif scheme_key == "pmfby":
        lines.append("✅ All farmers growing notified crops are eligible for PMFBY crop insurance.")
        if land_holding_hectares <= 2.0:
            lines.append("   → As a small/marginal farmer, you pay only 2% of sum insured as premium for Kharif crops.")
        lines.append("   → If you have a KCC loan, you are automatically enrolled — confirm with your bank.")
        lines.append("   → For self-enrollment: https://pmfby.gov.in/ before the season cut-off date.")

    elif scheme_key == "pm-kusum":
        lines.append("✅ You appear eligible for PM-KUSUM solar pump subsidy.")
        if land_holding_hectares >= 1.0:
            lines.append(f"   → Component A (solar plant): Your {land_holding_hectares:.2f} ha qualifies for a ground-mounted plant.")
        lines.append("   → Component B (standalone solar pump): 60–70% subsidy on pump cost.")
        lines.append(f"   → Apply through State DISCOM / REDA.")

    elif scheme_key == "pmksy":
        lines.append("✅ You are eligible for PMKSY micro-irrigation subsidy (drip / sprinkler).")
        if land_holding_hectares <= 2.0:
            lines.append("   → As a small/marginal farmer, you get 55% subsidy on equipment cost.")
        else:
            lines.append("   → You qualify for 45% subsidy on drip/sprinkler equipment.")
        lines.append("   → Apply through your State Agriculture Department portal.")
    else:
        lines.append("✅ Based on the information provided, you may be eligible.")
        lines.append("   → Please contact the scheme helpline or your District Agriculture Office for confirmation.")

    # Add state-specific note
    state_lower = state.lower().strip()
    state_note = STATE_NOTES.get(state_lower, "")
    if state_note:
        lines.append("")
        lines.append(f"🗺️ {state} Note: {state_note}")

    lines.append("")
    lines.append(f"📞 Kisan Call Centre: 1800-180-1551 (Toll-free, 6 AM – 10 PM)")
    lines.append(f"🌐 Official portal: {scheme_data.get('portal', 'Contact your District Agriculture Office')}")

    return "\n".join(lines)
