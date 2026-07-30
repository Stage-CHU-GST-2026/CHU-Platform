<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { goto } from '$app/navigation';
	import { createConversation } from '$lib/api/chat';
	import { listDatasets, deleteDataset } from '$lib/api/datasets';
	import type { DatasetSummary, DatasetStatus } from '$lib/api/datasets';
	import DatasetMetricsBanner from '$lib/components/app/datasets/DatasetMetricsBanner.svelte';
	import DatasetUploadModal from '$lib/components/app/datasets/DatasetUploadModal.svelte';
	import { IconRefresh, IconX, IconEye, IconMessages, IconTrash } from '@tabler/icons-svelte';

	let datasets = $state<DatasetSummary[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);

	// Filters & Search
	let statusFilter = $state<string>('all');
	let searchQuery = $state('');

	// Modals State
	let showUploadModal = $state(false);

	// Delete Confirmation Modal
	let deleteTargetItem = $state<DatasetSummary | null>(null);
	let isDeleting = $state(false);

	let pollInterval: ReturnType<typeof setInterval> | null = null;

	async function fetchDatasets(showLoadingState = true) {
		if (showLoadingState) loading = true;
		error = null;
		try {
			const filter = statusFilter === 'all' ? undefined : (statusFilter as DatasetStatus);
			datasets = await listDatasets(100, 0, filter);
		} catch (err: any) {
			error = err?.message || 'Failed to load datasets.';
		} finally {
			loading = false;
		}
	}

	onMount(() => {
		fetchDatasets(true);
		pollInterval = setInterval(() => {
			const hasPending = datasets.some(
				(d) => d.status === 'uploading' || d.status === 'processing'
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

	async function confirmDelete() {
		if (!deleteTargetItem || isDeleting) return;
		isDeleting = true;
		try {
			await deleteDataset(deleteTargetItem.id);
			datasets = datasets.filter((d) => d.id !== deleteTargetItem!.id);
			deleteTargetItem = null;
		} catch (err: any) {
			alert(`Failed to delete dataset: ${err?.message || err}`);
		} finally {
			isDeleting = false;
		}
	}

	async function startAnalysis(dataset: DatasetSummary) {
		try {
			const conv = await createConversation(`Dataset: ${dataset.original_filename}`, dataset.id);
			const initialPrompt = `I want to analyze the dataset "${dataset.original_filename}" (${dataset.rows?.toLocaleString() ?? 0} rows, ${dataset.columns ?? 0} columns). Could you summarize its structure and key trends?`;
			await goto(`/dashboard/conversation?id=${conv.id}&q=${encodeURIComponent(initialPrompt)}`);
		} catch (err) {
			console.error('Failed to launch conversation for dataset', err);
		}
	}

	function formatBytes(bytes: number | null): string {
		if (bytes === null || bytes === 0) return '0 B';
		const k = 1024;
		const sizes = ['B', 'KB', 'MB', 'GB'];
		const i = Math.floor(Math.log(bytes) / Math.log(k));
		const val = (bytes / Math.pow(k, i)).toFixed(1);
		return val + ' ' + sizes[i];
	}

	function formatRelativeTime(dateStr: string): string {
		const diff = Date.now() - new Date(dateStr).getTime();
		const mins = Math.floor(diff / 60000);
		if (mins < 1) return 'just now';
		if (mins < 60) return `${mins}m ago`;
		const hrs = Math.floor(mins / 60);
		if (hrs < 24) return `${hrs}h ago`;
		const days = Math.floor(hrs / 24);
		if (days < 7) return `${days}d ago`;
		return new Date(dateStr).toLocaleDateString();
	}

	function getStatusDotColor(status: DatasetStatus): string {
		switch (status) {
			case 'ready':
				return 'bg-success';
			case 'processing':
			case 'uploading':
				return 'bg-warning animate-pulse';
			case 'error':
				return 'bg-danger';
		}
	}

	function getFileExt(filename: string): string {
		return filename.split('.').pop()?.toUpperCase() || 'FILE';
	}
</script>

<svelte:head>
	<title>Datasets | CHU Platform</title>
	<meta name="description" content="Manage and analyze tabular datasets." />
</svelte:head>

<div class="w-full h-full p-6 md:p-8 flex flex-col space-y-6 overflow-y-auto">
	<!-- Page Header -->
	<div
		class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-border pb-5"
	>
		<div>
			<h1 class="text-2xl md:text-3xl font-bold tracking-tight text-text-primary">Datasets</h1>
			<p class="text-sm text-text-secondary mt-1">
				Manage, profile, and analyze tabular datasets for AI workflows.
			</p>
		</div>

		<button
			class="px-5 py-2.5 rounded bg-accent text-white hover:bg-accent-hover text-sm font-semibold shadow-xs transition-colors cursor-pointer shrink-0"
			onclick={() => (showUploadModal = true)}
		>
			Upload Dataset
		</button>
	</div>

	<!-- High-level Metrics -->
	<DatasetMetricsBanner {datasets} />

	<!-- Filter Tabs & Search Bar -->
	<div class="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-4 pt-2">
		<!-- Status Tabs -->
		<div class="flex items-center gap-2 border-b border-border text-sm">
			{#each [{ id: 'all', label: 'All Datasets' }, { id: 'ready', label: 'Ready' }, { id: 'processing', label: 'Processing' }, { id: 'uploading', label: 'Uploading' }, { id: 'error', label: 'Error' }] as tab}
				<button
					class="px-4 py-2.5 border-b-2 font-medium transition-colors cursor-pointer whitespace-nowrap {statusFilter ===
					tab.id
						? 'border-accent text-text-primary font-bold'
						: 'border-transparent text-text-secondary hover:text-text-primary'}"
					onclick={() => handleFilterChange(tab.id)}
				>
					{tab.label}
				</button>
			{/each}
		</div>

		<!-- Search & Refresh -->
		<div class="flex items-center gap-2 max-w-md w-full">
			<input
				bind:value={searchQuery}
				type="text"
				placeholder="Filter datasets by filename..."
				class="w-full px-3.5 py-2 bg-surface border border-border rounded text-sm font-mono text-text-primary placeholder:text-muted focus:outline-none focus:border-accent"
			/>

			<button
				class="p-2 rounded border border-border bg-surface hover:bg-surface-hover text-text-secondary hover:text-text-primary transition-colors cursor-pointer shrink-0"
				onclick={() => fetchDatasets(true)}
				aria-label="Refresh datasets"
				title="Refresh datasets"
			>
				<IconRefresh size={18} class={loading ? 'animate-spin' : ''} />
			</button>
		</div>
	</div>

	<!-- High-Density Datasets Table View (Full Width with Icon Actions) -->
	<div class="w-full flex-1">
		{#if loading && datasets.length === 0}
			<div
				class="h-48 border border-border rounded p-8 flex items-center justify-center text-sm font-mono text-muted bg-surface/30"
			>
				Loading datasets…
			</div>
		{:else if error}
			<div
				class="p-4 rounded border border-danger/20 bg-danger/10 text-danger text-sm font-medium flex items-center justify-between"
			>
				<span>{error}</span>
				<button class="underline text-sm font-semibold" onclick={() => fetchDatasets(true)}
					>Try again</button
				>
			</div>
		{:else if filteredDatasets.length === 0}
			<div
				class="h-48 border border-dashed border-border rounded p-8 flex flex-col items-center justify-center text-center bg-surface/30"
			>
				<p class="text-sm font-semibold text-text-primary">
					{searchQuery ? 'No matching datasets' : 'No datasets uploaded yet'}
				</p>
				<p class="text-sm text-muted max-w-sm mt-1">
					{searchQuery
						? `No dataset found matching "${searchQuery}".`
						: 'Upload CSV, Excel, or Parquet files to start profiling and querying.'}
				</p>
			</div>
		{:else}
			<div class="border border-border-subtle rounded-lg overflow-hidden bg-surface w-full">
				<table class="w-full text-left text-sm font-mono border-collapse">
					<thead>
						<tr
							class="bg-surface-elevated text-xs text-text-primary uppercase font-bold tracking-wide"
						>
							<th class="px-5 py-3.5">Format</th>
							<th class="px-5 py-3.5">Dataset Name</th>
							<th class="px-5 py-3.5">Status</th>
							<th class="px-5 py-3.5">Rows</th>
							<th class="px-5 py-3.5">Columns</th>
							<th class="px-5 py-3.5">Size</th>
							<th class="px-5 py-3.5">Uploaded</th>
							<th class="px-5 py-3.5 text-right">Actions</th>
						</tr>
					</thead>
					<tbody class="text-text-secondary">
						{#each filteredDatasets as ds (ds.id)}
							{@const ext = getFileExt(ds.original_filename)}
							{@const dotColor = getStatusDotColor(ds.status)}

							<tr class="hover:bg-surface-hover/50 transition-colors">
								<!-- Format Badge -->
								<td class="px-5 py-3.5">
									<span
										class="px-2.5 py-1 rounded bg-surface-elevated border border-border text-accent text-xs font-bold"
									>
										{ext}
									</span>
								</td>

								<!-- Filename (Clickable link to dataset detail page) -->
								<td class="px-5 py-3.5 font-bold text-text-primary text-sm">
									<a
										href="/dashboard/datasets/{ds.id}"
										class="hover:text-accent hover:underline transition-colors truncate block max-w-md"
										title="View dataset details"
									>
										{ds.original_filename}
									</a>
									{#if ds.status === 'error' && ds.error_message}
										<p class="text-xs text-danger font-sans mt-0.5">{ds.error_message}</p>
									{/if}
								</td>

								<!-- Status -->
								<td class="px-5 py-3.5">
									<div class="flex items-center gap-2">
										<span class="w-2.5 h-2.5 rounded-full {dotColor}"></span>
										<span class="capitalize text-text-primary font-medium text-xs">{ds.status}</span
										>
									</div>
								</td>

								<!-- Rows -->
								<td class="px-5 py-3.5 font-medium">
									{ds.rows !== null && ds.rows !== undefined ? ds.rows.toLocaleString() : '—'}
								</td>

								<!-- Columns -->
								<td class="px-5 py-3.5 font-medium">
									{ds.columns !== null && ds.columns !== undefined ? ds.columns : '—'}
								</td>

								<!-- Size -->
								<td class="px-5 py-3.5 font-medium">{formatBytes(ds.file_size)}</td>

								<!-- Uploaded -->
								<td class="px-5 py-3.5 font-sans text-muted text-xs"
									>{formatRelativeTime(ds.created_at)}</td
								>

								<!-- Actions (Clean Icon Buttons) -->
								<td class="px-5 py-3.5 text-right">
									<div class="flex items-center justify-end gap-1.5">
										<!-- View Details Icon -->
										<a
											href="/dashboard/datasets/{ds.id}"
											class="p-2 rounded text-text-secondary hover:text-accent hover:bg-surface-hover transition-colors inline-flex items-center justify-center"
											title="View dataset details & profiling"
											aria-label="View dataset details"
										>
											<IconEye size={18} />
										</a>

										<!-- Chat / Start Analysis Icon -->
										<button
											class="p-2 rounded text-text-secondary hover:text-accent hover:bg-surface-hover transition-colors disabled:opacity-30 disabled:hover:bg-transparent disabled:hover:text-text-secondary cursor-pointer inline-flex items-center justify-center"
											onclick={() => startAnalysis(ds)}
											disabled={ds.status !== 'ready'}
											title="Start AI Analysis Chat"
											aria-label="Start AI Analysis Chat"
										>
											<IconMessages size={18} />
										</button>

										<!-- Delete Icon -->
										<button
											class="p-2 rounded text-text-secondary hover:text-danger hover:bg-danger/10 transition-colors cursor-pointer inline-flex items-center justify-center"
											onclick={() => (deleteTargetItem = ds)}
											title="Delete dataset"
											aria-label="Delete dataset"
										>
											<IconTrash size={18} />
										</button>
									</div>
								</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
		{/if}
	</div>
</div>

<!-- Upload Modal -->
<DatasetUploadModal bind:open={showUploadModal} onUploaded={() => fetchDatasets(true)} />

<!-- Delete Confirmation Modal -->
{#if deleteTargetItem}
	<div
		class="fixed inset-0 z-[var(--z-modal)] bg-black/60 backdrop-blur-xs flex items-center justify-center p-4"
	>
		<div
			class="bg-surface border border-border rounded-lg p-6 max-w-md w-full shadow-2xl space-y-4"
		>
			<div class="flex items-center justify-between border-b border-border pb-3">
				<div>
					<h3 class="text-base font-semibold text-text-primary">Delete Dataset</h3>
					<p class="text-xs text-muted mt-0.5">This action cannot be undone.</p>
				</div>
				<button
					class="p-1.5 rounded text-muted hover:text-text-primary hover:bg-surface-hover transition-colors cursor-pointer"
					onclick={() => (deleteTargetItem = null)}
					aria-label="Close dialog"
					title="Close"
				>
					<IconX size={18} />
				</button>
			</div>

			<p class="text-sm text-text-secondary font-mono">
				Are you sure you want to delete dataset "{deleteTargetItem.original_filename}"?
			</p>

			<div class="flex items-center justify-end gap-3 pt-2">
				<button
					class="px-4 py-2 rounded border border-border text-sm font-medium text-text-secondary hover:text-text-primary hover:bg-surface-hover"
					onclick={() => (deleteTargetItem = null)}
					disabled={isDeleting}
				>
					Cancel
				</button>
				<button
					class="px-5 py-2 rounded bg-danger text-white hover:bg-danger/90 text-sm font-semibold"
					onclick={confirmDelete}
					disabled={isDeleting}
				>
					{isDeleting ? 'Deleting…' : 'Delete Permanently'}
				</button>
			</div>
		</div>
	</div>
{/if}
