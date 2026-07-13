<script lang="ts">
	import * as Conversation from '$lib/components/ai-elements/conversation';
	import * as Message from '$lib/components/ai-elements/message';
	import * as PromptInput from '$lib/components/ai-elements/prompt-input';
	import type { Message as PromptInputMessage } from '$lib/components/ai-elements/prompt-input';

	import MessageSquare from '@lucide/svelte/icons/message-square';

	interface MessageData {
		key: string;
		value: string;
		name: string;
	}

	// Static messages data using crypto.randomUUID()
	const messages: MessageData[] = [
		{
			key: crypto.randomUUID(),
			value: 'Hello, how are you?',
			name: 'Alex Johnson'
		},
		{
			key: crypto.randomUUID(),
			value: "I'm good, thank you! How can I assist you today?",
			name: 'AI Assistant'
		},
		{
			key: crypto.randomUUID(),
			value: "I'm looking for information about your services.",
			name: 'Alex Johnson'
		},
		{
			key: crypto.randomUUID(),
			value: 'Sure! We offer a variety of AI solutions. What are you interested in?',
			name: 'AI Assistant'
		},
		{
			key: crypto.randomUUID(),
			value: "I'm interested in natural language processing tools.",
			name: 'Alex Johnson'
		},
		{
			key: crypto.randomUUID(),
			value: 'Great choice! We have several NLP APIs. Would you like a demo?',
			name: 'AI Assistant'
		},
		{
			key: crypto.randomUUID(),
			value: 'Yes, a demo would be helpful.',
			name: 'Alex Johnson'
		},
		{
			key: crypto.randomUUID(),
			value: 'Alright, I can show you a sentiment analysis example. Ready?',
			name: 'AI Assistant'
		},
		{
			key: crypto.randomUUID(),
			value: 'Yes, please proceed.',
			name: 'Alex Johnson'
		},
		{
			key: crypto.randomUUID(),
			value: "Here is a sample: 'I love this product!' → Positive sentiment.",
			name: 'AI Assistant'
		},
		{
			key: crypto.randomUUID(),
			value: 'Impressive! Can it handle multiple languages?',
			name: 'Alex Johnson'
		},
		{
			key: crypto.randomUUID(),
			value: 'Absolutely, our models support over 20 languages.',
			name: 'AI Assistant'
		},
		{
			key: crypto.randomUUID(),
			value: 'How do I get started with the API?',
			name: 'Alex Johnson'
		},
		{
			key: crypto.randomUUID(),
			value: 'You can sign up on our website and get an API key instantly.',
			name: 'AI Assistant'
		},
		{
			key: crypto.randomUUID(),
			value: 'Is there a free trial available?',
			name: 'Alex Johnson'
		},
		{
			key: crypto.randomUUID(),
			value: 'Yes, we offer a 14-day free trial with full access.',
			name: 'AI Assistant'
		},
		{
			key: crypto.randomUUID(),
			value: 'What kind of support do you provide?',
			name: 'Alex Johnson'
		},
		{
			key: crypto.randomUUID(),
			value: 'We provide 24/7 chat and email support for all users.',
			name: 'AI Assistant'
		},
		{
			key: crypto.randomUUID(),
			value: 'Thank you for the information!',
			name: 'Alex Johnson'
		},
		{
			key: crypto.randomUUID(),
			value: "You're welcome! Let me know if you have any more questions.",
			name: 'AI Assistant'
		}
	];

	// Reactive state using Svelte 5 runes
	let visibleMessages = $state<MessageData[]>([]);

	// Auto-add messages effect using Svelte 5 $effect
	$effect(() => {
		let currentIndex = 0;
		const interval = setInterval(() => {
			if (currentIndex < messages.length && messages[currentIndex]) {
				const currentMessage = messages[currentIndex];
				visibleMessages = [
					...visibleMessages,
					{
						key: currentMessage.key,
						value: currentMessage.value,
						name: currentMessage.name
					}
				];
				currentIndex++;
			} else {
				clearInterval(interval);
			}
		}, 500);

		return () => clearInterval(interval);
	});

	function handleSubmit(message: PromptInputMessage) {
		console.log('Submitted message:', message.text);
		console.log('Files', message.files);
	}
</script>

<div class="flex h-dvh flex-col">
	<!-- Chat area: fills all remaining space -->
	<Conversation.Root class="flex-1 min-h-0">
		<Conversation.Content class="gap-4">
			{#if visibleMessages.length === 0}
				<Conversation.EmptyState
					description="Messages will appear here as the conversation progresses."
					title="Start a conversation"
				>
					{#snippet icon()}
						<MessageSquare class="size-6" />
					{/snippet}
				</Conversation.EmptyState>
			{:else}
				{#each visibleMessages as messageData, index (messageData.key)}
					<Message.Root from={index % 2 === 0 ? 'user' : 'assistant'}>
						<Message.Content>{messageData.value}</Message.Content>
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
				<PromptInput.Textarea placeholder="Type your message..." />
			</PromptInput.Body>
			<PromptInput.Toolbar class="justify-end">
				<PromptInput.Submit />
			</PromptInput.Toolbar>
		</PromptInput.Root>
	</div>
</div>
