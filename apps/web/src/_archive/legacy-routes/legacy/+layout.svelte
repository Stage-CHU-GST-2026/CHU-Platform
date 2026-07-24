<script lang="ts">
    import { AppShell } from '$lib/components/app';

    let { children } = $props();
</script>

<AppShell>
    {@render children()}
</AppShell>
