# Data Intelligence Layer (DIL) — Implementation Plan

> Transform CHU-Platform from "chat with your CSV" into an enterprise-grade data intelligence platform by building the DIL as described in [NEXT.md](file:///home/regisx001/CHU-Platform/NEXT.md), in incremental phases — each one delivering working, testable value.

---

## Current State Analysis

The platform is more mature than it might first appear. Here's what already exists and what's missing:

### ✅ What Already Exists

| Capability | Location |
|---|---|
| **`Dataset` DB model** with lifecycle states (`uploading`, `processing`, `ready`, `error`), `columns_info` JSONB, row/column counts | [models.py](file:///home/regisx001/CHU-Platform/apps/api/src/api/models/models.py) |
| **Background profiling** via `process_dataset()` — auto-runs after upload, computes column metadata in a thread executor | [dataset_service.py](file:///home/regisx001/CHU-Platform/apps/api/src/api/services/dataset_service.py) |
| **Dataset API** — upload, list (with status filter + pagination), detail, preview (top N rows), statistics, columns, delete | [datasets.py](file:///home/regisx001/CHU-Platform/apps/api/src/api/routers/datasets.py) |
| **Dataset detail page** (`/dashboard/datasets/[id]`) with 3 tabs: Data Preview, Schema & Profiling, Statistical Summary | [+page.svelte](file:///home/regisx001/CHU-Platform/apps/web/src/routes/dashboard/datasets/%5Bid%5D/+page.svelte) |
| **Dataset upload modal** with drag-and-drop, format validation, progress state | `DatasetUploadModal.svelte` |
| **Dataset metrics banner** — total datasets, ready count, total rows, storage usage | `DatasetMetricsBanner.svelte` |
| **Multi-format ingestion** — CSV, TSV, XLSX, XLS, Parquet, JSON, Feather with encoding/delimiter auto-detection | [engine.py](file:///home/regisx001/CHU-Platform/packages/analysis/src/analysis/engine.py) |
| **Structural profiling** — dtypes, nulls, uniques, basic stats per column | [profiler.py](file:///home/regisx001/CHU-Platform/packages/analysis/src/analysis/profiler.py) |
| **Descriptive statistics** — mean, median, min, max, std, quantiles, correlation | [statistics.py](file:///home/regisx001/CHU-Platform/packages/analysis/src/analysis/statistics.py) |
| **Missing values & duplicates detection**, IQR outlier detection | Analysis engine |
| **18 chart types**, chart artifacts, visualization tools | [charts.py](file:///home/regisx001/CHU-Platform/packages/analysis/src/analysis/charts.py) |
| **Conversation-Dataset linking** — conversations reference `dataset_id`, agent receives `[Dataset: path]` header | [conversations.py](file:///home/regisx001/CHU-Platform/apps/api/src/api/routers/conversations.py) |
| **Tool evidence tracking** — `ToolEvidence` DB model captures tool calls, parameters, results, execution times | [models.py](file:///home/regisx001/CHU-Platform/apps/api/src/api/models/models.py) |
| **3-second polling** for processing status on the datasets page | Datasets page |
| **DB dataset registry** — `register_db_datasets()` injects DB datasets into `ListDatasetsTool` | [agent_service.py](file:///home/regisx001/CHU-Platform/apps/api/src/api/services/agent_service.py) |

### ❌ What's Completely Missing

| DIL Component | Priority | Notes |
|---|---|---|
| **DatasetIntelligenceRecord** — persistent intelligence object | 🔴 Critical | No centralized intelligence record; profiling is stored as raw `columns_info` JSONB |
| **Enhanced lifecycle states** — `profiled`, `semantic_review`, `ready`, `archived` | 🔴 Critical | Current states: `uploading`, `processing`, `ready`, `error` — no semantic review step |
| **Quality Engine** — completeness, consistency, validity, integrity scoring | 🟡 High | Missing values exist but no composite quality scores |
| **Readiness Score** — weighted composite metric | 🟡 High | No readiness assessment; all `ready` datasets are treated equally |
| **Semantic Engine** — column meaning inference, concept mapping | 🟡 High | Columns are raw pandas dtypes, no business meaning |
| **Domain Detection** — dataset domain classification | 🟡 High | No domain awareness at all |
| **Confidence Engine** — confidence scores on inferences | 🟡 High | No confidence scores anywhere |
| **Human Validation Engine** — review tasks, approval workflow | 🟠 Medium | No human-in-the-loop |
| **Knowledge Engine** — medical/domain knowledge base | 🟠 Medium | No domain knowledge base |
| **Recommendation Engine** — suggested analyses | 🟠 Medium | Agent discovers analyses from scratch each time |
| **Organization Knowledge Base** — org-specific column mappings | 🟠 Medium | No per-organization concept persistence |
| **Agent Intelligence integration** — agent receives Intelligence Record | 🟡 High | Agent gets raw DataFrame, not intelligence |

---

## Proposed Changes

6 phases, each self-contained and delivering working features. Each builds on the previous.

---

### Phase 1 — Foundation: Intelligence Record + Quality Engine + Readiness Score

> **Goal**: Create the `DatasetIntelligenceRecord` DB model, enhance the existing profiling pipeline to produce a structured intelligence record, add a quality engine with composite scoring, and compute a readiness score. All deterministic — no AI.

---

#### [NEW] `packages/dil/` — Data Intelligence Layer Package

A new pure-Python package (no AI dependencies), following the same pattern as `packages/analysis/`.

```
packages/dil/
├── pyproject.toml
└── src/dil/
    ├── __init__.py
    ├── models.py                 # Pydantic models: IntelligenceRecord, StructuralProfile, QualityProfile, etc.
    ├── structural_profiler.py    # Enhanced profiler wrapping existing Profile system
    ├── quality_engine.py         # Completeness, consistency, validity, integrity scoring
    ├── readiness.py              # Weighted readiness score computation
    └── utils.py                  # Shared utilities
```

#### [NEW] `dil/structural_profiler.py`

Wraps and enhances the existing `packages/analysis/profiler.py`:
- Reuses existing `ProfileResult` and `ColumnProfile`
- Adds: **candidate ID detection** (columns with 100% unique, integer-like), **datetime detection** (date ranges, granularity), **categorical detection** (low cardinality + string type), **boolean detection**
- Outputs a structured `StructuralProfile` Pydantic model (not raw dict)

#### [NEW] `dil/quality_engine.py`

All deterministic, no AI:

| Metric | Calculation |
|---|---|
| **Completeness** | `1 - (total_nulls / total_cells)` — per-column and overall |
| **Uniqueness** | Ratio of rows without duplicate primary-key candidates |
| **Consistency** | Mixed types within columns, inconsistent category casing, whitespace issues |
| **Validity** | Detects impossible values: negative ages, future dates, out-of-range percentages, negative counts |
| **Integrity** | Referential consistency between related columns (e.g., start_date < end_date) |

Output: `QualityProfile` with per-column issues list and overall dimension scores (0-100).

#### [NEW] `dil/readiness.py`

Computes weighted readiness score:

```
Readiness = (Structure × 0.35) + (Quality × 0.35) + (Semantics × 0.15) + (Domain × 0.10) + (Knowledge × 0.05)
```

Phases 1-2 only have Structure and Quality. Missing dimensions are redistributed proportionally. Example with only Structure + Quality: `Structure × 0.50 + Quality × 0.50`.

#### [NEW] Database: `DatasetIntelligenceRecord` Model

Add to [models.py](file:///home/regisx001/CHU-Platform/apps/api/src/api/models/models.py):

| Column | Type | Purpose |
|---|---|---|
| `id` | UUID PK | |
| `dataset_id` | UUID FK → `datasets.id` (unique, cascade delete) | One-to-one with Dataset |
| `structural_profile` | JSONB | Full structural profile (enhanced) |
| `quality_profile` | JSONB | Quality scores, per-column issues |
| `readiness_score` | Float | 0-100 composite score |
| `readiness_breakdown` | JSONB | `{structure: 85, quality: 72, ...}` |
| `warnings` | JSONB | List of warnings/issues |
| `version` | Integer | Monotonic version counter |
| `created_at` | DateTime | |
| `updated_at` | DateTime | |

#### [MODIFY] `Dataset` Model — Lifecycle States

Extend the existing `dataset_status` enum:
- **Current**: `uploading`, `processing`, `ready`, `error`
- **New**: `uploading` → `profiling` → `profiled` → `semantic_review` → `ready` → `archived`, `error`

The `processing` state becomes `profiling` (more descriptive). The `ready` state now means "fully processed and meets readiness threshold", not just "file parsed".

#### [MODIFY] `dataset_service.py` — Enhanced Pipeline

Modify `process_dataset()`:
1. Load DataFrame (existing)
2. Run structural profiler → `StructuralProfile` (enhanced)
3. Run quality engine → `QualityProfile` (new)
4. Compute readiness score (new)
5. Create/update `DatasetIntelligenceRecord` in DB (new)
6. Set `status = profiled` (was `ready`)

#### [NEW] Alembic Migration

`0004_add_intelligence_records.py`:
- Create `dataset_intelligence_records` table
- Add new enum values to `dataset_status`
- Migrate existing `columns_info` data to intelligence records

#### [NEW] API Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/api/v1/datasets/{id}/intelligence` | Get full intelligence record |
| POST | `/api/v1/datasets/{id}/reprofile` | Re-run profiling + quality pipeline |

#### [MODIFY] Dataset Detail Page

Enhance the existing 3-tab detail page:

- **New header section**: Readiness score as a circular progress gauge, lifecycle status badge, readiness dimension breakdown
- **Enhance "Schema & Profiling" tab**: Add candidate ID badges, datetime range info, boolean/categorical type badges
- **New "Quality" tab**: Quality dimension gauges (completeness, uniqueness, consistency, validity), per-column issues list with severity indicators
- **Enhance dataset cards** on list page: Show readiness score, quality status indicator

---

### Phase 2 — Semantic Engine + Domain Detection (First AI Layer)

> **Goal**: Use the LLM to infer column meanings, detect the dataset domain, and generate semantic profiles with confidence scores. This is where "intelligence" truly begins.

---

#### [NEW] `packages/dil/semantic_engine.py`

Two-stage approach — **deterministic first, AI second**:

**Stage 1 — Heuristic Matching** (no LLM):
- Pattern-based column name matching (regex): `age`, `date_of_birth`, `email`, `phone`, `zip_code`, `glucose`, `bmi`, etc.
- Value-pattern detection: email format, phone format, URL, UUID, IP address
- Unit detection from column names or values: `mg/dL`, `mmol/L`, `kg`, `cm`

**Stage 2 — LLM Inference** (for unresolved columns):
- Send column name + sample values + structural profile to LLM
- Ask for: business meaning, entity type, possible units, semantic role (identifier/measure/dimension/target)
- Each inference gets a confidence score

Output: `SemanticProfile` — per-column annotations:
```python
@dataclass
class ColumnSemantic:
    column_name: str
    inferred_concept: str           # "Blood Glucose"
    semantic_role: str              # "measure", "identifier", "dimension", "target"
    entity_type: str | None         # "patient", "lab_result", "transaction"
    units: str | None               # "mg/dL"
    confidence: float               # 0.0 - 1.0
    source: str                     # "heuristic" or "llm"
    alternatives: list[dict]        # [{concept: "HbA1c", confidence: 0.72}, ...]
    needs_review: bool              # True if confidence < threshold
```

#### [NEW] `packages/dil/domain_detector.py`

**Heuristics first**:
- Keyword scoring on column names (glucose/bmi/patient → medical, revenue/profit → finance, temperature/sensor → IoT)
- Domain scores accumulated across all columns

**LLM fallback** when heuristics are inconclusive (no domain exceeds confidence threshold):
- Send column names + sample values + structural summary to LLM
- Ask for domain classification with reasoning

Output: `DomainProfile`:
```python
@dataclass
class DomainProfile:
    primary_domain: str             # "medical"
    confidence: float               # 0.92
    secondary_domains: list[dict]   # [{domain: "research", confidence: 0.45}]
    reasoning: str                  # "Contains columns: glucose, bmi, hba1c..."
    source: str                     # "heuristic" or "llm"
```

Supported domains: `medical`, `finance`, `retail`, `iot`, `manufacturing`, `marketing`, `geospatial`, `education`, `hr`, `generic`

#### [MODIFY] Intelligence Record Schema

Add columns to `DatasetIntelligenceRecord`:
- `semantic_profile` (JSONB) — per-column semantic annotations
- `domain_profile` (JSONB) — domain classification
- `column_relationships` (JSONB) — inferred relationships (correlation, functional dependencies)

#### [MODIFY] `dataset_service.py` — Semantic Pipeline

Extend `process_dataset()` with async semantic analysis:
1. Existing profiling pipeline (Phase 1) runs first
2. Status → `profiling_semantics`
3. Run semantic engine (heuristics → LLM if needed)
4. Run domain detector
5. Detect column relationships
6. Update intelligence record
7. If any columns have `needs_review = True` → status → `semantic_review`
8. If all confident → status → `ready`

#### [NEW] API Endpoints

| Method | Path | Description |
|---|---|---|
| POST | `/api/v1/datasets/{id}/analyze-semantics` | Trigger/re-run semantic analysis |

#### [MODIFY] Dataset Detail Page

- **New "Semantics" tab**: Column table showing inferred concepts, roles, units, confidence gauges, review-needed badges
- **Domain badge** in header with confidence level
- Columns with low confidence are highlighted (amber/red)
- Relationship diagram (optional — simple list showing correlations and dependencies)

#### [NEW] Alembic Migration

`0005_add_semantic_fields.py` — add JSONB columns to intelligence record.

---

### Phase 3 — Human Validation Engine

> **Goal**: Build the human-in-the-loop system. Low-confidence semantic mappings become review tasks. Resolved mappings are saved permanently.

---

#### [NEW] Database Model: `ReviewTask`

| Column | Type | Purpose |
|---|---|---|
| `id` | UUID PK | |
| `dataset_id` | UUID FK → `datasets.id` | |
| `column_name` | String | Which column needs review |
| `task_type` | Enum | `semantic_mapping`, `domain_validation`, `quality_override`, `unit_confirmation` |
| `suggestions` | JSONB | AI suggestions: `[{concept: "Blood Glucose", confidence: 0.96}, {concept: "HbA1c", confidence: 0.72}]` |
| `context` | JSONB | Sample values, structural info for reviewer context |
| `selected_value` | JSONB | Human selection (null until resolved) |
| `status` | Enum | `pending`, `approved`, `rejected`, `skipped` |
| `resolved_by` | String | User who resolved (for future multi-user) |
| `created_at` | DateTime | |
| `resolved_at` | DateTime | |

#### [NEW] Review Tasks API

| Method | Path | Description |
|---|---|---|
| GET | `/api/v1/review-tasks` | List all pending tasks (filterable by dataset_id, type) |
| GET | `/api/v1/review-tasks/stats` | Count of pending tasks per dataset |
| GET | `/api/v1/datasets/{id}/review-tasks` | List tasks for a specific dataset |
| POST | `/api/v1/review-tasks/{task_id}/resolve` | Resolve: approve a suggestion, provide custom mapping, or skip |
| POST | `/api/v1/review-tasks/{task_id}/reject` | Reject all suggestions (column remains unmapped) |

#### [NEW] Review Resolution Logic

When a review task is resolved:
1. Update `ReviewTask.status` and `selected_value`
2. Update the `SemanticProfile` in the intelligence record with the human-validated mapping
3. Recalculate readiness score (semantic confidence now 100% for this column)
4. If all review tasks for a dataset are resolved and readiness threshold met → status → `ready`

#### [MODIFY] Dataset Detail Page

- **Inline review on "Semantics" tab**: Review tasks appear as interactive cards next to the relevant column
- Each card shows: column name, sample values, AI suggestions with confidence bars, "Approve" / "Edit" / "Skip" buttons
- Real-time: approving updates the readiness score immediately

#### [NEW] Review Queue Page

`/dashboard/review/` — global view:
- All pending review tasks across all datasets
- Grouped by dataset
- Sort by priority (low confidence first)
- Bulk actions: approve all high-confidence suggestions

#### [MODIFY] Sidebar

Add review tasks badge count to the sidebar navigation (next to "Datasets").

#### [NEW] Alembic Migration

`0006_add_review_tasks.py` — create `review_tasks` table.

---

### Phase 4 — Knowledge Engine + Recommendation Engine

> **Goal**: Connect domain-specific knowledge and generate analysis recommendations. Medical knowledge first (CHU use case).

---

#### [NEW] `packages/dil/knowledge_engine.py`

**Medical Knowledge Base** (initially embedded in code, later DB-backed):

```python
MEDICAL_KNOWLEDGE = {
    "blood_glucose": {
        "aliases": ["glucose", "glycemia", "blood sugar", "FBG", "fasting glucose"],
        "normal_range": {"min": 70, "max": 100, "unit": "mg/dL", "fasting": True},
        "risk_factors": ["diabetes", "metabolic syndrome", "insulin resistance"],
        "recommended_charts": ["histogram", "box", "line"],
        "description": "Fasting blood glucose level"
    },
    "bmi": {
        "aliases": ["body mass index", "IMC"],
        "normal_range": {"min": 18.5, "max": 24.9, "unit": "kg/m²"},
        "risk_factors": ["obesity", "diabetes", "cardiovascular disease"],
        "categories": {"underweight": "<18.5", "normal": "18.5-24.9", "overweight": "25-29.9", "obese": ">=30"},
        "recommended_charts": ["histogram", "box", "pie"],
    },
    # ~50 common medical variables
}
```

When semantic mapping identifies a column as a known concept, the knowledge engine enriches it with:
- Normal ranges → enables validity checking ("3 values above normal range")
- Risk factor associations
- Recommended visualizations
- Unit validation

#### [NEW] Database Models

**`KnowledgeEntry`** — extensible domain knowledge:
| Column | Type | Purpose |
|---|---|---|
| `id` | UUID PK | |
| `concept` | String (unique per domain) | "blood_glucose" |
| `domain` | String | "medical" |
| `display_name` | String | "Blood Glucose" |
| `aliases` | JSONB | Alternative names |
| `normal_range` | JSONB | Expected value ranges |
| `risk_factors` | JSONB | Associated conditions |
| `recommended_charts` | JSONB | Suggested chart types |
| `description` | Text | Human-readable description |
| `metadata` | JSONB | Domain-specific extra data |

**`OrganizationMapping`** — organization-specific column mappings:
| Column | Type | Purpose |
|---|---|---|
| `id` | UUID PK | |
| `organization` | String | e.g., "CHU Tangier" (single-org for now) |
| `raw_column_name` | String | Original column name ("LAB_120") |
| `canonical_concept` | String FK | Mapped concept ("blood_glucose") |
| `confidence` | Float | |
| `source` | Enum | `human`, `ai`, `system` |
| `created_at` | DateTime | |

When a human validates `LAB_120 → Blood Glucose`, it's saved as an `OrganizationMapping`. Next time a dataset has `LAB_120`, it maps automatically.

#### [NEW] `packages/dil/recommendation_engine.py`

Generates analysis recommendations based on:
- Column types: numeric → histogram, datetime + numeric → time series, categorical → bar chart
- Domain knowledge: medical → survival analysis, cohort comparison; finance → trend analysis
- Column relationships: highly correlated pairs → regression; categorical + numeric → group comparison
- Data characteristics: many categories → top-N analysis, time column present → temporal analysis

Output:
```python
@dataclass
class AnalysisRecommendation:
    analysis_type: str              # "correlation_analysis", "cohort_comparison", "time_series"
    title: str                      # "Blood Glucose vs HbA1c Correlation"
    description: str                # "These two medical variables are expected to correlate..."
    columns_involved: list[str]     # ["glucose", "hba1c"]
    rationale: str                  # "Both are glycemic markers"
    priority: int                   # 1-5
    suggested_charts: list[str]     # ["scatter", "regression"]
```

#### [MODIFY] Intelligence Record

Add columns: `knowledge_enrichment` (JSONB), `recommendations` (JSONB).

#### [MODIFY] Dataset Detail Page

- **New "Knowledge" tab**: Shows matched knowledge entries per column (normal ranges, risk factors, descriptions)
- **New "Recommendations" tab**: Lists suggested analyses as cards with "Run Analysis" buttons (opens new conversation with pre-built prompt)
- Knowledge enrichment warnings (e.g., "5 glucose values above normal range") appear in the Quality tab

#### [NEW] Alembic Migration

`0007_add_knowledge_and_recommendations.py`

---

### Phase 5 — Agent Integration: Intelligence-First Analysis

> **Goal**: Rewire the AI agent to receive the Dataset Intelligence Record instead of discovering everything from scratch. This is the transformation described in NEXT.md.

---

#### [NEW] Tool: `GetDatasetIntelligenceTool`

```python
class GetDatasetIntelligenceTool(BaseTool):
    """Retrieves the Dataset Intelligence Record for a dataset.
    Returns: structural profile, semantic mappings, quality scores,
    domain, knowledge enrichment, recommendations, readiness score.
    """
```

The agent calls this FIRST before any analysis. It replaces the current pattern of calling `DescribeDatasetTool` → `ListColumnsTool` → `MissingValuesTool` manually.

#### [MODIFY] Agent System Prompt ([prompt.md](file:///home/regisx001/CHU-Platform/packages/agents/data_analyst/prompt.md))

Update to reference the Dataset Intelligence Record:

```markdown
## Dataset Intelligence
You have access to a pre-computed Dataset Intelligence Record for each dataset.
This record contains:
- Structural profile (types, nulls, uniques, statistics)
- Semantic mappings (what each column means, not just its dtype)
- Quality assessment (completeness, validity issues)
- Domain context (e.g., medical dataset)
- Knowledge enrichment (normal ranges, risk factors)
- Recommended analyses

ALWAYS start by calling `get_dataset_intelligence` before any analysis.
DO NOT re-discover what the intelligence record already tells you.
Focus on reasoning, hypothesis generation, and interpretation.
```

#### [MODIFY] Planner Prompt ([planner_prompt.md](file:///home/regisx001/CHU-Platform/packages/agents/data_analyst/prompts/planner_prompt.md))

The planner now:
- Receives the intelligence record summary as context
- Prioritizes recommended analyses from the DIL
- Skips data exploration steps (the DIL already did this)
- Factors in quality warnings (skip columns with >50% missing)
- References domain context ("this is a medical dataset, so…")

#### [MODIFY] Orchestrator

Before the planner runs:
1. Fetch the intelligence record for the linked dataset
2. Inject it into the planner's system message
3. Include top recommendations
4. Include quality warnings
5. Include readiness score — if below threshold, warn user before proceeding

#### [MODIFY] AgentService

Update `build_prompt()` to include intelligence summary:
```
[Dataset: /path/to/dataset.csv]
[Intelligence: {readiness: 92%, domain: medical, quality: 85%}]
[Recommendations: Correlation Analysis (glucose vs hba1c), Cohort Comparison (by age group)]
```

#### Fallback for Unprofiled Datasets

Datasets without intelligence records (uploaded before DIL existed) get a fallback path:
- Agent detects missing intelligence → triggers profiling on-the-fly
- Warning message: "This dataset hasn't been fully analyzed yet. Running intelligence profiling..."
- After profiling completes, agent continues with the intelligence record

---

### Phase 6 — Polish & Production Hardening

> **Goal**: UI polish, performance optimization, and production readiness.

---

#### Performance Optimizations
- **Lazy semantic analysis**: Only run LLM-based semantic analysis when explicitly triggered or when the user first tries to analyze the dataset
- **Caching**: Cache intelligence records in memory with TTL (similar to SessionManager pattern)
- **Batch profiling**: Allow re-profiling all datasets when knowledge base is updated

#### UI Enhancements
- **Dashboard intelligence overview**: Aggregate stats across all datasets (total ready, total pending review, average readiness)
- **Intelligence diff**: When re-profiling, show what changed (new columns detected, quality improved, etc.)
- **Knowledge base management page** (`/dashboard/knowledge/`): View and edit knowledge entries

#### Dataset Lifecycle Visualization
- Timeline component showing dataset progression through states
- Duration at each state (how long profiling took, how long in review)

---

## User Review Required

> [!IMPORTANT]
> **Phase 2 introduces LLM calls during dataset profiling.** The existing `process_dataset()` already runs as a background task, so this infrastructure exists. However, semantic analysis will be significantly slower (LLM calls). Should semantic analysis run automatically after upload, or require an explicit user trigger?

> [!IMPORTANT]
> **Phase 1 changes the `ready` state semantics.** Currently `ready` means "file parsed and profiled." After Phase 1, `ready` means "fully processed and meets readiness threshold." Existing `ready` datasets will need migration handling.

> [!WARNING]
> **Phase 5 changes the agent's core behavior.** After this phase, the agent expects intelligence records to exist. The fallback path handles unprofiled datasets, but the primary workflow shifts from "explore data" to "reason about pre-analyzed data."

---

## Open Questions

> [!IMPORTANT]
> **Semantic analysis trigger**: Should semantic analysis (Phase 2) run automatically after structural profiling, or should users click "Analyze Semantics" manually? Automatic is smoother UX but costs LLM tokens for every upload.

> [!IMPORTANT]
> **Multi-tenancy scope**: NEXT.md describes per-organization mappings (CHU Tangier vs. other hospitals). Should Phase 4 implement basic multi-tenancy, or build for a single organization first and add multi-tenancy later?

> [!NOTE]
> **Medical Knowledge Base scope**: How comprehensive should the initial knowledge base be? Options:
> - **Minimal** (~30 concepts): Common lab values (glucose, HbA1c, cholesterol, creatinine, hemoglobin, etc.)
> - **Standard** (~100 concepts): Above + vitals, common diagnoses, medications
> - **Comprehensive**: LOINC/ICD code mappings (significantly more complex)

> [!NOTE]
> **Readiness threshold**: What readiness score should be required before the "Analyze" button is enabled? Suggested: 70% (allows analysis with warnings) vs 85% (stricter quality gate).

---

## Verification Plan

### Automated Tests

```bash
# Phase 1: DIL package + DB models + quality engine
cd packages/dil && python -m pytest tests/
cd apps/api && python -m pytest tests/test_datasets.py tests/test_intelligence.py

# Phase 2: Semantic engine + domain detection
cd packages/dil && python -m pytest tests/test_semantic.py tests/test_domain.py

# Phase 3: Review tasks
cd apps/api && python -m pytest tests/test_review_tasks.py

# Phase 4: Knowledge engine + recommendations
cd packages/dil && python -m pytest tests/test_knowledge.py tests/test_recommendations.py

# Phase 5: Agent integration
cd packages/agents && python -m pytest tests/test_intelligence_tools.py
```

### Manual Verification

| Phase | Test Scenario | Expected Result |
|---|---|---|
| **1** | Upload a CSV with mixed quality | Dataset profiled, quality issues detected, readiness score < 100% |
| **1** | View dataset detail page | Readiness gauge, quality tab with issues, enhanced profiling tab |
| **2** | Upload a medical CSV (glucose, bmi, age) | Domain detected as "medical", columns mapped to concepts with confidence |
| **2** | Upload a finance CSV (revenue, date, region) | Domain detected as "finance", appropriate semantic roles assigned |
| **3** | Upload CSV with ambiguous column ("LAB_120") | Review task created, appears in review queue and on detail page |
| **3** | Resolve a review task | Intelligence record updated, readiness recalculated, mapping saved |
| **4** | Upload medical CSV after knowledge base populated | Normal range violations detected, recommended analyses generated |
| **4** | Upload new CSV with previously-mapped "LAB_120" | Auto-mapped via OrganizationMapping, no review needed |
| **5** | Chat with a fully profiled dataset | Agent uses intelligence record, skips exploration, references domain context |
| **5** | Chat with an unprofiled dataset | Agent warns and triggers profiling, then continues with intelligence |
