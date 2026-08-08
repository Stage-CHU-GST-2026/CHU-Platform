<script lang="ts">
	import * as Card from "$lib/components/ui/card";
	import { Button } from "$lib/components/ui/button";
	import { Input } from "$lib/components/ui/input";
	import { Badge } from "$lib/components/ui/badge";
	import * as Field from "$lib/components/ui/field";
	import Settings from "@lucide/svelte/icons/settings";
	import Save from "@lucide/svelte/icons/save";

	let backendUrl = $state("http://localhost:10000");
	let agentModel = $state("gpt-4o-mini");
</script>

<div class="w-full h-full overflow-y-auto p-6 max-w-4xl mx-auto flex flex-col gap-6">
	<!-- Page Header -->
	<div class="flex flex-col gap-1">
		<div class="flex items-center gap-2">
			<Badge variant="outline" class="gap-1.5 text-xs text-primary border-primary/30 bg-primary/10">
				<Settings data-icon="inline-start" class="size-3.5" />
				Configuration
			</Badge>
		</div>
		<h1 class="text-3xl font-bold tracking-tight">Settings</h1>
		<p class="text-muted-foreground text-sm">
			Manage API endpoints, model parameters, and platform preferences.
		</p>
	</div>

	<!-- Configuration Card -->
	<Card.Root class="border-border/60">
		<Card.Header>
			<Card.Title class="text-lg">Backend Integration</Card.Title>
			<Card.Description>
				Configure the FastAPI URL proxy target and default AI model settings.
			</Card.Description>
		</Card.Header>

		<Card.Content class="flex flex-col gap-4">
			<Field.FieldGroup>
				<Field.Field>
					<Field.FieldLabel for="backend-url">Backend API Endpoint</Field.FieldLabel>
					<Input id="backend-url" type="text" bind:value={backendUrl} class="font-mono text-xs" />
				</Field.Field>

				<Field.Field>
					<Field.FieldLabel for="agent-model">Agent LLM Model</Field.FieldLabel>
					<Input id="agent-model" type="text" bind:value={agentModel} class="font-mono text-xs" />
				</Field.Field>
			</Field.FieldGroup>
		</Card.Content>

		<Card.Footer class="flex justify-end border-t border-border/40 pt-4">
			<Button variant="default" class="gap-2">
				<Save data-icon="inline-start" class="size-4" />
				Save Settings
			</Button>
		</Card.Footer>
	</Card.Root>
</div>
