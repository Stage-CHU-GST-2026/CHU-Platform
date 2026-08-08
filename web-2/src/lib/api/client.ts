import { env } from "$env/dynamic/public";

export function getFullApiUrl(path: string): string {
	if (env.PUBLIC_BACKEND_API_URL) {
		return `${env.PUBLIC_BACKEND_API_URL}${path}`;
	}
	// If running on the server (SSR), default to backend http://localhost:10000
	if (typeof window === "undefined") {
		return `http://localhost:10000${path}`;
	}
	// Running in browser client: relative path resolves via Vite / Nginx proxy
	return path;
}

export const BACKEND_API_URL = env.PUBLIC_BACKEND_API_URL || (typeof window === "undefined" ? "http://localhost:10000" : "");

export interface ApiError {
	timestamp?: string;
	status: number;
	error?: string;
	code?: string;
	message: string;
	path?: string;
	module?: string;
	details?: any;
}

export type ApiResult<T> =
	| { ok: true; data: T }
	| { ok: false; status: number; error: ApiError };

export function parseApiError(
	resStatus: number,
	path: string,
	body: any,
	fallbackMessage?: string
): ApiError {
	if (typeof body === "object" && body !== null) {
		return {
			timestamp: body.timestamp || new Date().toISOString(),
			status: body.status || resStatus,
			error: body.error || "Error",
			code: body.code || (resStatus === 404 ? "NOT_FOUND" : resStatus === 401 ? "UNAUTHORIZED" : "ERROR"),
			message: body.detail || body.message || fallbackMessage || `Request failed with status ${resStatus}`,
			path: body.path || path,
			module: body.module || "SYSTEM",
			details: body.details || null
		};
	}
	return {
		timestamp: new Date().toISOString(),
		status: resStatus,
		error: "Error",
		code: "ERROR",
		message: typeof body === "string" && body.trim() ? body : (fallbackMessage || `Request failed with status ${resStatus}`),
		path,
		module: "SYSTEM",
		details: null
	};
}

/**
 * Generic fetch wrapper with JSON parsing and structured error handling.
 */
export async function apiFetch<T>(
	path: string,
	options: RequestInit = {}
): Promise<ApiResult<T>> {
	try {
		const url = getFullApiUrl(path);
		const isFormData = typeof FormData !== "undefined" && options.body instanceof FormData;

		const headers: Record<string, string> = {
			...(options.headers as Record<string, string>)
		};

		if (!isFormData && !headers["Content-Type"]) {
			headers["Content-Type"] = "application/json";
		}

		const res = await fetch(url, {
			...options,
			headers
		});

		if (res.status === 204) {
			return { ok: true, data: null as unknown as T };
		}

		const body = await res.json().catch(() => null);

		if (!res.ok) {
			return {
				ok: false,
				status: res.status,
				error: parseApiError(res.status, path, body)
			};
		}

		return { ok: true, data: body as T };
	} catch (err: any) {
		return {
			ok: false,
			status: 500,
			error: {
				timestamp: new Date().toISOString(),
				status: 500,
				error: "Network Error",
				code: "NETWORK_ERROR",
				message: err.message || "Failed to communicate with backend server",
				path,
				module: "CLIENT"
			}
		};
	}
}

/**
 * Fetch wrapper for raw responses (blobs, files, SSE).
 */
export async function apiFetchRaw(
	path: string,
	options: RequestInit = {}
): Promise<Response> {
	const url = getFullApiUrl(path);
	return fetch(url, options);
}
