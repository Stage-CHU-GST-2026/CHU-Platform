import { apiFetch, type ApiResult } from "./client";

export interface ColumnInfo {
	name: string;
	data_type: string;
	nullable: boolean;
	unique_count?: number | null;
	sample_values?: any[];
	semantic_category?: string | null;
	description?: string | null;
}

export interface DatasetSummary {
	id: string;
	original_filename: string;
	filepath: string;
	file_size: number;
	rows: number | null;
	columns: number | null;
	status: "pending" | "processing" | "ready" | "failed";
	created_at: string;
	updated_at: string;
}

export interface DatasetDetail extends DatasetSummary {
	error_message?: string | null;
	description?: string | null;
	column_info?: ColumnInfo[] | null;
}

export interface DatasetUploadResponse {
	id: string;
	original_filename: string;
	filepath: string;
	file_size: number;
	status: string;
	message: string;
}

export interface DatasetPreview {
	dataset_id: string;
	total_rows: number;
	total_columns: number;
	columns: string[];
	rows: Record<string, any>[];
}

export interface DatasetStatistics {
	dataset_id: string;
	total_rows: number;
	total_columns: number;
	numeric_columns: Record<string, {
		count: number;
		mean?: number;
		std?: number;
		min?: number;
		max?: number;
		median?: number;
	}>;
	categorical_columns: Record<string, {
		count: number;
		unique: number;
		top?: any;
		freq?: number;
	}>;
	missing_values: Record<string, number>;
}

export interface SemanticMappingItem {
	column_name: string;
	category_code?: string | null;
	category_name?: string | null;
	description?: string | null;
}

export interface SemanticMappingUpdate {
	column_name: string;
	category_code?: string | null;
	description?: string | null;
}

export interface DatasetContextResponse {
	dataset_id: string;
	original_filename: string;
	context_string: string;
	custom_instructions?: string | null;
}

export interface DatasetContextUpdate {
	custom_instructions?: string;
}

/**
 * Upload a dataset file (CSV, TSV, XLSX, Parquet, JSON, Feather).
 */
export async function uploadDataset(
	formData: FormData
): Promise<ApiResult<DatasetUploadResponse>> {
	return apiFetch<DatasetUploadResponse>("/api/v1/datasets/upload", {
		method: "POST",
		body: formData
	});
}

/**
 * List datasets with optional status filtering and pagination.
 */
export async function listDatasets(params?: {
	status_filter?: string;
	limit?: number;
	offset?: number;
}): Promise<ApiResult<DatasetSummary[]>> {
	const query = new URLSearchParams();
	if (params?.status_filter) query.set("status_filter", params.status_filter);
	if (params?.limit !== undefined) query.set("limit", params.limit.toString());
	if (params?.offset !== undefined) query.set("offset", params.offset.toString());

	const queryString = query.toString() ? `?${query.toString()}` : "";
	return apiFetch<DatasetSummary[]>(`/api/v1/datasets${queryString}`);
}

/**
 * Get dataset details by ID.
 */
export async function getDataset(id: string): Promise<ApiResult<DatasetDetail>> {
	return apiFetch<DatasetDetail>(`/api/v1/datasets/${id}`);
}

/**
 * Delete a dataset by ID.
 */
export async function deleteDataset(id: string): Promise<ApiResult<void>> {
	return apiFetch<void>(`/api/v1/datasets/${id}`, {
		method: "DELETE"
	});
}

/**
 * Get preview rows for a dataset.
 */
export async function getDatasetPreview(
	id: string,
	rows: number = 50
): Promise<ApiResult<DatasetPreview>> {
	return apiFetch<DatasetPreview>(`/api/v1/datasets/${id}/preview?rows=${rows}`);
}

/**
 * Get computed statistics for a dataset.
 */
export async function getDatasetStatistics(
	id: string
): Promise<ApiResult<DatasetStatistics>> {
	return apiFetch<DatasetStatistics>(`/api/v1/datasets/${id}/statistics`);
}

/**
 * Get column info list for a dataset.
 */
export async function getDatasetColumns(
	id: string
): Promise<ApiResult<ColumnInfo[]>> {
	return apiFetch<ColumnInfo[]>(`/api/v1/datasets/${id}/columns`);
}

/**
 * Get semantic mappings for a dataset.
 */
export async function getSemanticMappings(
	id: string
): Promise<ApiResult<SemanticMappingItem[]>> {
	return apiFetch<SemanticMappingItem[]>(`/api/v1/datasets/${id}/semantic-mappings`);
}

/**
 * Update semantic mappings for a dataset.
 */
export async function updateSemanticMappings(
	id: string,
	mappings: SemanticMappingUpdate[]
): Promise<ApiResult<SemanticMappingItem[]>> {
	return apiFetch<SemanticMappingItem[]>(`/api/v1/datasets/${id}/semantic-mappings`, {
		method: "PUT",
		body: JSON.stringify(mappings)
	});
}

/**
 * Get dataset context string used by the AI Agent.
 */
export async function getDatasetContext(
	id: string
): Promise<ApiResult<DatasetContextResponse>> {
	return apiFetch<DatasetContextResponse>(`/api/v1/datasets/${id}/context`);
}

/**
 * Update dataset context string or custom user instructions.
 */
export async function updateDatasetContext(
	id: string,
	custom_instructions: string
): Promise<ApiResult<DatasetContextResponse>> {
	return apiFetch<DatasetContextResponse>(`/api/v1/datasets/${id}/context`, {
		method: "PATCH",
		body: JSON.stringify({ custom_instructions })
	});
}
