<script lang="ts">
    import { app } from '$lib/state/app.svelte';
    import { page } from '$app/stores';
    import SidebarItem from './SidebarItem.svelte';
    import SidebarSection from './SidebarSection.svelte';
    
    import { IconPlus, IconBuildingHospital, IconLayoutSidebarLeftExpand, IconLayoutSidebarLeftCollapse, IconLayoutDashboard, IconRobot, IconMessages, IconDatabase, IconBooks, IconReportAnalytics, IconChartBar, IconSettings, IconSun, IconMoon } from '@tabler/icons-svelte';
    const currentPath = $derived($page.url.pathname);
</script>

<aside class="sidebar bg-sidebar border-r border-border flex flex-col z-[var(--z-sidebar)]">
    <!-- Header -->
    <div class="py-3 px-3 shrink-0 transition-all border-b border-border-subtle">
        <button class="w-full flex items-center h-6 px-2 rounded-md transition-all text-text-secondary cursor-pointer border border-border-subtle hover:bg-surface-hover hover:text-text-primary" class:justify-center={app.sidebarCollapsed}>
            <IconPlus size={16} stroke={2} class={app.sidebarCollapsed ? '' : 'mr-2'} />
            {#if !app.sidebarCollapsed}
                <span class="text-[13px] font-medium whitespace-nowrap">New Dashboard</span>
            {/if}
        </button>
    </div>

    <!-- Nav -->
    <nav class="flex-1 overflow-y-auto py-3 px-3 flex flex-col gap-0.5" role="navigation" aria-label="Main navigation">
        <SidebarItem href="/dashboard" icon={IconLayoutDashboard} label="Dashboard" {currentPath} />

        <!-- Other links have been removed/commented out for now until they are built -->
        <!--
        <SidebarSection label="Workspace">
            <SidebarItem href="/agents" icon={IconRobot} label="AI Agents" badge={8} {currentPath} />
            <SidebarItem href="/conversations" icon={IconMessages} label="Conversations" badge={47} {currentPath} />
            <SidebarItem href="/datasets" icon={IconDatabase} label="Datasets" badge={134} {currentPath} />
        </SidebarSection>
        -->
    </nav>

    <!-- Footer -->
    <div class="p-3 flex flex-col gap-1 shrink-0">
        <!-- <SidebarItem href="/settings" icon={IconSettings} label="Settings" {currentPath} /> -->
        
        <button
            class="group flex items-center h-6 px-2 rounded-md transition-all text-text-secondary cursor-pointer relative w-full hover:bg-surface-hover hover:text-text-primary"
            onclick={() => app.toggleTheme()}
            aria-label="Toggle theme"
        >
            <div class="flex items-center justify-center shrink-0 w-5 h-5">
                {#if app.theme === 'dark'}
                    <IconSun size={16} />
                {:else}
                    <IconMoon size={16} />
                {/if}
            </div>
            {#if !app.sidebarCollapsed}
                <span class="ml-3 text-[13px] font-medium whitespace-nowrap overflow-hidden truncate">{app.theme === 'dark' ? 'Light Mode' : 'Dark Mode'}</span>
            {/if}
        </button>
    </div>
</aside>

<style>
    .sidebar {
        grid-area: sidebar;
        height: 100vh;
        overflow: hidden;
        transition: width var(--transition-slow);
    }
</style>
