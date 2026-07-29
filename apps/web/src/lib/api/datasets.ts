/**
 * Datasets API client — interfaces and functions to interact with the FastAPI datasets backend.
 * Base route: /api/v1/datasets
 */

const API_BASE = "/api/v1";

export type DatasetStatus = "uploading" | "processing" | "profiling" | "profiled" | "semantic_review" | "ready" | "error";

export interface ColumnInfo {
    name: string;
    dtype: string;
    null_count: number;
    unique_count: number;
    sample?: string | null;
    is_numeric?: boolean;
    is_categorical?: boolean;
    is_datetime?: boolean;
    is_boolean?: boolean;
    is_candidate_id?: boolean;
    stats?: Record<string, any>;
}

export interface QualityIssue {
    column_name?: string | null;
    issue_type: string;
    severity: "info" | "low" | "medium" | "high" | "critical";
    description: string;
    affected_count: number;
}

export interface QualityProfile {
    overall_score: number;
    completeness: number;
    uniqueness: number;
    consistency: number;
    validity: number;
    integrity: number;
    issues: QualityIssue[];
}

export interface StructuralProfile {
    row_count: number;
    column_count: number;
    memory_mb: number;
    duplicate_rows: number;
    duplicate_percentage: number;
    columns: ColumnInfo[];
    candidate_ids: string[];
    datetime_columns: string[];
    numeric_columns: string[];
    categorical_columns: string[];
    boolean_columns: string[];
}

export interface ReadinessBreakdown {
    structure: number;
    quality: number;
    semantics: number;
    domain: number;
    knowledge: number;
}

export interface ConceptAlternative {
    concept: string;
    confidence: number;
    description?: string | null;
}

export interface ColumnSemantic {
    column_name: string;
    inferred_concept: string;
    semantic_role: "identifier" | "measure" | "dimension" | "target" | "datetime" | "text";
    entity_type?: string | null;
    units?: string | null;
    confidence: number;
    source: "heuristic" | "llm" | "human";
    alternatives?: ConceptAlternative[];
    needs_review?: boolean;
    description?: string | null;
}

export interface SemanticProfile {
    overall_confidence: number;
    columns: ColumnSemantic[];
    target_candidates: string[];
    predictor_candidates: string[];
}

export interface DomainProfile {
    primary_domain: string;
    confidence: number;
    reasoning: string;
    subdomains: string[];
}

export interface DatasetIntelligenceRecord {
    id: string;
    dataset_id: string;
    structural_profile: StructuralProfile | null;
    quality_profile: QualityProfile | null;
    semantic_profile: SemanticProfile | null;
    domain_profile: DomainProfile | null;
    readiness_score: number;
    readiness_breakdown: ReadinessBreakdown | null;
    warnings: string[] | null;
    version: number;
    created_at: string;
    updated_at: string;
}

export interface DatasetSummary {
    id: string;
    original_filename: string;
    file_size: number | null;
    mime_type: string;
    status: DatasetStatus;
    rows: number | null;
    columns: number | null;
    error_message: string | null;
    created_at: string;
    updated_at: string;
}

export interface DatasetDetail extends DatasetSummary {
    columns_info: ColumnInfo[] | null;
}

export interface DatasetUploadResponse {
    id: string;
    original_filename: string;
    status: DatasetStatus;
    message: string;
}

export interface PreviewRow {
    row_number: number;
    values: Record<string, string | number | boolean | null>;
}

export interface DatasetPreview {
    dataset_id: string;
    total_rows: number;
    total_columns: number;
    columns: string[];
    rows: PreviewRow[];
}

export interface DatasetStatistics {
    dataset_id: string;
    numeric_summary: Record<string, Record<string, number>> | null;
    missing_values: Record<string, number> | null;
    column_types: Record<string, string> | null;
}

/**
 * Upload a dataset file (CSV, TSV, XLSX, XLS, Parquet, JSON, Feather - up to 500MB).
 */
export async function uploadDataset(file: File): Promise<DatasetUploadResponse> {
    const formData = new FormData();
    formData.append("file", file);

    const res = await fetch(`${API_BASE}/datasets/upload`, {
        method: "POST",
        body: formData,
    });

    if (!res.ok) {
        let errDetail = `Upload failed with status ${res.status}`;
        try {
            const json = await res.json();
            if (json.detail) errDetail = json.detail;
        } catch {}
        throw new Error(errDetail);
    }

    return res.json();
}

