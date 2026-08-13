<script lang="ts">
	import { onMount } from "svelte";
	import { goto } from "$app/navigation";
	import * as Card from "$lib/components/ui/card";
	import { Button } from "$lib/components/ui/button";
	import { Badge } from "$lib/components/ui/badge";
	import { Input } from "$lib/components/ui/input";
	import { Textarea } from "$lib/components/ui/textarea";
	import * as Table from "$lib/components/ui/table";
	import * as Dialog from "$lib/components/ui/dialog";
	import * as Tabs from "$lib/components/ui/tabs";
	import * as Select from "$lib/components/ui/select";
	import * as Tooltip from "$lib/components/ui/tooltip";
	import { Skeleton } from "$lib/components/ui/skeleton";

	import ArrowLeft from "@lucide/svelte/icons/arrow-left";
	import RefreshCw from "@lucide/svelte/icons/refresh-cw";
	import Trash2 from "@lucide/svelte/icons/trash-2";
	import MessageSquare from "@lucide/svelte/icons/message-square";
	import Info from "@lucide/svelte/icons/info";
	import TableProperties from "@lucide/svelte/icons/table-properties";
	import FileAnalytics from "@lucide/svelte/icons/file-spreadsheet";
	import BarChart3 from "@lucide/svelte/icons/bar-chart-3";
	import Tag from "@lucide/svelte/icons/tag";
	import Check from "@lucide/svelte/icons/check";
	import Copy from "@lucide/svelte/icons/copy";
	import Save from "@lucide/svelte/icons/save";
	import AlertCircle from "@lucide/svelte/icons/alert-circle";
	import Search from "@lucide/svelte/icons/search";
	import Loader2 from "@lucide/svelte/icons/loader-2";
	import CheckCircle2 from "@lucide/svelte/icons/check-circle-2";

	import {
		getDataset,
		getDatasetPreview,
		getDatasetColumns,
		getDatasetStatistics,
		deleteDataset,
		getSemanticMappings,
		updateSemanticMappings,
		getDatasetContext,
		updateDatasetContext,
		type DatasetDetail,
		type DatasetPreview,
		type ColumnInfo,
		type DatasetStatistics,
		type SemanticMappingItem
	} from "$lib/api/datasets";
	import {
		listSemanticCategories,
		type SemanticCategoryItem
	} from "$lib/api/semantic-categories";
	import { createConversation } from "$lib/api/conversations";
	import { cn } from "$lib/utils";
	import type { PageData } from "./$types";

	interface Props {
		data: PageData;
	}

	let { data }: Props = $props();

	let datasetId = $derived(data.id);

	let dataset = $state<DatasetDetail | null>(null);
	let previewData = $state<DatasetPreview | null>(null);
	let columnsData = $state<ColumnInfo[]>([]);
	let statsData = $state<DatasetStatistics | null>(null);
	let categories = $state<SemanticCategoryItem[]>([]);

	let loading = $state(true);
	let error = $state<string | null>(null);

	// Active Tab State
	let activeTab = $state<string>("context");

	// Context Tab State
	let customInstructions = $state<string>("");
	let isSavingContext = $state(false);
	let contextSaveMsg = $state<string | null>(null);
	let contextError = $state<string | null>(null);

	async function saveContext() {
		if (isSavingContext || !datasetId) return;
		isSavingContext = true;
		contextError = null;
		try {
			const res = await updateDatasetContext(datasetId, customInstructions);
			if (res.ok) {
				contextSaveMsg = "Custom context saved successfully.";
				setTimeout(() => (contextSaveMsg = null), 3000);
			} else {
				contextError = res.error.message || "Failed to save context.";
			}
		} catch (err: any) {
			contextError = err?.message || "Failed to save context.";
		} finally {
			isSavingContext = false;
		}
	}

	// Preview Filters & Search
	let previewNumRows = $state(10);
	let previewSearch = $state("");
	let previewLoading = $state(false);

	async function reloadPreview() {
		if (!datasetId || dataset?.status !== "ready") return;
		previewLoading = true;
		try {
			const res = await getDatasetPreview(datasetId, previewNumRows);
			if (res.ok) {
				previewData = res.data;
			}
		} catch (err) {
			console.error("Failed to reload preview data", err);
		} finally {
			previewLoading = false;
		}
	}

	let filteredPreviewRows = $derived.by(() => {
		if (!previewData) return [];
		if (!previewSearch.trim()) return previewData.rows;
		const query = previewSearch.toLowerCase();
		return previewData.rows.filter((row) =>
			Object.values(row).some((val) => val !== null && String(val).toLowerCase().includes(query))
		);
	});

	// Schema Filters
	let schemaSearch = $state("");
	let filteredColumns = $derived.by(() => {
		if (!schemaSearch.trim()) return columnsData;
		const query = schemaSearch.toLowerCase();
		return columnsData.filter(
			(col) => col.name.toLowerCase().includes(query) || (col.data_type && col.data_type.toLowerCase().includes(query))
		);
	});

	// Stats Sub-Tab
	let statsSubTab = $state<"numeric" | "missing" | "categorical">("numeric");

	// Semantic Mapping State
	let semanticSearch = $state("");
	let semanticCategoryFilter = $state("all");
	let semanticMappings = $state<SemanticMappingItem[]>([]);
	let initialSemanticSnapshot = $state("");
	let isSavingSemantics = $state(false);
	let semanticSaveSuccess = $state<string | null>(null);
	let semanticError = $state<string | null>(null);

	let filteredSemanticItems = $derived.by(() => {
		let items = semanticMappings;
		if (semanticCategoryFilter !== "all") {
			items = items.filter((i) => (i.category_code || i.category_name) === semanticCategoryFilter);
		}
		if (semanticSearch.trim()) {
			const q = semanticSearch.toLowerCase();
			items = items.filter(
				(i) =>
					i.column_name.toLowerCase().includes(q) ||
					(i.description && i.description.toLowerCase().includes(q)) ||
					(i.category_name && i.category_name.toLowerCase().includes(q))
			);
		}
		return items;
	});

	let hasUnsavedSemantics = $derived(JSON.stringify(semanticMappings) !== initialSemanticSnapshot);

	async function persistSemanticMappings() {
		if (!hasUnsavedSemantics || isSavingSemantics || !datasetId) return;
		isSavingSemantics = true;
		semanticSaveSuccess = null;
		semanticError = null;

		try {
			const payload = semanticMappings.map((i) => ({
				column_name: i.column_name,
				category_code: i.category_code,
				description: i.description
			}));

			const res = await updateSemanticMappings(datasetId, payload);
			if (res.ok) {
				semanticMappings = res.data;
				initialSemanticSnapshot = JSON.stringify(res.data);
				semanticSaveSuccess = "Semantic concept mappings saved successfully.";
				setTimeout(() => (semanticSaveSuccess = null), 3000);
			} else {
				semanticError = res.error.message || "Failed to save semantic mappings.";
			}
		} catch (err: any) {
			semanticError = err?.message || "Failed to save mappings.";
		} finally {
			isSavingSemantics = false;
		}
	}

	function resetSemanticMappings() {
		semanticMappings = JSON.parse(initialSemanticSnapshot);
		semanticError = null;
	}

	// Copy feedback state
	let copiedCellId = $state<string | null>(null);

	function copyToClipboard(text: string, id: string) {
		navigator.clipboard.writeText(text);
		copiedCellId = id;
		setTimeout(() => {
			if (copiedCellId === id) copiedCellId = null;
		}, 1500);
	}

	// Delete Modal State
	let showDeleteModal = $state(false);
	let isDeleting = $state(false);

	async function confirmDelete() {
		if (!datasetId || isDeleting) return;
		isDeleting = true;
		try {
			const res = await deleteDataset(datasetId);
			if (res.ok) {
				await goto("/datasets");
			} else {
				alert(`Failed to delete dataset: ${res.error.message || "Unknown error"}`);
			}
		} catch (err: any) {
			alert(`Failed to delete dataset: ${err?.message || err}`);
		} finally {
			isDeleting = false;
		}
	}

	async function loadAllData() {
		if (!datasetId) return;
		loading = true;
		error = null;
		try {
			const [dsRes, catsRes] = await Promise.all([
				getDataset(datasetId),
				listSemanticCategories()
			]);

			if (!dsRes.ok) {
				error = dsRes.error.message || "Dataset not found.";
				return;
			}

			dataset = dsRes.data;
			if (catsRes.ok) {
				categories = catsRes.data;
			}

			if (dataset.status === "ready") {
				const [preview, cols, stats, semantics, ctx] = await Promise.allSettled([
					getDatasetPreview(datasetId, previewNumRows),
					getDatasetColumns(datasetId),
					getDatasetStatistics(datasetId),
					getSemanticMappings(datasetId),
					getDatasetContext(datasetId)
				]);

				if (preview.status === "fulfilled" && preview.value.ok) {
					previewData = preview.value.data;
				}
				if (cols.status === "fulfilled" && cols.value.ok) {
					columnsData = cols.value.data;
				}
				if (stats.status === "fulfilled" && stats.value.ok) {
					statsData = stats.value.data;
				}
				if (semantics.status === "fulfilled" && semantics.value.ok) {
					semanticMappings = semantics.value.data;
					initialSemanticSnapshot = JSON.stringify(semantics.value.data);
				}
				if (ctx.status === "fulfilled" && ctx.value.ok) {
					customInstructions = ctx.value.data.custom_instructions || "";
				}
			}
		} catch (err: any) {
			error = err?.message || "Failed to load dataset details.";
		} finally {
			loading = false;
		}
	}

	$effect(() => {
		if (datasetId) {
			loadAllData();
		}
	});

	async function startAnalysis() {
		if (!dataset) return;
		try {
			const res = await createConversation(`Dataset: ${dataset.original_filename}`, dataset.id);
			if (res.ok) {
				const convId = res.data.id;
				const initialPrompt = `I want to analyze the dataset "${dataset.original_filename}" (${dataset.rows?.toLocaleString() ?? 0} rows, ${dataset.columns ?? 0} columns). Could you summarize its structure and key trends?`;
				await goto(`/conversations/${convId}?q=${encodeURIComponent(initialPrompt)}`);
			}
		} catch (err) {
			console.error("Failed to launch conversation for dataset", err);
		}
	}

	function formatBytes(bytes: number | null): string {
		if (bytes === null || bytes === 0) return "0 B";
		const k = 1024;
		const sizes = ["B", "KB", "MB", "GB"];
		const i = Math.floor(Math.log(bytes) / Math.log(k));
		const val = (bytes / Math.pow(k, i)).toFixed(1);
		return val + " " + sizes[i];
	}

	function getFileExt(filename: string): string {
		return filename.split(".").pop()?.toUpperCase() || "FILE";
	}

	function formatNum(val: number | undefined | null): string {
		if (val === null || val === undefined) return "—";
		if (Number.isInteger(val)) return val.toLocaleString();
		return val.toFixed(3);
	}
