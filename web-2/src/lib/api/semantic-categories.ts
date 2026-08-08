import { apiFetch, type ApiResult } from "./client";

export interface SemanticCategoryItem {
	id: string;
	name: string;
	code: string;
	description?: string | null;
	data_type_hint?: string | null;
	created_at: string;
	updated_at: string;
}

export interface CreateSemanticCategoryPayload {
	name: string;
	code: string;
	description?: string;
	data_type_hint?: string;
}

export interface UpdateSemanticCategoryPayload {
	name?: string;
	description?: string;
	data_type_hint?: string;
}

/**
 * List all semantic categories.
 */
export async function listSemanticCategories(): Promise<ApiResult<SemanticCategoryItem[]>> {
	return apiFetch<SemanticCategoryItem[]>("/api/v1/semantic-categories");
}

/**
 * Create a new semantic category.
 */
export async function createSemanticCategory(
	payload: CreateSemanticCategoryPayload
): Promise<ApiResult<SemanticCategoryItem>> {
	return apiFetch<SemanticCategoryItem>("/api/v1/semantic-categories", {
		method: "POST",
		body: JSON.stringify(payload)
	});
}

/**
 * Get a semantic category by ID.
 */
export async function getSemanticCategory(
	id: string
): Promise<ApiResult<SemanticCategoryItem>> {
	return apiFetch<SemanticCategoryItem>(`/api/v1/semantic-categories/${id}`);
}

/**
 * Update a semantic category by ID.
 */
export async function updateSemanticCategory(
	id: string,
	payload: UpdateSemanticCategoryPayload
): Promise<ApiResult<SemanticCategoryItem>> {
	return apiFetch<SemanticCategoryItem>(`/api/v1/semantic-categories/${id}`, {
		method: "PATCH",
		body: JSON.stringify(payload)
	});
}

/**
 * Delete a semantic category by ID.
 */
export async function deleteSemanticCategory(
	id: string
): Promise<ApiResult<void>> {
	return apiFetch<void>(`/api/v1/semantic-categories/${id}`, {
		method: "DELETE"
	});
}
