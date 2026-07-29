<script lang="ts">
	import { app } from '$lib/state/app.svelte';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import SidebarItem from './SidebarItem.svelte';
	import { listConversations, deleteConversation, createConversation } from '$lib/api/chat';
	import type { ConversationSummary } from '$lib/api/chat';
	import { convo } from '$lib/state/conversations.svelte';
	import {
		IconPlus,
		IconLayoutDashboard,
		IconSun,
		IconMoon,
		IconMessages,
		IconTrash,
		IconLoader2,
		IconSettings,
		IconDatabase
	} from '@tabler/icons-svelte';
	import { base } from '$app/paths';

	const currentPath = $derived($page.url.pathname);
	const activeConvId = $derived($page.url.searchParams.get('id'));

	let conversations = $state<ConversationSummary[]>([]);
	let loading = $state(false);

	async function load() {
		try {
			loading = true;
			conversations = await listConversations(50);
		} catch (e) {
			// silently fail — API may not be up
		} finally {
			loading = false;
		}
	}

	onMount(load);

	// Re-fetch whenever the conversation page signals a new conversation was created
	$effect(() => {
		const _ = convo.refreshTick;
		load();
	});

	async function newConversation() {
		const conv = await createConversation();
		await load();
		goto(`/dashboard/conversation?id=${conv.id}`);
	}

	async function handleDelete(e: MouseEvent, id: string) {
		e.preventDefault();
		e.stopPropagation();
		await deleteConversation(id);
		conversations = conversations.filter((c) => c.id !== id);
		// If we deleted the active conversation, go back to dashboard
		if (activeConvId === id) goto('/dashboard/conversation');
	}

	function formatRelativeTime(dateStr: string): string {
		const diff = Date.now() - new Date(dateStr).getTime();
		const mins = Math.floor(diff / 60000);
		if (mins < 1) return 'just now';
		if (mins < 60) return `${mins}m ago`;
		const hrs = Math.floor(mins / 60);
		if (hrs < 24) return `${hrs}h ago`;
		const days = Math.floor(hrs / 24);
		if (days < 7) return `${days}d ago`;
		return new Date(dateStr).toLocaleDateString();
	}
</script>

<aside class="sidebar bg-transparent flex flex-col w-full h-full">
	<!-- Header: New Conversation button -->
	<div class="pt-5 px-4 pb-4 shrink-0 border-b border-border/60">
		<a
			href="{base}/dashboard/new-chat"
			class="inline-flex items-center justify-center gap-2 text-[13.5px] font-medium cursor-pointer transition-all duration-150 bg-surface text-text-primary border border-border hover:bg-surface-hover rounded-lg w-full !py-[10px] {app.sidebarCollapsed
				? '!justify-center !px-0'
				: '!justify-start !px-3'}"
		>
			<div class="flex items-center justify-center shrink-0">
				<IconPlus size={16} stroke={2} />
			</div>
			{#if !app.sidebarCollapsed}
				New Conversation
			{/if}
		</a>
	</div>

	<!-- Nav -->
	<nav
		class="flex-1 overflow-y-auto pt-3 px-3 pb-3 flex flex-col gap-0.5"
		role="navigation"
		aria-label="Main navigation"
	>
		<SidebarItem href="/dashboard" icon={IconLayoutDashboard} label="Dashboard" {currentPath} />
		<SidebarItem href="/dashboard/datasets" icon={IconDatabase} label="Datasets" {currentPath} />

		{#if !app.sidebarCollapsed}
			<!-- Conversations section -->
			<div class="mt-6 mb-2 px-3">
				<span class="text-[11px] font-semibold text-muted uppercase tracking-[0.06em]"
					>Conversations</span
				>
			</div>

			{#if loading}
				<div class="flex items-center gap-3 px-3 py-[9px] text-muted">
					<IconLoader2 size={16} class="animate-spin shrink-0" />
					<span class="text-[13.5px]">Loading…</span>
				</div>
			{:else if conversations.length === 0}
				<div class="px-3 py-[9px] text-[13.5px] text-muted italic">No conversations yet</div>
			{:else}
				{#each conversations as conv (conv.id)}
					{@const isActive = conv.id === activeConvId}
					<a
						href="/dashboard/conversation?id={conv.id}"
						class="group relative inline-flex items-center gap-2.5 text-[13.5px] font-medium cursor-pointer transition-colors duration-150 w-full rounded-lg px-3 py-2.5 mb-0.5 {isActive
							? 'bg-surface-hover/80 text-text-primary'
							: 'text-text-secondary hover:bg-surface-hover/50 hover:text-text-primary'}"
					>
						<div class="flex items-center justify-center shrink-0">
							<IconMessages
								size={16}
								stroke={1.5}
								class="transition-colors {isActive
									? 'text-text-primary'
									: 'text-muted group-hover:text-text-secondary'}"
							/>
						</div>
						<div class="flex-1 min-w-0">
							<span class="block truncate">
								{conv.title ?? 'New conversation'}
							</span>
							{#if conv.dataset_name}
								<span class="block text-[11px] text-muted truncate mt-0.5">
									📊 {conv.dataset_name}
								</span>
							{/if}
						</div>
						<!-- Delete button (shows on hover) -->
						<button
							class="shrink-0 opacity-0 group-hover:opacity-100 w-5 h-5 flex items-center justify-center rounded hover:text-danger transition-all"
							onclick={(e) => handleDelete(e, conv.id)}
							aria-label="Delete conversation"
						>
							<IconTrash size={11} stroke={1.5} />
						</button>
					</a>
				{/each}
			{/if}
		{/if}
	</nav>

	<!-- Footer -->
	<div class="p-3 flex flex-col gap-1 shrink-0 border-t border-border/60">
		<SidebarItem href="/dashboard/settings" icon={IconSettings} label="Settings" {currentPath} />
	</div>
</aside>
