<script lang="ts">
	import { app } from '$lib/state/app.svelte';
	import { goto } from '$app/navigation';
	import { clickOutside, trapFocus } from './common/actions';
	import { IconRobot, IconMessages, IconDatabase, IconSearch } from '@tabler/icons-svelte';

	let query = $state('');
	let selectedIndex = $state(0);
	let inputEl: HTMLInputElement;

	$effect(() => {
		if (app.cmdPaletteOpen) {
			query = '';
			selectedIndex = 0;
			if (inputEl) setTimeout(() => inputEl.focus(), 50);
		}
	});

	// Global keyboard shortcut
	$effect(() => {
		const handleGlobalKeydown = (e: KeyboardEvent) => {
			if (e.key === 'k' && (e.metaKey || e.ctrlKey)) {
				e.preventDefault();
				app.cmdPaletteOpen ? app.closeCommandPalette() : app.openCommandPalette();
			}
		};
		document.addEventListener('keydown', handleGlobalKeydown);
		return () => document.removeEventListener('keydown', handleGlobalKeydown);
	});

	const groups = [
		{
			label: 'Navigation',
			items: [
				{ id: 'nav-dashboard', label: 'Go to Dashboard', action: () => goto('/dashboard') },
				{ id: 'nav-agents', label: 'Go to AI Agents', action: () => goto('/agents') },
				{ id: 'nav-convos', label: 'Go to Conversations', action: () => goto('/conversations') },
				{ id: 'nav-datasets', label: 'Go to Datasets', action: () => goto('/dashboard/datasets') },
				{ id: 'nav-settings', label: 'Go to Settings', action: () => goto('/dashboard/settings') }
			]
		},
		{
			label: 'Quick Actions',
			items: [
				{ id: 'action-theme', label: 'Toggle Dark/Light Mode', action: () => app.toggleTheme() },
				{
					id: 'action-agent',
					label: 'Create New Agent',
					icon: IconRobot,
					action: () => {
						goto('/dashboard');
					}
				},
				{
					id: 'action-chat',
					label: 'New Conversation',
					icon: IconMessages,
					action: () => {
						goto('/dashboard/new-chat');
					}
				},
				{
					id: 'action-dataset',
					label: 'Upload Dataset',
					icon: IconDatabase,
					action: () => {
						goto('/dashboard/datasets');
					}
				}
			]
		}
	];

	let filteredGroups = $derived.by(() => {
		if (!query) return groups;
		const q = query.toLowerCase();

		return groups
			.map((group) => ({
				...group,
				items: group.items.filter((item) => item.label.toLowerCase().includes(q))
			}))
			.filter((group) => group.items.length > 0);
	});

	let flatItems = $derived(filteredGroups.flatMap((g) => g.items));

	function handleKeydown(e: KeyboardEvent) {
		if (!app.cmdPaletteOpen) return;

		if (e.key === 'Escape') {
			app.closeCommandPalette();
		} else if (e.key === 'ArrowDown') {
			e.preventDefault();
			selectedIndex = (selectedIndex + 1) % flatItems.length;
		} else if (e.key === 'ArrowUp') {
			e.preventDefault();
			selectedIndex = (selectedIndex - 1 + flatItems.length) % flatItems.length;
		} else if (e.key === 'Enter') {
			e.preventDefault();
			if (flatItems.length > 0) {
				const item = flatItems[selectedIndex];
				item.action();
				app.closeCommandPalette();
			}
		}
	}
</script>

<svelte:window onkeydown={handleKeydown} />

{#if app.cmdPaletteOpen}
	<div
		class="fixed inset-0 z-[var(--z-modal)] bg-black/50 backdrop-blur-sm flex items-start justify-center pt-[15vh] p-4 animate-in fade-in duration-200"
		role="presentation"
	>
		<div
			class="bg-surface border border-border rounded-lg shadow-2xl w-full max-w-2xl max-h-[70vh] flex flex-col overflow-hidden animate-in zoom-in-95 duration-200"
			role="dialog"
			aria-modal="true"
			aria-label="Command Palette"
			use:clickOutside={() => app.closeCommandPalette()}
			use:trapFocus={app.cmdPaletteOpen}
			tabindex="-1"
		>
			<div class="flex items-center px-4 border-b border-border bg-surface-elevated">
				<IconSearch size={20} class="text-muted shrink-0" />
				<input
					bind:this={inputEl}
					bind:value={query}
					type="text"
					placeholder="Search commands, navigate, or ask AI..."
					class="w-full h-14 bg-transparent border-none outline-none px-3 text-[15px] text-text-primary placeholder:text-muted"
				/>
				<div class="flex items-center gap-1 shrink-0">
					<kbd
						class="font-sans text-[10px] text-muted bg-canvas border border-border rounded px-1.5 py-0.5"
						>ESC</kbd
					>
				</div>
			</div>

			<div class="flex-1 overflow-y-auto p-2">
				{#if filteredGroups.length === 0}
					<div class="py-8 text-center text-muted text-[13px]">
						No results found for "{query}"
					</div>
				{:else}
					{@const allItems = flatItems}
					{#each filteredGroups as group}
						<div
							class="px-3 py-2 mt-2 first:mt-0 text-[11px] font-semibold text-text-secondary uppercase tracking-wider"
						>
							{group.label}
						</div>

						{#each group.items as item}
							{@const globalIndex = allItems.indexOf(item)}
							<button
								class="w-full text-left px-3 py-2.5 rounded-md flex items-center gap-3 transition-colors"
								class:bg-accent={globalIndex === selectedIndex}
								class:text-white={globalIndex === selectedIndex}
								class:text-text-primary={globalIndex !== selectedIndex}
								class:hover:bg-surface-hover={globalIndex !== selectedIndex}
								onclick={() => {
									item.action();
									app.closeCommandPalette();
								}}
								onmouseenter={() => (selectedIndex = globalIndex)}
							>
								{#if item.icon}
									<item.icon
										size={16}
										class={globalIndex === selectedIndex ? 'text-white' : 'text-muted'}
									/>
								{:else}
									<div class="w-4 h-4"></div>
								{/if}
								<span class="text-[13px] font-medium">{item.label}</span>

								{#if globalIndex === selectedIndex}
									<IconSearch size={14} class="ml-auto opacity-50" />
								{/if}
							</button>
						{/each}
					{/each}
				{/if}
			</div>

			<div
				class="px-4 py-3 bg-surface-elevated border-t border-border flex items-center justify-between text-[11px] text-muted"
			>
				<div class="flex items-center gap-4">
					<span class="flex items-center gap-1">
						<kbd class="font-sans bg-canvas border border-border rounded px-1">↑</kbd>
						<kbd class="font-sans bg-canvas border border-border rounded px-1">↓</kbd>
						to navigate
					</span>
					<span class="flex items-center gap-1">
						<kbd class="font-sans bg-canvas border border-border rounded px-1">↵</kbd>
						to select
					</span>
				</div>
				<span>CHU Analytics Platform</span>
			</div>
		</div>
	</div>
{/if}
