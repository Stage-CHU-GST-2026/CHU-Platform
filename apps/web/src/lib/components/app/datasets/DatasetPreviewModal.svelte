<script lang="ts">
	import { getDatasetPreview } from '$lib/api/datasets';
	import type { DatasetPreview, DatasetSummary } from '$lib/api/datasets';
	import { clickOutside, trapFocus } from '../common/actions';
	import { IconX, IconRefresh } from '@tabler/icons-svelte';

	let {
		dataset = $bindable<DatasetSummary | null>(null),
		open = $bindable(false)
	}: {
		dataset: DatasetSummary | null;
		open: boolean;
	} = $props();

	let previewData = $state<DatasetPreview | null>(null);
	let loading = $state(false);
	let error = $state<string | null>(null);
	let numRows = $state(25);
	let searchFilter = $state('');

	$effect(() => {
		if (open && dataset && dataset.status === 'ready') {
			loadPreview();
		}
	});

	async function loadPreview() {
		if (!dataset) return;
		loading = true;
		error = null;
		try {
			previewData = await getDatasetPreview(dataset.id, numRows);
		} catch (err: any) {
			error = err?.message || 'Failed to fetch dataset preview.';
		} finally {
			loading = false;
		}
	}

	function close() {
		open = false;
		dataset = null;
		previewData = null;
		error = null;
		searchFilter = '';
	}

	let filteredRows = $derived.by(() => {
		if (!previewData) return [];
		if (!searchFilter.trim()) return previewData.rows;
		const query = searchFilter.toLowerCase();

		return previewData.rows.filter((row) =>
			Object.values(row.values).some(
				(val) => val !== null && String(val).toLowerCase().includes(query)
			)
		);
	});

	function handleKeydown(e: KeyboardEvent) {
		if (open && e.key === 'Escape') {
			close();
		}
	}
</script>

<svelte:window onkeydown={handleKeydown} />

{#if open && dataset}
	<div
		class="fixed inset-0 z-[var(--z-modal)] bg-black/60 backdrop-blur-xs flex items-center justify-center p-4 lg:p-6 animate-in fade-in duration-150"
		role="presentation"
	>
		<div
			class="bg-surface border border-border rounded-lg shadow-2xl w-full h-[90vh] flex flex-col overflow-hidden animate-in zoom-in-95 duration-150"
			role="dialog"
			aria-modal="true"
			aria-labelledby="preview-modal-title"
			use:clickOutside={close}
			use:trapFocus={open}
			tabindex="-1"
		>
			<!-- Header with Icon-Only Close Button -->
			<div class="flex items-center justify-between px-6 py-4.5 border-b border-border bg-surface-elevated shrink-0">
				<div class="flex items-center gap-3 min-w-0">
					<span class="font-mono text-sm text-muted uppercase font-semibold">Preview:</span>
					<h3 id="preview-modal-title" class="text-base font-semibold font-mono text-text-primary truncate">
						{dataset.original_filename}
					</h3>
					<span class="text-xs font-mono text-muted">
						({dataset.rows?.toLocaleString() ?? '—'} rows × {dataset.columns ?? '—'} columns)
					</span>
				</div>

				<div class="flex items-center gap-3">
					<div class="flex items-center gap-2 text-sm text-text-secondary">
						<span>Rows:</span>
						<select
							bind:value={numRows}
							onchange={loadPreview}
							class="bg-surface border border-border rounded px-2.5 py-1 text-sm font-mono font-medium text-text-primary focus:outline-none cursor-pointer"
						>
							<option value={10}>10</option>
							<option value={25}>25</option>
							<option value={50}>50</option>
							<option value={100}>100</option>
						</select>
					</div>

					<button
						class="p-1.5 rounded text-muted hover:text-text-primary hover:bg-surface-hover transition-colors cursor-pointer"
						onclick={close}
						aria-label="Close dialog"
						title="Close"
					>
						<IconX size={20} />
					</button>
				</div>
			</div>

			<!-- Filter Bar with Icon-Only Reload Button -->
			<div class="px-6 py-3 border-b border-border bg-surface-elevated/40 flex items-center justify-between gap-4 shrink-0">
				<input
					bind:value={searchFilter}
					type="text"
					placeholder="Search values in preview table..."
					class="w-full max-w-md px-3.5 py-2 bg-surface border border-border rounded text-sm font-mono text-text-primary placeholder:text-muted focus:outline-none focus:border-accent"
				/>

				<button
					class="p-2 rounded border border-border bg-surface hover:bg-surface-hover text-text-secondary hover:text-text-primary transition-colors cursor-pointer"
					onclick={loadPreview}
					disabled={loading}
					aria-label="Reload preview data"
					title="Reload preview"
				>
					<IconRefresh size={18} class={loading ? 'animate-spin' : ''} />
				</button>
			</div>

			<!-- Content area -->
			<div class="flex-1 overflow-auto p-6 bg-canvas">
				{#if loading}
					<div class="h-full flex items-center justify-center text-sm font-mono text-muted">
						Loading preview data…
					</div>
				{:else if error}
					<div class="p-4 rounded bg-danger/10 border border-danger/20 text-danger text-sm font-medium">
						{error}
					</div>
				{:else if previewData && previewData.columns.length > 0}
					<div class="border border-border rounded overflow-hidden bg-surface">
						<div class="overflow-x-auto max-h-[calc(90vh-220px)]">
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
									{#each filteredRows as row}
										<tr class="hover:bg-surface-hover/60 transition-colors">
											<td class="px-3.5 py-2 text-xs text-muted border-r border-border/60 text-center select-none bg-surface/50">
												{row.row_number + 1}
											</td>
											{#each previewData.columns as col}
												{@const val = row.values[col]}
												<td class="px-4 py-2 text-text-secondary border-r border-border/30 whitespace-nowrap text-xs">
													{#if val === null || val === undefined}
														<span class="italic text-muted/50 font-sans">null</span>
													{:else if typeof val === 'boolean'}
														<span class="px-2 py-0.5 rounded text-xs font-bold {val ? 'text-success' : 'text-danger'}">
															{val ? 'TRUE' : 'FALSE'}
														</span>
													{:else}
														{val}
													{/if}
												</td>
											{/each}
										</tr>
									{/each}
								</tbody>
							</table>
						</div>
					</div>

					<div class="mt-3.5 flex items-center justify-between text-xs font-mono text-muted px-1">
						<span>Showing {filteredRows.length} of {previewData.rows.length} previewed rows</span>
						<span>Dataset Total: {previewData.total_rows.toLocaleString()} rows × {previewData.total_columns} columns</span>
					</div>
				{:else}
					<div class="h-full flex items-center justify-center text-sm font-mono text-muted">
						No preview data available.
					</div>
				{/if}
			</div>

			<!-- Footer -->
			<div class="px-6 py-4 bg-surface-elevated border-t border-border flex items-center justify-end shrink-0">
				<button
					type="button"
					class="px-5 py-2 rounded border border-border bg-surface hover:bg-surface-hover text-sm font-medium text-text-primary transition-colors cursor-pointer"
					onclick={close}
				>
					Close
				</button>
			</div>
		</div>
	</div>
{/if}
