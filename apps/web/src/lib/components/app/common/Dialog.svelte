<script lang="ts">
	import { type Snippet } from 'svelte';
	import { clickOutside, trapFocus } from './actions';
	import { IconX } from '@tabler/icons-svelte';

	interface Props {
		open: boolean;
		title?: string;
		description?: string;
		children: Snippet;
		footer?: Snippet;
		width?: string;
		onclose: () => void;
	}

	let { open, title, description, children, footer, width = 'max-w-lg', onclose } = $props();

	function handleKeydown(e: KeyboardEvent) {
		if (e.key === 'Escape' && open) {
			onclose();
		}
	}

	// Prevent body scroll when open
	$effect(() => {
		if (typeof document !== 'undefined') {
			if (open) {
				document.body.style.overflow = 'hidden';
			} else {
				document.body.style.overflow = '';
			}
		}
		return () => {
			if (typeof document !== 'undefined') {
				document.body.style.overflow = '';
			}
		};
	});
</script>

<svelte:window onkeydown={handleKeydown} />

{#if open}
	<div
		class="fixed inset-0 z-[var(--z-modal)] bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 animate-in fade-in duration-200"
		role="presentation"
	>
		<div
			class="bg-surface border border-border rounded-lg shadow-lg {width} w-full max-h-[90vh] flex flex-col animate-in zoom-in-95 duration-200"
			role="dialog"
			aria-modal="true"
			aria-labelledby={title ? 'dialog-title' : undefined}
			use:clickOutside={onclose}
			use:trapFocus={open}
			tabindex="-1"
		>
			<div class="px-6 py-4 border-b border-border flex items-center justify-between shrink-0">
				<div>
					{#if title}
						<h2 id="dialog-title" class="text-[16px] font-semibold text-text-primary">{title}</h2>
					{/if}
					{#if description}
						<p class="text-[13px] text-text-secondary mt-1">{description}</p>
					{/if}
				</div>
				<button
					class="text-muted hover:text-text-primary transition-colors rounded-sm"
					onclick={onclose}
					aria-label="Close dialog"
				>
					<IconX size={20} />
				</button>
			</div>

			<div class="p-6 overflow-y-auto">
				{@render children()}
			</div>

			{#if footer}
				<div
					class="px-6 py-4 border-t border-border bg-surface-elevated rounded-b-lg flex items-center justify-end gap-3 shrink-0"
				>
					{@render footer()}
				</div>
			{/if}
		</div>
	</div>
{/if}
