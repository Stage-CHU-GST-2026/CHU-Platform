<script lang="ts">
	import { createConversation } from '$lib/api/chat';
	import { goto } from '$app/navigation';
	import ChatComposer from '$lib/components/app/chat/ChatComposer.svelte';
	import type { DatasetSummary } from '$lib/api/datasets';

	let input = $state('');
	let isSubmitting = $state(false);
	let selectedDataset = $state<DatasetSummary | null>(null);

	async function submit() {
		const text = input.trim();
		if (!text || isSubmitting) return;

		isSubmitting = true;
		try {
			// Create a new conversation, optionally linked to a dataset
			const conv = await createConversation(
				selectedDataset ? `Dataset: ${selectedDataset.original_filename}` : undefined,
				selectedDataset?.id
			);
			// Navigate to conversation route with initial prompt
			await goto(`/dashboard/conversation?id=${conv.id}&q=${encodeURIComponent(text)}`);
		} catch (error) {
			console.error('Failed to create conversation', error);
			isSubmitting = false;
		}
	}
</script>

<svelte:head>
	<title>Dashboard | CHU Platform</title>
	<meta
		name="description"
		content="Manage your data analytics, models, and workflows in the CHU Platform dashboard."
	/>
</svelte:head>

<div
	class="flex flex-col items-center justify-center h-full w-full min-h-[calc(100vh-var(--topbar-height))] relative z-10 bg-bg"
>
	<div class="w-full max-w-[720px] flex flex-col items-center px-4 -mt-10">
		<!-- Hero Header -->
		<div class="flex flex-col items-center gap-3 mb-8 w-full">
			<h1
				class="text-3xl md:text-4xl font-semibold tracking-[-0.025em] leading-tight text-center text-text-primary"
			>
				Ask anything about your data
			</h1>

			<p class="text-sm md:text-base leading-relaxed text-text-secondary max-w-[500px] text-center">
				Intelligent workspace for business analytics. Generate insights, explore trends, and make
				data-driven decisions.
			</p>
		</div>

		<!-- Unified Composer -->
		<div class="w-full flex flex-col items-center">
			<ChatComposer bind:input isStreaming={isSubmitting} onsubmit={submit} bind:selectedDataset />

			<!-- Hint text -->
			<p class="mt-3 text-xs text-muted tracking-tight flex items-center gap-1.5 opacity-80">
				Press <kbd
					class="px-1.5 py-0.5 rounded border border-border bg-surface text-[10px]"
					>Enter</kbd
				> to send
			</p>
		</div>
	</div>
</div>
