<script lang="ts">
    import { type Snippet } from 'svelte';

    interface Props {
        columns?: 1 | 2 | 3 | 4;
        gap?: 'sm' | 'md' | 'lg';
        children: Snippet;
        class?: string;
    }

    let { columns = 3, gap = 'md', children, class: className = '' } = $props();

    const columnClasses = {
        1: 'grid-cols-1',
        2: 'grid-cols-1 md:grid-cols-2',
        3: 'grid-cols-1 md:grid-cols-2 xl:grid-cols-3',
        4: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4'
    };

    const gapClasses = {
        sm: 'gap-3',
        md: 'gap-4',
        lg: 'gap-6'
    };
</script>

<div class="grid {columnClasses[columns]} {gapClasses[gap]} {className}">
    {@render children()}
</div>
