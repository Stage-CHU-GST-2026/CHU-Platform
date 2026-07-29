# Data Intelligence Layer (DIL)

## Vision

The Data Intelligence Layer (DIL) is the core subsystem responsible for transforming raw datasets into structured, semantically enriched, validated, and AI-ready knowledge.

Rather than exposing raw tables directly to Large Language Models or analytical engines, the DIL creates an intelligent representation of the dataset that serves as the single source of truth for every downstream component.

The Data Intelligence Layer is executed once after dataset ingestion and continuously evolves through human validation, semantic enrichment, and analysis history.

---

# Why it exists

Traditional AI Data Analysts work like this:

```text
CSV
    │
    ▼
LLM
    │
    ▼
Guess...
```

Your platform will work like this

```text
CSV
    │
    ▼
Data Intelligence Layer
    │
    ▼
Dataset Intelligence Record
    │
    ▼
Planner
    │
    ▼
Statistics
    │
    ▼
Visualization
    │
    ▼
LLM
```

The LLM never sees a raw dataset.

It sees an intelligent description of the dataset.

---

# Responsibilities

The Data Intelligence Layer has one responsibility:

> Transform data into knowledge.

More specifically it should answer

* What is this dataset?
* What does every column represent?
* How trustworthy is the data?
* What analyses are possible?
* What risks exist?
* What information is missing?
* What needs human validation?
* What domain does this dataset belong to?
* How should downstream AI reason about this dataset?

---

# Architecture

```text
                     Data Intelligence Layer
                                │
 ┌──────────────┬──────────────┬──────────────┬──────────────┐
 │              │              │              │
 ▼              ▼              ▼              ▼
Structural   Semantic      Quality      Knowledge
Profiler     Engine        Engine       Engine
 │              │              │              │
 └──────────────┴──────────────┴──────────────┘
                │
                ▼
      Dataset Intelligence Record
```

---

# Components

## 1. Dataset Ingestion

Responsibilities

* Read CSV
* Excel
* Parquet
* SQL
* JSON

Detect

* encoding
* delimiter
* malformed rows
* schema
* file metadata

Output

```text
Raw Dataset
```

---

## 2. Structural Profiler

Purely deterministic.

No AI.

Responsibilities

* schema detection
* datatype inference
* missing values
* duplicates
* statistics
* unique values
* candidate IDs
* datetime detection
* categorical detection

Output

```text
Structural Profile
```

---

## 3. Semantic Engine

This is where intelligence begins.

Responsibilities

Identify

```text
Glucose

↓

Blood Glucose
```

Not

```text
float64
```

Infer

* concepts
* entities
* business meaning
* units
* medical variables
* relationships
* targets
* predictors

Output

```text
Semantic Profile
```

---

## 4. Domain Detection

Responsibilities

Infer

Medical

Finance

Retail

IoT

Manufacturing

Marketing

Geospatial

...

This influences everything later.

---

## 5. Quality Engine

Responsibilities

Measure

* completeness
* consistency
* validity
* uniqueness
* integrity

Detect

* impossible values
* duplicated IDs
* invalid units
* inconsistent categories

Output

```text
Quality Profile
```

---

## 6. Relationship Discovery

Responsibilities

Infer

* foreign keys
* entities
* functional dependencies
* candidate targets
* redundant columns
* correlations

---

## 7. Confidence Engine

Every intelligent decision receives confidence.

Example

```text
Blood Glucose

Confidence

98%
```

Everything becomes explainable.

---

## 8. Knowledge Engine

This is the component that connects with your Medical Knowledge Base.

Responsibilities

Retrieve

* aliases
* normal ranges
* diseases
* descriptions
* recommended analyses
* expected units

Example

```text
BMI

↓

Normal Range

18.5–24.9

↓

Recommended Charts

Histogram

↓

Known Risk Factor

Diabetes
```

---

## 9. Recommendation Engine

Instead of asking the planner to discover analyses

Generate recommendations.

Example

```text
Recommended Analyses

Classification

Correlation

Outlier Detection

Feature Importance

Survival Analysis
```

---

## 10. Human Validation Engine

One of the most important components.

Responsibilities

Detect

Unknown concepts

↓

Generate review tasks

↓

Human validates

↓

Knowledge saved

↓

Future datasets improve

---

# Dataset Intelligence Record

Everything above produces a single persistent object.

```text
Dataset Intelligence Record

├── Metadata
├── Structural Profile
├── Semantic Profile
├── Quality Profile
├── Domain
├── Relationships
├── Medical Knowledge
├── Recommendations
├── Confidence Scores
├── Warnings
├── Readiness Score
└── Version
```

This object is stored in PostgreSQL.

---

# Dataset Lifecycle

```text
Uploaded
      │
      ▼
Profiling
      │
      ▼
Semantic Resolution
      │
      ▼
Human Review
      │
      ▼
Knowledge Enrichment
      │
      ▼
Ready
      │
      ▼
Analysis
      │
      ▼
Archived
```

---

# Human Validation Workflow

Unknown column

```text
LAB_120
```

Semantic Engine

↓

Possible matches

```text
Blood Glucose

96%

HbA1c

72%

Creatinine

55%
```

User selects

Blood Glucose

↓

Saved permanently

↓

Next upload

Automatic mapping

---

# Organization Knowledge Base

This is different from the Medical Knowledge Base.

Medical Knowledge

Contains universal concepts.

Organization Knowledge

Contains local mappings.

Example

```text
Hospital

CHU Tangier

LAB_120

↓

Blood Glucose
```

Another hospital

```text
LAB_120

↓

Creatinine
```

Different mapping.

Same engine.

---

# Dataset Readiness

Every dataset receives a readiness score.

Example

```text
Dataset Readiness

96%

✓ Structure

✓ Quality

✓ Relationships

✓ Semantics

✓ Domain

✓ Medical Mapping

Ready for AI Analysis
```

The Analyze button should only be enabled when the dataset reaches the required readiness threshold.

---

# How the AI Agent Uses It

The AI agent never receives only a DataFrame.

Instead, it receives three inputs:

```text
Dataset
        +
Dataset Intelligence Record
        +
Organization Knowledge
```

This changes the role of the LLM completely. Rather than discovering what the data might represent, it starts from an already curated understanding of the dataset and focuses on reasoning, hypothesis generation, statistical interpretation, and communication.

---

# Design Principles

The Data Intelligence Layer should follow a few core principles:

* **Deterministic before AI**: use rules, statistics, and metadata first; only rely on an LLM when deterministic methods cannot resolve ambiguity.
* **Persistent knowledge**: intelligence generated once should be stored and reused, not recomputed unnecessarily.
* **Human-in-the-loop**: unresolved or low-confidence mappings should become review tasks instead of silent guesses.
* **Explainability**: every inferred concept, recommendation, or warning should include evidence and a confidence score.
* **Composable architecture**: each engine (profiling, semantics, quality, knowledge) should be independently testable and replaceable.
* **AI-ready output**: the final product of the DIL is not a report but a structured, versioned **Dataset Intelligence Record** that becomes the foundation for every analysis, visualization, and AI interaction in your platform.

This is the architectural layer that separates a generic "chat with your CSV" application from a true enterprise-grade data intelligence platform.
