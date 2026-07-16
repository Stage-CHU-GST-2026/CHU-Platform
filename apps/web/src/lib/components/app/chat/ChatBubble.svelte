<script lang="ts">
    import { marked } from 'marked';
    import { browser } from '$app/environment';
    import { IconSparkles } from '@tabler/icons-svelte';

    interface Props {
        role: 'user' | 'assistant';
        content: string;
        streaming?: boolean;
    }

    let { role, content, streaming = false } = $props<Props>();

    // Configure marked for clean output
    marked.setOptions({ breaks: true, gfm: true });

    let DOMPurify: any = null;
    if (browser) {
        import('dompurify').then(module => {
            DOMPurify = module.default;
        });
    }

    function renderMd(text: string): string {
        const html = marked.parse(text) as string;
        if (browser && DOMPurify) {
            return DOMPurify.sanitize(html, {
                ADD_TAGS: ['img', 'table', 'th', 'td', 'tr', 'thead', 'tbody'],
                ADD_ATTR: ['src', 'alt', 'title', 'href', 'target', 'rel']
            });
        }
        return html;
    }

    let tokens = $derived(content ? marked.lexer(content) : []);
</script>

<div class="msg-row {role}">
    <div class="msg-bubble {role}">
        {#if role === 'user'}
            <div class="whitespace-pre-wrap">{content}</div>
        {:else}
            <!-- Assistant styling -->
            <div class="msg-meta">
                <span>Data Analyst Agent</span>
                <span>·</span>
                <span>{streaming ? 'thinking…' : 'done'}</span>
            </div>

            {#if !content && streaming}
                <!-- Typing indicator before first token -->
                <span class="inline-flex gap-[5px] items-center h-5 mt-1">
                    <span class="typing-dot" style="animation-delay: 0ms"></span>
                    <span class="typing-dot" style="animation-delay: 160ms"></span>
                    <span class="typing-dot" style="animation-delay: 320ms"></span>
                </span>
            {:else if content}
                <!-- Progressive markdown render -->
                <div class="prose-agent flex flex-col">
                    {#each tokens as token, i (i)}
                        <div class="md-block">
                            {@html renderMd(token.raw)}
                        </div>
                    {/each}
                </div>
            {/if}
        {/if}
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
    .prose-agent :global(h1) { font-size: 1.25em; }
    .prose-agent :global(h2) { font-size: 1.15em; }
    .prose-agent :global(h3) { font-size: 1.05em; }
    .prose-agent :global(h4) { font-size: 1em; font-weight: 500; }

    .prose-agent :global(p) {
        margin: 0.65em 0;
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
        padding: 0.15em 0.4em;
        border-radius: 5px;
        font-family: var(--font-mono);
        font-size: 0.88em;
        border: 1px solid var(--color-border);
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
        font-size: 0.85em;
    }

    .prose-agent :global(table) {
        width: 100%;
        border-collapse: collapse;
        margin: 0.85em 0;
        font-size: 0.9em;
    }

    .prose-agent :global(th) {
        background: var(--color-surface-elevated);
        color: var(--color-text-secondary);
        font-weight: 600;
        text-align: left;
        padding: 0.5em 0.8em;
        border: 1px solid var(--color-border);
        letter-spacing: 0.01em;
    }

    .prose-agent :global(td) {
        padding: 0.45em 0.8em;
        border: 1px solid var(--color-border-subtle);
        color: var(--color-text-primary);
    }

    .prose-agent :global(strong) {
        color: var(--color-text-primary);
        font-weight: 650;
    }
</style>
