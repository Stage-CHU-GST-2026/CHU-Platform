<script lang="ts">
    import { type Snippet } from 'svelte';

    interface Props {
        title: string;
        subtitle?: string;
        children?: Snippet;
        class?: string;
    }

    let { title, subtitle, children, class: className = '' } = $props();
</script>

<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6 {className}">
    <div>
        <h1 class="text-[24px] font-semibold tracking-tight text-text-primary">{title}</h1>
        {#if subtitle}
            <p class="text-[14px] text-text-secondary mt-1">{subtitle}</p>
        {/if}
    </div>
    
    {#if children}
        <div class="flex items-center gap-3 shrink-0">
            {@render children()}
        </div>
    {/if}
</div>
