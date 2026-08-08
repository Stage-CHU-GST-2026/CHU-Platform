<script lang="ts">
	import * as Card from "$lib/components/ui/card";
	import { Button } from "$lib/components/ui/button";
	import { Badge } from "$lib/components/ui/badge";
	import { Input } from "$lib/components/ui/input";
	import * as Table from "$lib/components/ui/table";
	import Database from "@lucide/svelte/icons/database";
	import Upload from "@lucide/svelte/icons/upload";
	import FileText from "@lucide/svelte/icons/file-text";

	let search = $state("");
</script>

<div class="w-full h-full overflow-y-auto p-6 max-w-5xl mx-auto flex flex-col gap-6">
	<!-- Page Header -->
	<div class="flex items-center justify-between">
		<div class="flex flex-col gap-1">
			<div class="flex items-center gap-2">
				<Badge variant="outline" class="gap-1.5 text-xs text-primary border-primary/30 bg-primary/10">
					<Database data-icon="inline-start" class="size-3.5" />
					Data Hub
				</Badge>
			</div>
			<h1 class="text-3xl font-bold tracking-tight">Datasets</h1>
			<p class="text-muted-foreground text-sm">
				Manage uploaded CSVs, Parquet files, and dataset schemas for AI analysis.
			</p>
		</div>

		<Button variant="default" class="gap-2">
			<Upload data-icon="inline-start" class="size-4" />
			Upload Dataset
		</Button>
	</div>

	<!-- Search & Filter Card -->
	<Card.Root class="border-border/60">
		<Card.Header class="pb-3">
			<div class="flex items-center justify-between">
				<Card.Title class="text-base">Registered Datasets</Card.Title>
				<Input
					type="text"
					placeholder="Search datasets..."
					bind:value={search}
					class="w-64 text-xs"
				/>
			</div>
		</Card.Header>

		<Card.Content>
			<Table.Root>
				<Table.Header>
					<Table.Row>
						<Table.Head>Name</Table.Head>
						<Table.Head>Status</Table.Head>
						<Table.Head>Rows</Table.Head>
						<Table.Head>Columns</Table.Head>
						<Table.Head class="text-right">Actions</Table.Head>
					</Table.Row>
				</Table.Header>
				<Table.Body>
					<Table.Row>
						<Table.Cell class="font-medium flex items-center gap-2">
							<FileText class="size-4 text-muted-foreground" />
							patient_admissions_q3.csv
						</Table.Cell>
						<Table.Cell>
							<Badge variant="secondary" class="text-xs">Ready</Badge>
						</Table.Cell>
						<Table.Cell>12,450</Table.Cell>
						<Table.Cell>18</Table.Cell>
						<Table.Cell class="text-right">
							<Button variant="ghost" size="sm">Inspect</Button>
						</Table.Cell>
					</Table.Row>

					<Table.Row>
						<Table.Cell class="font-medium flex items-center gap-2">
							<FileText class="size-4 text-muted-foreground" />
							icu_capacity_metrics.parquet
						</Table.Cell>
						<Table.Cell>
							<Badge variant="secondary" class="text-xs">Ready</Badge>
						</Table.Cell>
						<Table.Cell>4,800</Table.Cell>
						<Table.Cell>12</Table.Cell>
						<Table.Cell class="text-right">
							<Button variant="ghost" size="sm">Inspect</Button>
						</Table.Cell>
					</Table.Row>
				</Table.Body>
			</Table.Root>
		</Card.Content>
	</Card.Root>
</div>
