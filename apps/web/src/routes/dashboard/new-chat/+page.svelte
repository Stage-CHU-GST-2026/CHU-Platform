<script lang="ts">
	import { createConversation } from '$lib/api/chat';
	import { goto } from '$app/navigation';
	import ChatComposer from '$lib/components/app/chat/ChatComposer.svelte';
	import type { DatasetSummary } from '$lib/api/datasets';
	import { t, m, getPromptLanguageInstruction } from '$lib/i18n';

	let input = $state('');
	let isSubmitting = $state(false);
	let selectedDataset = $state<DatasetSummary | null>(null);

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
</script>

<svelte:head>
	<title>{t(m.nav_new_chat)} | CHU Platform</title>
	<meta name="description" content={t(m.chat_hero_subtitle)} />
</svelte:head>

<div
	class="flex flex-col items-center justify-center h-full w-full min-h-[calc(100vh-var(--topbar-height))]"
>
	<div class="w-full max-w-[760px] flex flex-col items-center px-4 -mt-16">
		<!-- Hero -->
		<div class="flex flex-col items-center gap-2.5 mb-8 text-center">
			<h1
				class="text-[32px] md:text-[40px] font-semibold tracking-[-0.02em] leading-[1.15] text-text-primary"
				style="font-family: 'Cormorant Garamond', serif;"
			>
				{t(m.chat_hero_title)}
			</h1>
			<p class="text-[14px] md:text-[15px] text-text-secondary max-w-[460px] leading-relaxed">
				{t(m.chat_hero_subtitle)}
			</p>
		</div>

		<!-- Composer -->
		<div class="w-full">
			<ChatComposer
				bind:input
				isStreaming={isSubmitting}
				onsubmit={submit}
				bind:selectedDataset
				showModelSelector={false}
				showMicrophone={false}
				size="large"
			/>
		</div>
	</div>
</div>
