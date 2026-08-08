<script lang="ts">
	import * as Sidebar from "$lib/components/ui/sidebar/index.js";
	import { Button } from "$lib/components/ui/button";
	import Plus from "@lucide/svelte/icons/plus";
	import LayoutDashboard from "@lucide/svelte/icons/layout-dashboard";
	import Database from "@lucide/svelte/icons/database";
	import MessageSquare from "@lucide/svelte/icons/message-square";
	import Settings from "@lucide/svelte/icons/settings";
	import Activity from "@lucide/svelte/icons/activity";
	import Trash2 from "@lucide/svelte/icons/trash-2";
	import Loader2 from "@lucide/svelte/icons/loader-2";
	import { page } from "$app/state";
	import { goto, invalidateAll } from "$app/navigation";
	import { deleteConversation, listConversations, type ConversationSummary } from "$lib/api/conversations";
	import { onMount } from "svelte";

	interface Props {
		conversations?: ConversationSummary[];
		activeConversationId?: string | null;
		onNewConversation?: () => void;
		onDeleteConversation?: (id: string) => void;
	}

	let {
		conversations = [],
		activeConversationId = null,
		onNewConversation,
		onDeleteConversation
	}: Props = $props();

	let isCreatingChat = $state(false);
	let localList = $state<ConversationSummary[]>([]);

	// Keep local list in sync with parent conversations prop or client fetch
	$effect(() => {
		if (conversations && conversations.length > 0) {
			localList = conversations;
		}
	});

	async function fetchLatestConversations() {
		try {
			const res = await listConversations({ limit: 50 });
			if (res.ok && res.data) {
				localList = res.data;
			}
		} catch (e) {
			console.error("Failed to list conversations:", e);
		}
	}

	onMount(() => {
		fetchLatestConversations();
	});

	// Active route check helper
	let currentPath = $derived(page.url.pathname as string);
	let isDashboardActive = $derived(currentPath === "/" || currentPath === "/dashboard");
	let isDatasetsActive = $derived(currentPath.startsWith("/datasets"));
	let isSettingsActive = $derived(currentPath.startsWith("/settings"));

	async function handleNewChat() {
		if (onNewConversation) {
			onNewConversation();
			return;
		}

		await goto("/conversations/new");
	}

	async function handleDelete(id: string) {
		if (onDeleteConversation) {
			onDeleteConversation(id);
			return;
		}

		try {
			await deleteConversation(id);
			await fetchLatestConversations();
			await invalidateAll();
			if (currentPath.includes(id)) {
				await goto("/");
			}
		} catch (e) {
			console.error("Failed to delete conversation:", e);
		}
	}
</script>

