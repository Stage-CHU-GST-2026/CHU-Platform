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
        IconChevronDown,
        IconPlus,
        IconMicrophone,
        IconSparkles,
        IconSend
    } from '@tabler/icons-svelte';

    // Configure marked for clean output
    marked.setOptions({ breaks: true, gfm: true });

    async function renderMd(content: string): Promise<string> {
        const html = marked.parse(content) as string;
        if (browser) {
            const DOMPurify = (await import('dompurify')).default;
            return DOMPurify.sanitize(html, {
                ADD_TAGS: ['img'],
                ADD_ATTR: ['src', 'alt', 'title', 'href', 'target', 'rel']
            });
        }
        return html;
    }

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
    let textareaEl = $state<HTMLTextAreaElement | null>(null);

    function scrollToBottom() {
        if (scrollEl) scrollEl.scrollTop = scrollEl.scrollHeight;
    }

    function resizeTextarea() {
        if (textareaEl) {
            textareaEl.style.height = 'auto';
            textareaEl.style.height = textareaEl.scrollHeight + 'px';
        }
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
        resizeTextarea();

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

    function handleKeydown(e: KeyboardEvent) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            submit();
        }
    }
</script>


<div class="absolute inset-0 flex flex-col bg-canvas">
    <!-- Chat History Area -->
    <div class="flex-1 overflow-y-auto p-4 md:p-8 flex flex-col items-center" bind:this={scrollEl}>
        <div class="w-full max-w-[880px] flex flex-col gap-6 mt-4 pb-4">

            <!-- Loading state -->
            {#if isLoading}
                <div class="flex flex-col items-center justify-center h-48 text-center gap-3 mt-16">
                    <span class="w-6 h-6 rounded-full border-2 border-border border-t-accent animate-spin"></span>
                    <p class="text-muted text-[13px]">Loading conversation…</p>
                </div>
            <!-- Empty state -->
            {:else if messages.length === 0}
                <div class="flex flex-col items-center justify-center h-48 text-center gap-3 mt-16">
                    <div class="w-10 h-10 rounded-full bg-surface-elevated border border-border flex items-center justify-center text-accent">
                        <IconSparkles size={18} stroke={1.5} />
                    </div>
                    <p class="text-text-secondary text-[15px]">Start a conversation with the analytics agent.</p>
                    <p class="text-muted text-[13px]">Ask about patient data, generate reports, or run analysis.</p>
                </div>
            {/if}


            {#each messages as msg}
                {#if msg.role === 'user'}
                    <!-- User message -->
                    <div class="w-full bg-[#202020] border border-border-subtle rounded-xl px-5 py-4 text-[15.5px] leading-relaxed whitespace-pre-wrap text-text-secondary mt-4 shadow-sm">
                        {msg.content}
                    </div>
                {:else}
                    <!-- Agent message -->
                    <div class="w-full pt-4 pb-2 px-4">
                        <div class="w-full min-w-0 text-[16px] leading-relaxed text-text-secondary">
                            {#if msg.streaming}
                                {#if msg.content}
                                    <!-- Raw text while streaming — no Promise re-creation, no flash -->
                                    <span class="whitespace-pre-wrap">{msg.content}</span>
                                {:else}
                                    <!-- Typing indicator before first token -->
                                    <span class="inline-flex gap-1 items-center h-5">
                                        <span class="w-1.5 h-1.5 rounded-full bg-muted animate-bounce" style="animation-delay: 0ms"></span>
                                        <span class="w-1.5 h-1.5 rounded-full bg-muted animate-bounce" style="animation-delay: 150ms"></span>
                                        <span class="w-1.5 h-1.5 rounded-full bg-muted animate-bounce" style="animation-delay: 300ms"></span>
                                    </span>
                                {/if}
                            {:else if msg.content}
                                <!-- Stream done — render full markdown once -->
                                <div class="prose-agent">
                                    {#await renderMd(msg.content) then html}
                                        {@html html}
                                    {/await}
                                </div>
                            {/if}
                        </div>
                    </div>
                {/if}
            {/each}

            <!-- Error banner -->
            {#if error}
                <div class="w-full rounded-lg border border-danger bg-danger/10 px-4 py-3 text-[13px] text-danger flex items-center gap-2">
                    <span class="font-medium">Error:</span> {error}
                </div>
            {/if}

        </div>
    </div>

    <!-- Pinned Input Area -->
    <div class="w-full p-4 pb-6 flex justify-center shrink-0 border-t border-border-subtle">
        <div class="w-full max-w-[880px] bg-surface border border-border-subtle rounded-[14px] overflow-hidden flex items-center gap-2 px-3 shadow-sm focus-within:border-border transition-colors">
            
            <!-- Add button -->
            <button class="w-6 h-6 flex items-center justify-center rounded-md hover:bg-surface-hover text-text-secondary hover:text-text-primary transition-colors shrink-0" aria-label="Add attachment" disabled={isStreaming}>
                <IconPlus size={16} stroke={2} />
            </button>

            <!-- Textarea -->
            <textarea 
                bind:this={textareaEl}
                bind:value={input}
                class="flex-1 bg-transparent text-text-primary placeholder-muted resize-none focus:outline-none focus:ring-0 border-0 shadow-none p-0 text-[15.5px] leading-relaxed max-h-36 overflow-y-auto py-3 disabled:opacity-50"
                placeholder="Ask anything, @ to mention, / for actions"
                rows="1"
                disabled={isStreaming}
                onkeydown={handleKeydown}
                oninput={resizeTextarea}
            ></textarea>

            <!-- Right side: model selector + send/mic -->
            <div class="flex items-center gap-1 shrink-0">
                <button class="flex items-center gap-1.5 px-2 h-6 rounded-md hover:bg-surface-hover text-text-secondary hover:text-text-primary transition-colors text-[12px] font-medium">
                    <IconSparkles size={13} stroke={1.5} />
                    Gemini 3.1 Pro
                    <IconChevronDown size={13} stroke={2} class="opacity-70" />
                </button>

                {#if isStreaming}
                    <button class="w-6 h-6 flex items-center justify-center rounded-full bg-surface-elevated text-muted cursor-not-allowed" disabled aria-label="Sending">
                        <span class="w-3 h-3 rounded-full border-2 border-muted border-t-transparent animate-spin"></span>
                    </button>
                {:else if input.trim()}
                    <button 
                        onclick={submit}
                        class="w-6 h-6 flex items-center justify-center rounded-full bg-accent hover:opacity-90 text-white transition-opacity"
                        aria-label="Send message"
                    >
                        <IconSend size={13} stroke={2} />
                    </button>
                {:else}
                    <button class="w-6 h-6 flex items-center justify-center rounded-full bg-surface-elevated hover:bg-border text-text-secondary hover:text-text-primary transition-colors" aria-label="Voice input">
                        <IconMicrophone size={15} stroke={1.5} />
                    </button>
                {/if}
            </div>

        </div>
    </div>

</div>

<style>
    /* Scoped prose styles for agent markdown output */
    .prose-agent :global(h1),
    .prose-agent :global(h2),
    .prose-agent :global(h3) {
        color: var(--color-text-primary);
        font-weight: 600;
        margin-top: 1.2em;
        margin-bottom: 0.5em;
    }
    .prose-agent :global(h1) { font-size: 1.2em; }
    .prose-agent :global(h2) { font-size: 1.05em; }
    .prose-agent :global(h3) { font-size: 0.95em; }

    .prose-agent :global(p) {
        margin: 0.5em 0;
        color: inherit;
    }

    .prose-agent :global(ul) {
        list-style-type: disc;
    }

    .prose-agent :global(ol) {
        list-style-type: decimal;
    }

    .prose-agent :global(ul),
    .prose-agent :global(ol) {
        padding-left: 1.4em;
        margin: 0.5em 0;
        color: inherit;
    }

    .prose-agent :global(li) {
        margin: 0.25em 0;
    }

    .prose-agent :global(code) {
        background: var(--color-surface-elevated);
        color: var(--color-accent);
        padding: 0.15em 0.4em;
        border-radius: 4px;
        font-family: var(--font-mono);
        font-size: 0.875em;
        border: 1px solid var(--color-border);
    }

    .prose-agent :global(pre) {
        background: var(--color-surface-elevated);
        border: 1px solid var(--color-border);
        border-radius: 10px;
        padding: 1em 1.2em;
        overflow-x: auto;
        margin: 0.75em 0;
    }

    .prose-agent :global(pre code) {
        background: transparent;
        border: none;
        padding: 0;
        color: var(--color-text-secondary);
        font-size: 0.85em;
    }

    .prose-agent :global(table) {
        width: 100%;
        border-collapse: collapse;
        margin: 0.75em 0;
        font-size: 0.9em;
    }

    .prose-agent :global(th) {
        background: var(--color-surface-elevated);
        color: var(--color-text-secondary);
        font-weight: 600;
        text-align: left;
        padding: 0.5em 0.75em;
        border: 1px solid var(--color-border);
        font-size: 0.85em;
    }

    .prose-agent :global(td) {
        padding: 0.45em 0.75em;
        border: 1px solid var(--color-border-subtle);
        color: var(--color-text-primary);
    }

    .prose-agent :global(tr:nth-child(even) td) {
        background: var(--color-surface);
    }

    .prose-agent :global(blockquote) {
        border-left: 3px solid var(--color-accent);
        margin: 0.75em 0;
        padding: 0.5em 1em;
        background: var(--color-surface);
        border-radius: 0 8px 8px 0;
        color: var(--color-text-secondary);
        font-size: 0.9em;
    }

    .prose-agent :global(strong),
    .prose-agent :global(b) {
        color: var(--color-text-primary);
        font-weight: 700;
    }

    .prose-agent :global(a) {
        color: var(--color-accent);
        text-decoration: underline;
        text-underline-offset: 2px;
    }

    .prose-agent :global(img) {
        max-width: 100%;
        border-radius: 10px;
        border: 1px solid var(--color-border);
        margin: 0.75em 0;
        display: block;
    }

    .prose-agent :global(hr) {
        border: none;
        border-top: 1px solid var(--color-border-subtle);
        margin: 1.2em 0;
    }

    .prose-agent :global(em) {
        color: var(--color-text-secondary);
        font-style: italic;
    }
</style>
