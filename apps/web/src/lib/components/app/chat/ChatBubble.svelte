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
                    {#if streaming}
                        <div class="mt-2 flex">
                            <span class="inline-flex gap-[5px] items-center h-5 px-1">
                                <span class="typing-dot" style="animation-delay: 0ms"></span>
                                <span class="typing-dot" style="animation-delay: 160ms"></span>
                                <span class="typing-dot" style="animation-delay: 320ms"></span>
                            </span>
                        </div>
                    {/if}
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


</style>
