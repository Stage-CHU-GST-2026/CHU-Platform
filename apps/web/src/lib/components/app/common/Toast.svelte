<script lang="ts">
	import { app } from '$lib/state/app.svelte';
	import { IconInfoCircle, IconCheck, IconAlertTriangle, IconX } from '@tabler/icons-svelte';

	const icons = {
		info: IconInfoCircle,
		success: IconCheck,
		warning: IconAlertTriangle,
		error: IconAlertTriangle // or another error icon
	};

	const colors = {
		info: 'text-accent border-accent/20 bg-accent/5',
		success: 'text-success border-success/20 bg-success/5',
		warning: 'text-warning border-warning/20 bg-warning/5',
		error: 'text-danger border-danger/20 bg-danger/5'
	};
</script>

<div
	class="fixed bottom-4 right-4 z-[var(--z-toast)] flex flex-col gap-2 pointer-events-none"
	aria-live="polite"
>
	{#each app.toasts as toast (toast.id)}
		{@const Icon = icons[toast.type]}
		<div
			class="pointer-events-auto flex items-start gap-3 w-80 p-3 bg-surface-elevated border rounded-lg shadow-lg animate-in slide-in-from-right-full fade-in duration-300 {colors[
				toast.type
			]}"
			role="alert"
		>
			<div class="mt-0.5 shrink-0">
				<Icon size={18} />
			</div>
			<div class="flex-1">
				<h4 class="text-[13px] font-semibold text-text-primary">{toast.title}</h4>
				{#if toast.description}
					<p class="text-[12px] text-text-secondary mt-0.5">{toast.description}</p>
				{/if}
			</div>
			<button
				class="shrink-0 text-muted hover:text-text-primary transition-colors"
				onclick={() => app.dismissToast(toast.id)}
				aria-label="Dismiss"
			>
				<IconX size={16} />
			</button>
		</div>
	{/each}
</div>
