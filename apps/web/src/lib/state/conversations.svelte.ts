import type { Conversation, Message } from '$lib/types';
import { mockConversations } from '$lib/mock';

class ConversationsState {
    all = $state<Conversation[]>(mockConversations);
    activeId = $state<string | null>(null);
    streaming = $state(false);
    artifactPanel = $state<'open' | 'closed'>('open');
    artifactTab = $state<'output' | 'sources' | 'code' | 'files'>('output');
    searchQuery = $state('');
    pinned = $state<string[]>(['c1']);
    /** Incremented to signal the sidebar to refresh its conversation list */
    refreshTick = $state(0);

    get active(): Conversation | null {
        return this.all.find((c) => c.id === this.activeId) ?? null;
    }

    get messages(): Message[] {
        return this.active?.messages ?? [];
    }

    get pinnedConversations(): Conversation[] {
        return this.all.filter((c) => this.pinned.includes(c.id));
    }

    pin(id: string) {
        this.pinned = [...new Set([...this.pinned, id])];
    }

    unpin(id: string) {
        this.pinned = this.pinned.filter((p) => p !== id);
    }

    refresh() {
        this.refreshTick++;
    }

    async send(content: string): Promise<void> {
        if (!this.activeId) return;

        this.streaming = true;
        const c = this.active;
        if (c) {
            c.messages.push({
                id: crypto.randomUUID(),
                role: 'user',
                content,
                timestamp: new Date().toISOString()
            });

            // Simulate stream
            setTimeout(() => {
                c.messages.push({
                    id: crypto.randomUUID(),
                    role: 'assistant',
                    content: 'This is a simulated response.',
                    timestamp: new Date().toISOString()
                });
                this.streaming = false;
            }, 1000);
        }
    }
}

export const convo = new ConversationsState();
