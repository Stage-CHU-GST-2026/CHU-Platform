<script lang="ts">
    import { type Snippet } from 'svelte';

    interface Props {
        padding?: 'none' | 'sm' | 'md' | 'lg';
        hoverable?: boolean;
        header?: Snippet;
        children: Snippet;
        footer?: Snippet;
        class?: string;
    }

    let { 
        padding = 'md', 
        hoverable = false, 
        header, 
        children, 
        footer, 
        class: className = '' 
    } = $props();

    const paddingClasses = {
        none: 'p-0',
        sm: 'p-3',
        md: 'p-5',
        lg: 'p-6'
    };
</script>

<div 
    class="flex flex-col bg-surface border border-border rounded-lg shadow-sm transition-all overflow-hidden {className}"
    class:hover:shadow-md={hoverable}
    class:hover:border-muted={hoverable}
>
    {#if header}
        <div class="px-5 py-4 border-b border-border shrink-0">
            {@render header()}
        </div>
    {/if}
    
    <div class="flex-1 {paddingClasses[padding]}">
        {@render children()}
    </div>
    
    {#if footer}
        <div class="px-5 py-3 border-t border-border bg-surface-elevated shrink-0">
            {@render footer()}
        </div>
    {/if}
</div>
