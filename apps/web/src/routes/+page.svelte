<script lang="ts">
    import { goto } from '$app/navigation';
    import { onMount } from 'svelte';

    onMount(() => {
        goto('/dashboard', { replaceState: true });
    });
</script>

<div class="min-h-screen flex items-center justify-center bg-bg text-muted">
    Redirecting...
</div>
