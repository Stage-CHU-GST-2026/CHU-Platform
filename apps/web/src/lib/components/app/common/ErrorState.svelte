<script lang="ts">
	import { IconAlertTriangle } from '@tabler/icons-svelte';
	import Button from './Button.svelte';

	interface Props {
		title: string;
		description: string;
		retryAction?: () => void;
		retryLabel?: string;
		class?: string;
	}

	let {
		title,
		description,
		retryAction,
		retryLabel = 'Try Again',
		class: className = ''
	} = $props();
</script>

<div
	class="flex flex-col items-center justify-center text-center p-8 rounded-lg border border-danger/20 bg-danger/5 {className}"
>
	<div
		class="w-12 h-12 rounded-full bg-danger/10 flex items-center justify-center text-danger mb-4"
	>
		<IconAlertTriangle size={24} />
	</div>

	<h3 class="text-[14px] font-semibold text-text-primary mb-1">{title}</h3>
	<p class="text-[13px] text-text-secondary max-w-md mx-auto mb-6">{description}</p>

	{#if retryAction}
		<Button variant="secondary" onclick={retryAction}>{retryLabel}</Button>
	{/if}
</div>
