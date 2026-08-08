import { apiFetch, apiFetchRaw, type ApiResult } from "./client";
import type { ArtifactItem } from "./artifacts";

export interface MessageItem {
	id: number;
	conversation_id?: string;
	role: "user" | "assistant";
	content: string;
	created_at: string;
}

export interface ConversationSummary {
	id: string;
	title: string | null;
	dataset_id?: string | null;
	dataset_name?: string | null;
	created_at: string;
	updated_at: string;
	message_count: number;
	artifact_count: number;
}

export interface ConversationDetail {
	id: string;
	title: string | null;
	dataset_id?: string | null;
	dataset_name?: string | null;
	created_at: string;
	updated_at: string;
	messages: MessageItem[];
	artifacts?: ArtifactItem[];
}

export interface CreateConversationPayload {
	title?: string;
	dataset_id?: string | null;
}

export interface UpdateConversationPayload {
	title?: string;
	dataset_id?: string | null;
}

export interface ChatMessagePayload {
	message: string;
	dataset_path?: string;
}

/**
 * List all conversations, ordered by most recently updated first.
 */
export async function listConversations(params?: {
	limit?: number;
	offset?: number;
}): Promise<ApiResult<ConversationSummary[]>> {
	const query = new URLSearchParams();
	if (params?.limit !== undefined) query.set("limit", params.limit.toString());
	if (params?.offset !== undefined) query.set("offset", params.offset.toString());

	const queryString = query.toString() ? `?${query.toString()}` : "";
	return apiFetch<ConversationSummary[]>(`/api/v1/conversations${queryString}`);
}

/**
 * Create a new conversation.
 */
export async function createConversation(
	title?: string,
	datasetId?: string | null
): Promise<ApiResult<ConversationDetail>> {
	return apiFetch<ConversationDetail>("/api/v1/conversations", {
		method: "POST",
		body: JSON.stringify({
			...(title ? { title } : {}),
			...(datasetId ? { dataset_id: datasetId } : {})
		})
	});
}

/**
 * Get details for a single conversation, including messages and artifacts.
 */
export async function getConversation(
	id: string,
	includeArtifacts: boolean = true
): Promise<ApiResult<ConversationDetail>> {
	return apiFetch<ConversationDetail>(
		`/api/v1/conversations/${id}?include_artifacts=${includeArtifacts}`
	);
}

/**
 * Update the title of an existing conversation.
 */
export async function updateConversationTitle(
	id: string,
	title: string
): Promise<ApiResult<ConversationDetail>> {
	return apiFetch<ConversationDetail>(`/api/v1/conversations/${id}`, {
		method: "PATCH",
		body: JSON.stringify({ title })
	});
}

/**
 * Link or unlink a dataset to an existing conversation.
 */
export async function updateConversationDataset(
	id: string,
	datasetId: string | null
): Promise<ApiResult<ConversationDetail>> {
	return apiFetch<ConversationDetail>(`/api/v1/conversations/${id}`, {
		method: "PATCH",
		body: JSON.stringify({ dataset_id: datasetId })
	});
}

/**
 * Delete a conversation and all associated messages.
 */
export async function deleteConversation(
	id: string
): Promise<ApiResult<void>> {
	return apiFetch<void>(`/api/v1/conversations/${id}`, {
		method: "DELETE"
	});
}

/**
 * Stream SSE chat message response from FastAPI backend.
 */
export async function sendChatMessageStream(
	id: string,
	payload: ChatMessagePayload
): Promise<Response> {
	return apiFetchRaw(`/api/v1/conversations/${id}/chat`, {
		method: "POST",
		headers: {
			"Content-Type": "application/json"
		},
		body: JSON.stringify(payload)
	});
}
