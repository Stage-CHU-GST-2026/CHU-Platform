<script lang="ts">
    import { app } from '$lib/state/app.svelte';

    interface Props {
        label: string;
        children: import('svelte').Snippet;
    }

    let { label, children } = $props();
</script>

<div class="mt-4 mb-1">
    {#if !app.sidebarCollapsed}
        <div class="px-3 mb-2 text-[11px] font-semibold uppercase tracking-wider text-muted select-none truncate transition-opacity duration-200">
            {label}
        </div>
    {:else}
        <div class="h-[2px] w-4 mx-auto mb-2 bg-border rounded-full opacity-50"></div>
    {/if}
    <div class="flex flex-col gap-1">
        {@render children()}
    </div>
</div>
