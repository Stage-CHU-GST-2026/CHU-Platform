"""Domain Classification Engine."""

from __future__ import annotations

from dil.models import DomainProfile, SemanticProfile, StructuralProfile


MEDICAL_KEYWORDS = {
    "glucose", "insulin", "bmi", "bloodpressure", "skinthickness", "diabetes",
    "patient", "disease", "diagnosis", "symptom", "treatment", "hospital",
    "doctor", "cholesterol", "heart", "pulse", "cancer", "blood", "medical"
}

FINANCE_KEYWORDS = {
    "revenue", "profit", "sales", "transaction", "amount", "currency", "price",
    "credit", "debit", "bank", "account", "loan", "interest", "stock", "portfolio"
}

RETAIL_KEYWORDS = {
    "product", "item", "inventory", "customer", "order", "shipping", "category",
    "discount", "store", "sku", "basket"
}


def detect_domain(struct_profile: StructuralProfile, semantic_profile: SemanticProfile) -> DomainProfile:
    """Classify dataset domain."""
    col_names_lower = [c.name.lower() for c in struct_profile.columns]
    col_concepts_lower = [c.inferred_concept.lower() for c in semantic_profile.columns]

    all_words = set(col_names_lower + col_concepts_lower)

    medical_matches = len([w for w in all_words if any(k in w for k in MEDICAL_KEYWORDS)])
    finance_matches = len([w for w in all_words if any(k in w for k in FINANCE_KEYWORDS)])
    retail_matches = len([w for w in all_words if any(k in w for k in RETAIL_KEYWORDS)])

    total_cols = len(struct_profile.columns) or 1

    if medical_matches >= 2 or (medical_matches / total_cols) >= 0.25:
        conf = min(0.98, round(0.70 + (medical_matches / total_cols) * 0.5, 2))
        return DomainProfile(
            primary_domain="Medical / Healthcare",
            confidence=conf,
            reasoning=f"Identified {medical_matches} medical variables (glucose, insulin, bmi, etc.).",
            subdomains=["Endocrinology", "Clinical Diagnostics"],
        )
    elif finance_matches >= 2 or (finance_matches / total_cols) >= 0.25:
        conf = min(0.98, round(0.70 + (finance_matches / total_cols) * 0.5, 2))
        return DomainProfile(
            primary_domain="Finance & Banking",
            confidence=conf,
            reasoning=f"Identified {finance_matches} financial metrics.",
            subdomains=["Corporate Finance", "Transaction Logs"],
        )
    elif retail_matches >= 2 or (retail_matches / total_cols) >= 0.25:
        conf = min(0.98, round(0.70 + (retail_matches / total_cols) * 0.5, 2))
        return DomainProfile(
            primary_domain="Retail & E-commerce",
            confidence=conf,
            reasoning=f"Identified {retail_matches} retail/e-commerce attributes.",
            subdomains=["Sales Analysis", "Inventory Management"],
        )

    return DomainProfile(
        primary_domain="Generic Tabular",
        confidence=0.85,
        reasoning="Dataset attributes do not match a single specific enterprise domain keyword set.",
        subdomains=["General Statistics"],
    )
