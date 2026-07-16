<script lang="ts">
    import { app } from '$lib/state/app.svelte';
    import { IconCode, IconX } from '@tabler/icons-svelte';
</script>

<aside class="artifact-panel border-l border-border bg-canvas flex flex-col z-[var(--z-sidebar)] overflow-hidden">
    <!-- Header -->
    <div class="h-[var(--topbar-height)] shrink-0 border-b border-border flex items-center justify-between px-4">
        <div class="flex items-center gap-2 text-text-secondary font-medium text-[13px]">
            <IconCode size={16} stroke={1.5} />
            <span>Artifacts</span>
        </div>
        <button
            class="w-6 h-6 rounded flex items-center justify-center text-muted hover:text-text-primary hover:bg-surface transition-colors"
            onclick={() => app.toggleArtifact()}
            aria-label="Close artifact panel"
        >
            <IconX size={16} stroke={1.5} />
        </button>
    </div>

    <!-- Content -->
    <div class="flex-1 overflow-y-auto p-6 flex flex-col items-center justify-center text-center">
        <div class="w-12 h-12 rounded-full bg-surface-elevated flex items-center justify-center mb-4 text-muted">
            <IconCode size={24} stroke={1.5} />
        </div>
        <h3 class="text-text-primary font-medium text-[14.5px] mb-1">No Artifact Active</h3>
        <p class="text-text-secondary text-[13px] max-w-[240px] leading-relaxed">
            When the assistant generates code, UI components, or documents, they will appear here.
        </p>
    </div>
</aside>

<style>
    .artifact-panel {
        width: 100%;
        height: 100%;
    }
</style>
