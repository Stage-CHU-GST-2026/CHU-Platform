<script lang="ts">
    import { IconFolder, IconChevronDown, IconPlus, IconMicrophone, IconDeviceDesktop, IconSparkles } from '@tabler/icons-svelte';
</script>

<div class="flex flex-col items-center justify-center h-full w-full min-h-[calc(100vh-var(--topbar-height))]">
    <div class="w-full max-w-[720px] flex flex-col items-center px-4 -mt-16">
        <!-- Project Selector -->
        <button class="flex items-center text-text-secondary hover:text-text-primary transition-colors mb-3 px-3 py-1.5 rounded-md hover:bg-surface-hover">
            <IconFolder size={18} stroke={1.5} class="mr-2" />
            <span class="text-[13px] font-medium mr-1">CHU-Platform</span>
            <IconChevronDown size={14} stroke={2} class="opacity-70" />
        </button>
        
        <!-- Input Box -->
        <div class="w-full bg-surface border border-border-subtle rounded-[16px] overflow-hidden flex flex-col shadow-sm focus-within:border-border transition-colors">
            
            <!-- Text Input Area -->
            <div class="px-4 pt-4 pb-2">
                <textarea 
                    class="w-full bg-transparent text-text-primary placeholder-muted resize-none focus:outline-none focus:ring-0 border-0 shadow-none p-0 text-[15px] leading-relaxed max-h-36 overflow-y-auto"
                    placeholder="Ask anything, @ to mention, / for actions"
                    rows="1"
                    oninput={(e) => {
                        const target = e.currentTarget;
                        target.style.height = 'auto';
                        target.style.height = target.scrollHeight + 'px';
                    }}
                ></textarea>
            </div>
            
            <!-- Middle Row: Tools & Model -->
            <div class="px-3 pb-1 flex items-center justify-between">
                <div class="flex items-center gap-1">
                    <button class="w-6 h-6 flex items-center justify-center rounded-md hover:bg-surface-hover text-text-secondary hover:text-text-primary transition-colors" aria-label="Add attachment">
                        <IconPlus size={18} stroke={2} />
                    </button>
                    
                    <button class="flex items-center gap-1.5 px-2 h-6 rounded-md hover:bg-surface-hover text-text-secondary hover:text-text-primary transition-colors text-[12.5px] font-medium">
                        <IconSparkles size={14} stroke={1.5} />
                        Gemini 3.1 Pro (High)
                        <IconChevronDown size={14} stroke={2} class="opacity-70 ml-0.5" />
                    </button>
                </div>
                
                <button class="w-6 h-6 flex items-center justify-center rounded-full bg-surface-elevated hover:bg-border text-text-secondary hover:text-text-primary transition-colors mr-1" aria-label="Voice input">
                    <IconMicrophone size={16} stroke={1.5} />
                </button>
            </div>

            <!-- Bottom Row: Execution Environment -->
            <div class="px-3 pb-3 flex items-center">
                <button class="flex items-center gap-1.5 px-2 h-[26px] rounded-md hover:bg-surface-hover text-muted hover:text-text-secondary transition-colors text-[11.5px] font-medium">
                    <IconDeviceDesktop size={14} stroke={1.5} />
                    Local
                    <IconChevronDown size={12} stroke={2} class="opacity-70 ml-0.5" />
                </button>
            </div>
            
        </div>
    </div>
</div>
