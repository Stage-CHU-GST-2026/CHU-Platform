<script lang="ts">
    import AppShell from '$lib/components/app/shell/AppShell.svelte';

    let { children } = $props();
</script>

<AppShell>
    {@render children()}
</AppShell>
