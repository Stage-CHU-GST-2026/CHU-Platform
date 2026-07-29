"""Semantic Resolution Engine for concept mapping and business logic inference."""

from __future__ import annotations

import re
from typing import Any
import pandas as pd

from dil.models import (
    ColumnSemantic,
    ConceptAlternative,
    SemanticProfile,
    StructuralProfile,
)


CONCEPT_RULES: list[dict[str, Any]] = [
    {
        "pattern": re.compile(r"(?:_|^)(?:pregnancies|preg|parity)(?:_|$)", re.I),
        "concept": "Pregnancy Count",
        "role": "dimension",
        "units": "count",
        "entity": "patient",
        "confidence": 0.95,
        "description": "Number of times pregnant",
    },
    {
        "pattern": re.compile(r"(?:_|^)(?:glucose|glycemia|fbg|blood_sugar)(?:_|$)", re.I),
        "concept": "Blood Glucose Level",
        "role": "measure",
        "units": "mg/dL",
        "entity": "patient",
        "confidence": 0.96,
        "description": "Plasma glucose concentration a 2 hours in an oral glucose tolerance test",
    },
    {
        "pattern": re.compile(r"(?:_|^)(?:bloodpressure|bp|diastolic|systolic)(?:_|$)", re.I),
        "concept": "Blood Pressure",
        "role": "measure",
        "units": "mmHg",
        "entity": "patient",
        "confidence": 0.95,
        "description": "Diastolic blood pressure",
    },
    {
        "pattern": re.compile(r"(?:_|^)(?:skinthickness|skinfold|triceps)(?:_|$)", re.I),
        "concept": "Triceps Skin Fold Thickness",
        "role": "measure",
        "units": "mm",
        "entity": "patient",
        "confidence": 0.95,
        "description": "Triceps skin fold thickness",
    },
    {
        "pattern": re.compile(r"(?:_|^)(?:insulin|serum_insulin)(?:_|$)", re.I),
        "concept": "Serum Insulin",
        "role": "measure",
        "units": "mu U/ml",
        "entity": "patient",
        "confidence": 0.95,
        "description": "2-Hour serum insulin",
    },
    {
        "pattern": re.compile(r"(?:_|^)(?:bmi|body_mass_index|imc)(?:_|$)", re.I),
        "concept": "Body Mass Index",
        "role": "measure",
        "units": "kg/m²",
        "entity": "patient",
        "confidence": 0.98,
        "description": "Body mass index (weight in kg / (height in m)^2)",
    },
    {
        "pattern": re.compile(r"(?:_|^)(?:diabetespedigreefunction|pedigree|dpf)(?:_|$)", re.I),
        "concept": "Diabetes Pedigree Function",
        "role": "measure",
        "units": "score",
        "entity": "patient",
        "confidence": 0.96,
        "description": "Diabetes pedigree score based on family history",
    },
    {
        "pattern": re.compile(r"(?:_|^)(?:age|patient_age)(?:_|$)", re.I),
        "concept": "Patient Age",
        "role": "dimension",
        "units": "years",
        "entity": "patient",
        "confidence": 0.98,
        "description": "Age of patient in years",
    },
    {
        "pattern": re.compile(r"(?:_|^)(?:outcome|target|label|diabetes|diagnosis|class)(?:_|$)", re.I),
        "concept": "Diagnostic Outcome",
        "role": "target",
        "units": "binary (0/1)",
        "entity": "patient",
        "confidence": 0.95,
        "description": "Class variable (0: Non-diabetic, 1: Diabetic)",
    },
    {
        "pattern": re.compile(r"(?:_|^)(?:patient_id|subject_id|id|code|pk)(?:_|$)", re.I),
        "concept": "Patient Identifier",
        "role": "identifier",
        "units": None,
        "entity": "patient",
        "confidence": 0.90,
        "description": "Unique identifier record",
    },
    {
        "pattern": re.compile(r"(?:_|^)(?:revenue|sales|price|cost|amount)(?:_|$)", re.I),
        "concept": "Financial Amount",
        "role": "measure",
        "units": "currency",
        "entity": "transaction",
        "confidence": 0.90,
        "description": "Monetary value",
    },
]


def resolve_column_semantic(col_name: str, col_dtype: str, sample_val: str | None, is_id: bool) -> ColumnSemantic:
    """Resolve semantic concept for a single column."""
    # Check rules
    for rule in CONCEPT_RULES:
        if rule["pattern"].search(col_name):
            return ColumnSemantic(
                column_name=col_name,
                inferred_concept=rule["concept"],
                semantic_role=rule["role"],
                entity_type=rule["entity"],
                units=rule["units"],
                confidence=rule["confidence"],
                source="heuristic",
                description=rule["description"],
                needs_review=rule["confidence"] < 0.85,
            )

    # Generic fallbacks
    if is_id:
        return ColumnSemantic(
            column_name=col_name,
            inferred_concept=f"{col_name.replace('_', ' ').title()} ID",
            semantic_role="identifier",
            confidence=0.85,
            source="heuristic",
            needs_review=False,
        )

    if any(k in col_dtype.lower() for k in ["int", "float"]):
        return ColumnSemantic(
            column_name=col_name,
            inferred_concept=col_name.replace("_", " ").title(),
            semantic_role="measure",
            confidence=0.75,
            source="heuristic",
            needs_review=True,
            alternatives=[
                ConceptAlternative(concept=f"{col_name.title()} Value", confidence=0.70)
            ],
        )

    return ColumnSemantic(
        column_name=col_name,
        inferred_concept=col_name.replace("_", " ").title(),
        semantic_role="dimension",
        confidence=0.70,
        source="heuristic",
        needs_review=True,
    )


def generate_semantic_profile(df: pd.DataFrame, struct_profile: StructuralProfile) -> SemanticProfile:
    """Generate semantic profile for a dataset."""
    col_semantics: list[ColumnSemantic] = []
    target_candidates: list[str] = []
    predictor_candidates: list[str] = []

    for col_info in struct_profile.columns:
        semantic = resolve_column_semantic(
            col_name=col_info.name,
            col_dtype=col_info.dtype,
            sample_val=col_info.sample,
            is_id=col_info.is_candidate_id,
        )
        col_semantics.append(semantic)

        if semantic.semantic_role == "target":
            target_candidates.append(semantic.column_name)
        elif semantic.semantic_role in ("measure", "dimension"):
            predictor_candidates.append(semantic.column_name)

    conf_scores = [c.confidence for c in col_semantics]
    overall_conf = round(sum(conf_scores) / len(conf_scores), 2) if conf_scores else 1.0

    return SemanticProfile(
        overall_confidence=overall_conf,
        columns=col_semantics,
        target_candidates=target_candidates,
        predictor_candidates=predictor_candidates,
    )
