<script lang="ts">
    import { IconFolder, IconChevronDown, IconPlus, IconMicrophone, IconDeviceDesktop, IconSparkles } from '@tabler/icons-svelte';
    import { createConversation } from '$lib/api/chat';
    import { goto } from '$app/navigation';

    let input = $state('');
    let isSubmitting = $state(false);

    async function submit() {
        const text = input.trim();
        if (!text || isSubmitting) return;

        isSubmitting = true;
        try {
            // Create a new conversation
            const conv = await createConversation();
            // Navigate to conversation route with initial prompt
            await goto(`/dashboard/conversation?id=${conv.id}&q=${encodeURIComponent(text)}`);
        } catch (error) {
            console.error('Failed to create conversation', error);
            isSubmitting = false;
        }
    }

    function onKeyDown(e: KeyboardEvent) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            submit();
        }
    }
</script>

<div class="flex flex-col items-center justify-center h-full w-full min-h-[calc(100vh-var(--topbar-height))]">
    <div class="w-full max-w-[760px] flex flex-col items-center px-4 -mt-12">

        <!-- Hero Header -->
        <div class="flex flex-col items-center gap-5 mb-8 w-full">
            <div class="flex items-center gap-2 text-[13px] font-medium text-success tracking-wide">
                <span class="w-1.5 h-1.5 rounded-full bg-success opacity-80 shadow-[0_0_8px_var(--color-success)]"></span>
                v1.0 — Analytical Workspace
            </div>
            
            <h1 class="text-4xl md:text-[56px] font-black tracking-[-0.03em] leading-[1.05] text-text-primary max-w-[700px] text-center">
                The interface exists&nbsp;to support&nbsp;thinking.
            </h1>
            
            <p class="text-[16px] md:text-[17px] leading-[1.65] text-text-secondary max-w-[580px] mt-2 font-light text-center">
                A calm, focused environment where data is the primary content and AI acts as an invisible expert. Ask a question to begin.
            </p>
        </div>



        <!-- Input Box -->
        <div class="w-full bg-surface border border-border-subtle rounded-2xl overflow-hidden flex flex-col shadow-sm focus-within:border-border transition-colors duration-150">
            
            <!-- Text Input Area -->
            <div class="px-5 pt-4 pb-2">
                <textarea 
                    bind:value={input}
                    onkeydown={onKeyDown}
                    disabled={isSubmitting}
                    class="w-full bg-transparent text-text-primary placeholder-text-secondary resize-none focus:outline-none focus:ring-0 border-0 shadow-none p-0 text-[16px] md:text-[17px] leading-[1.65] max-h-[300px] overflow-y-auto tracking-[-0.005em] min-h-[60px]"
                    placeholder="Ask anything, @ to mention, / for actions…"
                    rows="2"
                    oninput={(e) => {
                        const target = e.currentTarget;
                        target.style.height = 'auto';
                        target.style.height = target.scrollHeight + 'px';
                    }}
                ></textarea>
            </div>
            
            <!-- Bottom Row: Tools, Model & Actions -->
            <div class="px-2.5 pb-2.5 flex items-center justify-between">
                <div class="flex items-center gap-0.5">
                    <button class="w-6 h-6 flex items-center justify-center rounded-md hover:bg-surface-hover text-muted hover:text-text-secondary transition-colors" aria-label="Add attachment">
                        <IconPlus size={14} stroke={2} />
                    </button>
                    
                    <button class="flex items-center gap-1 px-2 h-6 rounded-md hover:bg-surface-hover text-muted hover:text-text-secondary transition-colors text-[11.5px] font-medium tracking-[-0.01em]">
                        <IconSparkles size={11} stroke={1.5} class="text-accent" />
                        Gemini 3.1 Pro (High)
                        <IconChevronDown size={10} stroke={2} class="opacity-50" />
                    </button>

                    <button class="flex items-center gap-1 px-2 h-6 rounded-md hover:bg-surface-hover text-muted hover:text-text-secondary transition-colors text-[11.5px] font-medium tracking-[-0.01em]">
                        <IconDeviceDesktop size={12} stroke={1.5} />
                        Local
                        <IconChevronDown size={10} stroke={2} class="opacity-50" />
                    </button>
                </div>
                
                <button class="w-6 h-6 flex items-center justify-center rounded-full hover:bg-surface-hover text-muted hover:text-text-secondary transition-colors" aria-label="Voice input">
                    <IconMicrophone size={13} stroke={1.5} />
                </button>
            </div>
            
        </div>

        <!-- Hint text -->
        <p class="mt-3 text-[11.5px] text-muted text-center tracking-wide">
            Press <kbd class="px-1.5 py-0.5 rounded-md bg-surface border border-border-subtle text-[10.5px] font-mono">Enter</kbd> to send
            · <kbd class="px-1.5 py-0.5 rounded-md bg-surface border border-border-subtle text-[10.5px] font-mono">Shift+Enter</kbd> for a new line
        </p>

    </div>
</div>
