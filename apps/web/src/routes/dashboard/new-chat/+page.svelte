<script lang="ts">
	import { createConversation } from '$lib/api/chat';
	import { goto } from '$app/navigation';
	import ChatComposer from '$lib/components/app/chat/ChatComposer.svelte';

	let input = $state('');
	let isSubmitting = $state(false);

	async function submit() {
		const text = input.trim();
		if (!text || isSubmitting) return;

		isSubmitting = true;
		try {
			// Create a new conversation
			const conv = await createConversation();
			// Navigate to conversation route with initial prompt
			await goto(`/dashboard/conversation?id=${conv.id}&q=${encodeURIComponent(text)}`);
		} catch (error) {
			console.error('Failed to create conversation', error);
			isSubmitting = false;
		}
	}
</script>

<!-- Ambient Background Glow -->
<div class="fixed inset-0 pointer-events-none z-[-1] overflow-hidden bg-bg">
	<div
		class="absolute top-[-20%] left-1/2 -translate-x-1/2 w-[800px] h-[600px] bg-accent/5 blur-[120px] rounded-full mix-blend-screen opacity-60 animate-pulse-fade"
	></div>
</div>

<div
	class="flex flex-col items-center justify-center h-full w-full min-h-[calc(100vh-var(--topbar-height))] relative z-10"
>
	<div class="w-full max-w-[760px] flex flex-col items-center px-4 -mt-12">
		<!-- Hero Header -->
		<div class="flex flex-col items-center gap-4 mb-10 w-full mt-4">
			<h1
				class="text-4xl md:text-[52px] font-black tracking-[-0.03em] leading-[1.05] max-w-[700px] text-center bg-gradient-to-br from-text-primary via-text-primary to-text-secondary bg-clip-text text-transparent pb-1"
			>
				Ask anything about<br />your data.
			</h1>

			<p
				class="text-[16px] md:text-[17px] leading-[1.65] text-text-secondary max-w-[540px] mt-2 font-light text-center"
			>
				Your intelligent workspace for business analytics. Generate insights, explore trends, and
				make data-driven decisions.
			</p>
		</div>

		<!-- Unified Composer -->
		<div class="w-full flex flex-col items-center">
			<ChatComposer bind:input isStreaming={isSubmitting} onsubmit={submit} />

			<!-- Hint text -->
			<p class="mt-4 text-[11.5px] text-muted tracking-wide flex items-center gap-2 opacity-80">
				Press <kbd
					class="px-1.5 py-0.5 rounded border border-border-subtle bg-surface font-mono text-[10px]"
					>Enter</kbd
				> to send
			</p>
		</div>
	</div>
</div>
