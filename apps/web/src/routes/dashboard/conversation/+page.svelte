<script lang="ts">
    import { marked } from 'marked';
    import { browser } from '$app/environment';
    import { tick, onMount } from 'svelte';
    import { page } from '$app/stores';
    import { goto } from '$app/navigation';
    import {
        sendMessage,
        createConversation,
        getConversation,
        type ChatMessage
    } from '$lib/api/chat';
    import { refreshConversations } from '$lib/stores/conversations';
    import {
        IconSparkles,
    } from '@tabler/icons-svelte';
    import ChatLoadingState from '$lib/components/app/chat/ChatLoadingState.svelte';
    import ChatEmptyState from '$lib/components/app/chat/ChatEmptyState.svelte';
    import ChatBubble from '$lib/components/app/chat/ChatBubble.svelte';
    import ChatComposer from '$lib/components/app/chat/ChatComposer.svelte';

    // ── State ────────────────────────────────────────────────────────────
    interface Message {
        role: 'user' | 'assistant';
        content: string;
        streaming?: boolean;
    }

    let messages = $state<Message[]>([]);
    let conversationId = $state<string | null>(null);
    let input = $state('');
    let isStreaming = $state(false);
    let isLoading = $state(false);
    let error = $state<string | null>(null);

    let scrollEl = $state<HTMLDivElement | null>(null);

    function scrollToBottom() {
        if (scrollEl) scrollEl.scrollTop = scrollEl.scrollHeight;
    }

    // ── Load history when ?id changes ─────────────────────────────────
    async function loadConversation(id: string) {
        isLoading = true;
        error = null;
        try {
            const conv = await getConversation(id);
            conversationId = id;
            messages = conv.messages.map((m: ChatMessage) => ({
                role: m.role as 'user' | 'assistant',
                content: m.content
            }));
            await tick();
            scrollToBottom();
        } catch (e) {
            error = e instanceof Error ? e.message : 'Failed to load conversation';
        } finally {
            isLoading = false;
        }
    }

    onMount(() => {
        const id = $page.url.searchParams.get('id');
        if (id) loadConversation(id);
    });

    // Re-load when URL ?id param changes (e.g. clicking a different conversation)
    $effect(() => {
        const id = $page.url.searchParams.get('id');
        if (id && id !== conversationId) {
            messages = [];
            loadConversation(id);
        } else if (!id && conversationId) {
            messages = [];
            conversationId = null;
        }
    });

    // ── Send message ───────────────────────────────────────────────────
    async function submit() {
        const text = input.trim();
        if (!text || isStreaming) return;

        error = null;
        input = '';
        await tick();

        // Add user bubble immediately
        messages.push({ role: 'user', content: text });

        // Add empty streaming assistant slot
        const assistantIdx = messages.length;
        messages.push({ role: 'assistant', content: '', streaming: true });

        isStreaming = true;
        await tick();
        scrollToBottom();

        try {
            // Create a new conversation if we don't have one yet
            if (!conversationId) {
                const conv = await createConversation();
                conversationId = conv.id;
                // Update URL without full navigation
                goto(`/dashboard/conversation?id=${conv.id}`, { replaceState: true, noScroll: true });
                // Tell the sidebar to refresh
                refreshConversations();
            }

            await sendMessage(conversationId, text, {
                onToken(token) {
                    messages[assistantIdx].content += token;
                    messages = messages;
                    scrollToBottom();
                },
                onDone() {
                    messages[assistantIdx].streaming = false;
                    messages = messages;
                    isStreaming = false;
                    // Refresh sidebar so updated title/timestamp shows
                    refreshConversations();
                },
                onError(err) {
                    messages[assistantIdx].streaming = false;
                    messages[assistantIdx].content =
                        messages[assistantIdx].content || '_Error receiving response._';
                    messages = messages;
                    error = err.message;
                    isStreaming = false;
                }
            });

            // Fallback: end streaming if connection closed without explicit 'done'
            if (isStreaming) {
                messages[assistantIdx].streaming = false;
                messages = messages;
                isStreaming = false;
            }
        } catch (err) {
            messages[assistantIdx].streaming = false;
            messages = messages;
            error = err instanceof Error ? err.message : 'Unknown error';
            isStreaming = false;
        }
    }
</script>


