"""Deterministic Data Quality Engine."""

from __future__ import annotations

import re
from typing import Any
import pandas as pd
import numpy as np

from dil.models import QualityIssue, QualityProfile, StructuralProfile


AGE_REGEX = re.compile(r"(?:_|^)age(?:_|$)", re.IGNORECASE)
PERCENT_REGEX = re.compile(r"(?:_|^)(?:pct|percent|percentage|rate|ratio)(?:_|$)", re.IGNORECASE)


def evaluate_quality(df: pd.DataFrame, struct_profile: StructuralProfile) -> QualityProfile:
    """Compute quality dimension scores and detect issues."""
    issues: list[QualityIssue] = []
    total_rows = len(df)
    total_cols = len(df.columns)
    total_cells = total_rows * total_cols

    # 1. Completeness
    total_nulls = sum(c.null_count for c in struct_profile.columns)
    completeness_score = 100.0
    if total_cells > 0:
        completeness_score = round(100.0 - (total_nulls / total_cells * 100.0), 2)

    for col_info in struct_profile.columns:
        if col_info.null_percentage > 50.0:
            issues.append(
                QualityIssue(
                    column_name=col_info.name,
                    issue_type="high_missing_values",
                    severity="high" if col_info.null_percentage > 80.0 else "medium",
                    description=f"Column '{col_info.name}' has {col_info.null_percentage}% missing values ({col_info.null_count}/{total_rows}).",
                    affected_count=col_info.null_count,
                )
            )

    # 2. Uniqueness
    uniqueness_score = round(100.0 - struct_profile.duplicate_percentage, 2)
    if struct_profile.duplicate_rows > 0:
        issues.append(
            QualityIssue(
                column_name=None,
                issue_type="duplicate_rows",
                severity="medium" if struct_profile.duplicate_percentage < 10.0 else "high",
                description=f"Dataset contains {struct_profile.duplicate_rows} duplicate rows ({struct_profile.duplicate_percentage}%).",
                affected_count=struct_profile.duplicate_rows,
            )
        )

    # 3. Consistency
    consistency_deductions = 0.0
    for col_info in struct_profile.columns:
        series = df[col_info.name].dropna()
        if len(series) == 0:
            continue
        
        # Check string whitespace issues
        if col_info.is_categorical or series.dtype == object:
            str_series = series.astype(str)
            whitespace_count = int((str_series.str.strip() != str_series).sum())
            if whitespace_count > 0:
                consistency_deductions += min(10.0, (whitespace_count / total_rows) * 20.0)
                issues.append(
                    QualityIssue(
                        column_name=col_info.name,
                        issue_type="whitespace_inconsistency",
                        severity="low",
                        description=f"Column '{col_info.name}' contains {whitespace_count} values with leading or trailing whitespace.",
                        affected_count=whitespace_count,
                    )
                )

            # Check case inconsistency (e.g. "Male" vs "male")
            lower_uniques = str_series.str.lower().nunique()
            actual_uniques = str_series.nunique()
            if actual_uniques > lower_uniques:
                diff = actual_uniques - lower_uniques
                consistency_deductions += 5.0
                issues.append(
                    QualityIssue(
                        column_name=col_info.name,
                        issue_type="casing_inconsistency",
                        severity="low",
                        description=f"Column '{col_info.name}' has potential casing variations ({diff} duplicate categories when lowercased).",
                        affected_count=diff,
                    )
                )

    consistency_score = max(0.0, round(100.0 - consistency_deductions, 2))

    # 4. Validity (impossible / out of range values)
    validity_deductions = 0.0
    for col_info in struct_profile.columns:
        series = df[col_info.name].dropna()
        if len(series) == 0:
            continue

        # Age checks
        if col_info.is_numeric and AGE_REGEX.search(col_info.name):
            impossible_age = int(((series < 0) | (series > 150)).sum())
            if impossible_age > 0:
                validity_deductions += 15.0
                issues.append(
                    QualityIssue(
                        column_name=col_info.name,
                        issue_type="impossible_value",
                        severity="high",
                        description=f"Age column '{col_info.name}' has {impossible_age} impossible values (<0 or >150).",
                        affected_count=impossible_age,
                    )
                )

        # Percentage/Ratio checks (if named pct/percent and values exceed 100 or <0 for 0-100 scales)
        if col_info.is_numeric and PERCENT_REGEX.search(col_info.name):
            if series.max() <= 100.0 and (series < 0).any():
                invalid_count = int((series < 0).sum())
                validity_deductions += 10.0
                issues.append(
                    QualityIssue(
                        column_name=col_info.name,
                        issue_type="out_of_range",
                        severity="medium",
                        description=f"Percentage column '{col_info.name}' contains {invalid_count} negative values.",
                        affected_count=invalid_count,
                    )
                )

    validity_score = max(0.0, round(100.0 - validity_deductions, 2))

    # 5. Integrity
    integrity_score = 100.0

    # Overall Quality Score calculation
    overall_score = round(
        (completeness_score * 0.30)
        + (uniqueness_score * 0.25)
        + (consistency_score * 0.20)
        + (validity_score * 0.15)
        + (integrity_score * 0.10),
        2,
    )

    return QualityProfile(
        overall_score=overall_score,
        completeness=completeness_score,
        uniqueness=uniqueness_score,
        consistency=consistency_score,
        validity=validity_score,
        integrity=integrity_score,
        issues=issues,
    )
