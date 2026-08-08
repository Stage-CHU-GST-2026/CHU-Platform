import { getConversation, type ConversationDetail } from "$lib/server/conversations";
import { error } from "@sveltejs/kit";
import type { PageServerLoad } from "./$types";

export const load: PageServerLoad = async ({ params }) => {
	const conversationId = params.id;

	if (!conversationId) {
		throw error(400, "Invalid conversation ID");
	}

	const res = await getConversation(conversationId, true);

	if (!res.ok) {
		throw error(res.status, res.error.message || "Conversation not found");
	}

	return {
		conversation: res.data as ConversationDetail
	};
};
