<script lang="ts">
    import type { Component, Snippet } from 'svelte';

    interface Props {
        icon: Component<any>;
        title: string;
        description: string;
        children?: Snippet;
        class?: string;
    }

    let { icon: Icon, title, description, children, class: className = '' } = $props();
</script>

<div class="flex flex-col items-center justify-center text-center p-8 rounded-lg border border-dashed border-border bg-surface {className}">
    <div class="w-12 h-12 rounded-full bg-surface-elevated border border-border flex items-center justify-center text-muted mb-4">
        <Icon size={24} />
    </div>
    
    <h3 class="text-[14px] font-semibold text-text-primary mb-1">{title}</h3>
    <p class="text-[13px] text-text-secondary max-w-sm mx-auto mb-6">{description}</p>
    
    {#if children}
        <div class="flex items-center gap-3">
            {@render children()}
        </div>
    {/if}
</div>
