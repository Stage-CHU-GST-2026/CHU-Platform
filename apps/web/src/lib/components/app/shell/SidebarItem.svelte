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

    let { href, icon: Icon, label, badge, currentPath } = $props();

    let isActive = $derived(
        href === '/dashboard' ? currentPath === '/dashboard' : currentPath.startsWith(href)
    );
</script>

<a
    {href}
    class="group relative flex items-center h-6 px-2 rounded-md transition-all text-text-secondary cursor-pointer w-full overflow-hidden hover:bg-surface-hover hover:text-text-primary {isActive ? '!bg-surface !text-text-primary shadow-sm border border-border-subtle' : ''}"
    aria-current={isActive ? 'page' : undefined}
    aria-label={app.sidebarCollapsed ? label : undefined}
    title={app.sidebarCollapsed ? label : undefined}
>
    <div class="flex items-center justify-center shrink-0 w-5 h-5 transition-colors {isActive ? 'text-text-primary' : ''}">
        <Icon size={16} stroke={isActive ? 2 : 1.5} />
    </div>
    
    {#if !app.sidebarCollapsed}
        <span class="ml-2.5 text-[13px] font-medium whitespace-nowrap overflow-hidden text-ellipsis transition-opacity duration-200">{label}</span>
        
        {#if isActive}
            <div class="ml-auto w-[6px] h-[6px] rounded-full bg-accent"></div>
        {:else if badge !== undefined}
            <span class="ml-auto text-[10px] font-semibold bg-surface border border-border px-1.5 py-0.5 rounded-full min-w-[20px] text-center">
                {badge > 99 ? '99+' : badge}
            </span>
        {/if}
    {:else if badge !== undefined}
        <div class="absolute top-1 right-1 w-[6px] h-[6px] rounded-full bg-accent"></div>
    {/if}
</a>
