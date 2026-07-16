<script lang="ts">
	import { page } from '$app/stores';
	import { IconDotsVertical, IconLayoutSidebarRight, IconSparkles } from '@tabler/icons-svelte';

	let path = $derived($page.url.pathname);

	// Breadcrumb logic
	let breadcrumbs = $derived.by(() => {
		const segments = path.split('/').filter(Boolean);
		let current = 'Dashboard';
		if (segments.length > 0) {
			current = segments[segments.length - 1];
			// Basic formatting: capitalize and replace dashes with spaces
			current = current.charAt(0).toUpperCase() + current.slice(1).replace(/-/g, ' ');
		}
		
		return [
			{ label: 'CHU Platform', isLast: false },
			{ label: current, isLast: true }
		];
	});
</script>

<header class="topbar bg-canvas border-b border-border-subtle flex items-center justify-between px-4 z-[var(--z-topbar)]">
	<!-- Left: Breadcrumb -->
	<div class="flex items-center gap-2">
		<div class="w-5 h-5 rounded-md bg-accent/15 flex items-center justify-center">
			<IconSparkles size={11} stroke={2} class="text-accent" />
		</div>
		<div class="flex items-center text-[13px]">
			{#each breadcrumbs as crumb, i}
				{#if i > 0}
					<span class="mx-2 text-border opacity-60">·</span>
				{/if}
				<span class={crumb.isLast ? 'text-text-secondary font-medium tracking-[-0.01em]' : 'text-muted'}>
					{crumb.label}
				</span>
			{/each}
		</div>
	</div>

	<!-- Right: Actions -->
	<div class="flex items-center gap-0.5">
		<button
			class="w-6 h-6 rounded-md flex items-center justify-center text-muted hover:text-text-secondary hover:bg-surface-hover transition-colors"
			aria-label="More options"
		>
			<IconDotsVertical size={14} stroke={1.5} />
		</button>
		
		<button
			class="w-6 h-6 rounded-md flex items-center justify-center text-muted hover:text-text-secondary hover:bg-surface-hover transition-colors"
			aria-label="Toggle right panel"
		>
			<IconLayoutSidebarRight size={14} stroke={1.5} />
		</button>
	</div>
</header>

<style>
	.topbar {
		grid-area: topbar;
		height: var(--topbar-height);
	}
</style>
