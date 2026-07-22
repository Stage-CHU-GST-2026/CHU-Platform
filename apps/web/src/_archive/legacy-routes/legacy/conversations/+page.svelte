<script lang="ts">
	import EmptyState from '$lib/components/app/common/EmptyState.svelte';
	import Button from '$lib/components/app/common/Button.svelte';
	import { IconMessageCircle } from '@tabler/icons-svelte';
</script>

<svelte:head>
	<title>Conversations | CHU Analytics</title>
</svelte:head>

<div class="h-full flex items-center justify-center p-8">
	<EmptyState
		icon={IconMessageCircle}
		title="Your AI Workspace"
		description="Select a conversation from the sidebar or start a new one to interact with your specialized AI agents."
		class="border-none bg-transparent"
	>
		<Button variant="primary">New Conversation</Button>
	</EmptyState>
</div>
