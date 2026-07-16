<script lang="ts">
    import { app } from '$lib/state/app.svelte';
    import { 
        IconSettings, 
        IconPalette, 
        IconBrain, 
        IconShieldLock,
        IconMoon,
        IconSun,
        IconDeviceDesktop,
        IconCheck,
        IconPlus,
        IconTrash,
        IconDownload,
        IconKey
    } from '@tabler/icons-svelte';

    let activeTab = $state('appearance');

    const tabs = [
        { id: 'general', label: 'General', icon: IconSettings },
        { id: 'appearance', label: 'Appearance', icon: IconPalette },
        { id: 'ai-models', label: 'AI & Models', icon: IconBrain },
        { id: 'privacy', label: 'Data & Privacy', icon: IconShieldLock },
    ];
</script>

<div class="max-w-[840px] w-full mx-auto px-6 md:px-10 py-10 md:py-12">
    
    <!-- Header & Horizontal Navigation -->
    <div class="flex flex-col gap-6 mb-10">
        <h1 class="text-3xl font-black tracking-[-0.03em] text-text-primary ml-1">Settings</h1>
        
        <nav class="flex items-center gap-2 overflow-x-auto pb-1 scrollbar-hide border-b border-border-subtle">
            {#each tabs as tab}
                <button 
                    class="flex items-center gap-2 px-4 py-2.5 rounded-t-lg text-[13.5px] font-medium transition-all whitespace-nowrap relative {activeTab === tab.id ? 'text-text-primary' : 'text-text-secondary hover:text-text-primary hover:bg-surface-hover'}"
                    onclick={() => activeTab = tab.id}
                >
                    <tab.icon size={16} stroke={1.5} class={activeTab === tab.id ? 'text-accent' : 'text-muted'} />
                    {tab.label}
                    
                    {#if activeTab === tab.id}
                        <div class="absolute bottom-0 left-0 w-full h-[2px] bg-accent -mb-[1px]"></div>
                    {/if}
                </button>
            {/each}
        </nav>
    </div>

    <!-- Content Area -->
    <div class="w-full pb-20">
        
        {#if activeTab === 'appearance'}
            <div class="animate-in fade-in slide-in-from-bottom-2 duration-300 ease-out">
                <h2 class="text-[22px] font-bold tracking-tight text-text-primary mb-1">Appearance</h2>
                <p class="text-[14px] text-text-secondary mb-10">Customize the visual theme and density of your workspace.</p>

                <!-- Theme Selection -->
                <div class="mb-12">
                    <h3 class="text-[13px] font-bold uppercase tracking-widest text-muted mb-4">Theme</h3>
                    <div class="grid grid-cols-2 md:grid-cols-3 gap-5">
                        
                        <!-- System Theme -->
                        <button class="flex flex-col gap-3 group text-left" onclick={() => app.toggleTheme()}>
                            <div class="aspect-[4/3] rounded-xl border-2 border-border-subtle bg-gradient-to-br from-gray-100 to-[#1a1a1a] flex items-center justify-center transition-all relative overflow-hidden group-hover:border-border">
                            </div>
                            <span class="text-[13px] font-medium text-text-primary px-1">System Default</span>
                        </button>

                        <!-- Light Theme -->
                        <button class="flex flex-col gap-3 group text-left" onclick={() => { if(app.theme === 'dark') app.toggleTheme() }}>
                            <div class="aspect-[4/3] rounded-xl border-2 {app.theme === 'light' ? 'border-accent ring-4 ring-accent/10' : 'border-border-subtle group-hover:border-border'} bg-[#f4f4f5] flex flex-col gap-2 p-3 transition-all relative overflow-hidden">
                                <div class="w-full h-3 bg-white rounded-md shadow-sm"></div>
                                <div class="w-2/3 h-3 bg-white rounded-md shadow-sm"></div>
                                {#if app.theme === 'light'}
                                    <div class="absolute bottom-2 right-2 w-5 h-5 bg-accent text-white rounded-full flex items-center justify-center shadow-sm">
                                        <IconCheck size={12} stroke={3} />
                                    </div>
                                {/if}
                            </div>
                            <span class="text-[13px] font-medium text-text-primary px-1 {app.theme === 'light' ? 'text-accent' : ''}">Light Mode</span>
                        </button>

                        <!-- Dark Theme -->
                        <button class="flex flex-col gap-3 group text-left" onclick={() => { if(app.theme === 'light') app.toggleTheme() }}>
                            <div class="aspect-[4/3] rounded-xl border-2 {app.theme === 'dark' ? 'border-accent ring-4 ring-accent/10' : 'border-border-subtle group-hover:border-border'} bg-[#0a0a0a] flex flex-col gap-2 p-3 transition-all relative overflow-hidden">
                                <div class="w-full h-3 bg-[#1f1f1f] rounded-md border border-[#2a2a2a]"></div>
                                <div class="w-2/3 h-3 bg-[#1f1f1f] rounded-md border border-[#2a2a2a]"></div>
                                {#if app.theme === 'dark'}
                                    <div class="absolute bottom-2 right-2 w-5 h-5 bg-accent text-white rounded-full flex items-center justify-center shadow-sm">
                                        <IconCheck size={12} stroke={3} />
                                    </div>
                                {/if}
                            </div>
                            <span class="text-[13px] font-medium text-text-primary px-1 {app.theme === 'dark' ? 'text-accent' : ''}">Dark Mode</span>
                        </button>
                    </div>
                </div>

                <!-- Interface Density -->
                <div class="mb-10">
                    <h3 class="text-[13px] font-bold uppercase tracking-widest text-muted mb-4">Interface Density</h3>
                    <div class="flex flex-col gap-3">
                        <label class="flex items-center justify-between p-4 rounded-xl border border-border-subtle bg-surface cursor-pointer hover:border-border transition-colors">
                            <div class="flex items-center gap-3">
                                <input type="radio" name="density" class="w-4 h-4 text-accent border-muted focus:ring-accent" checked>
                                <div>
                                    <div class="text-[14px] font-medium text-text-primary">Comfortable</div>
                                    <div class="text-[13px] text-muted">More whitespace, easier to read.</div>
                                </div>
                            </div>
                        </label>
                        <label class="flex items-center justify-between p-4 rounded-xl border border-border-subtle bg-surface cursor-pointer hover:border-border transition-colors">
                            <div class="flex items-center gap-3">
                                <input type="radio" name="density" class="w-4 h-4 text-accent border-muted focus:ring-accent">
                                <div>
                                    <div class="text-[14px] font-medium text-text-primary">Compact</div>
                                    <div class="text-[13px] text-muted">Fit more data on the screen at once.</div>
                                </div>
                            </div>
                        </label>
                    </div>
                </div>
            </div>

        {:else if activeTab === 'general'}
            <div class="animate-in fade-in slide-in-from-bottom-2 duration-300 ease-out">
                <h2 class="text-[22px] font-bold tracking-tight text-text-primary mb-1">General Settings</h2>
                <p class="text-[14px] text-text-secondary mb-10">Manage your basic profile and workspace preferences.</p>

                <div class="flex flex-col gap-6">
                    <div class="flex flex-col gap-2">
                        <label class="text-[13px] font-medium text-text-primary ml-1">Display Name</label>
                        <input type="text" class="w-full bg-surface border border-border-subtle rounded-xl px-4 py-2.5 text-[14px] text-text-primary focus:outline-none focus:border-accent focus:ring-1 focus:ring-accent transition-all shadow-sm" value="Dr. Sarah Jenkins">
                    </div>
                    
                    <div class="flex flex-col gap-2">
                        <label class="text-[13px] font-medium text-text-primary ml-1">Email Address</label>
                        <input type="email" class="w-full bg-surface border border-border-subtle rounded-xl px-4 py-2.5 text-[14px] text-text-primary focus:outline-none focus:border-accent focus:ring-1 focus:ring-accent transition-all shadow-sm" value="sarah.jenkins@hospital.org" disabled>
                        <p class="text-[12px] text-muted ml-1 mt-1">Contact IT support to change your primary email.</p>
                    </div>

                    <div class="pt-4 mt-2 border-t border-border-subtle">
                        <button class="px-5 py-2.5 bg-text-primary text-bg rounded-xl text-[13.5px] font-medium shadow-sm hover:opacity-90 transition-opacity">
                            Save Changes
                        </button>
                    </div>
                </div>
            </div>

        {:else if activeTab === 'ai-models'}
            <div class="animate-in fade-in slide-in-from-bottom-2 duration-300 ease-out">
                <h2 class="text-[22px] font-bold tracking-tight text-text-primary mb-1">AI & Models</h2>
                <p class="text-[14px] text-text-secondary mb-10">Configure the reasoning engines powering your workspace.</p>

                <!-- Default Model -->
                <div class="mb-10">
                    <h3 class="text-[13px] font-bold uppercase tracking-widest text-muted mb-4">Default Model</h3>
                    <div class="p-5 rounded-xl border border-border-subtle bg-surface flex items-center justify-between shadow-sm">
                        <div class="flex items-center gap-4">
                            <div class="w-10 h-10 rounded-full bg-accent/10 flex items-center justify-center text-accent">
                                <IconBrain size={20} stroke={1.5} />
                            </div>
                            <div>
                                <div class="text-[14.5px] font-semibold text-text-primary">Gemini 3.1 Pro</div>
                                <div class="text-[13px] text-muted mt-0.5">High intelligence, best for complex analysis.</div>
                            </div>
                        </div>
                        <button class="px-4 py-2 rounded-lg border border-border text-[13px] font-medium text-text-primary hover:bg-surface-hover transition-colors">
                            Change
                        </button>
                    </div>
                </div>

                <!-- API Keys -->
                <div>
                    <div class="flex items-center justify-between mb-4">
                        <h3 class="text-[13px] font-bold uppercase tracking-widest text-muted">Provider Keys</h3>
                        <button class="flex items-center gap-1.5 text-[13px] font-medium text-accent hover:text-accent-hover transition-colors">
                            <IconPlus size={14} stroke={2} />
                            Add Key
                        </button>
                    </div>
                    
                    <div class="flex flex-col gap-3">
                        <div class="p-4 rounded-xl border border-border-subtle bg-surface flex items-center justify-between shadow-sm">
                            <div class="flex items-center gap-3">
                                <IconKey size={18} stroke={1.5} class="text-text-secondary" />
                                <span class="text-[14px] font-medium text-text-primary">OpenAI API</span>
                            </div>
                            <div class="flex items-center gap-4">
                                <span class="text-[13px] font-mono text-muted">sk-proj-...8f92</span>
                                <button class="text-muted hover:text-danger transition-colors"><IconTrash size={16} stroke={1.5} /></button>
                            </div>
                        </div>
                        
                        <div class="p-4 rounded-xl border border-border-subtle bg-surface flex items-center justify-between shadow-sm">
                            <div class="flex items-center gap-3">
                                <IconKey size={18} stroke={1.5} class="text-text-secondary" />
                                <span class="text-[14px] font-medium text-text-primary">Anthropic API</span>
                            </div>
                            <div class="flex items-center gap-4">
                                <span class="text-[13px] font-mono text-muted">sk-ant-...b1c2</span>
                                <button class="text-muted hover:text-danger transition-colors"><IconTrash size={16} stroke={1.5} /></button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

        {:else if activeTab === 'privacy'}
            <div class="animate-in fade-in slide-in-from-bottom-2 duration-300 ease-out">
                <h2 class="text-[22px] font-bold tracking-tight text-text-primary mb-1">Data & Privacy</h2>
                <p class="text-[14px] text-text-secondary mb-10">Manage your local storage and export your workspace data.</p>

                <div class="flex flex-col gap-4">
                    <!-- Export -->
                    <div class="p-5 rounded-xl border border-border-subtle bg-surface flex items-start justify-between shadow-sm">
                        <div class="flex flex-col gap-1 pr-6">
                            <div class="text-[14.5px] font-semibold text-text-primary">Export Workspace Data</div>
                            <div class="text-[13px] text-muted leading-relaxed">Download a JSON archive containing all your conversations, artifacts, and local preferences.</div>
                        </div>
                        <button class="shrink-0 flex items-center gap-2 px-4 py-2 rounded-lg border border-border text-[13px] font-medium text-text-primary hover:bg-surface-hover transition-colors">
                            <IconDownload size={16} stroke={1.5} />
                            Export Data
                        </button>
                    </div>

                    <!-- Clear Data -->
                    <div class="p-5 rounded-xl border border-danger/20 bg-danger/5 flex items-start justify-between shadow-sm mt-4">
                        <div class="flex flex-col gap-1 pr-6">
                            <div class="text-[14.5px] font-semibold text-danger">Danger Zone: Clear All Data</div>
                            <div class="text-[13px] text-danger/80 leading-relaxed">Permanently delete all local conversations and settings. This action cannot be undone.</div>
                        </div>
                        <button class="shrink-0 px-4 py-2 rounded-lg bg-danger text-white text-[13px] font-medium shadow-sm hover:bg-danger/90 transition-colors">
                            Clear Data
                        </button>
                    </div>
                </div>
            </div>
        {/if}

    </div>
</div>
