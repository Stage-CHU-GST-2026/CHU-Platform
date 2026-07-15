<script lang="ts">
    import { type Snippet } from 'svelte';
    import { clickOutside } from './actions';

    interface Props {
        trigger: Snippet;
        content: Snippet;
        align?: 'left' | 'right' | 'center';
        width?: string;
    }

    let { trigger, content, align = 'center', width = 'w-64' } = $props();

    let open = $state(false);

    function toggle() {
        open = !open;
    }

    function close() {
        open = false;
    }

    function handleKeydown(e: KeyboardEvent) {
        if (e.key === 'Escape') {
            close();
        }
    }
</script>

<div class="relative inline-block text-left" use:clickOutside={close} onkeydown={handleKeydown}>
    <button type="button" aria-haspopup="dialog" aria-expanded={open} onclick={toggle}>
        {@render trigger()}
    </button>

    {#if open}
        <div 
            class="absolute z-[var(--z-overlay)] mt-2 {width} rounded-md bg-surface-elevated border border-border shadow-lg p-3 animate-in fade-in zoom-in-95 duration-150"
            class:right-0={align === 'right'}
            class:left-0={align === 'left'}
            class:left-1/2={align === 'center'}
            class:-translate-x-1/2={align === 'center'}
            role="dialog"
            aria-modal="false"
        >
            {@render content()}
        </div>
    {/if}
</div>
