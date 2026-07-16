<script lang="ts">
    import { IconSparkles } from '@tabler/icons-svelte';
</script>

<div class="flex flex-col items-center justify-center h-64 text-center gap-4">
    <div class="w-12 h-12 rounded-2xl bg-surface border border-border flex items-center justify-center shadow-sm">
        <IconSparkles size={20} stroke={1.5} class="text-accent" />
    </div>
    <div class="flex flex-col gap-1">
        <p class="text-text-secondary text-[14px] font-medium tracking-[-0.01em]">Start a conversation</p>
        <p class="text-muted text-[12.5px] leading-relaxed max-w-[280px]">Ask about patient data, generate reports, or run analysis.</p>
    </div>
</div>
