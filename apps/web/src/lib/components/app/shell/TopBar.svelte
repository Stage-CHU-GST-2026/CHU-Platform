<script lang="ts">
	import { page } from '$app/stores';
	import { app } from '$lib/state/app.svelte';
	import { IconDotsVertical, IconLayoutSidebar, IconLayoutSidebarRight, IconLayoutDashboard, IconFileCheck, IconDownload, IconSun, IconMoon } from '@tabler/icons-svelte';

	let path = $derived($page.url.pathname);
	let isConversation = $derived(path.startsWith('/dashboard/conversation'));

	async function exportConversation() {
		const id = $page.url.searchParams.get('id');
		if (!id) return;
		try {
			const res = await fetch(`/api/v1/conversations/${id}`);
			if (!res.ok) throw new Error('Failed to fetch conversation');
			const data = await res.json();
			const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
			const url = URL.createObjectURL(blob);
			const a = document.createElement('a');
			a.href = url;
			a.download = `conversation-${id}.json`;
			document.body.appendChild(a);
			a.click();
			document.body.removeChild(a);
			URL.revokeObjectURL(url);
		} catch (err) {
			console.error(err);
		}
	}

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

<header class="topbar bg-surface border-b border-border flex items-center justify-between px-4 z-[var(--z-topbar)] text-text-primary">
	<!-- Left: Sidebar toggle & Breadcrumb -->
	<div class="flex items-center gap-3">
		<button
			class="w-8 h-8 rounded-md flex items-center justify-center text-text-secondary hover:text-text-primary hover:bg-surface-hover transition-colors cursor-pointer"
			onclick={() => app.toggleSidebar()}
			aria-label="Toggle sidebar"
		>
			<IconLayoutSidebar size={16} stroke={1.5} />
		</button>
		
		<div class="flex items-center text-[13px]">
			{#each breadcrumbs as crumb, i}
				{#if i > 0}
					<span class="mx-2 text-muted font-light">/</span>
				{/if}
				<span class={crumb.isLast ? 'text-text-primary font-medium' : 'text-text-secondary font-medium'}>
					{crumb.label}
				</span>
			{/each}
		</div>
	</div>

	<!-- Right: Actions -->
	<div class="flex items-center gap-3">
		{#if isConversation}
			<button
				class="w-8 h-8 rounded-md flex items-center justify-center text-text-secondary hover:text-text-primary hover:bg-surface-hover transition-colors cursor-pointer"
				title="Export conversation as JSON"
				onclick={exportConversation}
			>
				<IconDownload size={16} stroke={1.5} />
			</button>
		{/if}

		<!-- Theme Toggle Button -->
		<button
			class="w-8 h-8 rounded-md flex items-center justify-center text-text-secondary hover:text-text-primary hover:bg-surface-hover transition-colors cursor-pointer"
			title="Toggle Dark / Light Theme"
			onclick={() => app.toggleTheme()}
			aria-label="Toggle theme"
		>
			{#if app.theme === 'dark'}
				<IconSun size={16} stroke={1.5} />
			{:else}
				<IconMoon size={16} stroke={1.5} />
			{/if}
		</button>

		<button
			class="w-8 h-8 rounded-md flex items-center justify-center text-text-secondary hover:text-text-primary hover:bg-surface-hover transition-colors cursor-pointer"
			aria-label="More options"
		>
			<IconDotsVertical size={16} stroke={1.5} />
		</button>
		
		<!-- Artifact Toggle -->
		{#if isConversation}
			<button 
				class="flex items-center gap-1.5 px-3 py-1.5 rounded-md text-[12px] font-medium transition-colors border border-border cursor-pointer {app.artifactOpen ? 'bg-surface-elevated text-text-primary shadow-sm' : 'bg-surface text-text-secondary hover:text-text-primary hover:bg-surface-hover'}"
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
