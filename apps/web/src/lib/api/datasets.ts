/**
 * Datasets API client — interfaces and functions to interact with the FastAPI datasets backend.
 * Base route: /api/v1/datasets
 */

const API_BASE = "/api/v1";

export type DatasetStatus = "uploading" | "processing" | "ready" | "error";

export interface ColumnInfo {
    name: string;
    dtype: string;
    null_count: number;
    unique_count: number;
    sample?: string | null;
}

// ── Semantic Mapping ──────────────────────────────────────────────────

export interface SemanticMappingItem {
    column_name: string;
    dtype: string;
    mapped_concept: string;
    category: string;
    confidence: number;
    unit?: string | null;
    is_custom?: boolean;
}

export interface SemanticMappingUpdate {
    mappings: SemanticMappingItem[];
}

// ── Dataset Context ───────────────────────────────────────────────────

export interface DatasetContext {
    description: string | null;
    notes: string | null;
    tags: string[];
}

export interface DatasetContextUpdate {
    description?: string | null;
    notes?: string | null;
    tags?: string[] | null;
}

// ── Core Dataset Types ─────────────────────────────────────────────────

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
    semantic_mappings: SemanticMappingItem[] | null;
    context_description: string | null;
    context_notes: string | null;
    context_tags: string[];
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

// ── Upload ────────────────────────────────────────────────────────────

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

// ── List ──────────────────────────────────────────────────────────────

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

// ── Get single ────────────────────────────────────────────────────────

/**
 * Get full details for a single dataset (including column profiling, semantic
 * mappings, and business context).
 */
export async function getDataset(id: string): Promise<DatasetDetail> {
    const res = await fetch(`${API_BASE}/datasets/${encodeURIComponent(id)}`);
    if (!res.ok) {
        throw new Error(`Failed to fetch dataset details: ${res.status}`);
    }

    return res.json();
}

// ── Delete ────────────────────────────────────────────────────────────

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

// ── Preview ───────────────────────────────────────────────────────────

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

// ── Statistics ────────────────────────────────────────────────────────

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

// ── Column info ───────────────────────────────────────────────────────

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

// ── Semantic Mappings ─────────────────────────────────────────────────

/**
 * Fetch the semantic concept mappings for a dataset.
 */
export async function getSemanticMappings(id: string): Promise<SemanticMappingItem[]> {
    const res = await fetch(`${API_BASE}/datasets/${encodeURIComponent(id)}/semantic-mappings`);
    if (!res.ok) {
        let detail = `Failed to load semantic mappings: status ${res.status}`;
        try {
            const err = await res.json();
            if (err.detail) detail = err.detail;
        } catch {}
        throw new Error(detail);
    }

    return res.json();
}

/**
 * Replace all semantic mappings for a dataset (full overwrite).
 */
export async function saveSemanticMappings(
    id: string,
    mappings: SemanticMappingItem[]
): Promise<SemanticMappingItem[]> {
    const res = await fetch(
        `${API_BASE}/datasets/${encodeURIComponent(id)}/semantic-mappings`,
        {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ mappings }),
        }
    );

    if (!res.ok) {
        let detail = `Failed to save semantic mappings: status ${res.status}`;
        try {
            const err = await res.json();
            if (err.detail) detail = err.detail;
        } catch {}
        throw new Error(detail);
    }

    return res.json();
}

// ── Dataset Context ───────────────────────────────────────────────────

/**
 * Fetch the business context (description, notes, tags) for a dataset.
 */
export async function getDatasetContext(id: string): Promise<DatasetContext> {
    const res = await fetch(`${API_BASE}/datasets/${encodeURIComponent(id)}/context`);
    if (!res.ok) {
        let detail = `Failed to load dataset context: status ${res.status}`;
        try {
            const err = await res.json();
            if (err.detail) detail = err.detail;
        } catch {}
        throw new Error(detail);
    }

    return res.json();
}

/**
 * Partially update dataset context fields (PATCH semantics).
 * Only fields included in the payload are updated.
 */
export async function updateDatasetContext(
    id: string,
    payload: DatasetContextUpdate
): Promise<DatasetContext> {
    const res = await fetch(
        `${API_BASE}/datasets/${encodeURIComponent(id)}/context`,
        {
            method: "PATCH",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        }
    );

    if (!res.ok) {
        let detail = `Failed to update dataset context: status ${res.status}`;
        try {
            const err = await res.json();
            if (err.detail) detail = err.detail;
        } catch {}
        throw new Error(detail);
    }

    return res.json();
}
