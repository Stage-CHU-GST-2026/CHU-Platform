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
    class="group relative btn w-full !justify-start !rounded-[10px] !py-[10px] !px-3 mb-[2px] overflow-hidden !font-medium {isActive
        ? 'btn-secondary'
        : 'btn-ghost border border-transparent !shadow-none'}"
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
