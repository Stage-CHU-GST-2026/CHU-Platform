<script lang="ts">
    import { app } from '$lib/state/app.svelte';
    import type { Component } from 'svelte';

    interface Props {
        href: string;
        icon: Component<any>;
        label: string;
        badge?: number;
        currentPath: string;
    }

    let { href, icon: Icon, label, badge = undefined, currentPath } = $props();

    let isActive = $derived(
        href === '/dashboard' ? currentPath === '/dashboard' : currentPath.startsWith(href)
    );
</script>

<a
    {href}
    class="group relative inline-flex items-center gap-2.5 text-[13.5px] font-medium cursor-pointer transition-colors duration-150 w-full rounded-lg px-3 py-2.5 mb-0.5 {isActive
        ? 'bg-surface-hover/80 text-text-primary'
        : 'text-text-secondary hover:bg-surface-hover/50 hover:text-text-primary'}"
    aria-current={isActive ? 'page' : undefined}
    aria-label={app.sidebarCollapsed ? label : undefined}
    title={app.sidebarCollapsed ? label : undefined}
>
    <div class="flex items-center justify-center shrink-0">
        <Icon size={16} stroke={1.5} class="transition-colors {isActive ? 'text-text-primary' : 'text-muted group-hover:text-text-secondary'}" />
    </div>
    
    {#if !app.sidebarCollapsed}
        <span class="flex-1 whitespace-nowrap overflow-hidden text-ellipsis">{label}</span>
        
        {#if !isActive && badge !== undefined}
            <span class="ml-auto text-[10px] font-semibold bg-surface border border-border px-1.5 py-0.5 rounded-full min-w-[20px] text-center">
                {badge > 99 ? '99+' : badge}
            </span>
        {/if}
    {:else if badge !== undefined}
        <div class="absolute top-1 right-1 w-[5px] h-[5px] rounded-full bg-accent"></div>
    {/if}
</a>
