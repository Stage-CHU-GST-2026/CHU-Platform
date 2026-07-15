<script lang="ts">
	import { page } from '$app/stores';
	import { IconDotsVertical, IconLayoutSidebarRight } from '@tabler/icons-svelte';

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
			{ label: 'CHU-Platform', isLast: false },
			{ label: current, isLast: true }
		];
	});
</script>

<header class="topbar bg-canvas border-b border-border-subtle flex items-center justify-between px-4 z-[var(--z-topbar)]">
	<!-- Left: Breadcrumb -->
	<div class="flex items-center text-[13px]">
		{#each breadcrumbs as crumb, i}
			{#if i > 0}
				<span class="mx-2 text-border font-light">/</span>
			{/if}
			<span class={crumb.isLast ? 'text-text-secondary font-medium' : 'text-muted'}>
				{crumb.label}
			</span>
		{/each}
	</div>

	<!-- Right: Actions -->
	<div class="flex items-center gap-1">
		<button
			class="w-6 h-6 rounded-md flex items-center justify-center text-muted hover:text-text-secondary hover:bg-surface-hover transition-colors"
			aria-label="More options"
		>
			<IconDotsVertical size={16} stroke={1.5} />
		</button>
		
		<button
			class="w-6 h-6 rounded-md flex items-center justify-center text-muted hover:text-text-secondary hover:bg-surface-hover transition-colors"
			aria-label="Toggle right panel"
		>
			<IconLayoutSidebarRight size={16} stroke={1.5} />
		</button>
	</div>
</header>

<style>
	.topbar {
		grid-area: topbar;
		height: var(--topbar-height);
	}
</style>
