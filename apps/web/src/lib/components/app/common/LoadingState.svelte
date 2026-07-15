<script lang="ts">
	import { IconLoader2 } from '@tabler/icons-svelte';

	interface Props {
		text?: string;
		fullPage?: boolean;
		class?: string;
	}

	let { text = 'Loading...', fullPage = false, class: className = '' } = $props();
</script>

<div
	class="flex flex-col items-center justify-center gap-3 text-muted {className}"
	class:min-h-[50vh]={fullPage}
	class:h-full={!fullPage}
	class:w-full={!fullPage}
>
	<IconLoader2 size={24} class="animate-spin text-accent" />
	{#if text}
		<span class="text-[13px] font-medium">{text}</span>
	{/if}
</div>
