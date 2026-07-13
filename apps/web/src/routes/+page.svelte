<script lang="ts">
	import * as Conversation from '$lib/components/ai-elements/conversation';
	import * as Message from '$lib/components/ai-elements/message';
	import * as PromptInput from '$lib/components/ai-elements/prompt-input';
	import type { Message as PromptInputMessage } from '$lib/components/ai-elements/prompt-input';

	import MessageSquare from '@lucide/svelte/icons/message-square';

	const API_BASE = 'http://localhost:10000/api/v1';

	interface ChatMessage {
		key: string;
		role: 'user' | 'assistant';
		content: string;
	}

	let messages = $state<ChatMessage[]>([]);
	let threadId = $state<string | null>(null);
	let isLoading = $state(false);

	async function handleSubmit(input: PromptInputMessage) {
		if (isLoading || !input.text.trim()) return;

		// Ajouter le message utilisateur
		const userMsg: ChatMessage = {
			key: crypto.randomUUID(),
			role: 'user',
			content: input.text
		};
		messages = [...messages, userMsg];
		isLoading = true;

		// Créer un message assistant vide pour le streaming
		const assistantKey = crypto.randomUUID();
		const assistantMsg: ChatMessage = {
			key: assistantKey,
			role: 'assistant',
			content: ''
		};
		messages = [...messages, assistantMsg];

		try {
			// 1. Créer une nouvelle conversation si pas de threadId
			if (!threadId) {
				const res = await fetch(`${API_BASE}/chat/new`, { method: 'POST' });
				const data = await res.json();
				threadId = data.thread_id;
			}

			// 2. Envoyer le message et streamer la réponse via SSE
			const response = await fetch(`${API_BASE}/chat`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({
					message: input.text,
					thread_id: threadId
				})
			});

			const reader = response.body!.getReader();
			const decoder = new TextDecoder();
			let buffer = '';
			let currentEvent = '';

			while (true) {
				const { done, value } = await reader.read();
				if (done) break;

				buffer += decoder.decode(value, { stream: true });
				const lines = buffer.split('\n');
				buffer = lines.pop() || '';

				for (const line of lines) {
					if (line.startsWith('event: ')) {
						currentEvent = line.slice(7).trim();
						continue;
					}
					if (line.startsWith('data: ')) {
						const data = line.slice(6);
						// Ne traiter que les événements 'token'
						if (currentEvent === 'token') {
							messages = messages.map((m) =>
								m.key === assistantKey ? { ...m, content: m.content + data } : m
							);
						}
						currentEvent = '';
					}
				}
			}
		} catch (err) {
			console.error('API Error:', err);
			messages = messages.map((m) =>
				m.key === assistantKey
					? { ...m, content: '⚠️ Error: Could not reach the API. Make sure the backend is running.' }
					: m
			);
		} finally {
			isLoading = false;
		}
	}
</script>

<div class="flex h-dvh flex-col">
	<!-- Chat area: fills all remaining space -->
	<Conversation.Root class="flex-1 min-h-0">
		<Conversation.Content class="gap-4">
			{#if messages.length === 0}
				<Conversation.EmptyState
					description="Ask a question about your dataset to get started."
					title="Data Analyst Chat"
				>
					{#snippet icon()}
						<MessageSquare class="size-6" />
					{/snippet}
				</Conversation.EmptyState>
			{:else}
				{#each messages as msg (msg.key)}
					<Message.Root from={msg.role}>
						<Message.Content>{msg.content}</Message.Content>
					</Message.Root>
				{/each}
			{/if}
		</Conversation.Content>
		<Conversation.ScrollButton />
	</Conversation.Root>

	<!-- Prompt input: pinned to bottom with responsive width -->
	<div class="shrink-0 border-t bg-background px-4 py-3">
		<PromptInput.Root class="mx-auto max-w-2xl" onSubmit={handleSubmit}>
			<PromptInput.Body>
				<PromptInput.Textarea placeholder={isLoading ? 'Waiting for response...' : 'Ask about your dataset...'} />
			</PromptInput.Body>
			<PromptInput.Toolbar class="justify-end">
				<PromptInput.Submit />
			</PromptInput.Toolbar>
		</PromptInput.Root>
	</div>
</div>
