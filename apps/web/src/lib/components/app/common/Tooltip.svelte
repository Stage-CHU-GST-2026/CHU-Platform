<script lang="ts">
    import { type Snippet } from 'svelte';

    interface Props {
        content: string;
        placement?: 'top' | 'bottom' | 'left' | 'right';
        children: Snippet;
        delay?: number;
    }

    let { content, placement = 'top', children, delay = 400 } = $props();

    let isVisible = $state(false);
    let timeout: ReturnType<typeof setTimeout>;

    function show() {
        timeout = setTimeout(() => {
            isVisible = true;
        }, delay);
    }

    function hide() {
        clearTimeout(timeout);
        isVisible = false;
    }

    const placementClasses = {
        top: 'bottom-full left-1/2 -translate-x-1/2 mb-2',
        bottom: 'top-full left-1/2 -translate-x-1/2 mt-2',
        left: 'right-full top-1/2 -translate-y-1/2 mr-2',
        right: 'left-full top-1/2 -translate-y-1/2 ml-2'
    };
</script>

<!-- svelte-ignore a11y_no_static_element_interactions -->
<!-- svelte-ignore a11y_mouse_events_have_key_events -->
<div 
    class="relative inline-flex"
    onmouseenter={show}
    onmouseleave={hide}
    onfocusin={show}
    onfocusout={hide}
>
    {@render children()}
    
    {#if isVisible}
        <div 
            class="absolute z-50 px-2.5 py-1.5 text-[11px] font-medium text-white bg-surface-elevated border border-border-subtle rounded-md shadow-md whitespace-nowrap pointer-events-none {placementClasses[placement]} animate-in fade-in zoom-in-95 duration-100"
            role="tooltip"
        >
            {content}
        </div>
    {/if}
</div>
