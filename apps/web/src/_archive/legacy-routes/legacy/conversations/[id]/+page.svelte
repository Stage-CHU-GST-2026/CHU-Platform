<script lang="ts">
    import { page } from '$app/stores';
    import { convo } from '$lib/state/conversations.svelte';
    import { agents } from '$lib/state/agents.svelte';
    import Button from '$lib/components/app/common/Button.svelte';
    import Avatar from '$lib/components/app/common/Avatar.svelte';
    import MarkdownRenderer from '$lib/components/app/data/MarkdownRenderer.svelte';
    import Tabs from '$lib/components/app/common/Tabs.svelte';
    import { IconSend, IconPaperclip, IconLayoutSidebarRightCollapse, IconLayoutSidebarRightExpand, IconPin } from '@tabler/icons-svelte';
    import * as Icons from '@tabler/icons-svelte';

    let id = $derived($page.params.id);
    
    $effect(() => {
        if (id) convo.activeId = id;
    });

    let currentConvo = $derived(convo.active);
    let currentAgent = $derived(currentConvo ? agents.all.find(a => a.id === currentConvo.agentId) : null);
    let isPinned = $derived(currentConvo ? convo.pinned.includes(currentConvo.id) : false);

    // Dynamic icon resolution for the agent
    let AgentIcon = $derived(
        currentAgent?.icon ? ((Icons as Record<string, any>)[currentAgent.icon] || Icons.IconRobot) : Icons.IconRobot
    );

    let inputMessage = $state('');
    let messagesEndRef: HTMLDivElement;

    $effect(() => {
        if (currentConvo?.messages.length) {
            messagesEndRef?.scrollIntoView({ behavior: 'smooth' });
        }
    });

    async function handleSend() {
        if (!inputMessage.trim() || convo.streaming) return;
        const msg = inputMessage;
        inputMessage = '';
        await convo.send(msg);
    }

    function handleKeydown(e: KeyboardEvent) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    }
</script>

<svelte:head>
    <title>{currentConvo?.title || 'Conversation'} | CHU Analytics</title>
</svelte:head>

