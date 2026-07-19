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
    <!-- Textarea at the top -->
    <textarea 
        bind:this={textareaEl}
        bind:value={input}
        class="w-full bg-transparent text-white placeholder-muted resize-none focus:outline-none focus:ring-0 border-0 shadow-none px-2 py-1 text-[16px] leading-[1.65] min-h-[30px] max-h-40 overflow-y-auto disabled:opacity-40 tracking-[-0.005em]"
        placeholder="Ask anything, @ to mention, / for actions"
        rows="1"
        disabled={isStreaming}
        onkeydown={handleKeydown}
        oninput={resizeTextarea}
    ></textarea>

    <!-- Toolbar row at the bottom -->
    <div class="flex items-center justify-between w-full px-1">
        <!-- Left side: + button & Model selector -->
        <div class="flex items-center gap-1.5">
            <button
                class="w-7 h-7 flex items-center justify-center rounded-md hover:bg-surface-hover text-muted hover:text-text-secondary transition-colors shrink-0"
                aria-label="Add attachment"
                disabled={isStreaming}
            >
                <IconPlus size={16} stroke={2} />
            </button>

            <Dropdown items={modelItems} align="left" direction="up" width="w-48">
                {#snippet trigger()}
                    <div class="flex items-center gap-1.5 px-2 h-7 rounded-md hover:bg-surface-hover text-muted hover:text-text-secondary transition-colors text-[13.5px] font-medium tracking-[-0.01em]">
                        <span>{selectedModel} 3.1 Pro (High)</span>
                        <IconChevronDown size={14} stroke={2} class="opacity-50" />
                    </div>
                {/snippet}
            </Dropdown>
        </div>

        <!-- Right side: Mic & Send button -->
        <div class="flex items-center gap-3">
            <button class="flex items-center justify-center text-muted hover:text-text-secondary transition-colors" aria-label="Voice input">
                <IconMicrophone size={16} stroke={1.5} />
            </button>

            {#if isStreaming}
                <button class="w-8 h-8 flex items-center justify-center rounded-full bg-surface hover:bg-surface-hover text-muted cursor-not-allowed" disabled aria-label="Sending">
                    <span class="w-3.5 h-3.5 rounded-full border-[2px] border-muted border-t-transparent animate-spin"></span>
                </button>
            {:else}
                <button 
                    onclick={onsubmit}
                    disabled={!input.trim()}
                    class="flex items-center justify-center w-8 h-8 rounded-full transition-colors {input.trim() ? 'bg-surface hover:bg-accent text-text-primary hover:text-white' : 'bg-surface text-muted opacity-60 cursor-not-allowed'}"
                    aria-label="Send message"
                >
                    <IconArrowRight size={16} stroke={2} />
                </button>
            {/if}
        </div>
    </div>
</div>
