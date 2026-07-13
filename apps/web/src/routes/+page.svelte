<script lang="ts">
	import * as Conversation from '$lib/components/ai-elements/conversation';
	import * as Message from '$lib/components/ai-elements/message';
	import * as PromptInput from '$lib/components/ai-elements/prompt-input';
	import type { Message as PromptInputMessage } from '$lib/components/ai-elements/prompt-input';
	import { sendMessage, createThread } from '$lib/api/chat';

	import MessageSquare from '@lucide/svelte/icons/message-square';

	interface MessageData {
		key: string;
		value: string;
		role: 'user' | 'assistant';
	}

	let messages = $state<MessageData[]>([]);
	let chatStatus = $state<'ready' | 'submitted' | 'streaming'>('ready');
	let threadId = $state<string | undefined>(undefined);

	async function handleSubmit(prompt: PromptInputMessage) {
		const text = prompt.text.trim();
		if (!text || chatStatus !== 'ready') return;

		// Lock the UI immediately to prevent double-submits while the
		// thread is being created / before the first token arrives.
		chatStatus = 'submitted';

		// Create thread on first message
		if (!threadId) {
			try {
				const thread = await createThread();
				threadId = thread.threadId;
			} catch (err) {
				console.error('Failed to create thread:', err);
				chatStatus = 'ready';
				return;
			}
		}

		// Add user message directly into the reactive array — don't keep a
		// separate reference to the plain object, or it'll diverge in
		// identity from the proxied version Svelte stores internally.
		messages.push({
			key: crypto.randomUUID(),
			value: text,
			role: 'user'
		});

		// Prepare a placeholder for the assistant response
		const assistantKey = crypto.randomUUID();
		messages.push({ key: assistantKey, value: '', role: 'assistant' });
		chatStatus = 'streaming';

		// Stream the response
		try {
			// sendMessage returns the thread_id confirmed by the SSE stream
			// (the backend emits it as the very first event). We must persist
			// it so subsequent messages are sent to the same conversation.
			const confirmedThreadId = await sendMessage(text, threadId, {
				onToken: (token: string) => {
					// messages is already a reactive $state array/objects,
					// so mutate in place instead of rebuilding the whole array.
					const msg = messages.find((m) => m.key === assistantKey);
					if (msg) msg.value += token;
				},
				onDone: () => {
					chatStatus = 'ready';
				},
				onError: (err: Error) => {
					console.error('Stream error:', err);
					const msg = messages.find((m) => m.key === assistantKey);
					if (msg && !msg.value) msg.value = 'Sorry, something went wrong.';
					chatStatus = 'ready';
				}
			});
			if (confirmedThreadId) threadId = confirmedThreadId;
		} catch (err) {
			console.error('Chat request failed:', err);
			const msg = messages.find((m) => m.key === assistantKey);
			if (msg) msg.value = 'Failed to connect to the server.';
			chatStatus = 'ready';
		}
	}
</script>

{#if messages.length === 0}
	<!-- ===== LANDING: Centered prompt ===== -->
	<div class="flex h-dvh flex-col items-center justify-center px-4">
		<div class="mb-8 text-center">
			<MessageSquare class="mx-auto mb-4 size-10 text-primary" />
			<h1 class="text-2xl font-semibold tracking-tight">What can I help with?</h1>
			<p class="text-muted-foreground mt-1 text-sm">
				Ask a question or describe what you're looking for.
			</p>
		</div>
		<PromptInput.Root class="w-full max-w-3xl" onSubmit={handleSubmit}>
			<PromptInput.Body>
				<PromptInput.Textarea placeholder="Type your message..." />
			</PromptInput.Body>
			<PromptInput.Toolbar class="justify-end">
				<PromptInput.Submit status={chatStatus} />
			</PromptInput.Toolbar>
		</PromptInput.Root>
	</div>
{:else}
	<!-- ===== CONVERSATION: Messages + prompt at bottom ===== -->
	<div class="flex h-dvh flex-col">
		<Conversation.Root class="flex-1 min-h-0">
			<Conversation.Content class="flex-1 gap-0 overflow-y-auto">
				<div class="mx-auto flex w-full max-w-3xl flex-col gap-4 px-4 py-6">
					{#each messages as messageData (messageData.key)}
						<Message.Root from={messageData.role}>
							<Message.Content>
								{#if messageData.role === 'assistant'}
									<Message.Response content={messageData.value} />
								{:else}
									{messageData.value}
								{/if}
							</Message.Content>
						</Message.Root>
					{/each}
				</div>
			</Conversation.Content>
			<Conversation.ScrollButton />
		</Conversation.Root>

		<div class="shrink-0 border-t bg-background px-4 py-3">
			<PromptInput.Root class="mx-auto max-w-3xl" onSubmit={handleSubmit}>
				<PromptInput.Body>
					<PromptInput.Textarea placeholder="Type your message..." />
				</PromptInput.Body>
				<PromptInput.Toolbar class="justify-end">
					<PromptInput.Submit status={chatStatus} />
				</PromptInput.Toolbar>
			</PromptInput.Root>
		</div>
	</div>
{/if}
