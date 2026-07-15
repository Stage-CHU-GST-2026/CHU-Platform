/**
 * Shared conversations store.
 * The sidebar subscribes to this to know when to refresh the conversation list.
 */
import { writable } from 'svelte/store';

// Increment this to trigger a sidebar refresh
export const conversationRefreshTick = writable(0);

export function refreshConversations() {
    conversationRefreshTick.update(n => n + 1);
}