<Sidebar.Root class="h-full flex flex-col border-r border-border bg-sidebar text-sidebar-foreground">
	<!-- 1. TOP HEADER & NEW CONVERSATION BUTTON -->
	<Sidebar.Header class="p-3 pb-2 flex flex-col gap-3">
		<div class="flex items-center gap-2.5 px-1 py-1">
			<div class="flex size-8 items-center justify-center rounded-lg bg-primary text-primary-foreground font-semibold shadow-xs">
				<Activity class="size-4" />
			</div>
			<div class="flex flex-col min-w-0">
				<span class="text-sm font-semibold tracking-tight truncate">CHU AI Platform</span>
				<span class="text-[11px] text-muted-foreground truncate">Data Analyst Hub</span>
			</div>
		</div>

		<Button
			type="button"
			variant="default"
			disabled={isCreatingChat}
			onclick={handleNewChat}
			class="w-full justify-start gap-2 shadow-xs font-medium cursor-pointer"
		>
			{#if isCreatingChat}
				<Loader2 data-icon="inline-start" class="size-4 animate-spin" />
				<span>Creating...</span>
			{:else}
				<Plus data-icon="inline-start" class="size-4" />
				<span>New Conversation</span>
			{/if}
		</Button>
	</Sidebar.Header>

	<!-- 2. SEPARATOR 1 -->
	<Sidebar.Separator class="mx-3 my-1" />

	<!-- 3. MAIN NAVIGATION BUTTONS -->
	<div class="px-2 py-1">
		<Sidebar.Menu>
			<Sidebar.MenuItem>
				<Sidebar.MenuButton
					isActive={isDashboardActive}
					class="w-full justify-start gap-2 text-sm font-medium"
				>
					{#snippet child({ props })}
						<a href="/" title="Dashboard" {...props}>
							<LayoutDashboard data-icon="inline-start" class="size-4" />
							<span>Dashboard</span>
						</a>
					{/snippet}
				</Sidebar.MenuButton>
			</Sidebar.MenuItem>

			<Sidebar.MenuItem>
				<Sidebar.MenuButton
					isActive={isDatasetsActive}
					class="w-full justify-start gap-2 text-sm font-medium"
				>
					{#snippet child({ props })}
						<a href="/datasets" title="Datasets" {...props}>
							<Database data-icon="inline-start" class="size-4" />
							<span>Datasets</span>
						</a>
					{/snippet}
				</Sidebar.MenuButton>
			</Sidebar.MenuItem>
		</Sidebar.Menu>
	</div>

	<!-- 4. SEPARATOR 2 -->
	<Sidebar.Separator class="mx-3 my-1" />

	<!-- 5. SCROLLABLE CONVERSATION HISTORY LIST -->
	<Sidebar.Content class="flex-1 flex flex-col min-h-0 px-2 py-1 overflow-hidden">
		<Sidebar.Group class="flex flex-col h-full min-h-0">
			<Sidebar.GroupLabel class="text-[11px] font-semibold text-muted-foreground uppercase tracking-wider px-2 mb-1">
				Recent Conversations
			</Sidebar.GroupLabel>

			<!-- SCROLL CONTAINER FOR CONVERSATION HISTORY ONLY -->
			<div class="flex-1 overflow-y-auto min-h-0 pr-1 flex flex-col gap-0.5">
				{#if localList.length === 0}
					<div class="px-2 py-4 text-xs text-muted-foreground text-center italic">
						No conversation history yet.
					</div>
				{:else}
					{#each localList as item (item.id)}
						{@const isActive = activeConversationId === item.id || currentPath.includes(item.id)}
						<div class="group relative flex items-center w-full">
							<Sidebar.MenuButton
								isActive={isActive}
								class="w-full justify-start gap-2 text-xs font-normal pr-7 truncate"
							>
								{#snippet child({ props })}
									<a href={`/conversations/${item.id}`} title={item.title || "Untitled Conversation"} {...props}>
										<MessageSquare data-icon="inline-start" class="size-3.5 shrink-0 text-muted-foreground" />
										<span class="truncate">{item.title || "Untitled Conversation"}</span>
									</a>
								{/snippet}
							</Sidebar.MenuButton>

							<button
								type="button"
								onclick={(e) => {
									e.preventDefault();
									e.stopPropagation();
									handleDelete(item.id);
								}}
								aria-label="Delete conversation"
								class="absolute right-1 opacity-0 group-hover:opacity-100 p-1 text-muted-foreground hover:text-destructive transition-opacity rounded-md cursor-pointer"
							>
								<Trash2 class="size-3" />
							</button>
						</div>
					{/each}
				{/if}
			</div>
		</Sidebar.Group>
	</Sidebar.Content>

	<!-- 6. SEPARATOR 3 & BOTTOM SETTINGS BUTTON -->
	<Sidebar.Separator class="mx-3 my-1" />

	<Sidebar.Footer class="p-2">
		<Sidebar.Menu>
			<Sidebar.MenuItem>
				<Sidebar.MenuButton
					isActive={isSettingsActive}
					class="w-full justify-start gap-2 text-sm font-medium"
				>
					{#snippet child({ props })}
						<a href="/settings" title="Settings" {...props}>
							<Settings data-icon="inline-start" class="size-4" />
							<span>Settings</span>
						</a>
					{/snippet}
				</Sidebar.MenuButton>
			</Sidebar.MenuItem>
		</Sidebar.Menu>
	</Sidebar.Footer>
</Sidebar.Root>
