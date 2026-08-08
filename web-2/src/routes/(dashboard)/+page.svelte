<script lang="ts">
	import { Button } from "$lib/components/ui/button";
	import * as Card from "$lib/components/ui/card";
	import { Input } from "$lib/components/ui/input";
	import { Badge } from "$lib/components/ui/badge";
	import * as Field from "$lib/components/ui/field";
	import Sparkles from "@lucide/svelte/icons/sparkles";
	import ArrowRight from "@lucide/svelte/icons/arrow-right";
	import Database from "@lucide/svelte/icons/database";
	import Bot from "@lucide/svelte/icons/bot";
	import Activity from "@lucide/svelte/icons/activity";
	import MessageSquare from "@lucide/svelte/icons/message-square";
	import { createConversation } from "$lib/api/conversations";
	import { goto, invalidateAll } from "$app/navigation";

	let query = $state("");
	let isAnalyzing = $state(false);

	async function handleSubmit(e: SubmitEvent) {
		e.preventDefault();
		if (!query.trim()) return;

		isAnalyzing = true;
		try {
			const res = await createConversation();
			if (res.ok && res.data) {
				await invalidateAll();
				await goto(`/conversations/${res.data.id}`);
			}
		} catch (err) {
			console.error("Failed to start new conversation:", err);
		} finally {
			isAnalyzing = false;
		}
	}
</script>

<div class="w-full h-full overflow-y-auto p-6 max-w-4xl mx-auto flex flex-col gap-6 pt-4">
	<!-- Hero Header -->
	<div class="flex flex-col gap-2">
		<div class="flex items-center gap-2">
			<Badge variant="outline" class="gap-1.5 text-xs text-primary border-primary/30 bg-primary/10">
				<Activity data-icon="inline-start" class="size-3.5" />
				AI Data Analyst
			</Badge>
			<Badge variant="secondary" class="text-xs font-mono">
				Svelte 5
			</Badge>
		</div>
		<h1 class="text-3xl font-bold tracking-tight">Data Analyst Dashboard</h1>
		<p class="text-muted-foreground text-sm">
			Ask questions about your healthcare data, upload datasets, and stream AI analysis.
		</p>
	</div>

	<!-- Main Query Card -->
	<Card.Root class="border-border/60 shadow-xs">
		<Card.Header>
			<div class="flex items-center justify-between">
				<div class="flex items-center gap-2">
					<Bot class="size-5 text-primary" />
					<Card.Title class="text-lg">Start a New Conversation</Card.Title>
				</div>
				<Badge variant="outline" class="gap-1 text-xs">
					<Database data-icon="inline-start" class="size-3" />
					PostgreSQL Backend
				</Badge>
			</div>
			<Card.Description>
				Type a prompt or dataset metric to launch an interactive chat turn.
			</Card.Description>
		</Card.Header>

		<Card.Content class="flex flex-col gap-4">
			<form onsubmit={handleSubmit} class="flex flex-col gap-3">
				<Field.FieldGroup>
					<Field.Field>
						<Field.FieldLabel for="dashboard-query" class="sr-only">Prompt</Field.FieldLabel>
						<div class="flex gap-2">
							<Input
								id="dashboard-query"
								type="text"
								placeholder="e.g. Show monthly patient admission rates..."
								bind:value={query}
								class="flex-1 py-5"
							/>
							<Button type="submit" disabled={isAnalyzing || !query.trim()} class="px-5">
								{#if isAnalyzing}
									<Sparkles data-icon="inline-start" class="size-4 animate-spin" />
									Creating...
								{:else}
									Ask AI
									<ArrowRight data-icon="inline-end" class="size-4" />
								{/if}
							</Button>
						</div>
					</Field.Field>
				</Field.FieldGroup>
			</form>
		</Card.Content>

		<Card.Footer class="flex justify-between items-center text-xs text-muted-foreground border-t border-border/40 pt-4">
			<span class="flex items-center gap-1">
				<MessageSquare class="size-3.5" />
				Streaming enabled
			</span>
			<span class="font-mono">API Proxy: /api/v1</span>
		</Card.Footer>
	</Card.Root>
</div>
