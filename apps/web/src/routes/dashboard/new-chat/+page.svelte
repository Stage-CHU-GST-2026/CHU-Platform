<script lang="ts">
	import { tick } from 'svelte';
	import { createConversation } from '$lib/api/chat';
	import { goto } from '$app/navigation';
	import ChatComposer from '$lib/components/app/chat/ChatComposer.svelte';
	import type { DatasetSummary } from '$lib/api/datasets';
	import {
		IconChartBar,
		IconTrendingUp,
		IconGlobe,
		IconAward,
		IconSparkles
	} from '@tabler/icons-svelte';

	let input = $state('');
	let isSubmitting = $state(false);
	let selectedDataset = $state<DatasetSummary | null>(null);

	const suggestions: { text: string; icon: typeof IconSparkles }[] = [
		{ text: 'Analyze sales trends for Q1 2026', icon: IconChartBar },
		{ text: 'Show me monthly revenue breakdown', icon: IconTrendingUp },
		{ text: 'Compare performance across regions', icon: IconGlobe },
		{ text: 'Identify top 10 customers by revenue', icon: IconAward }
	];

	async function submit() {
		const text = input.trim();
		if (!text || isSubmitting) return;

		isSubmitting = true;
		try {
			const conv = await createConversation(
				selectedDataset ? `Dataset: ${selectedDataset.original_filename}` : undefined,
				selectedDataset?.id
			);
			await goto(`/dashboard/conversation?id=${conv.id}&q=${encodeURIComponent(text)}`);
		} catch (error) {
			console.error('Failed to create conversation', error);
			isSubmitting = false;
		}
	}

	async function submitSuggestion(text: string) {
		if (isSubmitting) return;
		input = text;
		await tick();
		await submit();
	}
</script>

<svelte:head>
	<title>New Chat | CHU Platform</title>
	<meta name="description" content="Start a new conversation with the Data Analyst Agent." />
</svelte:head>

<div
	class="flex flex-col items-center justify-center h-full w-full min-h-[calc(100vh-var(--topbar-height))]"
>
	<div class="w-full max-w-[640px] flex flex-col items-center px-4 -mt-16">
		<!-- Hero -->
		<div class="flex flex-col items-center gap-3 mb-8 text-center">
			<div
				class="w-10 h-10 rounded-xl bg-surface border border-border flex items-center justify-center mb-1"
			>
				<IconSparkles size={18} stroke={1.5} class="text-accent" />
			</div>
			<h1
				class="text-[28px] md:text-[34px] font-semibold tracking-[-0.02em] leading-[1.15] text-text-primary"
				style="font-family: 'Cormorant Garamond', serif;"
			>
				What would you like to explore?
			</h1>
			<p class="text-[14px] text-text-secondary max-w-[420px] leading-relaxed">
				Ask questions about your data, generate reports, and uncover insights.
			</p>
		</div>

		<!-- Composer -->
		<div class="w-full mb-6">
			<ChatComposer bind:input isStreaming={isSubmitting} onsubmit={submit} bind:selectedDataset />
		</div>

		<!-- Suggestions -->
		<div class="w-full">
			<p class="text-[11px] font-medium text-muted uppercase tracking-[0.06em] mb-3 px-1">
				Try asking
			</p>
			<div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
				{#each suggestions as s}
					<button
						class="flex items-center gap-2.5 text-left px-3.5 py-2.5 rounded-lg border border-border bg-surface hover:bg-surface-hover text-text-secondary hover:text-text-primary transition-colors text-[13px] font-medium cursor-pointer disabled:opacity-40"
						onclick={() => submitSuggestion(s.text)}
						disabled={isSubmitting}
					>
						<svelte:component this={s.icon} size={15} stroke={1.5} class="shrink-0 text-muted" />
						<span class="truncate">{s.text}</span>
					</button>
				{/each}
			</div>
		</div>
	</div>
</div>
