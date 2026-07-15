<script lang="ts">
    import { app } from '$lib/state/app.svelte';
    import Sidebar from './Sidebar.svelte';
    import TopBar from './TopBar.svelte';
    import CommandPalette from '../CommandPalette.svelte';
    import Toast from '../common/Toast.svelte';

    let { children } = $props();
</script>

<div
    class="app-shell"
    style="--sidebar-current-width: {app.sidebarWidth};"
>
    <Sidebar />
    <TopBar />
    <main class="main-content">
        {@render children()}
    </main>
</div>

<CommandPalette />
<Toast />

<style>
    .app-shell {
        display: grid;
        grid-template-columns: var(--sidebar-current-width) 1fr;
        grid-template-rows: var(--topbar-height) 1fr;
        grid-template-areas:
            'sidebar topbar'
            'sidebar content';
        min-height: 100vh;
        width: 100%;
        background-color: var(--color-bg);
        transition: grid-template-columns var(--transition-slow);
    }

    .main-content {
        grid-area: content;
        overflow-y: auto;
        position: relative;
    }
</style>
