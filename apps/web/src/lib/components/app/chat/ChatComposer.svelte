<script lang="ts">
    import { IconChevronDown, IconPlus, IconMicrophone, IconSparkles, IconBrain, IconMessageCircle, IconArrowRight, IconSquare } from '@tabler/icons-svelte';
    import Dropdown, { type DropdownItem } from '$lib/components/app/common/Dropdown.svelte';

    interface Props {
        input: string;
        isStreaming: boolean;
        onsubmit: () => void;
    }

    let { input = $bindable(), isStreaming, onsubmit } = $props<Props>();

    let textareaEl = $state<HTMLTextAreaElement | null>(null);
    let selectedModel = $state('Gemini');
    let focused = $state(false);

    const modelItems: DropdownItem[] = [
        { label: 'Gemini', icon: IconSparkles, action: () => selectedModel = 'Gemini' },
        { label: 'Claude', icon: IconBrain, action: () => selectedModel = 'Claude' },
        { label: 'ChatGPT', icon: IconMessageCircle, action: () => selectedModel = 'ChatGPT' },
    ];

    let hasText = $derived(input.trim().length > 0);

    export function resizeTextarea() {
        if (textareaEl) {
            textareaEl.style.height = 'auto';
            textareaEl.style.height = textareaEl.scrollHeight + 'px';
        }
    }

    function handleKeydown(e: KeyboardEvent) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            if (hasText && !isStreaming) onsubmit();
        }
    }

    function handleStop() {
        // Reload the page to stop the current stream — the backend
        // will detect the disconnected client and abort generation.
        window.location.reload();
    }
</script>

<div class="composer {focused ? 'composer-focused' : ''}">
    <!-- Textarea at the top -->
    <textarea
        bind:this={textareaEl}
        bind:value={input}
        class="w-full bg-transparent text-text-primary placeholder-muted resize-none focus:outline-none focus:ring-0 border-0 shadow-none px-3 pt-2 text-[15.5px] leading-[1.7] min-h-[28px] max-h-48 overflow-y-auto disabled:opacity-40"
        placeholder="Ask anything..."
        rows="1"
        disabled={isStreaming}
        onkeydown={handleKeydown}
        oninput={resizeTextarea}
        onfocus={() => focused = true}
        onblur={() => focused = false}
    ></textarea>

    <!-- Toolbar row at the bottom -->
    <div class="flex items-center justify-between w-full px-1.5 pb-0.5">
        <!-- Left side: + button & Model selector -->
        <div class="flex items-center gap-1">
            <button
                class="w-8 h-8 flex items-center justify-center rounded-md hover:bg-surface-hover text-muted hover:text-text-secondary transition-colors shrink-0 cursor-pointer disabled:opacity-30"
                aria-label="Add attachment"
                disabled={isStreaming}
            >
                <IconPlus size={16} stroke={2} />
            </button>

            <Dropdown items={modelItems} align="left" direction="up" width="w-48">
                {#snippet trigger()}
                    <button class="flex items-center gap-1.5 px-2.5 h-8 rounded-md hover:bg-surface-hover text-muted hover:text-text-secondary transition-colors text-[12.5px] font-medium">
                        <IconSparkles size={14} stroke={1.5} />
                        <span>{selectedModel}</span>
                        <IconChevronDown size={12} stroke={2} class="opacity-40" />
                    </button>
                {/snippet}
            </Dropdown>

            <!-- Hint text -->
            <span class="hidden sm:inline text-[11.5px] text-muted/50 ml-2 select-none">Shift + Enter for new line</span>
        </div>

        <!-- Right side: Actions -->
        <div class="flex items-center gap-2">
            <button class="flex items-center justify-center w-8 h-8 rounded-md text-muted hover:text-text-secondary hover:bg-surface-hover transition-colors cursor-pointer" aria-label="Voice input">
                <IconMicrophone size={16} stroke={1.5} />
            </button>

            {#if isStreaming}
                <button
                    onclick={handleStop}
                    class="flex items-center justify-center gap-1.5 px-3 h-8 rounded-lg bg-surface border border-border text-text-secondary hover:bg-surface-hover hover:text-danger transition-colors cursor-pointer text-[12.5px] font-medium"
                    aria-label="Stop generating"
                >
                    <IconSquare size={12} stroke={2} />
                    Stop
                </button>
            {:else}
                <button
                    onclick={onsubmit}
                    disabled={!hasText}
                    class="flex items-center justify-center w-8 h-8 rounded-lg transition-all duration-150 cursor-pointer {hasText ? 'bg-accent text-black hover:brightness-[1.15] active:brightness-[0.95] shadow-sm' : 'bg-surface text-muted opacity-50 cursor-not-allowed'}"
                    aria-label="Send message"
                >
                    <IconArrowRight size={18} stroke={2} />
                </button>
            {/if}
        </div>
    </div>
</div>
