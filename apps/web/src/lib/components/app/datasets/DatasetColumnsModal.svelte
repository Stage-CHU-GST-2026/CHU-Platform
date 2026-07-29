<script lang="ts">
	import { getDatasetColumns } from '$lib/api/datasets';
	import type { ColumnInfo, DatasetSummary } from '$lib/api/datasets';
	import { clickOutside, trapFocus } from '../common/actions';
	import { IconX } from '@tabler/icons-svelte';

	let {
		dataset = $bindable<DatasetSummary | null>(null),
		open = $bindable(false)
	}: {
		dataset: DatasetSummary | null;
		open: boolean;
	} = $props();

	let columns = $state<ColumnInfo[]>([]);
	let loading = $state(false);
	let error = $state<string | null>(null);
	let searchFilter = $state('');

	$effect(() => {
		if (open && dataset && dataset.status === 'ready') {
			loadColumns();
		}
	});

	async function loadColumns() {
		if (!dataset) return;
		loading = true;
		error = null;
		try {
			columns = await getDatasetColumns(dataset.id);
		} catch (err: any) {
			error = err?.message || 'Failed to fetch column metadata.';
		} finally {
			loading = false;
		}
	}

	function close() {
		open = false;
		dataset = null;
		columns = [];
		error = null;
		searchFilter = '';
	}

	let filteredColumns = $derived.by(() => {
		if (!searchFilter.trim()) return columns;
		const query = searchFilter.toLowerCase();
		return columns.filter(
			(col) =>
				col.name.toLowerCase().includes(query) ||
				col.dtype.toLowerCase().includes(query)
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
			class="bg-surface border border-border rounded-lg shadow-2xl w-full max-w-5xl h-[85vh] flex flex-col overflow-hidden animate-in zoom-in-95 duration-150"
			role="dialog"
			aria-modal="true"
			aria-labelledby="columns-modal-title"
			use:clickOutside={close}
			use:trapFocus={open}
			tabindex="-1"
		>
			<!-- Header with Icon-Only Close Button -->
			<div class="flex items-center justify-between px-6 py-4.5 border-b border-border bg-surface-elevated shrink-0">
				<div class="flex items-center gap-3 min-w-0">
					<span class="font-mono text-sm text-muted uppercase font-semibold">Schema Profiling:</span>
					<h3 id="columns-modal-title" class="text-base font-semibold font-mono text-text-primary truncate">
						{dataset.original_filename}
					</h3>
					<span class="text-xs font-mono text-muted">
						({columns.length} columns profiled)
					</span>
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

			<!-- Filter Bar -->
			<div class="px-6 py-3 border-b border-border bg-surface-elevated/40 flex items-center justify-between gap-4 shrink-0">
				<input
					bind:value={searchFilter}
					type="text"
					placeholder="Filter columns by name or type..."
					class="w-full max-w-md px-3.5 py-2 bg-surface border border-border rounded text-sm font-mono text-text-primary placeholder:text-muted focus:outline-none focus:border-accent"
				/>

				<span class="text-sm font-mono text-muted">
					Showing {filteredColumns.length} of {columns.length} columns
				</span>
			</div>

			<!-- Content area -->
			<div class="flex-1 overflow-auto p-6 bg-canvas">
				{#if loading}
					<div class="h-full flex items-center justify-center text-sm font-mono text-muted">
						Loading column profiling data…
					</div>
				{:else if error}
					<div class="p-4 rounded bg-danger/10 border border-danger/20 text-danger text-sm font-medium">
						{error}
					</div>
				{:else if filteredColumns.length > 0}
					<div class="border border-border rounded overflow-hidden bg-surface">
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
												<div class="w-16 h-2 bg-surface-elevated border border-border rounded overflow-hidden">
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
					<div class="h-full flex items-center justify-center text-sm font-mono text-muted">
						No columns found matching filter.
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
