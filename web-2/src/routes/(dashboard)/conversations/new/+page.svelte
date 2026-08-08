<script lang="ts">
	import * as PromptInput from "$lib/components/ai-elements/prompt-input";
	import * as Select from "$lib/components/ui/select";
	import { Input } from "$lib/components/ui/input";
	import Database from "@lucide/svelte/icons/database";
	import X from "@lucide/svelte/icons/x";
	import Search from "@lucide/svelte/icons/search";
	import { createConversation } from "$lib/api/conversations";
	import { listDatasets, type DatasetSummary } from "$lib/api/datasets";
	import { goto, invalidateAll } from "$app/navigation";
	import { onMount } from "svelte";

	let selectedDataset = $state<DatasetSummary | null>(null);
	let availableDatasets = $state<DatasetSummary[]>([]);
	let loadingDatasets = $state(false);
	let datasetSearchQuery = $state("");
	let isSubmitting = $state(false);

	let filteredDatasets = $derived.by(() => {
		if (!datasetSearchQuery.trim()) return availableDatasets;
		const q = datasetSearchQuery.toLowerCase();
		return availableDatasets.filter((d) =>
			d.original_filename.toLowerCase().includes(q)
		);
	});

	async function loadDatasets() {
		loadingDatasets = true;
		try {
			const res = await listDatasets({ limit: 100, status_filter: "ready" });
			if (res.ok && res.data) {
				availableDatasets = res.data;
			} else {
				availableDatasets = [];
			}
		} catch (err) {
			console.error("Failed to load datasets:", err);
			availableDatasets = [];
		} finally {
			loadingDatasets = false;
		}
	}

	onMount(() => {
		loadDatasets();
	});

	function handleSelectValue(val: string) {
		if (!val || val === "none") {
			selectedDataset = null;
		} else {
			const found = availableDatasets.find((d) => d.id === val);
			if (found) selectedDataset = found;
		}
	}

	function handleRemoveDataset() {
		selectedDataset = null;
	}

	async function handleSubmit(messageInput: { text?: string }, event: SubmitEvent) {
		const userQuery = messageInput?.text?.trim() || "";
		if (!userQuery || isSubmitting) return;

		isSubmitting = true;
		try {
			const title = selectedDataset
				? `Dataset: ${selectedDataset.original_filename}`
				: undefined;

			const res = await createConversation(title, selectedDataset?.id);

			if (res.ok && res.data) {
				await invalidateAll();
				await goto(`/conversations/${res.data.id}?q=${encodeURIComponent(userQuery)}`);
			}
		} catch (err) {
			console.error("Failed to create conversation:", err);
			isSubmitting = false;
		}
	}
</script>

