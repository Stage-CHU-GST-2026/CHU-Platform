<script lang="ts">
	import { convo } from '$lib/state/conversations.svelte';
	import { page } from '$app/stores';
	import { IconMessagePlus, IconPin, IconMessage } from '@tabler/icons-svelte';

	let { children } = $props();

	function formatDate(dateStr: string) {
		const d = new Date(dateStr);
		const now = new Date();
		const diff = now.getTime() - d.getTime();

		if (diff < 1000 * 60 * 60 * 24) {
			return d.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' });
		}
		return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
	}
</script>

<div class="flex h-full w-full overflow-hidden">
	<!-- Conversation Sidebar -->
	<div class="w-64 shrink-0 border-r border-border bg-surface flex flex-col z-10">
		<div class="p-4 border-b border-border flex items-center justify-between shrink-0">
			<h2 class="text-[14px] font-semibold text-text-primary">Conversations</h2>
			<button
				class="text-accent hover:text-white hover:bg-accent p-1.5 rounded-md transition-colors"
				aria-label="New Conversation"
			>
				<IconMessagePlus size={18} />
			</button>
		</div>

		<div class="flex-1 overflow-y-auto">
			<!-- Pinned -->
			{#if convo.pinnedConversations.length > 0}
				<div class="py-2">
					<div
						class="px-4 py-1 text-[11px] font-semibold text-text-secondary uppercase tracking-wider flex items-center gap-1.5"
					>
						<IconPin size={12} /> Pinned
					</div>
					{#each convo.pinnedConversations as c}
						{@const isActive = $page.params.id === c.id}
						<a
							href="/conversations/{c.id}"
							class="flex flex-col gap-1 mx-2 my-1 px-3 py-2 rounded-lg transition-colors border border-transparent"
							class:bg-surface-elevated={isActive}
							class:border-border={isActive}
							class:hover:bg-surface-hover={!isActive}
						>
							<div class="flex justify-between items-center text-[13px]">
								<span
									class="font-medium truncate mr-2"
									class:text-text-primary={isActive}
									class:text-text-secondary={!isActive}>{c.title}</span
								>
								<span class="text-[10px] text-muted shrink-0">{formatDate(c.updatedAt)}</span>
							</div>
							{#if c.messages.length > 0}
								<span class="text-[12px] text-muted truncate"
									>{c.messages[c.messages.length - 1].content}</span
								>
							{/if}
						</a>
					{/each}
				</div>
			{/if}

			<div class="py-2">
				<div
					class="px-4 py-1 text-[11px] font-semibold text-text-secondary uppercase tracking-wider flex items-center gap-1.5"
				>
					<IconMessage size={12} /> Recent
				</div>
				{#each convo.all.filter((c) => !convo.pinned.includes(c.id)) as c}
					{@const isActive = $page.params.id === c.id}
					<a
						href="/conversations/{c.id}"
						class="flex flex-col gap-1 mx-2 my-1 px-3 py-2 rounded-lg transition-colors border border-transparent"
						class:bg-surface-elevated={isActive}
						class:border-border={isActive}
						class:hover:bg-surface-hover={!isActive}
					>
						<div class="flex justify-between items-center text-[13px]">
							<span
								class="font-medium truncate mr-2"
								class:text-text-primary={isActive}
								class:text-text-secondary={!isActive}>{c.title}</span
							>
							<span class="text-[10px] text-muted shrink-0">{formatDate(c.updatedAt)}</span>
						</div>
						{#if c.messages.length > 0}
							<span class="text-[12px] text-muted truncate"
								>{c.messages[c.messages.length - 1].content}</span
							>
						{/if}
					</a>
				{/each}
			</div>
		</div>
	</div>

	<!-- Main Content Area -->
	<div class="flex-1 min-w-0 bg-canvas relative">
		{@render children()}
	</div>
</div>
