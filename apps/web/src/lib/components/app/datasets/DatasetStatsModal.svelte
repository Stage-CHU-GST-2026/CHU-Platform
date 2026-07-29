<script lang="ts">
	import { getDatasetStatistics } from '$lib/api/datasets';
	import type { DatasetStatistics, DatasetSummary } from '$lib/api/datasets';
	import { clickOutside, trapFocus } from '../common/actions';
	import { IconX } from '@tabler/icons-svelte';

	let {
		dataset = $bindable<DatasetSummary | null>(null),
		open = $bindable(false)
	}: {
		dataset: DatasetSummary | null;
		open: boolean;
	} = $props();

	let stats = $state<DatasetStatistics | null>(null);
	let loading = $state(false);
	let error = $state<string | null>(null);
	let activeTab = $state<'numeric' | 'missing' | 'types'>('numeric');

	$effect(() => {
		if (open && dataset && dataset.status === 'ready') {
			loadStats();
		}
	});

	async function loadStats() {
		if (!dataset) return;
		loading = true;
		error = null;
		try {
			stats = await getDatasetStatistics(dataset.id);
		} catch (err: any) {
			error = err?.message || 'Failed to fetch dataset statistics.';
		} finally {
			loading = false;
		}
	}

	function close() {
		open = false;
		dataset = null;
		stats = null;
		error = null;
		activeTab = 'numeric';
	}

	function formatNum(val: number | undefined | null): string {
		if (val === null || val === undefined) return '—';
		if (Number.isInteger(val)) return val.toLocaleString();
		return val.toFixed(3);
	}

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
			aria-labelledby="stats-modal-title"
			use:clickOutside={close}
			use:trapFocus={open}
			tabindex="-1"
		>
			<!-- Header with Icon-Only Close Button -->
			<div class="flex items-center justify-between px-6 py-4.5 border-b border-border bg-surface-elevated shrink-0">
				<div class="flex items-center gap-3 min-w-0">
					<span class="font-mono text-sm text-muted uppercase font-semibold">Statistics:</span>
					<h3 id="stats-modal-title" class="text-base font-semibold font-mono text-text-primary truncate">
						{dataset.original_filename}
					</h3>
					<span class="text-xs font-mono text-muted">
						({dataset.rows?.toLocaleString() ?? '—'} rows × {dataset.columns ?? '—'} columns)
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

			<!-- Tab Navigation -->
			<div class="px-6 py-2.5 border-b border-border bg-surface-elevated/40 flex items-center gap-3 shrink-0">
				<button
					class="px-4 py-1.5 rounded text-sm font-medium font-mono transition-colors cursor-pointer {activeTab === 'numeric'
						? 'bg-surface-elevated text-text-primary border border-border shadow-xs font-bold'
						: 'text-text-secondary hover:text-text-primary hover:bg-surface-hover'}"
					onclick={() => (activeTab = 'numeric')}
				>
					Numeric Summary
				</button>
				<button
					class="px-4 py-1.5 rounded text-sm font-medium font-mono transition-colors cursor-pointer {activeTab === 'missing'
						? 'bg-surface-elevated text-text-primary border border-border shadow-xs font-bold'
						: 'text-text-secondary hover:text-text-primary hover:bg-surface-hover'}"
					onclick={() => (activeTab = 'missing')}
				>
					Missing Values
				</button>
				<button
					class="px-4 py-1.5 rounded text-sm font-medium font-mono transition-colors cursor-pointer {activeTab === 'types'
						? 'bg-surface-elevated text-text-primary border border-border shadow-xs font-bold'
						: 'text-text-secondary hover:text-text-primary hover:bg-surface-hover'}"
					onclick={() => (activeTab = 'types')}
				>
					Column Types
				</button>
			</div>

			<!-- Content area -->
			<div class="flex-1 overflow-auto p-6 bg-canvas">
				{#if loading}
					<div class="h-full flex items-center justify-center text-sm font-mono text-muted">
						Computing statistics…
					</div>
				{:else if error}
					<div class="p-4 rounded bg-danger/10 border border-danger/20 text-danger text-sm font-medium">
						{error}
					</div>
				{:else if stats}
					{#if activeTab === 'numeric'}
						{#if stats.numeric_summary && Object.keys(stats.numeric_summary).length > 0}
							<div class="border border-border rounded overflow-hidden bg-surface">
								<div class="overflow-x-auto max-h-[calc(85vh-230px)]">
									<table class="w-full text-left text-sm font-mono border-collapse">
										<thead>
											<tr class="bg-surface-elevated border-b border-border text-xs uppercase font-bold text-text-primary">
												<th class="px-4 py-3 bg-surface-elevated border-r border-border/40">
													Metric / Column
												</th>
												{#each Object.keys(stats.numeric_summary) as col}
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
													{#each Object.keys(stats.numeric_summary) as col}
														{@const metricVal = stats.numeric_summary[col]?.[metric]}
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
							<div class="h-full flex items-center justify-center text-sm font-mono text-muted py-12">
								No numeric columns found in this dataset.
							</div>
						{/if}
					{:else if activeTab === 'missing'}
						{#if stats.missing_values && Object.keys(stats.missing_values).length > 0}
							<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
								{#each Object.entries(stats.missing_values) as [col, missingCount]}
									{@const totalRows = dataset.rows || 1}
									{@const pct = Math.round((missingCount / totalRows) * 100)}
									
									<div class="bg-surface border border-border rounded p-4 font-mono text-sm flex flex-col gap-2.5">
										<div class="flex items-center justify-between">
											<span class="font-bold text-text-primary">{col}</span>
											<span class="text-muted">{missingCount.toLocaleString()} nulls ({pct}%)</span>
										</div>
										
										<div class="w-full h-2 bg-surface-elevated border border-border/50 rounded overflow-hidden">
											<div
												class="h-full {pct > 50 ? 'bg-danger' : pct > 0 ? 'bg-warning' : 'bg-success'}"
												style="width: {pct}%"
											></div>
										</div>
									</div>
								{/each}
							</div>
						{:else}
							<div class="h-full flex items-center justify-center text-sm font-mono text-muted py-12">
								No missing values data available.
							</div>
						{/if}
					{:else if activeTab === 'types'}
						{#if stats.column_types && Object.keys(stats.column_types).length > 0}
							<div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3 font-mono text-sm">
								{#each Object.entries(stats.column_types) as [col, typeStr]}
									<div class="bg-surface border border-border rounded p-3 flex items-center justify-between">
										<span class="text-text-primary font-medium truncate mr-2">{col}</span>
										<span class="px-2.5 py-1 rounded bg-surface-elevated border border-border text-accent shrink-0 text-xs font-semibold">
											{typeStr}
										</span>
									</div>
								{/each}
							</div>
						{:else}
							<div class="h-full flex items-center justify-center text-sm font-mono text-muted py-12">
								No column types available.
							</div>
						{/if}
					{/if}
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
