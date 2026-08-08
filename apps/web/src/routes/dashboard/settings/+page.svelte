<script lang="ts">
    import { app } from '$lib/state/app.svelte';
    import { i18n, t, m } from '$lib/i18n';
    import { 
        IconPalette, 
        IconCheck,
        IconTag,
        IconChevronRight,
        IconSun,
        IconMoon,
        IconDeviceDesktop
    } from '@tabler/icons-svelte';

    let activeTab = $state<'appearance' | 'semantics'>('appearance');

    const tabs = [
        { id: 'appearance', label: 'Appearance & Language', icon: IconPalette },
        { id: 'semantics', label: 'Semantic Categories', icon: IconTag }
    ] as const;
</script>

<svelte:head>
	<title>{t(m.settings_title)} | CHU Platform</title>
	<meta name="description" content={t(m.settings_subtitle)} />
</svelte:head>

<div class="w-full max-w-[1024px] mx-auto px-4 sm:px-6 py-8 md:py-12 grid grid-cols-1 md:grid-cols-[220px_1fr] gap-8 md:gap-16 items-start">
    
    <!-- Sidebar Navigation -->
    <aside class="flex flex-col gap-6 w-full sticky top-16">
        <div class="px-3">
            <h1 class="text-xl font-bold tracking-tight text-text-primary">{t(m.settings_title)}</h1>
            <p class="text-xs text-text-secondary mt-1">{t(m.settings_subtitle)}</p>
        </div>
        
        <nav class="flex flex-col gap-0.5">
            {#each tabs as tab}
                <button 
                    class="group relative inline-flex items-center gap-2.5 text-[13.5px] font-medium cursor-pointer transition-colors duration-150 w-full rounded-lg px-3 py-2.5 text-left {activeTab === tab.id 
                        ? 'bg-surface-hover/80 text-text-primary' 
                        : 'text-text-secondary hover:bg-surface-hover/50 hover:text-text-primary'}"
                    onclick={() => activeTab = tab.id}
                >
                    <div class="flex items-center justify-center shrink-0">
                        <tab.icon size={16} stroke={1.5} class="transition-colors {activeTab === tab.id ? 'text-text-primary' : 'text-muted group-hover:text-text-secondary'}" />
                    </div>
                    <span class="flex-1 whitespace-nowrap overflow-hidden text-ellipsis">{tab.label}</span>
                </button>
            {/each}
        </nav>
    </aside>

    <!-- Content Area -->
    <main class="w-full max-w-[600px] pb-16">
        
        {#if activeTab === 'appearance'}
            <div class="animate-in fade-in slide-in-from-bottom-2 duration-300 flex flex-col space-y-8">
                <!-- Header -->
                <div class="border-b border-border/80 pb-5">
                    <h2 class="text-lg font-bold tracking-tight text-text-primary mb-1">{t(m.settings_theme)}</h2>
                    <p class="text-xs text-text-secondary">{t(m.settings_theme_desc)}</p>
                </div>

                <!-- Language Selection -->
                <div class="space-y-3">
                    <h3 class="text-xs font-bold uppercase tracking-wider text-text-secondary">{t(m.settings_language)}</h3>
                    <p class="text-xs text-muted">{t(m.settings_language_desc)}</p>
                    <div class="grid grid-cols-2 gap-3.5 pt-1">
                        <!-- English -->
                        <button
                            class="flex items-center justify-between p-4 rounded-xl border transition-all cursor-pointer {i18n.locale === 'en' ? 'border-accent bg-accent/10 text-accent font-bold shadow-xs' : 'border-border/80 bg-surface/50 text-text-secondary hover:text-text-primary hover:bg-surface'}"
                            onclick={() => i18n.setLocale('en')}
                        >
                            <div class="flex items-center gap-2.5">
                                <span class="text-base">🇬🇧</span>
                                <span class="text-xs font-semibold">{t(m.settings_lang_en)}</span>
                            </div>
                            {#if i18n.locale === 'en'}
                                <IconCheck size={16} stroke={2.5} class="text-accent" />
                            {/if}
                        </button>

                        <!-- French -->
                        <button
                            class="flex items-center justify-between p-4 rounded-xl border transition-all cursor-pointer {i18n.locale === 'fr' ? 'border-accent bg-accent/10 text-accent font-bold shadow-xs' : 'border-border/80 bg-surface/50 text-text-secondary hover:text-text-primary hover:bg-surface'}"
                            onclick={() => i18n.setLocale('fr')}
                        >
                            <div class="flex items-center gap-2.5">
                                <span class="text-base">🇫🇷</span>
                                <span class="text-xs font-semibold">{t(m.settings_lang_fr)}</span>
                            </div>
                            {#if i18n.locale === 'fr'}
                                <IconCheck size={16} stroke={2.5} class="text-accent" />
                            {/if}
                        </button>
                    </div>
                </div>

                <!-- Theme Selection -->
                <div class="space-y-3 pt-4 border-t border-border/60">
                    <h3 class="text-xs font-bold uppercase tracking-wider text-text-secondary">Theme</h3>
                    <div class="grid grid-cols-3 gap-4 pt-1">
                        
                        <!-- System Theme -->
                        <button class="flex flex-col gap-2.5 group text-left cursor-pointer" onclick={() => {
                            const isSystemLight = window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches;
                            app.setTheme(isSystemLight ? 'light' : 'dark');
                        }}>
                            <div class="aspect-[16/10] w-full rounded-xl border border-border/80 bg-gradient-to-br from-gray-200 via-gray-400 to-[#121212] flex items-center justify-center transition-all group-hover:border-accent group-hover:shadow-sm">
                                <IconDeviceDesktop size={20} class="text-white drop-shadow-md" />
                            </div>
                            <span class="text-xs font-semibold text-text-primary text-center">System</span>
                        </button>

                        <!-- Light Theme -->
                        <button class="flex flex-col gap-2.5 group text-left cursor-pointer" onclick={() => app.setTheme('light')}>
                            <div class="aspect-[16/10] w-full rounded-xl border {app.theme === 'light' ? 'border-accent ring-2 ring-accent/20' : 'border-border/80 group-hover:border-accent'} bg-[#f4f4f5] flex flex-col gap-1.5 p-2.5 transition-all relative justify-center items-center">
                                <IconSun size={20} class="text-amber-500" />
                            </div>
                            <span class="text-xs font-semibold {app.theme === 'light' ? 'text-accent font-bold' : 'text-text-secondary'} text-center">{t(m.settings_theme_light)}</span>
                        </button>

                        <!-- Dark Theme -->
                        <button class="flex flex-col gap-2.5 group text-left cursor-pointer" onclick={() => app.setTheme('dark')}>
                            <div class="aspect-[16/10] w-full rounded-xl border {app.theme === 'dark' ? 'border-accent ring-2 ring-accent/20' : 'border-border/80 group-hover:border-accent'} bg-[#0d1117] flex flex-col gap-1.5 p-2.5 transition-all relative justify-center items-center">
                                <IconMoon size={20} class="text-indigo-400" />
                            </div>
                            <span class="text-xs font-semibold {app.theme === 'dark' ? 'text-accent font-bold' : 'text-text-secondary'} text-center">{t(m.settings_theme_dark)}</span>
                        </button>
                    </div>
                </div>
            </div>

        {:else if activeTab === 'semantics'}
            <div class="animate-in fade-in slide-in-from-bottom-2 duration-300 flex flex-col space-y-6">
                <div class="border-b border-border/80 pb-5">
                    <h2 class="text-lg font-bold tracking-tight text-text-primary mb-1">Semantic Categories</h2>
                    <p class="text-xs text-text-secondary">Configure domain classification buckets used in dataset column mappings.</p>
                </div>

                <div class="flex flex-col gap-5 p-6 border border-border/80 rounded-2xl bg-surface/60 shadow-xs">
                    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                        <div class="flex items-center gap-3.5">
                            <div class="w-10 h-10 rounded-xl bg-accent/15 border border-accent/30 flex items-center justify-center text-accent shrink-0">
                                <IconTag size={20} stroke={2} />
                            </div>
                            <div>
                                <h3 class="text-sm font-bold text-text-primary">Manage Categories</h3>
                                <p class="text-xs text-muted mt-0.5">Create, edit, or remove clinical/statistical categories stored in PostgreSQL.</p>
                            </div>
                        </div>
                        <a 
                            href="/dashboard/settings/semantic-categories" 
                            class="inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-accent text-black font-bold text-xs hover:brightness-110 transition-all shadow-xs shrink-0"
                        >
                            Open Category Manager
                            <IconChevronRight size={14} stroke={2.5} />
                        </a>
                    </div>
                </div>
            </div>
        {/if}

    </main>
</div>
