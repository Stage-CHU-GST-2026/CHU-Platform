<script lang="ts">
    import { IconFolder, IconChevronDown, IconPlus, IconMicrophone, IconDeviceDesktop, IconSparkles } from '@tabler/icons-svelte';
</script>

<div class="flex flex-col items-center justify-center h-full w-full min-h-[calc(100vh-var(--topbar-height))]">
    <div class="w-full max-w-[680px] flex flex-col items-center px-4 -mt-12">

        <!-- Greeting / Project Selector -->
        <div class="flex flex-col items-center gap-3 mb-6">
            <div class="w-11 h-11 rounded-2xl bg-accent/15 border border-accent/20 flex items-center justify-center shadow-sm">
                <IconSparkles size={20} stroke={1.5} class="text-accent" />
            </div>
            <button class="flex items-center text-text-secondary hover:text-text-primary transition-colors px-3 py-1.5 rounded-lg hover:bg-surface-hover gap-1.5">
                <IconFolder size={15} stroke={1.5} />
                <span class="text-[13px] font-medium tracking-[-0.01em]">CHU-Platform</span>
                <IconChevronDown size={12} stroke={2} class="opacity-50" />
            </button>
        </div>

        <!-- Input Box -->
        <div class="w-full bg-surface border border-border-subtle rounded-2xl overflow-hidden flex flex-col shadow-sm focus-within:border-border transition-colors duration-150">
            
            <!-- Text Input Area -->
            <div class="px-4 pt-3.5 pb-1.5">
                <textarea 
                    class="w-full bg-transparent text-text-primary placeholder-muted resize-none focus:outline-none focus:ring-0 border-0 shadow-none p-0 text-[13.5px] leading-[1.65] max-h-40 overflow-y-auto tracking-[-0.005em]"
                    placeholder="Ask anything, @ to mention, / for actions…"
                    rows="1"
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
