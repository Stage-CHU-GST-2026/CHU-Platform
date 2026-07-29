<script lang="ts">
	import type { DatasetSummary } from '$lib/api/datasets';

	let { datasets = [] }: { datasets: DatasetSummary[] } = $props();

	function formatBytes(bytes: number | null): string {
		if (bytes === null || bytes === 0) return '0 B';
		const k = 1024;
		const sizes = ['B', 'KB', 'MB', 'GB'];
		const i = Math.floor(Math.log(bytes) / Math.log(k));
		const val = (bytes / Math.pow(k, i)).toFixed(1);
		return val + ' ' + sizes[i];
	}

	let metrics = $derived.by(() => {
		const totalCount = datasets.length;
		const readyCount = datasets.filter((d) => d.status === 'ready').length;
		const totalRows = datasets.reduce((acc, d) => acc + (d.rows || 0), 0);
		const totalBytes = datasets.reduce((acc, d) => acc + (d.file_size || 0), 0);

		return [
			{
				label: 'TOTAL DATASETS',
				value: totalCount.toString(),
				subtext: `${readyCount} ready for analysis`
			},
			{
				label: 'READY STATUS',
				value: readyCount.toString(),
				subtext: totalCount > 0 ? `${Math.round((readyCount / totalCount) * 100)}% processed` : '0%'
			},
			{
				label: 'INDEXED ROWS',
				value: totalRows.toLocaleString(),
				subtext: 'Across all datasets'
			},
			{
				label: 'STORAGE USED',
				value: formatBytes(totalBytes),
				subtext: 'Max 500 MB / file'
			}
		];
	});
</script>

<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 w-full">
	{#each metrics as metric}
		<div class="bg-surface border border-border rounded-lg p-5 flex flex-col justify-between">
			<span class="text-xs font-mono font-semibold text-text-secondary tracking-wider">
				{metric.label}
			</span>
			<div class="mt-2.5 mb-1.5 flex items-baseline gap-2">
				<span class="text-3xl font-bold font-mono text-text-primary tracking-tight">
					{metric.value}
				</span>
			</div>
			<span class="text-sm text-muted font-sans">{metric.subtext}</span>
		</div>
	{/each}
</div>
