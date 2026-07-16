<script lang="ts">
    import { IconChevronDown, IconPlus, IconMicrophone, IconSparkles, IconSend, IconBrain, IconMessageCircle, IconArrowRight } from '@tabler/icons-svelte';
    import Dropdown, { type DropdownItem } from '$lib/components/app/common/Dropdown.svelte';

    interface Props {
        input: string;
        isStreaming: boolean;
        onsubmit: () => void;
    }

    let { input = $bindable(), isStreaming, onsubmit } = $props<Props>();

    let textareaEl = $state<HTMLTextAreaElement | null>(null);
    let selectedModel = $state('Gemini');

    const modelItems: DropdownItem[] = [
        { label: 'Gemini', icon: IconSparkles, action: () => selectedModel = 'Gemini' },
        { label: 'Claude', icon: IconBrain, action: () => selectedModel = 'Claude' },
        { label: 'ChatGPT', icon: IconMessageCircle, action: () => selectedModel = 'ChatGPT' },
    ];

    export function resizeTextarea() {
        if (textareaEl) {
            textareaEl.style.height = 'auto';
            textareaEl.style.height = textareaEl.scrollHeight + 'px';
        }
    }

    function handleKeydown(e: KeyboardEvent) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            onsubmit();
        }
    }
</script>

<div class="composer">
    <!-- Add button -->
    <button
        class="w-6 h-6 flex items-center justify-center rounded-md hover:bg-surface-hover text-muted hover:text-text-secondary transition-colors shrink-0"
        aria-label="Add attachment"
        disabled={isStreaming}
    >
        <IconPlus size={14} stroke={2} />
    </button>

    <!-- Textarea -->
    <textarea 
        bind:this={textareaEl}
        bind:value={input}
        class="flex-1 bg-transparent text-white placeholder-muted resize-none focus:outline-none focus:ring-0 border-0 shadow-none p-0 text-[14.5px] leading-[1.65] max-h-40 overflow-y-auto disabled:opacity-40 tracking-[-0.005em]"
        placeholder="Ask anything…"
        rows="1"
        disabled={isStreaming}
        onkeydown={handleKeydown}
        oninput={resizeTextarea}
    ></textarea>

    <!-- Right side: model selector + send/mic -->
    <div class="flex items-center gap-0.5 shrink-0">
        <Dropdown items={modelItems} align="left" direction="up" width="w-36">
            {#snippet trigger()}
                <div class="flex items-center gap-1 px-2 h-6 rounded-md hover:bg-surface-hover text-muted hover:text-text-secondary transition-colors text-[11.5px] font-medium tracking-[-0.01em]">
                    {#if selectedModel === 'Gemini'}
                        <IconSparkles size={11} stroke={1.5} class="text-accent" />
                    {:else if selectedModel === 'Claude'}
                        <IconBrain size={11} stroke={1.5} />
                    {:else}
                        <IconMessageCircle size={11} stroke={1.5} />
                    {/if}
                    <span>{selectedModel}</span>
                    <IconChevronDown size={10} stroke={2} class="opacity-50" />
                </div>
            {/snippet}
        </Dropdown>

        {#if isStreaming}
            <button class="w-6 h-6 flex items-center justify-center rounded-full bg-surface-elevated text-muted cursor-not-allowed" disabled aria-label="Sending">
                <span class="w-2.5 h-2.5 rounded-full border border-muted border-t-transparent animate-spin"></span>
            </button>
        {:else if input.trim()}
            <button 
                onclick={onsubmit}
                class="flex items-center justify-center h-6 px-2.5 rounded-md bg-accent hover:opacity-90 text-white transition-opacity"
                aria-label="Send message"
            >
                <IconArrowRight size={13} stroke={2} />
            </button>
        {:else}
            <button class="w-6 h-6 flex items-center justify-center rounded-full hover:bg-surface-hover text-muted hover:text-text-secondary transition-colors" aria-label="Voice input">
                <IconMicrophone size={13} stroke={1.5} />
            </button>
        {/if}
    </div>
</div>
