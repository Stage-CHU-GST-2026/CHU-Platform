<script lang="ts">
	import { page } from '$app/stores';
	import { app } from '$lib/state/app.svelte';
	import { IconDotsVertical, IconLayoutSidebar, IconLayoutSidebarRight, IconLayoutDashboard, IconFileCheck } from '@tabler/icons-svelte';

	let path = $derived($page.url.pathname);
	let isConversation = $derived(path.startsWith('/dashboard/conversation'));

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

<header class="topbar bg-[#0a0a0a] border-b border-[#1f1f1f] flex items-center justify-between px-4 z-[var(--z-topbar)] text-white">
	<!-- Left: Sidebar toggle & Breadcrumb -->
	<div class="flex items-center gap-3">
		<button
			class="w-7 h-7 rounded-md flex items-center justify-center text-gray-400 hover:text-white hover:bg-white/10 transition-colors"
			onclick={() => app.toggleSidebar()}
			aria-label="Toggle sidebar"
		>
			<IconLayoutSidebar size={16} stroke={1.5} />
		</button>
		
		<div class="flex items-center text-[13px]">
			{#each breadcrumbs as crumb, i}
				{#if i > 0}
					<span class="mx-2 text-gray-600 font-light">/</span>
				{/if}
				<span class={crumb.isLast ? 'text-gray-100 font-medium' : 'text-gray-400 font-medium'}>
					{crumb.label}
				</span>
			{/each}
		</div>
	</div>

	<!-- Right: Actions -->
	<div class="flex items-center gap-3">
		<button
			class="w-7 h-7 rounded-md flex items-center justify-center text-gray-400 hover:text-white hover:bg-white/10 transition-colors"
			aria-label="More options"
		>
			<IconDotsVertical size={16} stroke={1.5} />
		</button>
		
		<!-- Artifact Toggle -->
		{#if isConversation}
			<button 
				class="flex items-center gap-1.5 px-3 py-1.5 rounded-md text-[12px] font-medium transition-colors border border-[#262626] {app.artifactOpen ? 'bg-[#2a2a2a] text-white shadow-sm' : 'bg-[#141414] text-gray-400 hover:text-gray-200 hover:bg-[#1a1a1a]'}"
				onclick={() => app.toggleArtifact()}
			>
				<IconFileCheck size={14} stroke={1.5} />
				Artifacts
			</button>
		{/if}
	</div>
</header>

<style>
	.topbar {
		grid-area: topbar;
		height: var(--topbar-height);
	}
</style>
