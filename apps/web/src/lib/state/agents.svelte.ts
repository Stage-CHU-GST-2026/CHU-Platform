import type { Agent, AgentStatus } from '$lib/types';
import { mockAgents } from '$lib/mock';

class AgentsState {
    all = $state<Agent[]>(mockAgents);
    searchQuery = $state('');
    statusFilter = $state<AgentStatus | 'all'>('all');
    viewMode = $state<'grid' | 'list'>('grid');
    selected = $state<Agent | null>(null);

    get filtered(): Agent[] {
        return this.all.filter(
            (a) =>
                (this.statusFilter === 'all' || a.status === this.statusFilter) &&
                (!this.searchQuery || a.name.toLowerCase().includes(this.searchQuery.toLowerCase()))
        );
    }

    get grouped(): Record<string, Agent[]> {
        return this.filtered.reduce(
            (acc, a) => {
                (acc[a.category] ??= []).push(a);
                return acc;
            },
            {} as Record<string, Agent[]>
        );
    }
}

export const agents = new AgentsState();