<div class="flex flex-col items-center justify-center h-full w-full p-4 overflow-y-auto">
	<div class="w-full max-w-3xl flex flex-col items-center gap-8 -mt-12">
		<!-- Hero Title & Subtitle -->
		<div class="flex flex-col items-center gap-3 text-center">
			<h1 class="text-3xl md:text-4xl font-semibold tracking-tight text-foreground">
				What would you like to explore?
			</h1>
			<p class="text-sm md:text-base text-muted-foreground max-w-md leading-relaxed">
				Ask questions about your data, generate reports, and uncover insights.
			</p>
		</div>

		<!-- Centered Large Composer -->
		<div class="w-full flex flex-col gap-2">
			<!-- Attached Dataset Pill -->
			{#if selectedDataset}
				<div class="flex items-center gap-2 px-1">
					<div class="inline-flex items-center gap-2 px-3 py-1.5 rounded-xl bg-primary/10 border border-primary/25 text-xs font-medium text-foreground shadow-xs backdrop-blur-md">
						<Database class="size-3.5 text-primary shrink-0" />
						<span class="font-semibold truncate max-w-xs">{selectedDataset.original_filename}</span>
						{#if selectedDataset.rows || selectedDataset.columns}
							<span class="text-[11px] font-mono text-muted-foreground border-l border-border/60 pl-2">
								{selectedDataset.rows?.toLocaleString() ?? '?'} rows &middot; {selectedDataset.columns ?? '?'} cols
							</span>
						{/if}
						<button
							type="button"
							onclick={handleRemoveDataset}
							class="ml-1 p-0.5 rounded-md text-muted-foreground hover:text-destructive hover:bg-destructive/10 transition-colors cursor-pointer"
							title="Remove dataset"
						>
							<X class="size-3.5" />
						</button>
					</div>
				</div>
			{/if}

			<PromptInput.Root class="p-3 shadow-2xl border border-border/70 bg-background/95 backdrop-blur-xl rounded-2xl" onSubmit={handleSubmit}>
				<PromptInput.Body>
					<PromptInput.Textarea
						placeholder={selectedDataset ? `Ask anything about "${selectedDataset.original_filename}"...` : "Ask anything..."}
						class="min-h-[64px] text-base"
					/>
				</PromptInput.Body>
				<PromptInput.Toolbar class="justify-between pt-2">
					<!-- Shadcn-Svelte Select Dataset Selector with Search -->
					<Select.Root
						type="single"
						value={selectedDataset?.id || "none"}
						onValueChange={handleSelectValue}
						onOpenChange={(open) => {
							if (open) {
								datasetSearchQuery = "";
								if (availableDatasets.length === 0) loadDatasets();
							}
						}}
					>
						<Select.Trigger class="w-auto min-w-[180px] h-9 gap-2 rounded-xl bg-background/80 backdrop-blur-sm border-border/80 text-xs font-medium cursor-pointer">
							<Database class="size-4 text-primary shrink-0" />
							<span class="truncate max-w-[160px]">
								{selectedDataset ? selectedDataset.original_filename : "Attach Dataset"}
							</span>
						</Select.Trigger>
						<Select.Content class="w-80 max-h-80 z-50 p-0 overflow-hidden">
							<!-- Search Input Box inside Select Content -->
							<div class="p-2 border-b border-border/60 bg-muted/40 sticky top-0 z-10">
								<div class="relative w-full">
									<Input
										type="text"
										placeholder="Search datasets..."
										bind:value={datasetSearchQuery}
										class="h-8 text-xs pl-8 bg-background"
										onclick={(e) => e.stopPropagation()}
										onkeydown={(e) => e.stopPropagation()}
									/>
									<Search class="absolute left-2.5 top-2.5 size-3.5 text-muted-foreground" />
								</div>
							</div>

							<Select.Group class="p-1">
								<Select.GroupHeading class="text-[11px] font-bold text-muted-foreground uppercase px-2 py-1.5">
									Available Datasets
								</Select.GroupHeading>

								{#if selectedDataset}
									<Select.Item value="none" label="None (Detach dataset)" class="text-xs text-muted-foreground italic">
										None (Detach dataset)
									</Select.Item>
								{/if}

								{#if loadingDatasets}
									<div class="p-4 text-center text-xs text-muted-foreground">Loading datasets...</div>
								{:else if filteredDatasets.length === 0}
									<div class="p-4 text-center text-xs text-muted-foreground">
										No matching datasets found.
									</div>
								{:else}
									{#each filteredDatasets as ds (ds.id)}
										<Select.Item value={ds.id} label={ds.original_filename} class="text-xs flex items-center justify-between py-2">
											<div class="flex flex-col min-w-0">
												<span class="font-semibold truncate">{ds.original_filename}</span>
												<span class="text-[10px] text-muted-foreground font-mono">
													{ds.rows?.toLocaleString() ?? '?'} rows &middot; {ds.columns ?? '?'} cols
												</span>
											</div>
										</Select.Item>
									{/each}
								{/if}
							</Select.Group>
						</Select.Content>
					</Select.Root>

					<PromptInput.Submit disabled={isSubmitting} />
				</PromptInput.Toolbar>
			</PromptInput.Root>
		</div>
	</div>
</div>
