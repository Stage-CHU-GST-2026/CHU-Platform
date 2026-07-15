<script lang="ts">
    import { type Component, type Snippet } from 'svelte';
    import { clickOutside } from './actions';
    import {  } from '@tabler/icons-svelte';

    export interface DropdownItem {
        label: string;
        icon?: Component<any>;
        action?: () => void;
        separator?: boolean;
        disabled?: boolean;
    }

    interface Props {
        items: DropdownItem[];
        trigger: Snippet;
        align?: 'left' | 'right';
        width?: string;
    }

    let { items, trigger, align = 'left', width = 'w-48' } = $props();

    let open = $state(false);

    function toggle() {
        open = !open;
    }

    function close() {
        open = false;
    }

    function handleAction(action?: () => void) {
        if (action) {
            action();
            close();
        }
    }

    function handleKeydown(e: KeyboardEvent) {
        if (e.key === 'Escape') {
            close();
        }
    }
</script>

<div class="relative inline-block text-left" use:clickOutside={close} onkeydown={handleKeydown}>
    <button type="button" aria-haspopup="true" aria-expanded={open} onclick={toggle}>
        {@render trigger()}
    </button>

    {#if open}
        <div 
            class="absolute z-[var(--z-overlay)] mt-1 {width} rounded-md bg-surface-elevated border border-border shadow-md py-1 animate-in fade-in zoom-in-95 duration-100"
            class:right-0={align === 'right'}
            class:left-0={align === 'left'}
            role="menu"
            aria-orientation="vertical"
        >
            {#each items as item}
                {#if item.separator}
                    <div class="h-px bg-border my-1 mx-2"></div>
                {:else}
                    <button
                        type="button"
                        class="w-full text-left px-3 py-1.5 text-[13px] flex items-center transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                        class:text-text-primary={!item.disabled}
                        class:text-text-secondary={item.disabled}
                        class:hover:bg-surface-hover={!item.disabled}
                        class:hover:text-text-primary={!item.disabled}
                        role="menuitem"
                        disabled={item.disabled}
                        onclick={() => handleAction(item.action)}
                    >
                        {#if item.icon}
                            <item.icon size={16} class="mr-2 text-muted" />
                        {/if}
                        {item.label}
                    </button>
                {/if}
            {/each}
        </div>
    {/if}
</div>
