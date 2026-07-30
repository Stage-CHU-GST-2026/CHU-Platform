<script lang="ts">
    import { app } from '$lib/state/app.svelte';
    import { 
        IconSettings, 
        IconPalette, 
        IconBrain, 
        IconShieldLock,
        IconCheck,
        IconPlus,
        IconTrash,
        IconDownload,
        IconKey,
        IconTag,
        IconChevronRight
    } from '@tabler/icons-svelte';

    let activeTab = $state('appearance');

    const tabs = [
        { id: 'general', label: 'General', icon: IconSettings },
        { id: 'appearance', label: 'Appearance', icon: IconPalette },
        { id: 'ai-models', label: 'AI & Models', icon: IconBrain },
        { id: 'semantics', label: 'Semantic Categories', icon: IconTag },
        { id: 'privacy', label: 'Data & Privacy', icon: IconShieldLock },
    ];
</script>

<svelte:head>
	<title>Settings | CHU Platform</title>
	<meta name="description" content="Configure your CHU Platform preferences, models, and account settings." />
</svelte:head>

<div class="w-full max-w-[1024px] mx-auto px-6 py-10 md:py-16 grid grid-cols-1 md:grid-cols-[220px_1fr] gap-12 md:gap-24 items-start">
    
    <!-- Sidebar Navigation -->
    <aside class="flex flex-col gap-8 w-full sticky top-16">
        <h1 class="text-[22px] font-semibold tracking-[-0.02em] text-text-primary px-3">Settings</h1>
        
        <nav class="flex flex-col gap-1">
            {#each tabs as tab}
                <button 
                    class="flex items-center gap-3 px-3 py-2 rounded-md text-[13.5px] font-medium transition-colors w-full text-left {activeTab === tab.id ? 'text-text-primary bg-surface/60' : 'text-text-secondary hover:text-text-primary hover:bg-surface/40'}"
                    onclick={() => activeTab = tab.id}
                >
                    <tab.icon size={16} stroke={1.5} class={activeTab === tab.id ? 'text-text-primary' : 'text-muted'} />
                    {tab.label}
                </button>
            {/each}
        </nav>
    </aside>

    <!-- Content Area -->
    <main class="w-full max-w-[560px] pb-24 min-h-[60vh]">
        
        {#if activeTab === 'appearance'}
            <div class="animate-in fade-in slide-in-from-bottom-2 duration-500 ease-out flex flex-col">
                <div class="border-b border-border-subtle pb-6 mb-10">
                    <h2 class="text-[18px] font-semibold tracking-tight text-text-primary mb-1">Appearance</h2>
                    <p class="text-[13.5px] text-text-secondary">Customize the visual theme and density of your workspace.</p>
                </div>

                <!-- Theme Selection -->
                <div class="mb-12">
                    <h3 class="text-[12px] font-medium uppercase tracking-[0.05em] text-muted mb-5">Theme</h3>
                    <div class="grid grid-cols-2 md:grid-cols-3 gap-6">
                        
                        <!-- System Theme -->
                        <button class="flex flex-col gap-3 group text-left" onclick={() => app.toggleTheme()}>
                            <div class="aspect-[4/3] w-full rounded-lg border border-border-subtle bg-gradient-to-br from-gray-100 to-[#1a1a1a] flex items-center justify-center transition-colors group-hover:border-text-secondary">
                            </div>
                            <span class="text-[13px] font-medium text-text-primary">System</span>
                        </button>

                        <!-- Light Theme -->
                        <button class="flex flex-col gap-3 group text-left" onclick={() => { if(app.theme === 'dark') app.toggleTheme() }}>
                            <div class="aspect-[4/3] w-full rounded-lg border {app.theme === 'light' ? 'border-text-primary' : 'border-border-subtle group-hover:border-text-secondary'} bg-[#f4f4f5] flex flex-col gap-2 p-3 transition-colors relative">
                                <div class="w-full h-2 bg-white rounded-sm"></div>
                                <div class="w-2/3 h-2 bg-white rounded-sm"></div>
                            </div>
                            <span class="text-[13px] font-medium {app.theme === 'light' ? 'text-text-primary' : 'text-text-secondary'}">Light</span>
                        </button>

                        <!-- Dark Theme -->
                        <button class="flex flex-col gap-3 group text-left" onclick={() => { if(app.theme === 'light') app.toggleTheme() }}>
                            <div class="aspect-[4/3] w-full rounded-lg border {app.theme === 'dark' ? 'border-text-primary' : 'border-border-subtle group-hover:border-text-secondary'} bg-[#0a0a0a] flex flex-col gap-2 p-3 transition-colors relative">
                                <div class="w-full h-2 bg-[#1f1f1f] rounded-sm"></div>
                                <div class="w-2/3 h-2 bg-[#1f1f1f] rounded-sm"></div>
                            </div>
                            <span class="text-[13px] font-medium {app.theme === 'dark' ? 'text-text-primary' : 'text-text-secondary'}">Dark</span>
                        </button>
                    </div>
                </div>

                <!-- Interface Density -->
                <div>
                    <h3 class="text-[12px] font-medium uppercase tracking-[0.05em] text-muted mb-5">Interface Density</h3>
                    <div class="flex flex-col gap-1 border border-border-subtle rounded-lg overflow-hidden bg-transparent">
                        <label class="flex items-center justify-between p-4 cursor-pointer hover:bg-surface/30 transition-colors border-b border-border-subtle">
                            <div class="flex items-center gap-4">
                                <div class="flex flex-col">
                                    <span class="text-[14px] font-medium text-text-primary">Comfortable</span>
                                    <span class="text-[13px] text-muted mt-0.5">More whitespace, easier to read.</span>
                                </div>
                            </div>
                            <div class="w-4 h-4 rounded-full border border-text-secondary flex items-center justify-center">
                                <div class="w-2 h-2 rounded-full bg-text-primary"></div>
                            </div>
                        </label>
                        <label class="flex items-center justify-between p-4 cursor-pointer hover:bg-surface/30 transition-colors">
                            <div class="flex items-center gap-4">
                                <div class="flex flex-col">
                                    <span class="text-[14px] font-medium text-text-primary">Compact</span>
                                    <span class="text-[13px] text-muted mt-0.5">Fit more data on the screen at once.</span>
                                </div>
                            </div>
                            <div class="w-4 h-4 rounded-full border border-border flex items-center justify-center">
                            </div>
                        </label>
                    </div>
                </div>
            </div>

        {:else if activeTab === 'general'}
            <div class="animate-in fade-in slide-in-from-bottom-2 duration-500 ease-out flex flex-col">
                <div class="border-b border-border-subtle pb-6 mb-10">
                    <h2 class="text-[18px] font-semibold tracking-tight text-text-primary mb-1">General Settings</h2>
                    <p class="text-[13.5px] text-text-secondary">Manage your basic profile and workspace preferences.</p>
                </div>

                <div class="flex flex-col gap-8">
                    <div class="flex flex-col gap-2">
                        <label class="text-[13px] font-medium text-text-primary">Display Name</label>
                        <input type="text" class="w-full bg-transparent border-0 border-b border-border-subtle px-0 py-2 text-[15px] text-text-primary placeholder-muted focus:ring-0 focus:border-text-primary transition-colors rounded-none" value="Dr. Sarah Jenkins">
                    </div>
                    
                    <div class="flex flex-col gap-2">
                        <label class="text-[13px] font-medium text-text-primary">Email Address</label>
                        <input type="email" class="w-full bg-transparent border-0 border-b border-border-subtle px-0 py-2 text-[15px] text-text-secondary placeholder-muted focus:ring-0 transition-colors rounded-none opacity-70 cursor-not-allowed" value="sarah.jenkins@hospital.org" disabled>
                        <p class="text-[12.5px] text-muted mt-1">Contact IT support to change your primary email.</p>
                    </div>

                    <div class="pt-6 mt-4">
                        <button class="px-5 py-2 bg-text-primary text-bg rounded-md text-[13px] font-medium hover:opacity-90 transition-opacity">
                            Save Changes
                        </button>
                    </div>
                </div>
            </div>

        {:else if activeTab === 'ai-models'}
            <div class="animate-in fade-in slide-in-from-bottom-2 duration-500 ease-out flex flex-col">
                <div class="border-b border-border-subtle pb-6 mb-10">
                    <h2 class="text-[18px] font-semibold tracking-tight text-text-primary mb-1">AI & Models</h2>
                    <p class="text-[13.5px] text-text-secondary">Configure the reasoning engines powering your workspace.</p>
                </div>

                <!-- Default Model -->
                <div class="mb-12">
                    <h3 class="text-[12px] font-medium uppercase tracking-[0.05em] text-muted mb-5">Default Model</h3>
                    <div class="flex items-center justify-between py-2">
                        <div class="flex items-center gap-4">
                            <div class="flex flex-col">
                                <span class="text-[14px] font-medium text-text-primary">Gemini 3.1 Pro</span>
                                <span class="text-[13px] text-muted mt-0.5">High intelligence, best for complex analysis.</span>
                            </div>
                        </div>
                        <button class="text-[13px] font-medium text-text-secondary hover:text-text-primary transition-colors underline decoration-border hover:decoration-text-secondary underline-offset-4">
                            Change
                        </button>
                    </div>
                </div>

                <!-- API Keys -->
                <div>
                    <div class="flex items-center justify-between mb-5">
                        <h3 class="text-[12px] font-medium uppercase tracking-[0.05em] text-muted">Provider Keys</h3>
                        <button class="flex items-center gap-1.5 text-[13px] font-medium text-text-primary hover:opacity-70 transition-opacity">
                            <IconPlus size={14} stroke={1.5} />
                            Add Key
                        </button>
                    </div>
                    
                    <div class="flex flex-col border-y border-border-subtle divide-y divide-border-subtle">
                        <div class="py-4 flex items-center justify-between group">
                            <div class="flex items-center gap-3">
                                <IconKey size={16} stroke={1.5} class="text-text-secondary" />
                                <span class="text-[14px] text-text-primary">OpenAI API</span>
                            </div>
                            <div class="flex items-center gap-6">
                                <span class="text-[13.5px] text-muted">sk-proj-...8f92</span>
                                <button class="text-muted hover:text-danger transition-colors opacity-0 group-hover:opacity-100" aria-label="Delete key">
                                    <IconTrash size={16} stroke={1.5} />
                                </button>
                            </div>
                        </div>
                        
                        <div class="py-4 flex items-center justify-between group">
                            <div class="flex items-center gap-3">
                                <IconKey size={16} stroke={1.5} class="text-text-secondary" />
                                <span class="text-[14px] text-text-primary">Anthropic API</span>
                            </div>
                            <div class="flex items-center gap-6">
                                <span class="text-[13.5px] text-muted">sk-ant-...b1c2</span>
                                <button class="text-muted hover:text-danger transition-colors opacity-0 group-hover:opacity-100" aria-label="Delete key">
                                    <IconTrash size={16} stroke={1.5} />
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

        {:else if activeTab === 'semantics'}
            <div class="animate-in fade-in slide-in-from-bottom-2 duration-500 ease-out flex flex-col">
                <div class="border-b border-border-subtle pb-6 mb-10">
                    <h2 class="text-[18px] font-semibold tracking-tight text-text-primary mb-1">Semantic Categories</h2>
                    <p class="text-[13.5px] text-text-secondary">Configure domain classification buckets used in dataset column mappings.</p>
                </div>

                <div class="flex flex-col gap-6 p-6 border border-border-subtle rounded-xl bg-surface/30">
                    <div class="flex items-center justify-between">
                        <div class="flex items-center gap-3">
                            <div class="p-2 rounded-lg bg-surface-elevated text-accent">
                                <IconTag size={20} />
                            </div>
                            <div>
                                <h3 class="text-[14px] font-medium text-text-primary">Manage Categories</h3>
                                <p class="text-[12.5px] text-muted">Create, edit, or remove domain classification categories stored in the database.</p>
                            </div>
                        </div>
                        <a 
                            href="/dashboard/settings/semantic-categories" 
                            class="inline-flex items-center gap-2 px-4 py-2 rounded-md bg-text-primary text-bg text-[13px] font-medium hover:opacity-90 transition-opacity"
                        >
                            Open Category Manager
                            <IconChevronRight size={14} />
                        </a>
                    </div>
                </div>
            </div>

        {:else if activeTab === 'privacy'}
            <div class="animate-in fade-in slide-in-from-bottom-2 duration-500 ease-out flex flex-col">
                <div class="border-b border-border-subtle pb-6 mb-10">
                    <h2 class="text-[18px] font-semibold tracking-tight text-text-primary mb-1">Data & Privacy</h2>
                    <p class="text-[13.5px] text-text-secondary">Manage your local storage and export your workspace data.</p>
                </div>

                <div class="flex flex-col gap-10">
                    <!-- Export -->
                    <div class="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
                        <div class="flex flex-col gap-1 pr-4 max-w-[340px]">
                            <span class="text-[14px] font-medium text-text-primary">Export Workspace Data</span>
                            <span class="text-[13px] text-muted leading-relaxed">Download a JSON archive containing all your conversations, artifacts, and local preferences.</span>
                        </div>
                        <button class="shrink-0 flex items-center justify-center gap-2 px-4 py-2 rounded-md border border-border-subtle bg-transparent text-[13px] font-medium text-text-primary hover:bg-surface/30 transition-colors">
                            <IconDownload size={16} stroke={1.5} />
                            Export Data
                        </button>
                    </div>

                    <!-- Clear Data -->
                    <div class="flex flex-col sm:flex-row sm:items-start justify-between gap-4 pt-10 border-t border-border-subtle">
                        <div class="flex flex-col gap-1 pr-4 max-w-[340px]">
                            <span class="text-[14px] font-medium text-danger">Clear All Data</span>
                            <span class="text-[13px] text-muted leading-relaxed">Permanently delete all local conversations and settings. This action cannot be undone.</span>
                        </div>
                        <button class="shrink-0 px-4 py-2 rounded-md bg-danger/10 text-danger text-[13px] font-medium hover:bg-danger/20 transition-colors">
                            Delete Data
                        </button>
                    </div>
                </div>
            </div>
        {/if}

    </main>
</div>
