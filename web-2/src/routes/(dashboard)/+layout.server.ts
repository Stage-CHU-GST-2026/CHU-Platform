import { listConversations, type ConversationSummary } from "$lib/server/conversations";
import type { LayoutServerLoad } from "./$types";

export const load: LayoutServerLoad = async () => {
	const res = await listConversations({ limit: 50 });
	const conversations: ConversationSummary[] = res.ok ? res.data : [];

	return {
		conversations
	};
};
