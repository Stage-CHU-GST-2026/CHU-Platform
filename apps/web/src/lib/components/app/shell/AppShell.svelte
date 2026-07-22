<script lang="ts">
    import { app } from '$lib/state/app.svelte';
    import { PaneGroup, Pane, PaneResizer } from 'paneforge';
    import Sidebar from './Sidebar.svelte';
    import TopBar from './TopBar.svelte';
    import ArtifactPanel from './ArtifactPanel.svelte';
    import CommandPalette from '../CommandPalette.svelte';
    import Toast from '../common/Toast.svelte';
    import { onMount } from 'svelte';
    import { page } from '$app/stores';

    let { children } = $props();
    let mounted = $state(false);

    let isConversation = $derived($page.url.pathname.startsWith('/dashboard/conversation'));
    let showArtifacts = $derived(app.artifactOpen && isConversation);

    onMount(() => {
        mounted = true;
    });
</script>

<div class="h-screen w-full flex flex-row bg-bg overflow-hidden text-text-primary transition-opacity duration-200" style="opacity: {mounted ? 1 : 0};">
    {#if !app.sidebarCollapsed}
        <div class="w-[260px] shrink-0 h-full bg-bg overflow-hidden">
            <Sidebar />
        </div>
    {/if}

    <!-- Content area with padding — top, left, right only, flush to bottom -->
    <div class="flex-1 flex flex-col min-w-0 pt-3 pr-3 pl-0 overflow-hidden">
        <div class="flex-1 bg-canvas border border-border rounded-t-2xl shadow-sm flex flex-col overflow-hidden">
            <PaneGroup direction="horizontal" autoSaveId="app-layout">
                <Pane defaultSize={showArtifacts ? 52 : 100}>
                    <div class="flex flex-col h-full w-full relative">
                        <TopBar />
                        <main class="flex-1 overflow-y-auto relative bg-transparent">
                            {@render children()}
                        </main>
                    </div>
                </Pane>

                {#if showArtifacts}
                    <PaneResizer class="resizer" />
                    <Pane defaultSize={48} minSize={20} maxSize={60}>
                        <ArtifactPanel />
                    </Pane>
                {/if}
            </PaneGroup>
        </div>
    </div>
</div>

<CommandPalette />
<Toast />
