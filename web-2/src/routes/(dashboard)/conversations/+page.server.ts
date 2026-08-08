import { redirect } from "@sveltejs/kit";
import { createConversation, listConversations } from "$lib/server/conversations";
import type { PageServerLoad } from "./$types";

export const load: PageServerLoad = async () => {
	const listRes = await listConversations({ limit: 1 });
	if (listRes.ok && listRes.data.length > 0) {
		throw redirect(303, `/conversations/${listRes.data[0].id}`);
	}

	const newRes = await createConversation();
	if (newRes.ok && newRes.data) {
		throw redirect(303, `/conversations/${newRes.data.id}`);
	}

	throw redirect(303, "/");
};
