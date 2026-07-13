<script lang="ts">
	import { sendMessage, createThread } from '$lib/api/chat';

	interface MessageData {
		key: string;
		value: string;
		role: 'user' | 'assistant';
	}

	let messages = $state<MessageData[]>([]);
	let chatStatus = $state<'ready' | 'submitted' | 'streaming'>('ready');
	let threadId = $state<string | undefined>(undefined);
	let inputValue = $state('');

	async function handleSubmit(e: Event) {
		e.preventDefault();

		const text = inputValue.trim();
		if (!text || chatStatus !== 'ready') return;

		inputValue = '';
		chatStatus = 'submitted';

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

		messages.push({
			key: crypto.randomUUID(),
			value: text,
			role: 'user'
		});

		const assistantKey = crypto.randomUUID();
		messages.push({ key: assistantKey, value: '', role: 'assistant' });
		chatStatus = 'streaming';

		try {
			await sendMessage(text, threadId, {
				onToken: (token: string) => {
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
		} catch (err) {
			console.error('Chat request failed:', err);
			const msg = messages.find((m) => m.key === assistantKey);
			if (msg) msg.value = 'Failed to connect to the server.';
			chatStatus = 'ready';
		}
	}
</script>

<div class="mx-auto flex h-dvh max-w-2xl flex-col p-4">
	<h1 class="mb-2 text-lg font-semibold">Streaming test</h1>
	<p class="mb-4 text-sm text-muted-foreground">
		status: <code>{chatStatus}</code> | threadId: <code>{threadId ?? 'none'}</code>
	</p>

	<div class="flex-1 space-y-3 overflow-y-auto rounded border p-3">
		{#each messages as messageData (messageData.key)}
			<div class="rounded p-2 {messageData.role === 'user' ? 'bg-blue-50' : 'bg-gray-50'}">
				<strong class="text-xs uppercase text-muted-foreground">{messageData.role}</strong>
				<p class="whitespace-pre-wrap">{messageData.value}</p>
			</div>
		{/each}
	</div>

	<form onsubmit={handleSubmit} class="mt-4 flex gap-2">
		<input
			type="text"
			bind:value={inputValue}
			placeholder="Type a message..."
			disabled={chatStatus !== 'ready'}
			class="flex-1 rounded border px-3 py-2"
		/>
		<button
			type="submit"
			disabled={chatStatus !== 'ready' || !inputValue.trim()}
			class="rounded bg-blue-600 px-4 py-2 text-white disabled:opacity-50"
		>
			Send
		</button>
	</form>
</div>
