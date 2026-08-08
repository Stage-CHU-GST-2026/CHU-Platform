import { apiFetch, type ApiResult } from "./client";

export interface HealthResponse {
	status: string;
}

/**
 * Perform health check on the backend API server.
 */
export async function checkHealth(): Promise<ApiResult<HealthResponse>> {
	return apiFetch<HealthResponse>("/health");
}
