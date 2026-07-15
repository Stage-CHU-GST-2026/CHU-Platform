<script lang="ts">
	import { type Snippet } from 'svelte';
	import { clickOutside, trapFocus } from './actions';
	import { IconX } from '@tabler/icons-svelte';

	interface Props {
		open: boolean;
		title?: string;
		children: Snippet;
		footer?: Snippet;
		width?: string;
		position?: 'right' | 'left';
		onclose: () => void;
	}

	let { open, title, children, footer, width = 'w-96', position = 'right', onclose } = $props();

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
		class="fixed inset-0 z-[var(--z-overlay)] bg-black/40 backdrop-blur-sm animate-in fade-in duration-200"
		role="presentation"
	>
		<div
			class="fixed top-0 bottom-0 {position === 'right'
				? 'right-0'
				: 'left-0'} bg-surface border-l border-border {width} shadow-2xl flex flex-col transition-transform duration-300 ease-out {position ===
			'right'
				? 'translate-x-0'
				: 'translate-x-0'} animate-in {position === 'right'
				? 'slide-in-from-right-full'
				: 'slide-in-from-left-full'}"
			role="dialog"
			aria-modal="true"
			aria-labelledby={title ? 'drawer-title' : undefined}
			use:clickOutside={onclose}
			use:trapFocus={open}
			tabindex="-1"
		>
			<div class="px-5 py-4 border-b border-border flex items-center justify-between shrink-0">
				{#if title}
					<h2 id="drawer-title" class="text-[15px] font-semibold text-text-primary">{title}</h2>
				{/if}
				<button
					class="text-muted hover:text-text-primary transition-colors rounded-sm"
					onclick={onclose}
					aria-label="Close drawer"
				>
					<IconX size={20} />
				</button>
			</div>

			<div class="flex-1 overflow-y-auto">
				{@render children()}
			</div>

			{#if footer}
				<div class="px-5 py-4 border-t border-border bg-surface-elevated shrink-0">
					{@render footer()}
				</div>
			{/if}
		</div>
	</div>
{/if}