{#if currentConvo && currentAgent}
    <div class="h-full flex relative">
        <!-- Main Chat Area -->
        <div class="flex-1 flex flex-col min-w-0 transition-all" class:mr-[400px]={convo.artifactPanel === 'open'}>
            
            <!-- Chat Header -->
            <div class="h-14 px-6 border-b border-border bg-surface/80 backdrop-blur-sm flex items-center justify-between shrink-0 sticky top-0 z-10">
                <div class="flex items-center gap-3">
                    <div class="w-8 h-8 rounded bg-surface-elevated flex items-center justify-center text-accent">
                        <AgentIcon size={18} />
                    </div>
                    <div>
                        <h2 class="text-[14px] font-semibold text-text-primary leading-none">{currentConvo.title}</h2>
                        <span class="text-[11px] text-text-secondary">{currentAgent.name}</span>
                    </div>
                </div>
                
                <div class="flex items-center gap-2">
                    <Button 
                        variant="ghost" 
                        size="icon" 
                        onclick={() => isPinned ? convo.unpin(currentConvo.id) : convo.pin(currentConvo.id)}
                        class={isPinned ? 'text-accent' : ''}
                    >
                        <IconPin size={16} />
                    </Button>
                    <div class="w-px h-4 bg-border mx-1"></div>
                    <Button 
                        variant="ghost" 
                        size="icon" 
                        onclick={() => convo.artifactPanel = convo.artifactPanel === 'open' ? 'closed' : 'open'}
                    >
                        {#if convo.artifactPanel === 'open'}
                            <IconLayoutSidebarRightExpand size={16} />
                        {:else}
                            <IconLayoutSidebarRightCollapse size={16} />
                        {/if}
                    </Button>
                </div>
            </div>

            <!-- Messages List -->
            <div class="flex-1 overflow-y-auto px-4 py-6 md:px-8 space-y-6 scroll-smooth">
                {#each currentConvo.messages as msg}
                    <div class="flex gap-4 max-w-4xl mx-auto" class:flex-row-reverse={msg.role === 'user'}>
                        
                        {#if msg.role === 'user'}
                            <Avatar name="Sarah Jenkins" size="sm" class="mt-1" />
                        {:else}
                            <div class="w-8 h-8 rounded bg-surface-elevated border border-border flex items-center justify-center text-accent shrink-0 mt-1">
                                <AgentIcon size={18} />
                            </div>
                        {/if}

                        <div class="flex flex-col max-w-[85%] min-w-0" class:items-end={msg.role === 'user'}>
                            <div 
                                class="px-5 py-3.5 rounded-2xl text-[14px] shadow-sm"
                                class:bg-accent={msg.role === 'user'}
                                class:text-white={msg.role === 'user'}
                                class:bg-surface={msg.role !== 'user'}
                                class:border={msg.role !== 'user'}
                                class:border-border={msg.role !== 'user'}
                                class:text-text-primary={msg.role !== 'user'}
                                class:rounded-tr-sm={msg.role === 'user'}
                                class:rounded-tl-sm={msg.role !== 'user'}
                            >
                                {#if msg.role === 'user'}
                                    <div class="whitespace-pre-wrap">{msg.content}</div>
                                {:else}
                                    <MarkdownRenderer content={msg.content} />
                                    
                                    <!-- Embedded Artifact Reference -->
                                    {#if msg.artifacts && msg.artifacts.length > 0}
                                        <div class="mt-4 flex flex-col gap-2">
                                            {#each msg.artifacts as artifact}
                                                <button 
                                                    class="flex items-center gap-3 p-3 rounded-lg border border-border bg-canvas hover:border-accent transition-colors text-left"
                                                    onclick={() => { convo.artifactPanel = 'open'; }}
                                                >
                                                    <div class="w-8 h-8 rounded bg-surface-elevated flex items-center justify-center text-accent shrink-0">
                                                        <Icons.IconChartBar size={16} />
                                                    </div>
                                                    <div class="flex-1 min-w-0">
                                                        <div class="text-[13px] font-medium text-text-primary truncate">{artifact.title}</div>
                                                        <div class="text-[11px] text-text-secondary uppercase tracking-wider">{artifact.type}</div>
                                                    </div>
                                                    <Icons.IconLayoutSidebarRightCollapse size={16} class="text-muted" />
                                                </button>
                                            {/each}
                                        </div>
                                    {/if}
                                {/if}
                            </div>
                            <span class="text-[10px] text-muted mt-1 px-1">
                                {new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                            </span>
                        </div>
                    </div>
                {/each}
                
                {#if convo.streaming}
                    <div class="flex gap-4 max-w-4xl mx-auto">
                        <div class="w-8 h-8 rounded bg-surface-elevated border border-border flex items-center justify-center text-accent shrink-0 mt-1">
                            <AgentIcon size={18} />
                        </div>
                        <div class="px-5 py-4 rounded-2xl rounded-tl-sm bg-surface border border-border shadow-sm flex items-center gap-1">
                            <span class="w-1.5 h-1.5 rounded-full bg-accent animate-bounce" style="animation-delay: 0ms;"></span>
                            <span class="w-1.5 h-1.5 rounded-full bg-accent animate-bounce" style="animation-delay: 150ms;"></span>
                            <span class="w-1.5 h-1.5 rounded-full bg-accent animate-bounce" style="animation-delay: 300ms;"></span>
                        </div>
                    </div>
                {/if}
                <div bind:this={messagesEndRef} class="h-4"></div>
            </div>

            <!-- Input Area -->
            <div class="p-4 md:px-8 border-t border-border bg-canvas shrink-0">
                <div class="max-w-4xl mx-auto relative">
                    <div class="absolute inset-y-0 left-2 flex items-center">
                        <Button variant="ghost" size="icon" class="text-muted hover:text-text-primary">
                            <IconPaperclip size={18} />
                        </Button>
                    </div>
                    <textarea
                        bind:value={inputMessage}
                        onkeydown={handleKeydown}
                        placeholder="Message {currentAgent.name}..."
                        rows="1"
                        class="w-full pl-12 pr-14 py-4 bg-surface border border-border rounded-xl text-[14px] text-text-primary placeholder:text-muted focus:outline-none focus:border-accent focus:ring-1 focus:ring-accent/50 resize-none min-h-[56px] max-h-48 shadow-sm transition-all overflow-hidden"
                    ></textarea>
                    <div class="absolute inset-y-0 right-2 flex items-center">
                        <Button 
                            variant="primary" 
                            size="icon" 
                            class="h-10 w-10 rounded-lg {inputMessage.trim() ? '' : 'opacity-50 pointer-events-none'}"
                            onclick={handleSend}
                            loading={convo.streaming}
                        >
                            <IconSend size={18} class={inputMessage.trim() ? 'translate-x-[1px]' : ''} />
                        </Button>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Artifact / Detail Panel (Right Sidebar) -->
        {#if convo.artifactPanel === 'open'}
            <div class="w-[400px] absolute right-0 top-0 bottom-0 border-l border-border bg-surface flex flex-col z-20 shadow-2xl animate-in slide-in-from-right-full duration-300">
                <div class="px-4 border-b border-border flex items-center justify-between shrink-0 h-14 bg-surface-elevated">
                    <h3 class="text-[13px] font-semibold text-text-primary">Artifact Inspector</h3>
                    <Button variant="ghost" size="icon" onclick={() => convo.artifactPanel = 'closed'}>
                        <IconLayoutSidebarRightExpand size={16} />
                    </Button>
                </div>
                
                <Tabs 
                    active={convo.artifactTab}
                    onchange={id => convo.artifactTab = id as any}
                    tabs={[
                        { id: 'output', label: 'Output' },
                        { id: 'code', label: 'Code' },
                        { id: 'sources', label: 'Sources' }
                    ]}
                />
                
                <div class="flex-1 overflow-y-auto p-6 flex flex-col items-center justify-center text-center">
                    <!-- Temporary placeholder for artifact content -->
                    <div class="w-16 h-16 rounded-full bg-surface-elevated border border-border flex items-center justify-center text-muted mb-4">
                        <Icons.IconChartBar size={32} />
                    </div>
                    <h4 class="text-[14px] font-medium text-text-primary mb-2">Admissions Q2</h4>
                    <p class="text-[13px] text-text-secondary">Interactive preview will appear here.</p>
                </div>
            </div>
        {/if}
    </div>
{/if}
