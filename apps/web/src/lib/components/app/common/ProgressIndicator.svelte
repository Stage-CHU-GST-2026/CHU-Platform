<script lang="ts">
    interface Props {
        value: number; // 0-100
        label?: string;
        showValue?: boolean;
        class?: string;
        barClass?: string;
    }

    let { 
        value, 
        label, 
        showValue = true, 
        class: className = '', 
        barClass = 'bg-accent' 
    } = $props();

    let clampedValue = $derived(Math.max(0, Math.min(100, value)));
</script>

<div class="flex flex-col gap-1.5 w-full {className}">
    {#if label || showValue}
        <div class="flex justify-between items-center text-[12px]">
            {#if label}
                <span class="font-medium text-text-secondary">{label}</span>
            {/if}
            {#if showValue}
                <span class="text-text-primary tabular-nums">{Math.round(clampedValue)}%</span>
            {/if}
        </div>
    {/if}
    
    <div class="w-full h-1.5 bg-surface-elevated rounded-full overflow-hidden">
        <div 
            class="h-full rounded-full transition-all duration-300 ease-out {barClass}"
            style="width: {clampedValue}%"
        ></div>
    </div>
</div>
