<script lang="ts">
    import { app } from '$lib/state/app.svelte';
    import { IconCode, IconX, IconDownload, IconPhoto, IconTable } from '@tabler/icons-svelte';
    import { marked } from 'marked';
    import { browser } from '$app/environment';

    let DOMPurify: any = null;
    if (browser) {
        import('dompurify').then(module => {
            DOMPurify = module.default;
        });
    }

    function renderMd(text: string): string {
        if (!text) return '';
        const html = marked.parse(text) as string;
        if (browser && DOMPurify) {
            return DOMPurify.sanitize(html);
        }
        return html;
    }

    let activeTabId = $state('overview');
    let openTabs = $state<string[]>([]);

    function openArtifactTab(id: string) {
        if (!openTabs.includes(id)) {
            openTabs.push(id);
        }
        activeTabId = id;
    }

    function closeArtifactTab(id: string, event: Event) {
        event.stopPropagation();
        openTabs = openTabs.filter(t => t !== id);
        if (activeTabId === id) {
            activeTabId = 'overview';
        }
    }
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

    <!-- Tab Bar -->
    <div class="flex items-center overflow-x-auto border-b border-border bg-surface-elevated shrink-0 scrollbar-hide">
        <!-- Overview Tab -->
        <button 
            class="px-4 py-2 text-[13px] font-medium border-r border-border transition-colors flex items-center gap-2 {activeTabId === 'overview' ? 'bg-canvas text-text-primary' : 'text-muted hover:bg-surface'}"
            onclick={() => activeTabId = 'overview'}
        >
            <IconTable size={14} />
            Overview
        </button>
        
        <!-- Artifact Tabs -->
        {#each openTabs as tabId}
            {@const artifact = app.activeArtifacts.find(a => a.id === tabId)}
            {#if artifact}
                <div class="flex items-center border-r border-border group {activeTabId === tabId ? 'bg-canvas' : 'bg-surface-elevated hover:bg-surface'}">
                    <button 
                        class="pl-4 pr-2 py-2 text-[13px] font-medium transition-colors flex items-center gap-2 {activeTabId === tabId ? 'text-text-primary' : 'text-muted'}"
                        onclick={() => activeTabId = tabId}
                    >
                        <IconPhoto size={14} />
                        <span class="truncate max-w-[120px]">{artifact.filename}</span>
                    </button>
                    <button 
                        class="pr-3 pl-1 text-muted opacity-0 group-hover:opacity-100 hover:text-text-primary transition-opacity"
                        onclick={(e) => closeArtifactTab(tabId, e)}
                        aria-label="Close tab"
                    >
                        <IconX size={14} />
                    </button>
                </div>
            {/if}
        {/each}
    </div>

    <!-- Content -->
    <div class="flex-1 overflow-y-auto bg-canvas relative">
        {#if activeTabId === 'overview'}
            <div class="p-4 flex flex-col gap-2">
                {#if app.activeArtifacts.length === 0}
                    <div class="h-full flex flex-col items-center justify-center text-center p-6 mt-10">
                        <div class="w-12 h-12 rounded-full bg-surface-elevated flex items-center justify-center mb-4 text-muted">
                            <IconCode size={24} stroke={1.5} />
                        </div>
                        <h3 class="text-text-primary font-medium text-[14.5px] mb-1">No Artifact Active</h3>
                        <p class="text-text-secondary text-[13px] max-w-[240px] leading-relaxed">
                            When the assistant generates code, UI components, or documents, they will appear here.
                        </p>
                    </div>
                {:else}
                    <div class="text-[12px] font-medium text-muted uppercase tracking-wider mb-2 px-1">Files</div>
                    {#each app.activeArtifacts as artifact}
                        <button 
                            class="w-full text-left flex items-center justify-between p-3 rounded-lg border border-border bg-surface hover:bg-surface-hover transition-colors group"
                            onclick={() => openArtifactTab(artifact.id)}
                        >
                            <div class="flex items-center gap-3 overflow-hidden">
                                <div class="w-8 h-8 rounded bg-surface-elevated flex items-center justify-center shrink-0 text-blue-500">
                                    <IconPhoto size={16} />
                                </div>
                                <div class="flex flex-col truncate">
                                    <span class="text-[13px] font-medium text-text-primary truncate">{artifact.filename}</span>
                                    <span class="text-[11.5px] text-muted">{(artifact.file_size / 1024).toFixed(1)} KB</span>
                                </div>
                            </div>
                            <div class="text-muted opacity-0 group-hover:opacity-100 transition-opacity">
                                <IconCode size={16} />
                            </div>
                        </button>
                    {/each}
                {/if}
            </div>
        {:else}
            <!-- Detail View -->
            {@const activeArtifact = app.activeArtifacts.find(a => a.id === activeTabId)}
            {#if activeArtifact}
                <div class="absolute inset-0 flex flex-col">
                    <div class="flex items-center justify-between px-4 py-3 border-b border-border bg-surface">
                        <div class="flex flex-col">
                            <span class="text-[13px] font-medium text-text-primary">{activeArtifact.filename}</span>
                            <span class="text-[11.5px] text-muted">{new Date(activeArtifact.created_at).toLocaleString()}</span>
                        </div>
                        <a 
                            href={activeArtifact.url}
                            download={activeArtifact.filename}
                            class="btn btn-secondary !px-3 !py-1.5 !text-[12.5px] gap-2"
                            title="Download Artifact"
                            target="_blank"
                            rel="noopener noreferrer"
                        >
                            <IconDownload size={14} stroke={1.5} />
                            <span>Download</span>
                        </a>
                    </div>
                    <div class="flex-1 overflow-auto p-6 flex flex-col bg-canvas items-center">
                        {#if activeArtifact.mime_type.startsWith('image/')}
                            <img src={activeArtifact.url} alt={activeArtifact.filename} class="max-w-full rounded-md shadow-sm border border-border-subtle" />
                        {:else if activeArtifact.mime_type === 'text/markdown'}
                            <div class="w-full max-w-[800px] prose-agent">
                                {#await fetch(activeArtifact.url).then(r => r.text())}
                                    <div class="flex items-center gap-2 text-muted justify-center py-10">
                                        <span class="w-4 h-4 rounded-full border-2 border-muted border-t-transparent animate-spin"></span>
                                        <span class="text-[13px]">Loading content...</span>
                                    </div>
                                {:then text}
                                    {@html renderMd(text)}
                                {:catch error}
                                    <div class="text-danger">Failed to load content.</div>
                                {/await}
                            </div>
                        {:else}
                            <div class="text-text-secondary text-[13px] flex items-center justify-center gap-2 mt-10">
                                <IconCode size={16} />
                                <span>{activeArtifact.mime_type} preview not supported yet.</span>
                            </div>
                        {/if}
                    </div>
                </div>
            {/if}
        {/if}
    </div>
</aside>

<style>
    .artifact-panel {
        width: 100%;
        height: 100%;
    }
    .scrollbar-hide::-webkit-scrollbar {
        display: none;
    }
    .scrollbar-hide {
        -ms-overflow-style: none;
        scrollbar-width: none;
    }
</style>