/**
 * List all datasets with optional pagination and status filter.
 */
export async function listDatasets(
    limit = 50,
    offset = 0,
    status?: DatasetStatus
): Promise<DatasetSummary[]> {
    let url = `${API_BASE}/datasets?limit=${limit}&offset=${offset}`;
    if (status) {
        url += `&status=${encodeURIComponent(status)}`;
    }

    const res = await fetch(url);
    if (!res.ok) {
        throw new Error(`Failed to fetch datasets: ${res.status}`);
    }

    return res.json();
}

/**
 * Get full details for a single dataset (including column profiling metadata).
 */
export async function getDataset(id: string): Promise<DatasetDetail> {
    const res = await fetch(`${API_BASE}/datasets/${encodeURIComponent(id)}`);
    if (!res.ok) {
        throw new Error(`Failed to fetch dataset details: ${res.status}`);
    }

    return res.json();
}

/**
 * Delete a dataset and its file from disk.
 */
export async function deleteDataset(id: string): Promise<void> {
    const res = await fetch(`${API_BASE}/datasets/${encodeURIComponent(id)}`, {
        method: "DELETE",
    });

    if (!res.ok) {
        throw new Error(`Failed to delete dataset: ${res.status}`);
    }
}

/**
 * Preview first N rows of a ready dataset.
 */
export async function getDatasetPreview(id: string, n = 10): Promise<DatasetPreview> {
    const res = await fetch(`${API_BASE}/datasets/${encodeURIComponent(id)}/preview?n=${n}`);
    if (!res.ok) {
        let detail = `Failed to preview dataset: status ${res.status}`;
        try {
            const err = await res.json();
            if (err.detail) detail = err.detail;
        } catch {}
        throw new Error(detail);
    }

    return res.json();
}

/**
 * Compute & return statistical summaries for numeric columns and missing value counts.
 */
export async function getDatasetStatistics(id: string): Promise<DatasetStatistics> {
    const res = await fetch(`${API_BASE}/datasets/${encodeURIComponent(id)}/statistics`);
    if (!res.ok) {
        let detail = `Failed to load statistics: status ${res.status}`;
        try {
            const err = await res.json();
            if (err.detail) detail = err.detail;
        } catch {}
        throw new Error(detail);
    }

    return res.json();
}

/**
 * Return column schema metadata for a dataset.
 */
export async function getDatasetColumns(id: string): Promise<ColumnInfo[]> {
    const res = await fetch(`${API_BASE}/datasets/${encodeURIComponent(id)}/columns`);
    if (!res.ok) {
        throw new Error(`Failed to fetch column metadata: ${res.status}`);
    }

    return res.json();
}

/**
 * Return Dataset Intelligence Record (DIL structural profile, quality profile, readiness score).
 */
export async function getDatasetIntelligence(id: string): Promise<DatasetIntelligenceRecord> {
    const res = await fetch(`${API_BASE}/datasets/${encodeURIComponent(id)}/intelligence`);
    if (!res.ok) {
        let detail = `Failed to fetch dataset intelligence: ${res.status}`;
        try {
            const err = await res.json();
            if (err.detail) detail = err.detail;
        } catch {}
        throw new Error(detail);
    }

    return res.json();
}

/**
 * Trigger background re-profiling of a dataset.
 */
export async function reprofileDataset(id: string): Promise<void> {
    const res = await fetch(`${API_BASE}/datasets/${encodeURIComponent(id)}/reprofile`, {
        method: "POST",
    });

    if (!res.ok) {
        throw new Error(`Failed to re-profile dataset: ${res.status}`);
    }
}

/**
 * Update or override a column's semantic mapping (concept, role, units, etc.).
 */
export async function updateSemanticMapping(
    datasetId: string,
    payload: {
        column_name: string;
        inferred_concept: string;
        semantic_role: string;
        units?: string | null;
        entity_type?: string | null;
        description?: string | null;
    }
): Promise<DatasetIntelligenceRecord> {
    const res = await fetch(`${API_BASE}/datasets/${encodeURIComponent(datasetId)}/update-semantic-mapping`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
    });

    if (!res.ok) {
        let detail = `Failed to update semantic mapping: ${res.status}`;
        try {
            const err = await res.json();
            if (err.detail) detail = err.detail;
        } catch {}
        throw new Error(detail);
    }

    return res.json();
}
