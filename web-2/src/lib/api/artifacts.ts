import { apiFetch, apiFetchRaw, BACKEND_API_URL, type ApiResult } from "./client";

export interface ArtifactItem {
	id: string;
	conversation_id: string;
	filename: string;
	mime_type: string;
	file_size: number | null;
	url: string;
	created_at: string;
}

export interface PlanStepItem {
	id: number;
	title?: string;
	name?: string;
	description?: string;
	tool_hint?: string;
}

export interface PlanData {
	plan_title?: string;
	steps: PlanStepItem[];
}

/**
 * List all artifacts for a conversation.
 */
export async function listArtifacts(params: {
	conversation_id: string;
	limit?: number;
	offset?: number;
}): Promise<ApiResult<ArtifactItem[]>> {
	const query = new URLSearchParams({
		conversation_id: params.conversation_id
	});

	if (params.limit !== undefined) query.set("limit", params.limit.toString());
	if (params.offset !== undefined) query.set("offset", params.offset.toString());

	return apiFetch<ArtifactItem[]>(`/api/v1/artifacts?${query.toString()}`);
}

/**
 * Get metadata for a single artifact by ID.
 */
export async function getArtifact(id: string): Promise<ApiResult<ArtifactItem>> {
	return apiFetch<ArtifactItem>(`/api/v1/artifacts/${id}`);
}

/**
 * Fetch plan JSON data from an artifact.
 */
export async function fetchPlanFromArtifact(artifact: ArtifactItem): Promise<PlanData | null> {
	if (!artifact.mime_type.includes("plan") && !artifact.filename.includes("plan")) return null;
	try {
		const res = await apiFetchRaw(`/api/v1/artifacts/${artifact.id}/file`);
		if (!res.ok) return null;
		return await res.json();
	} catch {
		return null;
	}
}

/**
 * Get direct download/display URL for an artifact file.
 */
export function getArtifactFileUrl(id: string): string {
	return `${BACKEND_API_URL}/api/v1/artifacts/${id}/file`;
}

/**
 * Get direct URL for a generated chart image by filename.
 */
export function getChartFileUrl(filename: string): string {
	return `${BACKEND_API_URL}/api/v1/charts/${filename}`;
}

/**
 * Download the raw artifact file buffer/blob.
 */
export async function downloadArtifactFile(id: string): Promise<Response> {
	return apiFetchRaw(`/api/v1/artifacts/${id}/file`);
}
