<script lang="ts">
	import { onMount, onDestroy } from "svelte";
	import { goto } from "$app/navigation";
	import * as Card from "$lib/components/ui/card";
	import { Button } from "$lib/components/ui/button";
	import { Badge } from "$lib/components/ui/badge";
	import { Input } from "$lib/components/ui/input";
	import * as Table from "$lib/components/ui/table";
	import * as Dialog from "$lib/components/ui/dialog";
	import * as Tabs from "$lib/components/ui/tabs";
	import * as Field from "$lib/components/ui/field";
	import * as Tooltip from "$lib/components/ui/tooltip";
	import { Skeleton } from "$lib/components/ui/skeleton";
	import Database from "@lucide/svelte/icons/database";
	import Upload from "@lucide/svelte/icons/upload";
	import FileText from "@lucide/svelte/icons/file-text";
	import RefreshCw from "@lucide/svelte/icons/refresh-cw";
	import Search from "@lucide/svelte/icons/search";
	import Trash2 from "@lucide/svelte/icons/trash-2";
	import Eye from "@lucide/svelte/icons/eye";
	import MessageSquare from "@lucide/svelte/icons/message-square";
	import CheckCircle2 from "@lucide/svelte/icons/check-circle-2";
	import AlertCircle from "@lucide/svelte/icons/alert-circle";
	import HardDrive from "@lucide/svelte/icons/hard-drive";
	import Layers from "@lucide/svelte/icons/layers";
	import Loader2 from "@lucide/svelte/icons/loader-2";
	import FileSpreadsheet from "@lucide/svelte/icons/file-spreadsheet";
	import X from "@lucide/svelte/icons/x";

	import {
		listDatasets,
		uploadDataset,
		deleteDataset,
		type DatasetSummary
	} from "$lib/api/datasets";
	import { createConversation } from "$lib/api/conversations";
	import { cn } from "$lib/utils";

	let datasets = $state<DatasetSummary[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);

	// Filters & Search
	let statusFilter = $state<string>("all");
	let searchQuery = $state("");

	// Modals State
	let showUploadModal = $state(false);
	let uploadFile = $state<File | null>(null);
	let uploadDragOver = $state(false);
	let isUploading = $state(false);
	let uploadError = $state<string | null>(null);

	// Delete Confirmation Modal
	let deleteTargetItem = $state<DatasetSummary | null>(null);
	let isDeleting = $state(false);

	let pollInterval: ReturnType<typeof setInterval> | null = null;

	async function fetchDatasets(showLoadingState = true) {
		if (showLoadingState) loading = true;
		error = null;
		try {
			const res = await listDatasets({
				status_filter: statusFilter === "all" ? undefined : statusFilter,
				limit: 100
			});
			if (res.ok) {
				datasets = res.data;
			} else {
				error = res.error.message || "Failed to load datasets.";
			}
		} catch (err: any) {
			error = err?.message || "Failed to load datasets.";
		} finally {
			loading = false;
		}
	}

	onMount(() => {
		fetchDatasets(true);
		pollInterval = setInterval(() => {
			const hasPending = datasets.some(
				(d) => d.status === "pending" || d.status === "processing"
			);
			if (hasPending) {
				fetchDatasets(false);
			}
		}, 3000);
	});

	onDestroy(() => {
		if (pollInterval) clearInterval(pollInterval);
	});

	function handleFilterChange(newFilter: string) {
		statusFilter = newFilter;
		fetchDatasets(true);
	}

	let filteredDatasets = $derived.by(() => {
		if (!searchQuery.trim()) return datasets;
		const q = searchQuery.toLowerCase();
		return datasets.filter((d) => d.original_filename.toLowerCase().includes(q));
	});

	let metrics = $derived.by(() => {
		const total = datasets.length;
		const ready = datasets.filter((d) => d.status === "ready").length;
		const processing = datasets.filter(
			(d) => d.status === "processing" || d.status === "pending"
		).length;
		const totalRows = datasets.reduce((acc, d) => acc + (d.rows || 0), 0);
		const totalBytes = datasets.reduce((acc, d) => acc + (d.file_size || 0), 0);
		return { total, ready, processing, totalRows, totalBytes };
	});

	async function confirmDelete() {
		if (!deleteTargetItem || isDeleting) return;
		isDeleting = true;
		try {
			const res = await deleteDataset(deleteTargetItem.id);
			if (res.ok) {
				datasets = datasets.filter((d) => d.id !== deleteTargetItem!.id);
				deleteTargetItem = null;
			} else {
				alert(`Failed to delete dataset: ${res.error.message || "Unknown error"}`);
			}
		} catch (err: any) {
			alert(`Failed to delete dataset: ${err?.message || err}`);
		} finally {
			isDeleting = false;
		}
	}

	async function startAnalysis(dataset: DatasetSummary) {
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

	function handleFileSelect(e: Event) {
		const input = e.target as HTMLInputElement;
		if (input.files && input.files[0]) {
			uploadFile = input.files[0];
			uploadError = null;
		}
	}

	function handleDrop(e: DragEvent) {
		e.preventDefault();
		uploadDragOver = false;
		if (e.dataTransfer?.files && e.dataTransfer.files[0]) {
			uploadFile = e.dataTransfer.files[0];
			uploadError = null;
		}
	}

	async function handleUploadSubmit() {
		if (!uploadFile || isUploading) return;
		isUploading = true;
		uploadError = null;

		try {
			const formData = new FormData();
			formData.append("file", uploadFile);

			const res = await uploadDataset(formData);
			if (res.ok) {
				showUploadModal = false;
				uploadFile = null;
				fetchDatasets(true);
			} else {
				uploadError = res.error.message || "Failed to upload file.";
			}
		} catch (err: any) {
			uploadError = err?.message || "Failed to upload dataset file.";
		} finally {
			isUploading = false;
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

	function formatRelativeTime(dateStr: string): string {
		if (!dateStr) return "—";
		const diff = Date.now() - new Date(dateStr).getTime();
		const mins = Math.floor(diff / 60000);
		if (mins < 1) return "just now";
		if (mins < 60) return `${mins}m ago`;
		const hrs = Math.floor(mins / 60);
		if (hrs < 24) return `${hrs}h ago`;
		const days = Math.floor(hrs / 24);
		if (days < 7) return `${days}d ago`;
		return new Date(dateStr).toLocaleDateString();
	}

	function getFileExt(filename: string): string {
		return filename.split(".").pop()?.toUpperCase() || "FILE";
	}
</script>

<svelte:head>
	<title>Datasets | CHU Platform</title>
	<meta name="description" content="Manage, profile, and analyze tabular datasets." />
</svelte:head>

<div class="w-full h-full overflow-y-auto p-6 md:p-8 max-w-7xl mx-auto flex flex-col gap-6">
	<!-- Page Header -->
	<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-border/60">
		<div class="flex flex-col gap-1">
			<div class="flex items-center gap-2">
				<Badge variant="outline" class="gap-1.5 text-xs text-primary border-primary/30 bg-primary/10">
					<Database data-icon="inline-start" class="size-3.5" />
					Data Hub
				</Badge>
			</div>
			<h1 class="text-3xl font-bold tracking-tight">Datasets</h1>
			<p class="text-muted-foreground text-sm">
				Manage, profile, and analyze tabular datasets for AI workflows.
			</p>
		</div>

		<Button variant="default" class="gap-2 shrink-0" onclick={() => (showUploadModal = true)}>
			<Upload data-icon="inline-start" class="size-4" />
			Upload Dataset
		</Button>
	</div>

	<!-- High-level Metric KPI Cards -->
	<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
		<Card.Root class="border-border/60 shadow-xs">
			<Card.Header class="flex flex-row items-center justify-between pb-2 space-y-0">
				<Card.Title class="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
					Total Datasets
				</Card.Title>
				<Database class="size-4 text-muted-foreground" />
			</Card.Header>
			<Card.Content>
				<div class="text-2xl font-bold">{metrics.total}</div>
				<p class="text-xs text-muted-foreground mt-1">
					{metrics.totalRows.toLocaleString()} total rows cataloged
				</p>
			</Card.Content>
		</Card.Root>

		<Card.Root class="border-border/60 shadow-xs">
			<Card.Header class="flex flex-row items-center justify-between pb-2 space-y-0">
				<Card.Title class="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
					Ready for AI
				</Card.Title>
				<CheckCircle2 class="size-4 text-emerald-500" />
			</Card.Header>
			<Card.Content>
				<div class="text-2xl font-bold text-emerald-600 dark:text-emerald-400">{metrics.ready}</div>
				<p class="text-xs text-muted-foreground mt-1">
					Fully profiled and indexed
				</p>
			</Card.Content>
		</Card.Root>

		<Card.Root class="border-border/60 shadow-xs">
			<Card.Header class="flex flex-row items-center justify-between pb-2 space-y-0">
				<Card.Title class="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
					Ingestion Queue
				</Card.Title>
				<Loader2 class={cn("size-4 text-amber-500", metrics.processing > 0 && "animate-spin")} />
			</Card.Header>
			<Card.Content>
				<div class="text-2xl font-bold text-amber-600 dark:text-amber-400">{metrics.processing}</div>
				<p class="text-xs text-muted-foreground mt-1">
					{metrics.processing > 0 ? "Active background processing" : "Queue idle"}
				</p>
			</Card.Content>
		</Card.Root>

		<Card.Root class="border-border/60 shadow-xs">
			<Card.Header class="flex flex-row items-center justify-between pb-2 space-y-0">
				<Card.Title class="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
					Disk Storage
				</Card.Title>
				<HardDrive class="size-4 text-muted-foreground" />
			</Card.Header>
			<Card.Content>
				<div class="text-2xl font-bold font-mono">{formatBytes(metrics.totalBytes)}</div>
				<p class="text-xs text-muted-foreground mt-1">
					CSV, XLSX, Parquet storage
				</p>
			</Card.Content>
		</Card.Root>
	</div>

	<!-- Main Datasets Table & Filtering Card -->
	<Card.Root class="border-border/60 shadow-sm flex flex-col">
		<Card.Header class="pb-4 border-b border-border/40">
			<div class="flex flex-col md:flex-row items-stretch md:items-center justify-between gap-4">
				<!-- Filter Tabs -->
				<Tabs.Root value={statusFilter} onValueChange={handleFilterChange} class="w-full md:w-auto">
					<Tabs.List class="grid grid-cols-5 w-full md:w-auto text-xs">
						<Tabs.Trigger value="all">All ({datasets.length})</Tabs.Trigger>
						<Tabs.Trigger value="ready">Ready</Tabs.Trigger>
						<Tabs.Trigger value="processing">Processing</Tabs.Trigger>
						<Tabs.Trigger value="pending">Pending</Tabs.Trigger>
						<Tabs.Trigger value="failed">Failed</Tabs.Trigger>
					</Tabs.List>
				</Tabs.Root>

				<!-- Search Input & Refresh Button -->
				<div class="flex items-center gap-2 w-full md:w-72">
					<div class="relative w-full">
						<Input
							type="text"
							placeholder="Search datasets..."
							bind:value={searchQuery}
							class="pl-8 text-xs h-9 bg-background"
						/>
						<Search class="absolute left-2.5 top-2.5 size-3.5 text-muted-foreground" />
					</div>

					<Button
						variant="outline"
						size="icon"
						class="size-9 shrink-0"
						onclick={() => fetchDatasets(true)}
						title="Refresh dataset list"
					>
						<RefreshCw data-icon="inline-start" class={cn("size-4", loading && "animate-spin")} />
					</Button>
				</div>
			</div>
		</Card.Header>

		<Card.Content class="p-0">
			{#if loading && datasets.length === 0}
				<div class="p-8 flex flex-col gap-3">
					{#each Array(4) as _}
						<Skeleton class="h-12 w-full rounded-md" />
					{/each}
				</div>
			{:else if error}
				<div class="p-6 text-center flex flex-col items-center gap-3">
					<AlertCircle class="size-8 text-destructive" />
					<p class="text-sm font-medium text-destructive">{error}</p>
					<Button variant="outline" size="sm" onclick={() => fetchDatasets(true)}>Try Again</Button>
				</div>
			{:else if filteredDatasets.length === 0}
				<div class="p-12 text-center flex flex-col items-center gap-3 text-muted-foreground">
					<FileSpreadsheet class="size-10 text-muted-foreground/50" />
					<p class="text-sm font-semibold text-foreground">
						{searchQuery ? "No matching datasets found" : "No datasets uploaded yet"}
					</p>
					<p class="text-xs max-w-sm">
						{searchQuery
							? `No dataset matches "${searchQuery}". Try clearing your search.`
							: "Upload CSV, Excel, or Parquet files to start profiling and querying."}
					</p>
					{#if !searchQuery}
						<Button variant="outline" size="sm" class="mt-2 gap-2" onclick={() => (showUploadModal = true)}>
							<Upload data-icon="inline-start" class="size-3.5" />
							Upload First Dataset
						</Button>
					{/if}
				</div>
			{:else}
				<Table.Root>
					<Table.Header>
						<Table.Row class="bg-muted/40 text-xs font-semibold uppercase tracking-wider">
							<Table.Head class="w-20">Format</Table.Head>
							<Table.Head>Dataset Name</Table.Head>
							<Table.Head class="w-32">Status</Table.Head>
							<Table.Head class="w-28">Rows</Table.Head>
							<Table.Head class="w-28">Columns</Table.Head>
							<Table.Head class="w-28">Size</Table.Head>
							<Table.Head class="w-36">Uploaded</Table.Head>
							<Table.Head class="text-right w-36">Actions</Table.Head>
						</Table.Row>
					</Table.Header>
					<Table.Body>
						{#each filteredDatasets as ds (ds.id)}
							{@const ext = getFileExt(ds.original_filename)}
							<Table.Row class="hover:bg-muted/30 transition-colors">
								<!-- Format Badge -->
								<Table.Cell>
									<Badge variant="outline" class="font-mono text-[10px] font-bold tracking-tight">
										{ext}
									</Badge>
								</Table.Cell>

								<!-- Dataset Name -->
								<Table.Cell class="font-semibold">
									<a
										href="/datasets/{ds.id}"
										class="hover:text-primary hover:underline transition-colors truncate block max-w-md text-sm"
										title="View dataset details"
									>
										{ds.original_filename}
									</a>
								</Table.Cell>

								<!-- Status Badge -->
								<Table.Cell>
									{#if ds.status === "ready"}
										<Badge variant="secondary" class="gap-1.5 text-xs text-emerald-600 bg-emerald-500/10 border-emerald-500/20">
											<span class="size-1.5 rounded-full bg-emerald-500"></span>
											Ready
										</Badge>
									{:else if ds.status === "processing" || ds.status === "pending"}
										<Badge variant="secondary" class="gap-1.5 text-xs text-amber-600 bg-amber-500/10 border-amber-500/20">
											<span class="size-1.5 rounded-full bg-amber-500 animate-pulse"></span>
											{ds.status}
										</Badge>
									{:else}
										<Badge variant="destructive" class="gap-1.5 text-xs">
											<AlertCircle class="size-3" />
											Failed
										</Badge>
									{/if}
								</Table.Cell>

								<!-- Rows -->
								<Table.Cell class="font-mono text-xs">
									{ds.rows !== null && ds.rows !== undefined ? ds.rows.toLocaleString() : "—"}
								</Table.Cell>

								<!-- Columns -->
								<Table.Cell class="font-mono text-xs">
									{ds.columns !== null && ds.columns !== undefined ? ds.columns : "—"}
								</Table.Cell>

								<!-- Size -->
								<Table.Cell class="font-mono text-xs text-muted-foreground">
									{formatBytes(ds.file_size)}
								</Table.Cell>

								<!-- Uploaded -->
								<Table.Cell class="text-xs text-muted-foreground whitespace-nowrap">
									{formatRelativeTime(ds.created_at)}
								</Table.Cell>

								<!-- Actions -->
								<Table.Cell class="text-right">
									<div class="flex items-center justify-end gap-1">
										<!-- Inspect Details -->
										<Tooltip.Root>
											<Tooltip.Trigger>
												<Button
													variant="ghost"
													size="icon"
													class="size-8"
													href="/datasets/{ds.id}"
												>
													<Eye class="size-4 text-muted-foreground" />
												</Button>
											</Tooltip.Trigger>
											<Tooltip.Content>Inspect Schema & Preview</Tooltip.Content>
										</Tooltip.Root>

										<!-- Start AI Analysis -->
										<Tooltip.Root>
											<Tooltip.Trigger>
												<Button
													variant="ghost"
													size="icon"
													class="size-8 text-primary hover:text-primary hover:bg-primary/10"
													disabled={ds.status !== "ready"}
													onclick={() => startAnalysis(ds)}
												>
													<MessageSquare class="size-4" />
												</Button>
											</Tooltip.Trigger>
											<Tooltip.Content>Start AI Analysis Chat</Tooltip.Content>
										</Tooltip.Root>

										<!-- Delete Dataset -->
										<Tooltip.Root>
											<Tooltip.Trigger>
												<Button
													variant="ghost"
													size="icon"
													class="size-8 text-muted-foreground hover:text-destructive hover:bg-destructive/10"
													onclick={() => (deleteTargetItem = ds)}
												>
													<Trash2 class="size-4" />
												</Button>
											</Tooltip.Trigger>
											<Tooltip.Content>Delete Dataset</Tooltip.Content>
										</Tooltip.Root>
									</div>
								</Table.Cell>
							</Table.Row>
						{/each}
					</Table.Body>
				</Table.Root>
			{/if}
		</Card.Content>
	</Card.Root>
</div>

<!-- Upload Dataset Modal -->
<Dialog.Root bind:open={showUploadModal}>
	<Dialog.Content class="sm:max-w-md">
		<Dialog.Header>
			<Dialog.Title class="flex items-center gap-2">
				<Upload data-icon="inline-start" class="size-5 text-primary" />
				Upload Dataset
			</Dialog.Title>
			<Dialog.Description class="text-xs">
				Upload CSV, XLSX, TSV, Parquet, or JSON files for AI profiling and querying.
			</Dialog.Description>
		</Dialog.Header>

		{#if uploadError}
			<div class="p-3 rounded-lg bg-destructive/10 border border-destructive/20 text-destructive text-xs font-medium flex items-center justify-between">
				<span>{uploadError}</span>
				<Button variant="ghost" size="icon" class="size-6 text-destructive" onclick={() => (uploadError = null)}>
					<X class="size-3.5" />
				</Button>
			</div>
		{/if}

		<!-- Drag and Drop Dropzone -->
		<div
			class={cn(
				"border-2 border-dashed rounded-xl p-6 text-center flex flex-col items-center justify-center gap-3 transition-colors cursor-pointer bg-muted/20",
				uploadDragOver ? "border-primary bg-primary/5" : "border-border/80 hover:border-primary/60",
				uploadFile && "border-emerald-500/60 bg-emerald-500/5"
			)}
			ondragover={(e: DragEvent) => { e.preventDefault(); uploadDragOver = true; }}
			ondragleave={() => (uploadDragOver = false)}
			ondrop={handleDrop}
			onclick={() => document.getElementById("dataset-file-input")?.click()}
			onkeydown={(e) => e.key === "Enter" && document.getElementById("dataset-file-input")?.click()}
			role="button"
			tabindex="0"
		>
			<input
				id="dataset-file-input"
				type="file"
				accept=".csv,.tsv,.xlsx,.xls,.parquet,.json,.feather"
				class="hidden"
				onchange={handleFileSelect}
			/>

			{#if uploadFile}
				<FileSpreadsheet class="size-10 text-emerald-500" />
				<div class="flex flex-col gap-0.5">
					<span class="font-semibold text-sm truncate max-w-xs">{uploadFile.name}</span>
					<span class="text-xs text-muted-foreground font-mono">{formatBytes(uploadFile.size)}</span>
				</div>
				<Button
					variant="outline"
					size="sm"
					class="mt-1 text-xs"
					onclick={(e) => { e.stopPropagation(); uploadFile = null; }}
				>
					Choose Different File
				</Button>
			{:else}
				<Upload class="size-10 text-muted-foreground/60" />
				<div class="flex flex-col gap-1">
					<p class="text-sm font-semibold">Click to browse or drag & drop</p>
					<p class="text-xs text-muted-foreground">Supported formats: CSV, XLSX, Parquet, JSON, TSV</p>
				</div>
			{/if}
		</div>

		<Dialog.Footer class="gap-2 sm:gap-0">
			<Button variant="outline" onclick={() => (showUploadModal = false)} disabled={isUploading}>
				Cancel
			</Button>
			<Button
				variant="default"
				onclick={handleUploadSubmit}
				disabled={!uploadFile || isUploading}
				class="gap-2"
			>
				{#if isUploading}
					<Loader2 data-icon="inline-start" class="size-4 animate-spin" />
					Uploading...
				{:else}
					<Upload data-icon="inline-start" class="size-4" />
					Confirm Upload
				{/if}
			</Button>
		</Dialog.Footer>
	</Dialog.Content>
</Dialog.Root>

<!-- Delete Confirmation Modal -->
<Dialog.Root open={Boolean(deleteTargetItem)} onOpenChange={(open) => !open && (deleteTargetItem = null)}>
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

		{#if deleteTargetItem}
			<p class="text-sm font-medium text-foreground py-2">
				Are you sure you want to delete dataset <span class="font-bold font-mono">"{deleteTargetItem.original_filename}"</span>?
			</p>
		{/if}

		<Dialog.Footer class="gap-2 sm:gap-0">
			<Button variant="outline" onclick={() => (deleteTargetItem = null)} disabled={isDeleting}>
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