</script>

<svelte:head>
	<title>{dataset ? dataset.original_filename : "Dataset Detail"} | CHU Platform</title>
	<meta name="description" content="Detailed profiling and schema preview for dataset." />
</svelte:head>

<div class="w-full h-full overflow-y-auto p-6 md:p-8 max-w-7xl mx-auto flex flex-col gap-6">
	<!-- Top Navigation Bar -->
	<div class="flex items-center justify-between border-b border-border/60 pb-3">
		<Button variant="ghost" size="sm" href="/datasets" class="gap-2 text-xs font-semibold text-muted-foreground hover:text-foreground">
			<ArrowLeft data-icon="inline-start" class="size-4" />
			Back to Datasets
		</Button>

		<div class="flex items-center gap-2">
			<Button
				variant="outline"
				size="icon"
				class="size-8"
				onclick={loadAllData}
				title="Reload dataset data"
			>
				<RefreshCw data-icon="inline-start" class={cn("size-3.5", loading && "animate-spin")} />
			</Button>

			{#if dataset}
				<Button
					variant="outline"
					size="icon"
					class="size-8 text-destructive hover:bg-destructive/10 hover:text-destructive"
					onclick={() => (showDeleteModal = true)}
					title="Delete dataset"
				>
					<Trash2 data-icon="inline-start" class="size-3.5" />
				</Button>
			{/if}
		</div>
	</div>

	{#if loading}
		<div class="p-12 flex flex-col items-center justify-center gap-4 text-center">
			<Loader2 class="size-8 animate-spin text-primary" />
			<p class="text-xs font-mono text-muted-foreground">Loading dataset profiling and schemas...</p>
		</div>
	{:else if error || !dataset}
		<Card.Root class="border-destructive/30 bg-destructive/5">
			<Card.Content class="p-6 flex flex-col gap-3">
				<div class="flex items-center gap-2 text-destructive font-semibold text-sm">
					<AlertCircle class="size-4" />
					<span>{error || "Dataset not found."}</span>
				</div>
				<Button variant="outline" size="sm" href="/datasets" class="self-start">Return to Datasets List</Button>
			</Card.Content>
		</Card.Root>
	{:else}
		<!-- Header Metadata Banner -->
		<Card.Root class="border-border/60 shadow-sm">
			<Card.Content class="p-6 flex flex-col md:flex-row md:items-center justify-between gap-6">
				<div class="flex flex-col gap-3 min-w-0 flex-1">
					<div class="flex flex-wrap items-center gap-3">
						<Badge variant="outline" class="font-mono text-xs font-bold text-primary bg-primary/10 border-primary/30">
							{getFileExt(dataset.original_filename)}
						</Badge>

						<h1 class="text-2xl font-bold tracking-tight truncate">{dataset.original_filename}</h1>

						{#if dataset.status === "ready"}
							<Badge variant="secondary" class="gap-1.5 text-xs text-emerald-600 bg-emerald-500/10 border-emerald-500/20">
								<span class="size-1.5 rounded-full bg-emerald-500"></span>
								Ready
							</Badge>
						{:else}
							<Badge variant="secondary" class="gap-1.5 text-xs text-amber-600 bg-amber-500/10 border-amber-500/20">
								<span class="size-1.5 rounded-full bg-amber-500 animate-pulse"></span>
								{dataset.status}
							</Badge>
						{/if}
					</div>

					<!-- Quick Metadata Chips -->
					<div class="flex flex-wrap items-center gap-4 text-xs font-mono text-muted-foreground">
						<div>
							<span class="text-foreground font-semibold">Rows:</span>
							<span class="ml-1">{dataset.rows?.toLocaleString() ?? "—"}</span>
						</div>
						<span>•</span>
						<div>
							<span class="text-foreground font-semibold">Columns:</span>
							<span class="ml-1">{dataset.columns ?? "—"}</span>
						</div>
						<span>•</span>
						<div>
							<span class="text-foreground font-semibold">Size:</span>
							<span class="ml-1">{formatBytes(dataset.file_size)}</span>
						</div>
						<span>•</span>
						<div>
							<span class="text-foreground font-semibold">Uploaded:</span>
							<span class="ml-1">{new Date(dataset.created_at).toLocaleDateString()}</span>
						</div>
					</div>

					{#if dataset.error_message}
						<div class="p-3 rounded-lg bg-destructive/10 border border-destructive/20 text-destructive text-xs font-medium">
							<strong>Error processing file:</strong> {dataset.error_message}
						</div>
					{/if}
				</div>

				<!-- Primary Action Button -->
				<div class="flex items-center gap-3 shrink-0">
					<Button
						variant="default"
						size="lg"
						class="gap-2"
						onclick={startAnalysis}
						disabled={dataset.status !== "ready"}
					>
						<MessageSquare data-icon="inline-start" class="size-4" />
						Start AI Analysis
					</Button>
				</div>
			</Card.Content>
		</Card.Root>

		<!-- Main Tabs Navigation -->
		<Tabs.Root value={activeTab} onValueChange={(val) => (activeTab = val)} class="w-full flex flex-col gap-4">
			<Tabs.List class="grid grid-cols-2 md:grid-cols-5 w-full bg-muted/40 p-1 rounded-xl">
				<Tabs.Trigger value="context" class="gap-2 text-xs">
					<Info class="size-3.5" />
					Context
				</Tabs.Trigger>

				<Tabs.Trigger value="preview" class="gap-2 text-xs">
					<TableProperties class="size-3.5" />
					Data Preview
				</Tabs.Trigger>

				<Tabs.Trigger value="schema" class="gap-2 text-xs">
					<FileAnalytics class="size-3.5" />
					Schema & Profiling
					{#if columnsData.length > 0}
						<Badge variant="secondary" class="ml-1 px-1.5 py-0 text-[10px]">{columnsData.length}</Badge>
					{/if}
				</Tabs.Trigger>

				<Tabs.Trigger value="stats" class="gap-2 text-xs">
					<BarChart3 class="size-3.5" />
					Statistical Summary
				</Tabs.Trigger>

				<Tabs.Trigger value="semantics" class="gap-2 text-xs">
					<Tag class="size-3.5" />
					Semantic Mapping
				</Tabs.Trigger>
			</Tabs.List>

			<!-- 1. Context & AI Instructions Tab -->
			<Tabs.Content value="context" class="flex flex-col gap-4">
				<Card.Root class="border-border/60">
					<Card.Header>
						<Card.Title class="text-base flex items-center gap-2">
							<Info class="size-4 text-primary" />
							AI Agent Prompt Context & Custom Instructions
						</Card.Title>
						<Card.Description class="text-xs">
							Provide domain context, background knowledge, or specialized analysis rules for the AI Agent when exploring this dataset.
						</Card.Description>
					</Card.Header>

					<Card.Content class="flex flex-col gap-4">
						{#if contextSaveMsg}
							<div class="p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-600 dark:text-emerald-400 text-xs font-medium flex items-center gap-2">
								<CheckCircle2 class="size-4" />
								<span>{contextSaveMsg}</span>
							</div>
						{/if}

						{#if contextError}
							<div class="p-3 rounded-lg bg-destructive/10 border border-destructive/20 text-destructive text-xs font-medium">
								{contextError}
							</div>
						{/if}

						<div class="flex flex-col gap-2">
							<label for="custom-instructions-input" class="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
								Custom Domain Instructions
							</label>
							<Textarea
								id="custom-instructions-input"
								placeholder="e.g. Focus on glucose and BMI trends for patient outcome analysis. Filter out zero values in Insulin column."
								bind:value={customInstructions}
								rows={6}
								class="text-sm bg-background font-mono"
							/>
						</div>

						<div class="flex items-center justify-end gap-2 pt-2">
							<Button variant="default" size="sm" onclick={saveContext} disabled={isSavingContext} class="gap-2">
								{#if isSavingContext}
									<Loader2 data-icon="inline-start" class="size-4 animate-spin" />
									Saving...
								{:else}
									<Save data-icon="inline-start" class="size-4" />
									Save Instructions
								{/if}
							</Button>
						</div>
					</Card.Content>
				</Card.Root>
			</Tabs.Content>

			<!-- 2. Data Preview Tab -->
			<Tabs.Content value="preview" class="flex flex-col gap-4">
				<Card.Root class="border-border/60">
					<Card.Header class="pb-3 border-b border-border/40">
						<div class="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-4">
							<div class="relative w-full sm:w-80">
								<Input
									type="text"
									placeholder="Search cells in preview..."
									bind:value={previewSearch}
									class="pl-8 text-xs h-9"
								/>
								<Search class="absolute left-2.5 top-2.5 size-3.5 text-muted-foreground" />
							</div>

							<div class="flex items-center justify-between sm:justify-end gap-3 text-xs font-mono text-muted-foreground">
								<div class="flex items-center gap-2">
									<span>Rows:</span>
									<select
										bind:value={previewNumRows}
										onchange={reloadPreview}
										class="bg-background border border-border/70 rounded-md px-2.5 py-1 text-xs font-semibold focus:outline-none cursor-pointer"
									>
										<option value={10}>10 rows</option>
										<option value={25}>25 rows</option>
										<option value={50}>50 rows</option>
										<option value={100}>100 rows</option>
									</select>
								</div>

								<Button variant="outline" size="icon" class="size-8" onclick={reloadPreview} disabled={previewLoading}>
									<RefreshCw data-icon="inline-start" class={cn("size-3.5", previewLoading && "animate-spin")} />
								</Button>
							</div>
						</div>
					</Card.Header>

					<Card.Content class="p-0">
						{#if previewLoading}
							<div class="p-12 text-center text-xs font-mono text-muted-foreground">Reloading preview grid...</div>
						{:else if previewData && previewData.columns.length > 0}
							<div class="overflow-x-auto max-h-[60vh]">
								<Table.Root>
									<Table.Header>
										<Table.Row class="bg-muted/40 text-xs font-bold uppercase sticky top-0 z-10">
											<Table.Head class="w-12 text-center">#</Table.Head>
											{#each previewData.columns as col}
												<Table.Head class="whitespace-nowrap font-mono text-foreground">{col}</Table.Head>
											{/each}
										</Table.Row>
									</Table.Header>
									<Table.Body>
										{#each filteredPreviewRows as row, rIdx}
											<Table.Row class="hover:bg-muted/30 transition-colors font-mono text-xs">
												<Table.Cell class="text-center text-muted-foreground text-[11px] select-none bg-muted/20">
													{rIdx + 1}
												</Table.Cell>
												{#each previewData.columns as col}
													{@const val = row[col]}
													{@const cellId = `${rIdx}-${col}`}
													<Table.Cell class="whitespace-nowrap group relative">
														{#if val === null || val === undefined}
															<span class="italic text-muted-foreground/40 font-sans">null</span>
														{:else if typeof val === "boolean"}
															<Badge variant={val ? "secondary" : "destructive"} class="text-[10px] font-mono px-1.5 py-0">
																{val ? "TRUE" : "FALSE"}
															</Badge>
														{:else}
															<span>{val}</span>
															<Button
																variant="ghost"
																size="icon"
																class="opacity-0 group-hover:opacity-100 ml-1.5 size-5 inline-flex items-center justify-center p-0"
																onclick={() => copyToClipboard(String(val), cellId)}
																title="Copy value"
															>
																{#if copiedCellId === cellId}
																	<Check class="size-3 text-emerald-500" />
																{:else}
																	<Copy class="size-3 text-muted-foreground" />
																{/if}
															</Button>
														{/if}
													</Table.Cell>
												{/each}
											</Table.Row>
										{/each}
									</Table.Body>
								</Table.Root>
							</div>

							<div class="p-3 border-t border-border/40 flex items-center justify-between text-xs font-mono text-muted-foreground">
								<span>Showing {filteredPreviewRows.length} previewed rows</span>
								<span>Total: {previewData.total_rows.toLocaleString()} rows × {previewData.total_columns} columns</span>
							</div>
						{:else}
							<div class="p-12 text-center text-xs font-mono text-muted-foreground">
								No preview data available.
							</div>
						{/if}
					</Card.Content>
				</Card.Root>
			</Tabs.Content>

			<!-- 3. Schema & Profiling Tab -->
			<Tabs.Content value="schema" class="flex flex-col gap-4">
				<Card.Root class="border-border/60">
					<Card.Header class="pb-3 border-b border-border/40">
						<div class="flex items-center justify-between gap-4">
							<div class="relative w-full sm:w-80">
								<Input
									type="text"
									placeholder="Filter columns by name or type..."
									bind:value={schemaSearch}
									class="pl-8 text-xs h-9"
								/>
								<Search class="absolute left-2.5 top-2.5 size-3.5 text-muted-foreground" />
							</div>

							<span class="text-xs font-mono text-muted-foreground">
								Showing {filteredColumns.length} of {columnsData.length} columns
							</span>
						</div>
					</Card.Header>

					<Card.Content class="p-0">
						{#if filteredColumns.length > 0}
							<Table.Root>
								<Table.Header>
									<Table.Row class="bg-muted/40 text-xs font-semibold uppercase">
										<Table.Head class="w-12">#</Table.Head>
										<Table.Head>Column Name</Table.Head>
										<Table.Head>Data Type</Table.Head>
										<Table.Head>Unique Count</Table.Head>
										<Table.Head>Sample Values</Table.Head>
									</Table.Row>
								</Table.Header>
								<Table.Body>
									{#each filteredColumns as col, idx}
										<Table.Row class="hover:bg-muted/30 transition-colors text-xs font-mono">
											<Table.Cell class="text-muted-foreground text-[11px]">{idx + 1}</Table.Cell>
											<Table.Cell class="font-bold text-foreground font-sans text-sm">{col.name}</Table.Cell>
											<Table.Cell>
												<Badge variant="outline" class="font-mono text-[10px] text-primary">
													{col.data_type}
												</Badge>
											</Table.Cell>
											<Table.Cell>{col.unique_count !== null && col.unique_count !== undefined ? col.unique_count.toLocaleString() : "—"}</Table.Cell>
											<Table.Cell class="text-muted-foreground truncate max-w-md">
												{col.sample_values && col.sample_values.length > 0 ? col.sample_values.join(", ") : "—"}
											</Table.Cell>
										</Table.Row>
									{/each}
								</Table.Body>
							</Table.Root>
						{:else}
							<div class="p-12 text-center text-xs font-mono text-muted-foreground">
								No columns matching search criteria.
							</div>
						{/if}
					</Card.Content>
				</Card.Root>
			</Tabs.Content>

			<!-- 4. Statistical Summary Tab -->
			<Tabs.Content value="stats" class="flex flex-col gap-4">
				<Card.Root class="border-border/60">
					<Card.Header class="pb-3">
						<div class="flex items-center justify-between">
							<Card.Title class="text-base">Statistical Profiles & Distribution</Card.Title>
							<Tabs.Root value={statsSubTab} onValueChange={(val) => (statsSubTab = val as any)}>
								<Tabs.List class="text-xs">
									<Tabs.Trigger value="numeric">Numeric Matrix</Tabs.Trigger>
									<Tabs.Trigger value="missing">Missing Values</Tabs.Trigger>
									<Tabs.Trigger value="categorical">Column Types</Tabs.Trigger>
								</Tabs.List>
							</Tabs.Root>
						</div>
					</Card.Header>

					<Card.Content>
						{#if statsData}
							{#if statsSubTab === "numeric"}
								{#if statsData.numeric_columns && Object.keys(statsData.numeric_columns).length > 0}
									<div class="overflow-x-auto">
										<Table.Root>
											<Table.Header>
												<Table.Row class="bg-muted/40 text-xs uppercase font-bold">
													<Table.Head>Metric / Column</Table.Head>
													{#each Object.keys(statsData.numeric_columns) as col}
														<Table.Head class="text-primary font-mono whitespace-nowrap">{col}</Table.Head>
													{/each}
												</Table.Row>
											</Table.Header>
											<Table.Body>
												{#each ["count", "mean", "std", "min", "median", "max"] as metric}
													<Table.Row class="hover:bg-muted/30 font-mono text-xs">
														<Table.Cell class="font-bold font-sans capitalize bg-muted/20">{metric}</Table.Cell>
														{#each Object.keys(statsData.numeric_columns) as col}
															{@const val = (statsData.numeric_columns[col] as any)?.[metric]}
															<Table.Cell class="whitespace-nowrap">{formatNum(val)}</Table.Cell>
														{/each}
													</Table.Row>
												{/each}
											</Table.Body>
										</Table.Root>
									</div>
								{:else}
									<div class="p-8 text-center text-xs font-mono text-muted-foreground">
										No numeric columns in dataset.
									</div>
								{/if}
							{:else if statsSubTab === "missing"}
								{#if statsData.missing_values && Object.keys(statsData.missing_values).length > 0}
									<div class="grid grid-cols-1 md:grid-cols-2 gap-3">
										{#each Object.entries(statsData.missing_values) as [col, missingCount]}
											{@const totalRows = dataset.rows || 1}
											{@const pct = Math.round((missingCount / totalRows) * 100)}
											<div class="p-3.5 rounded-lg border border-border/60 bg-muted/20 flex flex-col gap-2 font-mono text-xs">
												<div class="flex items-center justify-between">
													<span class="font-bold text-foreground font-sans">{col}</span>
													<span class="text-muted-foreground">{missingCount.toLocaleString()} nulls ({pct}%)</span>
												</div>
												<div class="w-full h-2 bg-muted rounded-full overflow-hidden">
													<div
														class={cn(
															"h-full transition-all",
															pct > 50 ? "bg-destructive" : pct > 0 ? "bg-amber-500" : "bg-emerald-500"
														)}
														style="width: {pct}%"
													></div>
												</div>
											</div>
										{/each}
									</div>
								{:else}
									<div class="p-8 text-center text-xs font-mono text-muted-foreground">
										No missing values recorded.
									</div>
								{/if}
							{:else if statsSubTab === "categorical"}
								{#if statsData.categorical_columns && Object.keys(statsData.categorical_columns).length > 0}
									<div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
										{#each Object.entries(statsData.categorical_columns) as [col, info]}
											<div class="p-3.5 rounded-lg border border-border/60 bg-muted/20 flex items-center justify-between text-xs">
												<span class="font-semibold truncate max-w-[140px]">{col}</span>
												<Badge variant="outline" class="font-mono text-[10px]">
													{info.unique} unique values
												</Badge>
											</div>
										{/each}
									</div>
								{:else}
									<div class="p-8 text-center text-xs font-mono text-muted-foreground">
										No categorical columns recorded.
									</div>
								{/if}
							{/if}
						{:else}
							<div class="p-8 text-center text-xs font-mono text-muted-foreground">
								Statistical summary unavailable.
							</div>
						{/if}
					</Card.Content>
				</Card.Root>
			</Tabs.Content>

			<!-- 5. Semantic Concept Mapping Tab -->
			<Tabs.Content value="semantics" class="flex flex-col gap-4">
				<Card.Root class="border-border/60">
					<Card.Header class="pb-3 border-b border-border/40">
						<div class="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-4">
							<div class="flex items-center gap-3 flex-1">
								<div class="relative w-full max-w-xs">
									<Input
										type="text"
										placeholder="Filter columns or concepts..."
										bind:value={semanticSearch}
										class="pl-8 text-xs h-9"
									/>
									<Search class="absolute left-2.5 top-2.5 size-3.5 text-muted-foreground" />
								</div>

								<Select.Root
									type="single"
									value={semanticCategoryFilter}
									onValueChange={(val) => (semanticCategoryFilter = val || "all")}
								>
									<Select.Trigger class="w-48 h-9 text-xs">
										<Tag class="size-3.5 text-primary shrink-0 mr-1.5" />
										<span class="truncate">
											{semanticCategoryFilter === "all" ? `All Categories (${semanticMappings.length})` : semanticCategoryFilter}
										</span>
									</Select.Trigger>
									<Select.Content>
										<Select.Item value="all" label="All Categories">All Categories</Select.Item>
										{#each categories as cat}
											<Select.Item value={cat.code || cat.name} label={cat.name}>
												{cat.name}
											</Select.Item>
										{/each}
									</Select.Content>
								</Select.Root>
							</div>

							<!-- Save & Reset Action Controls -->
							<div class="flex items-center gap-2 shrink-0">
								{#if hasUnsavedSemantics}
									<span class="text-xs text-amber-500 font-medium">Unsaved changes</span>
									<Button variant="outline" size="sm" onclick={resetSemanticMappings} disabled={isSavingSemantics}>
										Discard
									</Button>
									<Button variant="default" size="sm" onclick={persistSemanticMappings} disabled={isSavingSemantics} class="gap-1.5">
										{#if isSavingSemantics}
											<Loader2 data-icon="inline-start" class="size-3.5 animate-spin" />
											Saving...
										{:else}
											<Save data-icon="inline-start" class="size-3.5" />
											Save Mappings
										{/if}
									</Button>
								{/if}
							</div>
						</div>
					</Card.Header>

					<Card.Content class="p-0">
						{#if semanticSaveSuccess}
							<div class="m-4 p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-600 dark:text-emerald-400 text-xs font-medium flex items-center gap-2">
								<CheckCircle2 class="size-4" />
								<span>{semanticSaveSuccess}</span>
							</div>
						{/if}

						{#if semanticError}
							<div class="m-4 p-3 rounded-lg bg-destructive/10 border border-destructive/20 text-destructive text-xs font-medium">
								{semanticError}
							</div>
						{/if}

						{#if filteredSemanticItems.length > 0}
							<Table.Root>
								<Table.Header>
									<Table.Row class="bg-muted/40 text-xs font-semibold uppercase">
										<Table.Head>Raw Column</Table.Head>
										<Table.Head>Business Description / Concept</Table.Head>
										<Table.Head>Semantic Domain Category</Table.Head>
									</Table.Row>
								</Table.Header>
								<Table.Body>
									{#each filteredSemanticItems as item}
										<Table.Row class="hover:bg-muted/30 transition-colors">
											<Table.Cell class="font-bold text-sm font-sans">{item.column_name}</Table.Cell>
											<Table.Cell>
												<Input
													type="text"
													bind:value={item.description}
													placeholder="Add business context label..."
													class="h-8 text-xs font-mono max-w-md bg-background"
												/>
											</Table.Cell>
											<Table.Cell>
												<Select.Root
													type="single"
													value={item.category_code || "uncategorized"}
													onValueChange={(val) => (item.category_code = val === "uncategorized" ? null : val)}
												>
													<Select.Trigger class="w-48 h-8 text-xs">
														<span class="truncate">
															{categories.find((c) => c.code === item.category_code)?.name || item.category_code || "Uncategorized"}
														</span>
													</Select.Trigger>
													<Select.Content>
														<Select.Item value="uncategorized" label="Uncategorized">Uncategorized</Select.Item>
														{#each categories as cat}
															<Select.Item value={cat.code} label={cat.name}>{cat.name}</Select.Item>
														{/each}
													</Select.Content>
												</Select.Root>
											</Table.Cell>
										</Table.Row>
									{/each}
								</Table.Body>
							</Table.Root>
						{:else}
							<div class="p-12 text-center text-xs font-mono text-muted-foreground">
								No semantic mappings found.
							</div>
						{/if}
					</Card.Content>
				</Card.Root>
			</Tabs.Content>
		</Tabs.Root>
	{/if}
</div>

<!-- Delete Confirmation Modal -->
<Dialog.Root open={showDeleteModal} onOpenChange={(open) => (showDeleteModal = open)}>
	<Dialog.Content class="sm:max-w-md">
		<Dialog.Header>
			<Dialog.Title class="text-destructive flex items-center gap-2">
				<AlertCircle data-icon="inline-start" class="size-5" />
				Delete Dataset
			</Dialog.Title>
			<Dialog.Description class="text-xs">
				This action is permanent and cannot be undone.
			</Dialog.Description>
		</Dialog.Header>

		{#if dataset}
			<p class="text-sm font-medium text-foreground py-2">
				Are you sure you want to delete dataset <span class="font-bold font-mono">"{dataset.original_filename}"</span>?
			</p>
		{/if}

		<Dialog.Footer class="gap-2 sm:gap-0">
			<Button variant="outline" onclick={() => (showDeleteModal = false)} disabled={isDeleting}>
				Cancel
			</Button>
			<Button variant="destructive" onclick={confirmDelete} disabled={isDeleting} class="gap-2">
				{#if isDeleting}
					<Loader2 data-icon="inline-start" class="size-4 animate-spin" />
					Deleting...
				{:else}
					<Trash2 data-icon="inline-start" class="size-4" />
					Delete Permanently
				{/if}
			</Button>
		</Dialog.Footer>
	</Dialog.Content>
</Dialog.Root>
