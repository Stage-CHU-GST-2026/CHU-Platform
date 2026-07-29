<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/state';
	import { goto } from '$app/navigation';
	import { createConversation } from '$lib/api/chat';
	import {
		getDataset,
		getDatasetPreview,
		getDatasetColumns,
		getDatasetStatistics,
		deleteDataset
	} from '$lib/api/datasets';
	import type {
		DatasetDetail,
		DatasetPreview,
		ColumnInfo,
		DatasetStatistics,
		DatasetStatus
	} from '$lib/api/datasets';
	import {
		IconArrowLeft,
		IconEye,
		IconMessages,
		IconTrash,
		IconRefresh,
		IconTable,
		IconFileAnalytics,
		IconChartBar,
		IconCopy,
		IconCheck
	} from '@tabler/icons-svelte';

	let datasetId = $derived(page.params.id);

	let dataset = $state<DatasetDetail | null>(null);
	let previewData = $state<DatasetPreview | null>(null);
	let columnsData = $state<ColumnInfo[]>([]);
	let statsData = $state<DatasetStatistics | null>(null);

	let loading = $state(true);
	let error = $state<string | null>(null);

	// Tabs state
	let activeTab = $state<'preview' | 'schema' | 'stats'>('preview');

	// Preview Filters
	let previewNumRows = $state(25);
	let previewSearch = $state('');
	let previewLoading = $state(false);

	// Schema Filters
	let schemaSearch = $state('');

	// Stats Active Sub-Tab
	let statsSubTab = $state<'numeric' | 'missing' | 'types'>('numeric');

	// Copy feedback state
	let copiedState = $state<string | null>(null);

	// Delete modal
	let showDeleteModal = $state(false);
	let isDeleting = $state(false);

	async function loadAllData() {
		if (!datasetId) return;
		loading = true;
		error = null;
		try {
			const ds = await getDataset(datasetId);
			dataset = ds;

			if (ds.status === 'ready') {
				// Fetch preview, columns, and stats concurrently
				const [preview, cols, stats] = await Promise.allSettled([
					getDatasetPreview(datasetId, previewNumRows),
					getDatasetColumns(datasetId),
					getDatasetStatistics(datasetId)
				]);

				if (preview.status === 'fulfilled') previewData = preview.value;
				if (cols.status === 'fulfilled') columnsData = cols.value;
				if (stats.status === 'fulfilled') statsData = stats.value;
			}
		} catch (err: any) {
			error = err?.message || 'Failed to load dataset details.';
		} finally {
			loading = false;
		}
	}

	async function reloadPreview() {
		if (!datasetId || dataset?.status !== 'ready') return;
		previewLoading = true;
		try {
			previewData = await getDatasetPreview(datasetId, previewNumRows);
		} catch (err) {
			console.error('Failed to reload preview data', err);
		} finally {
			previewLoading = false;
		}
	}

	onMount(() => {
		loadAllData();
	});

	$effect(() => {
		if (datasetId) {
			loadAllData();
		}
	});

	let filteredPreviewRows = $derived.by(() => {
		if (!previewData) return [];
		if (!previewSearch.trim()) return previewData.rows;
		const query = previewSearch.toLowerCase();

		return previewData.rows.filter((row) =>
			Object.values(row.values).some(
				(val) => val !== null && String(val).toLowerCase().includes(query)
			)
		);
	});

	let filteredColumns = $derived.by(() => {
		if (!schemaSearch.trim()) return columnsData;
		const query = schemaSearch.toLowerCase();
		return columnsData.filter(
			(col) =>
				col.name.toLowerCase().includes(query) ||
				col.dtype.toLowerCase().includes(query)
		);
	});

	async function startAnalysis() {
		if (!dataset) return;
		try {
			const conv = await createConversation(`Dataset: ${dataset.original_filename}`);
			const initialPrompt = `I want to analyze the dataset "${dataset.original_filename}" (${dataset.rows?.toLocaleString() ?? 0} rows, ${dataset.columns ?? 0} columns). Could you summarize its structure and key trends?`;
			await goto(`/dashboard/conversation?id=${conv.id}&q=${encodeURIComponent(initialPrompt)}`);
		} catch (err) {
			console.error('Failed to launch conversation for dataset', err);
		}
	}

	async function confirmDelete() {
		if (!dataset || isDeleting) return;
		isDeleting = true;
		try {
			await deleteDataset(dataset.id);
			await goto('/dashboard/datasets');
		} catch (err: any) {
			alert(`Failed to delete dataset: ${err?.message || err}`);
			isDeleting = false;
		}
	}

	function copyToClipboard(text: string, id: string) {
		navigator.clipboard.writeText(text);
		copiedState = id;
		setTimeout(() => {
			if (copiedState === id) copiedState = null;
		}, 1500);
	}

	function formatBytes(bytes: number | null): string {
		if (bytes === null || bytes === 0) return '0 B';
		const k = 1024;
		const sizes = ['B', 'KB', 'MB', 'GB'];
		const i = Math.floor(Math.log(bytes) / Math.log(k));
		const val = (bytes / Math.pow(k, i)).toFixed(1);
		return val + ' ' + sizes[i];
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

	function formatNum(val: number | undefined | null): string {
		if (val === null || val === undefined) return '—';
		if (Number.isInteger(val)) return val.toLocaleString();
		return val.toFixed(3);
	}
</script>

<svelte:head>
	<title>{dataset ? dataset.original_filename : 'Dataset Detail'} | CHU Platform</title>
	<meta name="description" content="Detailed profiling and preview for dataset." />
</svelte:head>

<div class="w-full h-full p-6 md:p-8 flex flex-col space-y-6 overflow-y-auto">
	<!-- Top Navigation Breadcrumbs -->
	<div class="flex items-center justify-between border-b border-border pb-4">
		<a
			href="/dashboard/datasets"
			class="inline-flex items-center gap-2 text-sm font-semibold text-text-secondary hover:text-text-primary transition-colors"
		>
			<IconArrowLeft size={18} />
			<span>Back to Datasets</span>
		</a>

		<div class="flex items-center gap-2">
			<button
				class="p-2 rounded border border-border bg-surface hover:bg-surface-hover text-text-secondary hover:text-text-primary transition-colors cursor-pointer"
				onclick={loadAllData}
				aria-label="Reload dataset"
				title="Reload dataset data"
			>
				<IconRefresh size={18} class={loading ? 'animate-spin' : ''} />
			</button>

			{#if dataset}
				<button
					class="p-2 rounded border border-danger/30 text-danger hover:bg-danger/10 transition-colors cursor-pointer"
					onclick={() => (showDeleteModal = true)}
					aria-label="Delete dataset"
					title="Delete dataset"
				>
					<IconTrash size={18} />
				</button>
			{/if}
		</div>
	</div>

	{#if loading}
		<div class="h-64 border border-border rounded-lg p-8 flex flex-col items-center justify-center text-center bg-surface/30 space-y-3">
			<IconRefresh size={24} class="animate-spin text-accent" />
			<p class="text-sm font-mono text-muted">Loading dataset details and profiling schemas…</p>
		</div>
	{:else if error || !dataset}
		<div class="p-6 rounded-lg border border-danger/20 bg-danger/10 text-danger text-sm font-medium flex flex-col gap-3">
			<span>{error || 'Dataset not found.'}</span>
			<div>
				<a href="/dashboard/datasets" class="underline text-sm font-semibold">Return to Datasets list</a>
			</div>
		</div>
	{:else}
		<!-- Header Information Banner (Full Width UX) -->
		<div class="bg-surface border border-border rounded-lg p-6 flex flex-col md:flex-row md:items-center justify-between gap-6">
			<div class="space-y-3 min-w-0 flex-1">
				<div class="flex flex-wrap items-center gap-3">
					<span class="px-2.5 py-1 rounded bg-surface-elevated border border-border text-accent text-xs font-bold font-mono">
						{getFileExt(dataset.original_filename)}
					</span>

					<h1 class="text-2xl font-bold font-mono text-text-primary truncate">
						{dataset.original_filename}
					</h1>

					<div class="flex items-center gap-2 px-2.5 py-1 rounded bg-surface-elevated border border-border">
						<span class="w-2.5 h-2.5 rounded-full {getStatusDotColor(dataset.status)}"></span>
						<span class="capitalize text-xs font-semibold font-mono text-text-primary">{dataset.status}</span>
					</div>
				</div>

				<!-- Quick Chips -->
				<div class="flex flex-wrap items-center gap-4 text-sm font-mono text-text-secondary">
					<div>
						<span class="text-muted">Rows:</span>
						<span class="font-bold text-text-primary ml-1">{dataset.rows?.toLocaleString() ?? '—'}</span>
					</div>
					<span class="text-border">•</span>
					<div>
						<span class="text-muted">Columns:</span>
						<span class="font-bold text-text-primary ml-1">{dataset.columns ?? '—'}</span>
					</div>
					<span class="text-border">•</span>
					<div>
						<span class="text-muted">Size:</span>
						<span class="font-bold text-text-primary ml-1">{formatBytes(dataset.file_size)}</span>
					</div>
					<span class="text-border">•</span>
					<div>
						<span class="text-muted">Uploaded:</span>
						<span class="text-text-primary ml-1">{new Date(dataset.created_at).toLocaleDateString()}</span>
					</div>
				</div>

				{#if dataset.error_message}
					<div class="p-3 rounded bg-danger/10 border border-danger/20 text-danger text-xs font-sans">
						<strong>Error processing file:</strong> {dataset.error_message}
					</div>
				{/if}
			</div>

			<!-- Main Action Button -->
			<div class="flex items-center gap-3 shrink-0">
				<button
					class="px-5 py-2.5 rounded bg-accent text-white hover:bg-accent-hover text-sm font-semibold shadow-xs transition-colors cursor-pointer inline-flex items-center gap-2 disabled:opacity-40 disabled:cursor-not-allowed"
					onclick={startAnalysis}
					disabled={dataset.status !== 'ready'}
				>
					<IconMessages size={18} />
					<span>Start AI Analysis</span>
				</button>
			</div>
		</div>

		<!-- Main Tab Navigation -->
		<div class="border-b border-border flex items-center gap-4 text-sm">
			<button
				class="px-5 py-3 border-b-2 font-medium font-mono transition-colors cursor-pointer inline-flex items-center gap-2 {activeTab === 'preview'
					? 'border-accent text-text-primary font-bold'
					: 'border-transparent text-text-secondary hover:text-text-primary'}"
				onclick={() => (activeTab = 'preview')}
			>
				<IconTable size={18} />
				<span>Data Preview</span>
			</button>

			<button
				class="px-5 py-3 border-b-2 font-medium font-mono transition-colors cursor-pointer inline-flex items-center gap-2 {activeTab === 'schema'
					? 'border-accent text-text-primary font-bold'
					: 'border-transparent text-text-secondary hover:text-text-primary'}"
				onclick={() => (activeTab = 'schema')}
			>
				<IconFileAnalytics size={18} />
				<span>Schema & Profiling</span>
				<span class="px-2 py-0.5 rounded-full bg-surface-elevated text-xs border border-border text-muted">
					{columnsData.length}
				</span>
			</button>

			<button
				class="px-5 py-3 border-b-2 font-medium font-mono transition-colors cursor-pointer inline-flex items-center gap-2 {activeTab === 'stats'
					? 'border-accent text-text-primary font-bold'
					: 'border-transparent text-text-secondary hover:text-text-primary'}"
				onclick={() => (activeTab = 'stats')}
			>
				<IconChartBar size={18} />
				<span>Statistical Summary</span>
			</button>
		</div>

		<!-- TAB CONTENT PANES -->
		{#if activeTab === 'preview'}
			<!-- Preview Pane -->
			<div class="flex flex-col gap-4">
				<!-- Controls bar -->
				<div class="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-4">
					<input
						bind:value={previewSearch}
						type="text"
						placeholder="Search cell values in preview..."
						class="w-full max-w-md px-3.5 py-2 bg-surface border border-border rounded text-sm font-mono text-text-primary placeholder:text-muted focus:outline-none focus:border-accent"
					/>

					<div class="flex items-center justify-between sm:justify-end gap-3 text-sm font-mono text-text-secondary">
						<div class="flex items-center gap-2">
							<span>Limit rows:</span>
							<select
								bind:value={previewNumRows}
								onchange={reloadPreview}
								class="bg-surface border border-border rounded px-3 py-1.5 text-sm font-mono font-medium text-text-primary focus:outline-none cursor-pointer"
							>
								<option value={10}>10 rows</option>
								<option value={25}>25 rows</option>
								<option value={50}>50 rows</option>
								<option value={100}>100 rows</option>
							</select>
						</div>

						<button
							class="p-2 rounded border border-border bg-surface hover:bg-surface-hover text-text-secondary hover:text-text-primary transition-colors cursor-pointer"
							onclick={reloadPreview}
							disabled={previewLoading}
							aria-label="Reload preview data"
							title="Reload preview"
						>
							<IconRefresh size={18} class={previewLoading ? 'animate-spin' : ''} />
						</button>
					</div>
				</div>

				<!-- Table View -->
				{#if previewLoading}
					<div class="h-64 border border-border rounded p-8 flex items-center justify-center text-sm font-mono text-muted bg-surface/30">
						Reloading preview data…
					</div>
				{:else if previewData && previewData.columns.length > 0}
					<div class="border border-border rounded overflow-hidden bg-surface w-full">
						<div class="overflow-x-auto max-h-[60vh]">
							<table class="w-full text-left text-sm font-mono border-collapse">
								<thead>
									<tr class="bg-surface-elevated border-b border-border sticky top-0 z-10">
										<th class="px-3.5 py-2.5 text-xs text-muted border-r border-border/60 w-14 text-center select-none bg-surface-elevated">
											#
										</th>
										{#each previewData.columns as col}
											<th class="px-4 py-2.5 text-xs font-bold text-text-primary border-r border-border/40 whitespace-nowrap bg-surface-elevated uppercase tracking-wide">
												{col}
											</th>
										{/each}
									</tr>
								</thead>
								<tbody class="divide-y divide-border/40">
									{#each filteredPreviewRows as row}
										<tr class="hover:bg-surface-hover/60 transition-colors">
											<td class="px-3.5 py-2 text-xs text-muted border-r border-border/60 text-center select-none bg-surface/50">
												{row.row_number + 1}
											</td>
											{#each previewData.columns as col}
												{@const val = row.values[col]}
												{@const cellId = `${row.row_number}-${col}`}
												<td class="px-4 py-2 text-text-secondary border-r border-border/30 whitespace-nowrap text-xs group relative">
													{#if val === null || val === undefined}
														<span class="italic text-muted/50 font-sans">null</span>
													{:else if typeof val === 'boolean'}
														<span class="px-2 py-0.5 rounded text-xs font-bold {val ? 'text-success' : 'text-danger'}">
															{val ? 'TRUE' : 'FALSE'}
														</span>
													{:else}
														<span>{val}</span>
														<button
															class="opacity-0 group-hover:opacity-100 ml-2 p-0.5 text-muted hover:text-text-primary transition-opacity cursor-pointer inline-flex items-center"
															onclick={() => copyToClipboard(String(val), cellId)}
															title="Copy value"
														>
															{#if copiedState === cellId}
																<IconCheck size={12} class="text-success" />
															{:else}
																<IconCopy size={12} />
															{/if}
														</button>
													{/if}
												</td>
											{/each}
										</tr>
									{/each}
								</tbody>
							</table>
						</div>
					</div>

					<div class="flex items-center justify-between text-xs font-mono text-muted px-1">
						<span>Showing {filteredPreviewRows.length} of {previewData.rows.length} previewed rows</span>
						<span>Total: {previewData.total_rows.toLocaleString()} rows × {previewData.total_columns} columns</span>
					</div>
				{:else}
					<div class="h-48 border border-dashed border-border rounded p-8 flex items-center justify-center text-sm font-mono text-muted bg-surface/30">
						No preview data available for this dataset.
					</div>
				{/if}
			</div>

		{:else if activeTab === 'schema'}
			<!-- Schema & Profiling Pane -->
			<div class="flex flex-col gap-4">
				<div class="flex items-center justify-between gap-4">
					<input
						bind:value={schemaSearch}
						type="text"
						placeholder="Filter columns by name or type..."
						class="w-full max-w-md px-3.5 py-2 bg-surface border border-border rounded text-sm font-mono text-text-primary placeholder:text-muted focus:outline-none focus:border-accent"
					/>

					<span class="text-sm font-mono text-muted">
						Showing {filteredColumns.length} of {columnsData.length} columns
					</span>
				</div>

				{#if filteredColumns.length > 0}
					<div class="border border-border rounded overflow-hidden bg-surface w-full">
						<table class="w-full text-left text-sm font-mono border-collapse">
							<thead>
								<tr class="bg-surface-elevated border-b border-border text-xs text-text-primary uppercase font-bold tracking-wide">
									<th class="px-4 py-3">#</th>
									<th class="px-4 py-3">Column Name</th>
									<th class="px-4 py-3">Data Type</th>
									<th class="px-4 py-3">Null Count</th>
									<th class="px-4 py-3">Null %</th>
									<th class="px-4 py-3">Unique Values</th>
									<th class="px-4 py-3">Sample Value</th>
								</tr>
							</thead>
							<tbody class="divide-y divide-border/40 text-text-secondary">
								{#each filteredColumns as col, i}
									{@const totalRows = dataset.rows || 1}
									{@const nullPct = Math.round((col.null_count / totalRows) * 100)}
									<tr class="hover:bg-surface-hover/50 transition-colors">
										<td class="px-4 py-2.5 text-muted select-none text-xs">{i + 1}</td>
										<td class="px-4 py-2.5 font-bold text-text-primary">{col.name}</td>
										<td class="px-4 py-2.5">
											<span class="px-2.5 py-1 rounded bg-surface-elevated border border-border text-accent font-semibold text-xs">
												{col.dtype}
											</span>
										</td>
										<td class="px-4 py-2.5 font-medium">{col.null_count.toLocaleString()}</td>
										<td class="px-4 py-2.5">
											<div class="flex items-center gap-2">
												<span>{nullPct}%</span>
												<div class="w-20 h-2 bg-surface-elevated border border-border rounded overflow-hidden">
													<div class="h-full bg-warning" style="width: {nullPct}%"></div>
												</div>
											</div>
										</td>
										<td class="px-4 py-2.5 font-medium">{col.unique_count.toLocaleString()}</td>
										<td class="px-4 py-2.5 text-muted truncate max-w-xs">{col.sample ?? '—'}</td>
									</tr>
								{/each}
							</tbody>
						</table>
					</div>
				{:else}
					<div class="h-48 border border-dashed border-border rounded p-8 flex items-center justify-center text-sm font-mono text-muted bg-surface/30">
						No columns found matching filter.
					</div>
				{/if}
			</div>

		{:else if activeTab === 'stats'}
			<!-- Statistical Summary Pane -->
			<div class="flex flex-col gap-5">
				<!-- Sub-tabs -->
				<div class="flex items-center gap-3 border-b border-border pb-2">
					<button
						class="px-4 py-1.5 rounded text-sm font-medium font-mono transition-colors cursor-pointer {statsSubTab === 'numeric'
							? 'bg-surface-elevated text-text-primary border border-border shadow-xs font-bold'
							: 'text-text-secondary hover:text-text-primary hover:bg-surface-hover'}"
						onclick={() => (statsSubTab = 'numeric')}
					>
						Numeric Summary
					</button>
					<button
						class="px-4 py-1.5 rounded text-sm font-medium font-mono transition-colors cursor-pointer {statsSubTab === 'missing'
							? 'bg-surface-elevated text-text-primary border border-border shadow-xs font-bold'
							: 'text-text-secondary hover:text-text-primary hover:bg-surface-hover'}"
						onclick={() => (statsSubTab = 'missing')}
					>
						Missing Values
					</button>
					<button
						class="px-4 py-1.5 rounded text-sm font-medium font-mono transition-colors cursor-pointer {statsSubTab === 'types'
							? 'bg-surface-elevated text-text-primary border border-border shadow-xs font-bold'
							: 'text-text-secondary hover:text-text-primary hover:bg-surface-hover'}"
						onclick={() => (statsSubTab = 'types')}
					>
						Column Types
					</button>
				</div>

				{#if statsData}
					{#if statsSubTab === 'numeric'}
						{#if statsData.numeric_summary && Object.keys(statsData.numeric_summary).length > 0}
							<div class="border border-border rounded overflow-hidden bg-surface w-full">
								<div class="overflow-x-auto max-h-[60vh]">
									<table class="w-full text-left text-sm font-mono border-collapse">
										<thead>
											<tr class="bg-surface-elevated border-b border-border text-xs uppercase font-bold text-text-primary">
												<th class="px-4 py-3 bg-surface-elevated border-r border-border/40">
													Metric / Column
												</th>
												{#each Object.keys(statsData.numeric_summary) as col}
													<th class="px-4 py-3 text-accent border-r border-border/40 whitespace-nowrap bg-surface-elevated">
														{col}
													</th>
												{/each}
											</tr>
										</thead>
										<tbody class="divide-y divide-border/40 text-text-secondary">
											{#each ['count', 'mean', 'std', 'min', '25%', '50%', '75%', 'max'] as metric}
												<tr class="hover:bg-surface-hover/50 transition-colors">
													<td class="px-4 py-2.5 font-bold text-text-primary border-r border-border/40 capitalize bg-surface/50">
														{metric}
													</td>
													{#each Object.keys(statsData.numeric_summary) as col}
														{@const metricVal = statsData.numeric_summary[col]?.[metric]}
														<td class="px-4 py-2.5 border-r border-border/30 whitespace-nowrap">
															{formatNum(metricVal)}
														</td>
													{/each}
												</tr>
											{/each}
										</tbody>
									</table>
								</div>
							</div>
						{:else}
							<div class="h-48 border border-dashed border-border rounded p-8 flex items-center justify-center text-sm font-mono text-muted bg-surface/30">
								No numeric columns present for numerical matrix calculation.
							</div>
						{/if}
					{:else if statsSubTab === 'missing'}
						{#if statsData.missing_values && Object.keys(statsData.missing_values).length > 0}
							<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
								{#each Object.entries(statsData.missing_values) as [col, missingCount]}
									{@const totalRows = dataset.rows || 1}
									{@const pct = Math.round((missingCount / totalRows) * 100)}
									
									<div class="bg-surface border border-border rounded-lg p-4 font-mono text-sm flex flex-col gap-2.5">
										<div class="flex items-center justify-between">
											<span class="font-bold text-text-primary">{col}</span>
											<span class="text-muted">{missingCount.toLocaleString()} nulls ({pct}%)</span>
										</div>
										
										<div class="w-full h-2.5 bg-surface-elevated border border-border/50 rounded overflow-hidden">
											<div
												class="h-full {pct > 50 ? 'bg-danger' : pct > 0 ? 'bg-warning' : 'bg-success'}"
												style="width: {pct}%"
											></div>
										</div>
									</div>
								{/each}
							</div>
						{:else}
							<div class="h-48 border border-dashed border-border rounded p-8 flex items-center justify-center text-sm font-mono text-muted bg-surface/30">
								No missing values recorded.
							</div>
						{/if}
					{:else if statsSubTab === 'types'}
						{#if statsData.column_types && Object.keys(statsData.column_types).length > 0}
							<div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3 font-mono text-sm">
								{#each Object.entries(statsData.column_types) as [col, typeStr]}
									<div class="bg-surface border border-border rounded-lg p-3.5 flex items-center justify-between">
										<span class="text-text-primary font-medium truncate mr-2">{col}</span>
										<span class="px-2.5 py-1 rounded bg-surface-elevated border border-border text-accent shrink-0 text-xs font-semibold">
											{typeStr}
										</span>
									</div>
								{/each}
							</div>
						{:else}
							<div class="h-48 border border-dashed border-border rounded p-8 flex items-center justify-center text-sm font-mono text-muted bg-surface/30">
								No column types recorded.
							</div>
						{/if}
					{/if}
				{:else}
					<div class="h-48 border border-dashed border-border rounded p-8 flex items-center justify-center text-sm font-mono text-muted bg-surface/30">
						Statistical summary unavailable.
					</div>
				{/if}
			</div>
		{/if}
	{/if}
</div>

<!-- Delete Confirmation Modal -->
{#if showDeleteModal && dataset}
	<div class="fixed inset-0 z-[var(--z-modal)] bg-black/60 backdrop-blur-xs flex items-center justify-center p-4">
		<div class="bg-surface border border-border rounded-lg p-6 max-w-md w-full shadow-2xl space-y-4">
			<div class="flex items-center justify-between border-b border-border pb-3">
				<div>
					<h3 class="text-base font-semibold text-text-primary">Delete Dataset</h3>
					<p class="text-xs text-muted mt-0.5">This action cannot be undone.</p>
				</div>
				<button
					class="p-1.5 rounded text-muted hover:text-text-primary hover:bg-surface-hover transition-colors cursor-pointer"
					onclick={() => (showDeleteModal = false)}
					aria-label="Close dialog"
					title="Close"
				>
					<IconX size={18} />
				</button>
			</div>

			<p class="text-sm text-text-secondary font-mono">
				Are you sure you want to delete dataset "{dataset.original_filename}"?
			</p>

			<div class="flex items-center justify-end gap-3 pt-2">
				<button
					class="px-4 py-2 rounded border border-border text-sm font-medium text-text-secondary hover:text-text-primary hover:bg-surface-hover"
					onclick={() => (showDeleteModal = false)}
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
