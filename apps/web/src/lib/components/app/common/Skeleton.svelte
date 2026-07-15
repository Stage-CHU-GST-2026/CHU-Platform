<script lang="ts">
    interface Props {
        width?: string;
        height?: string;
        rounded?: string;
        class?: string;
    }

    let {
        width = '100%',
        height = '1rem',
        rounded = 'rounded-md',
        class: className = ''
    } = $props();
</script>

<div 
    class="bg-surface-elevated overflow-hidden {rounded} {className}" 
    style="width: {width}; height: {height};"
    aria-hidden="true"
>
    <!-- We use the custom pulse-fade animation defined in layout.css -->
    <div class="w-full h-full animate-[pulse-fade_2s_ease-in-out_infinite] bg-border/50"></div>
</div>
