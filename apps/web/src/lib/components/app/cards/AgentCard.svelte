<script lang="ts">
    import type { Agent } from '$lib/types';
    import Card from './Card.svelte';
    import StatusBadge from '../common/StatusBadge.svelte';
    import ProgressIndicator from '../common/ProgressIndicator.svelte';
    import Button from '../common/Button.svelte';
    import * as Icons from '@tabler/icons-svelte';

    interface Props {
        agent: Agent;
        class?: string;
    }

    let { agent, class: className = '' } = $props();

    // Safely map icon string to actual component function with fallback to IconRobot
    let Icon = $derived.by(() => {
        const candidate = (Icons as Record<string, any>)[agent.icon];
        return typeof candidate === 'function' ? candidate : Icons.IconRobot;
    });
</script>

<Card hoverable class={className}>
    <div class="flex items-start gap-4 mb-4">
        <div class="w-11 h-11 rounded-lg bg-surface-elevated border border-border flex items-center justify-center text-accent shrink-0">
            <Icon size={24} />
        </div>
        
        <div class="flex-1 min-w-0">
            <div class="flex items-start justify-between gap-2">
                <h3 class="text-[14px] font-semibold text-text-primary truncate">{agent.name}</h3>
                <StatusBadge status={agent.status} class="shrink-0" />
            </div>
            <p class="text-[12px] text-text-secondary line-clamp-2 mt-1">{agent.description}</p>
        </div>
    </div>
    
    <div class="mb-4">
        <div class="text-[11px] font-semibold text-text-secondary uppercase tracking-wider mb-2">Capabilities</div>
        <div class="flex flex-wrap gap-1.5">
            {#each agent.capabilities.slice(0, 3) as cap}
                <span class="px-2 py-0.5 rounded-full bg-surface-elevated border border-border text-[11px] text-text-primary">
                    {cap}
                </span>
            {/each}
            {#if agent.capabilities.length > 3}
                <span class="px-2 py-0.5 rounded-full bg-surface-elevated border border-border text-[11px] text-text-secondary">
                    +{agent.capabilities.length - 3}
                </span>
            {/if}
        </div>
    </div>
    
    <div class="mb-5">
        <div class="flex justify-between items-center text-[11px] mb-1.5">
            <span class="font-medium text-text-secondary">Workload</span>
            <span class="text-text-primary tabular-nums">{agent.workload}%</span>
        </div>
        <ProgressIndicator value={agent.workload} showValue={false} barClass={agent.workload > 85 ? 'bg-warning' : 'bg-accent'} />
        
        <div class="flex justify-between items-center text-[11px] text-text-secondary mt-2">
            <span>Queue: {agent.queue} tasks</span>
            <span>Avg: {agent.avgExecutionTime}</span>
        </div>
    </div>
    
    <div class="flex items-center justify-between pt-4 border-t border-border">
        <span class="text-[11px] text-muted">Run: {agent.lastRun}</span>
        <div class="flex items-center gap-2">
            <Button variant="ghost" size="sm">Configure</Button>
            <Button variant="primary" size="sm">Run</Button>
        </div>
    </div>
</Card>