<div class="absolute inset-0 flex flex-col bg-canvas">
    <!-- Chat History Area -->
    <div class="flex-1 overflow-y-auto flex flex-col items-center px-4 md:px-8" bind:this={scrollEl}>
        <div class="w-full max-w-[820px] pt-8 pb-6 conversation">

            <!-- Loading state -->
            {#if isLoading}
                <ChatLoadingState />

            <!-- Empty state -->
            {:else if messages.length === 0}
                <ChatEmptyState />
            {/if}

            {#each messages as msg, i}
                <ChatBubble 
                    role={msg.role} 
                    content={msg.content} 
                    streaming={msg.streaming} 
                />
            {/each}

            <!-- Error banner -->
            {#if error}
                <div class="w-full mt-3 rounded-xl border border-danger/30 bg-danger/8 px-4 py-3 text-[12.5px] text-danger flex items-center gap-2 shadow-sm">
                    <span class="font-semibold">Error:</span> {error}
                </div>
            {/if}

        </div>
    </div>

    <!-- Pinned Input Area -->
    <div class="w-full px-4 pb-4 pt-2.5 flex justify-center shrink-0 border-t border-border-subtle bg-canvas">
        <ChatComposer 
            bind:input={input} 
            isStreaming={isStreaming} 
            onsubmit={submit} 
        />
    </div>
</div>

<style>
    /* Typing indicator dots */
    .typing-dot {
        width: 5px;
        height: 5px;
        border-radius: 50%;
        background: var(--color-muted);
        animation: bounce-dot 1.2s ease-in-out infinite;
        display: inline-block;
    }

    @keyframes bounce-dot {
        0%, 80%, 100% { transform: translateY(0); opacity: 0.35; }
        40%            { transform: translateY(-4px); opacity: 0.9; }
    }

    /* ── Scoped prose styles for agent markdown output ── */
    .prose-agent :global(h1),
    .prose-agent :global(h2),
    .prose-agent :global(h3),
    .prose-agent :global(h4) {
        color: var(--color-text-primary);
        font-weight: 600;
        letter-spacing: -0.02em;
        margin-top: 1.4em;
        margin-bottom: 0.45em;
        line-height: 1.3;
    }
    .prose-agent :global(h1) { font-size: 1.1em; }
    .prose-agent :global(h2) { font-size: 1.0em; }
    .prose-agent :global(h3) { font-size: 0.95em; }
    .prose-agent :global(h4) { font-size: 0.9em; font-weight: 500; }

    .prose-agent :global(p) {
        margin: 0.55em 0;
        color: var(--color-text-primary);
    }

    .prose-agent :global(p:first-child) {
        margin-top: 0;
    }

    .prose-agent :global(ul) {
        list-style-type: disc;
    }

    .prose-agent :global(ol) {
        list-style-type: decimal;
    }

    .prose-agent :global(ul),
    .prose-agent :global(ol) {
        padding-left: 1.35em;
        margin: 0.55em 0;
        color: var(--color-text-primary);
    }

    .prose-agent :global(li) {
        margin: 0.3em 0;
        line-height: 1.6;
    }

    .prose-agent :global(code) {
        background: var(--color-surface-elevated);
        color: var(--color-accent);
        padding: 0.1em 0.38em;
        border-radius: 5px;
        font-family: var(--font-mono);
        font-size: 0.84em;
        border: 1px solid var(--color-border);
        letter-spacing: 0;
    }

    .prose-agent :global(pre) {
        background: var(--color-surface-elevated);
        border: 1px solid var(--color-border-subtle);
        border-radius: 10px;
        padding: 0.9em 1.1em;
        overflow-x: auto;
        margin: 0.85em 0;
    }

    .prose-agent :global(pre code) {
        background: transparent;
        border: none;
        padding: 0;
        color: var(--color-text-primary);
        font-size: 0.83em;
        letter-spacing: 0;
    }

    .prose-agent :global(table) {
        width: 100%;
        border-collapse: collapse;
        margin: 0.85em 0;
        font-size: 0.88em;
    }

    .prose-agent :global(th) {
        background: var(--color-surface-elevated);
        color: var(--color-text-secondary);
        font-weight: 600;
        text-align: left;
        padding: 0.5em 0.8em;
        border: 1px solid var(--color-border);
        font-size: 0.85em;
        letter-spacing: 0.01em;
    }

    .prose-agent :global(td) {
        padding: 0.45em 0.8em;
        border: 1px solid var(--color-border-subtle);
        color: var(--color-text-primary);
        font-size: 0.88em;
    }

    .prose-agent :global(tr:nth-child(even) td) {
        background: var(--color-surface);
    }

    .prose-agent :global(blockquote) {
        border-left: 2px solid var(--color-accent);
        margin: 0.85em 0;
        padding: 0.5em 1em;
        background: color-mix(in srgb, var(--color-accent) 6%, transparent);
        border-radius: 0 8px 8px 0;
        color: var(--color-text-primary);
        font-size: 0.92em;
    }

    .prose-agent :global(strong),
    .prose-agent :global(b) {
        color: var(--color-text-primary);
        font-weight: 650;
    }

    .prose-agent :global(a) {
        color: var(--color-accent);
        text-decoration: underline;
        text-underline-offset: 2px;
        text-decoration-thickness: 1px;
    }

    .prose-agent :global(img) {
        max-width: 100%;
        border-radius: 10px;
        border: 1px solid var(--color-border);
        margin: 0.85em 0;
        display: block;
    }

    .prose-agent :global(hr) {
        border: none;
        border-top: 1px solid var(--color-border-subtle);
        margin: 1.4em 0;
    }

    .prose-agent :global(em) {
        color: var(--color-text-primary);
        font-style: italic;
        opacity: 0.85;
    }
</style>
