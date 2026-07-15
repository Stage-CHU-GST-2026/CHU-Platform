<script lang="ts">
    import { type Snippet } from 'svelte';

    interface Props {
        title?: string;
        action?: Snippet;
        children: Snippet;
        class?: string;
        contentClass?: string;
    }

    let { title, action, children, class: className = '', contentClass = '' } = $props();
</script>

<section class="mb-8 {className}">
    {#if title || action}
        <div class="flex items-center justify-between mb-4">
            {#if title}
                <h2 class="text-[16px] font-semibold tracking-tight text-text-primary">{title}</h2>
            {/if}
            {#if action}
                <div>{@render action()}</div>
            {/if}
        </div>
    {/if}
    
    <div class={contentClass}>
        {@render children()}
    </div>
</section>
