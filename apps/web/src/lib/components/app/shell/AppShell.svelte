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

<div class="h-screen w-full bg-bg overflow-hidden flex flex-col text-text-primary transition-opacity duration-200" style="opacity: {mounted ? 1 : 0};">
    <PaneGroup direction="horizontal" autoSaveId="app-layout">
        {#if !app.sidebarCollapsed}
            <Pane defaultSize={18} minSize={12} maxSize={30}>
                <Sidebar />
            </Pane>
            <PaneResizer class="resizer" />
        {/if}

        <Pane defaultSize={showArtifacts ? 52 : 82}>
            <div class="flex flex-col h-full w-full relative">
                <TopBar />
                <main class="flex-1 overflow-y-auto relative bg-bg">
                    {@render children()}
                </main>
            </div>
        </Pane>

        {#if showArtifacts}
            <PaneResizer class="resizer" />
            <Pane defaultSize={30} minSize={20} maxSize={50}>
                <ArtifactPanel />
            </Pane>
        {/if}
    </PaneGroup>
</div>

<CommandPalette />
<Toast />
