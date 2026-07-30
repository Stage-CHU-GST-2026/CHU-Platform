<script lang="ts">
    import { app } from '$lib/state/app.svelte';
    import { IconCode, IconX, IconDownload, IconPhoto, IconTable, IconCircleCheck, IconFileDescription } from '@tabler/icons-svelte';
    import { marked } from 'marked';
    import { browser } from '$app/environment';
    import { PLAN_MIME_TYPE } from '$lib/api/chat';
    import type { PlanData } from '$lib/api/chat';

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

    function openArtifactTab(id: string) {
        if (!app.openArtifactTabs.includes(id)) {
            app.openArtifactTabs = [...app.openArtifactTabs, id];
        }
        app.activeArtifactTabId = id;
    }

    function closeArtifactTab(id: string, event: Event) {
        event.stopPropagation();
        app.openArtifactTabs = app.openArtifactTabs.filter(t => t !== id);
        if (app.activeArtifactTabId === id) {
            app.activeArtifactTabId = 'overview';
        }
    }

    // Derived groupings for the overview — excludes .json, groups by type
    let artifactGroups = $derived.by(() => {
        const filtered = app.activeArtifacts.filter(
            a => !a.filename.endsWith('.json')
        );

        const groups: { label: string; icon: any; items: typeof filtered }[] = [];

        const docs = filtered.filter(a => a.mime_type === 'text/markdown' || a.filename.endsWith('.md'));
        const images = filtered.filter(a => a.mime_type.startsWith('image/'));
        const other = filtered.filter(a =>
            !a.mime_type.startsWith('image/') &&
            !(a.mime_type === 'text/markdown' || a.filename.endsWith('.md'))
        );

        if (docs.length) groups.push({ label: 'Documents', icon: IconFileDescription, items: docs });
        if (images.length) groups.push({ label: 'Images', icon: IconPhoto, items: images });
        if (other.length) groups.push({ label: 'Other', icon: IconCode, items: other });

        return groups;
    });

    let hasVisibleArtifacts = $derived(artifactGroups.some(g => g.items.length > 0));

</script>

<aside class="artifact-panel border-l border-border bg-canvas flex flex-col z-[var(--z-sidebar)] overflow-hidden">
    <!-- Header -->
    <div class="h-[var(--topbar-height)] shrink-0 border-b border-border flex items-center justify-between px-4">
        <div class="flex items-center gap-2 text-text-secondary font-medium text-[13px]">
            <IconCode size={16} stroke={1.5} />
            <span>Artifacts</span>
        </div>
        <button
            class="w-8 h-8 rounded flex items-center justify-center text-muted hover:text-text-primary hover:bg-surface transition-colors cursor-pointer"
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
            class="px-4 py-2 text-[13px] font-medium border-r border-border transition-colors flex items-center gap-2 cursor-pointer {app.activeArtifactTabId === 'overview' ? 'bg-canvas text-text-primary' : 'text-muted hover:bg-surface'}"
            onclick={() => app.activeArtifactTabId = 'overview'}
        >
            <IconTable size={14} />
            Overview
        </button>
        
        <!-- Artifact Tabs -->
        {#each app.openArtifactTabs as tabId}
            {@const artifact = app.activeArtifacts.find(a => a.id === tabId)}
            {#if artifact}
                <div class="flex items-center border-r border-border group {app.activeArtifactTabId === tabId ? 'bg-canvas' : 'bg-surface-elevated hover:bg-surface'}">
                    <button 
                        class="pl-4 pr-2 py-2 text-[13px] font-medium transition-colors flex items-center gap-2 {app.activeArtifactTabId === tabId ? 'text-text-primary' : 'text-muted'}"
                        onclick={() => app.activeArtifactTabId = tabId}
                    >
                        <IconPhoto size={14} />
                        <span class="truncate max-w-[120px]">{artifact.filename}</span>
                    </button>
                    <button 
                        class="pr-3 pl-1 text-muted opacity-0 group-hover:opacity-100 hover:text-text-primary transition-opacity cursor-pointer"
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
        {#if app.activeArtifactTabId === 'overview'}
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
                            class="w-full text-left flex items-center justify-between p-3 rounded-lg border border-border bg-surface hover:bg-surface-hover transition-colors group cursor-pointer"
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
            {@const activeArtifact = app.activeArtifacts.find(a => a.id === app.activeArtifactTabId)}
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
                            class="inline-flex items-center justify-center gap-2 text-[12.5px] font-medium cursor-pointer transition-colors duration-150 bg-surface text-text-primary border border-border hover:bg-surface-hover rounded-lg px-3 py-1.5"
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
                        {:else if activeArtifact.mime_type === PLAN_MIME_TYPE}
                            {#await fetch(`/api/v1/artifacts/${encodeURIComponent(activeArtifact.id)}/file`).then(r => r.json())}
                                <div class="flex items-center gap-2 text-muted justify-center py-10">
                                    <span class="w-4 h-4 rounded-full border-2 border-muted border-t-transparent animate-spin"></span>
                                    <span class="text-[13px]">Loading plan...</span>
                                </div>
                            {:then plan}
                                <div class="w-full max-w-[560px] flex flex-col gap-5 py-2">
                                    <!-- Header -->
                                    <div>
                                        <p class="text-[10.5px] text-muted uppercase tracking-widest mb-1">Execution Plan</p>
                                        <h3 class="text-text-primary font-semibold text-[15px] tracking-tight leading-snug">
                                            {plan.plan_title || 'Unnamed Plan'}
                                        </h3>
                                        <p class="text-[12px] text-muted mt-1">{plan.steps?.length ?? 0} steps · completed</p>
                                    </div>

                                    <!-- Step track -->
                                    <div class="flex flex-col border-l-[1.5px] border-border-subtle pl-4 gap-0">
                                        {#each plan.steps ?? [] as step, i}
                                            <div class="flex items-start gap-3 py-3 relative">
                                                <!-- Node -->
                                                <div class="flex items-center justify-center w-[18px] shrink-0 mt-0.5 -ml-[22px] z-[1]">
                                                    <div class="w-[14px] h-[14px] rounded-full bg-success/15 flex items-center justify-center">
                                                        <IconCircleCheck size={10} stroke={2.5} class="text-success" />
                                                    </div>
                                                </div>
                                                <!-- Content -->
                                                <div class="flex-1 min-w-0">
                                                    <div class="flex items-center gap-2">
                                                        <span class="text-[13px] font-medium text-text-primary">{step.title}</span>
                                                        <span class="text-[10.5px] text-success">done</span>
                                                    </div>
                                                    <p class="text-[12px] text-text-secondary mt-0.5 leading-relaxed">{step.description}</p>
                                                </div>
                                            </div>
                                        {/each}
                                    </div>
                                </div>
                            {:catch}
                                <div class="text-danger text-[13px]">Failed to load execution plan.</div>
                            {/await}
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
