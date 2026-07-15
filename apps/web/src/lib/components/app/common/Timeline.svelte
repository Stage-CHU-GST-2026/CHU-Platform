<script lang="ts">
    import type { Component } from 'svelte';
    import {  } from '@tabler/icons-svelte';

    export interface TimelineEvent {
        id: string;
        title: string;
        description?: string;
        timestamp: string;
        icon?: Component<any>;
        type?: 'info' | 'success' | 'warning' | 'error';
    }

    interface Props {
        events: TimelineEvent[];
        class?: string;
    }

    let { events, class: className = '' } = $props();

    const colors = {
        info: 'text-accent border-accent bg-accent/10',
        success: 'text-success border-success bg-success/10',
        warning: 'text-warning border-warning bg-warning/10',
        error: 'text-danger border-danger bg-danger/10'
    };
</script>

<div class="relative pl-3 {className}">
    <div class="absolute top-2 bottom-2 left-[15px] w-px bg-border"></div>
    
    <div class="flex flex-col gap-6">
        {#each events as event}
            {@const color = colors[event.type || 'info']}
            <div class="relative flex gap-4">
                <div class="relative z-10 shrink-0 w-6 h-6 rounded-full flex items-center justify-center {color} bg-canvas">
                    {#if event.icon}
                        <event.icon size={12} />
                    {:else}
                        <div class="w-2 h-2 rounded-full bg-current"></div>
                    {/if}
                </div>
                
                <div class="flex flex-col pt-0.5">
                    <div class="flex items-baseline gap-2">
                        <span class="text-[13px] font-medium text-text-primary">{event.title}</span>
                        <span class="text-[11px] text-muted">{event.timestamp}</span>
                    </div>
                    {#if event.description}
                        <p class="text-[12px] text-text-secondary mt-1">{event.description}</p>
                    {/if}
                </div>
            </div>
        {/each}
    </div>
</div>
