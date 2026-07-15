<script lang="ts">
    import type { Component } from 'svelte';

    export interface TabItem {
        id: string;
        label: string;
        icon?: Component<any>;
        disabled?: boolean;
    }

    interface Props {
        tabs: TabItem[];
        active: string;
        onchange?: (id: string) => void;
        class?: string;
    }

    let { tabs, active = $bindable(), onchange, class: className = '' } = $props();

    // To track positions for the animated underline
    let tabElements = $state<Record<string, HTMLElement>>({});
    let indicatorStyle = $state('');

    $effect(() => {
        const el = tabElements[active];
        if (el) {
            indicatorStyle = `width: ${el.offsetWidth}px; transform: translateX(${el.offsetLeft}px);`;
        }
    });

    function selectTab(id: string, disabled: boolean = false) {
        if (disabled) return;
        active = id;
        onchange?.(id);
    }
</script>

<div class="relative border-b border-border flex items-center {className}" role="tablist">
    {#each tabs as tab (tab.id)}
        <button
            bind:this={tabElements[tab.id]}
            role="tab"
            aria-selected={active === tab.id}
            aria-controls="panel-{tab.id}"
            disabled={tab.disabled}
            class="h-10 px-4 text-[13px] font-medium transition-colors flex items-center gap-2 relative z-10"
            class:text-text-primary={active === tab.id}
            class:text-text-secondary={active !== tab.id}
            class:hover:text-text-primary={active !== tab.id && !tab.disabled}
            class:opacity-50={tab.disabled}
            class:cursor-not-allowed={tab.disabled}
            onclick={() => selectTab(tab.id, tab.disabled)}
        >
            {#if tab.icon}
                <tab.icon size={16} />
            {/if}
            {tab.label}
        </button>
    {/each}
    
    <!-- Animated underline -->
    <div
        class="absolute bottom-0 left-0 h-[2px] bg-accent transition-all duration-300 ease-out z-20"
        style={indicatorStyle}
    ></div>
</div>
