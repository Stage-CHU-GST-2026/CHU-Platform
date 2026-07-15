<script lang="ts">
	import { datasets } from '$lib/state/datasets.svelte';
	import PageHeader from '$lib/components/app/layout/PageHeader.svelte';
	import Toolbar from '$lib/components/app/data/Toolbar.svelte';
	import FilterBar from '$lib/components/app/data/FilterBar.svelte';
	import SearchBar from '$lib/components/app/data/SearchBar.svelte';
	import Pagination from '$lib/components/app/data/Pagination.svelte';
	import Button from '$lib/components/app/common/Button.svelte';
	import StatusBadge from '$lib/components/app/common/StatusBadge.svelte';
	import FileUploader from '$lib/components/app/common/FileUploader.svelte';
	import Dialog from '$lib/components/app/common/Dialog.svelte';
	import EmptyState from '$lib/components/app/common/EmptyState.svelte';
	import Drawer from '$lib/components/app/common/Drawer.svelte';
	import DatasetTable from '$lib/components/app/data/DatasetTable.svelte';
	import Tabs from '$lib/components/app/common/Tabs.svelte';
	import { IconDatabase, IconUpload, IconFileDescription } from '@tabler/icons-svelte';

	let filters = $state([
		{
			id: 'type',
			label: 'Type',
			value: 'all',
			options: [
				{ label: 'All Types', value: 'all' },
				{ label: 'Tabular', value: 'tabular' },
				{ label: 'FHIR', value: 'fhir' },
				{ label: 'HL7', value: 'hl7' }
			]
		}
	]);

	let uploadOpen = $state(false);
	let selectedDatasetId = $state<string | null>(null);
	let selectedDataset = $derived(datasets.all.find((d) => d.id === selectedDatasetId));

	function formatDate(dateStr: string) {
		return new Date(dateStr).toLocaleDateString('en-US', {
			month: 'short',
			day: 'numeric',
			year: 'numeric'
		});
	}
</script>

<svelte:head>
	<title>Datasets | CHU Analytics</title>
</svelte:head>

<div class="p-8 max-w-7xl mx-auto h-full flex flex-col">
	<PageHeader title="Datasets" subtitle="Manage structured and unstructured data sources.">
		<Button variant="secondary" icon={IconDatabase}>Connect Database</Button>
		<Button variant="primary" icon={IconUpload} onclick={() => (uploadOpen = true)}
			>Upload Files</Button
		>
	</PageHeader>

	<Toolbar>
		<SearchBar bind:value={datasets.search} placeholder="Search datasets..." class="w-64" />
		<div class="w-px h-6 bg-border mx-2"></div>
		<FilterBar bind:filters />
	</Toolbar>

	<div class="flex-1 mt-4 border border-border bg-surface rounded-lg overflow-hidden flex flex-col">
		<div class="overflow-x-auto flex-1">
			<table class="w-full text-left border-collapse">
				<thead>
					<tr class="bg-surface-elevated border-b border-border">
						<th
							class="px-5 py-3 text-[12px] font-medium text-text-secondary w-full cursor-pointer hover:text-text-primary transition-colors"
							onclick={() => datasets.sort('name')}>Name</th
						>
						<th
							class="px-5 py-3 text-[12px] font-medium text-text-secondary cursor-pointer hover:text-text-primary transition-colors"
							onclick={() => datasets.sort('type')}>Type</th
						>
						<th
							class="px-5 py-3 text-[12px] font-medium text-text-secondary text-right cursor-pointer hover:text-text-primary transition-colors"
							onclick={() => datasets.sort('rows')}>Rows</th
						>
						<th
							class="px-5 py-3 text-[12px] font-medium text-text-secondary cursor-pointer hover:text-text-primary transition-colors"
							onclick={() => datasets.sort('size')}>Size</th
						>
						<th class="px-5 py-3 text-[12px] font-medium text-text-secondary text-center"
							>Quality</th
						>
						<th
							class="px-5 py-3 text-[12px] font-medium text-text-secondary cursor-pointer hover:text-text-primary transition-colors"
							onclick={() => datasets.sort('status')}>Status</th
						>
						<th
							class="px-5 py-3 text-[12px] font-medium text-text-secondary cursor-pointer hover:text-text-primary transition-colors"
							onclick={() => datasets.sort('updatedAt')}>Updated</th
						>
					</tr>
				</thead>
				<tbody>
					{#if datasets.paginated.length === 0}
						<tr>
							<td colspan="7">
								<EmptyState
									icon={IconFileDescription}
									title="No datasets found"
									description="Upload a new dataset or connect a database to get started."
									class="border-none m-8"
								/>
							</td>
						</tr>
					{:else}
						{#each datasets.paginated as dataset}
							<tr
								class="border-b border-border/50 hover:bg-surface-hover transition-colors cursor-pointer"
								onclick={() => (selectedDatasetId = dataset.id)}
							>
								<td
									class="px-5 py-3 text-[13px] font-medium text-text-primary flex items-center gap-3"
								>
									<IconDatabase size={16} class="text-muted shrink-0" />
									{dataset.name}
								</td>
								<td class="px-5 py-3 text-[12px] text-text-secondary uppercase tracking-wider"
									>{dataset.type}</td
								>
								<td class="px-5 py-3 text-[13px] text-text-secondary text-right tabular-nums"
									>{dataset.rows.toLocaleString()}</td
								>
								<td class="px-5 py-3 text-[13px] text-text-secondary tabular-nums"
									>{dataset.size}</td
								>
								<td class="px-5 py-3 text-[13px] text-text-secondary text-center">
									<span
										class="inline-flex items-center justify-center w-8 h-8 rounded-full border border-border"
										class:text-success={dataset.quality >= 90}
										class:text-warning={dataset.quality >= 70 && dataset.quality < 90}
										class:text-danger={dataset.quality < 70}
									>
										{dataset.quality}
									</span>
								</td>
								<td class="px-5 py-3 text-[13px] text-text-secondary">
									<StatusBadge status={dataset.status} />
								</td>
								<td class="px-5 py-3 text-[13px] text-text-secondary"
									>{formatDate(dataset.updatedAt)}</td
								>
							</tr>
						{/each}
					{/if}
				</tbody>
			</table>
		</div>

		<div class="px-5 py-3 border-t border-border bg-surface-elevated shrink-0">
			<Pagination bind:page={datasets.page} totalPages={datasets.totalPages} />
		</div>
	</div>
</div>

<Dialog
	open={uploadOpen}
	onclose={() => (uploadOpen = false)}
	title="Upload Dataset"
	description="Drag and drop files to upload to the workspace."
>
	<FileUploader accept=".csv,.json,.jsonl,.txt" multiple />
</Dialog>

<!-- Dataset Details Drawer -->
<Drawer
	open={!!selectedDataset}
	onclose={() => (selectedDatasetId = null)}
	title={selectedDataset?.name}
	width="w-[800px]"
>
	{#if selectedDataset}
		<div class="flex flex-col h-full">
			<div class="px-6 py-4 bg-surface-elevated border-b border-border grid grid-cols-4 gap-4">
				<div>
					<div class="text-[11px] text-text-secondary mb-1">Type</div>
					<div class="text-[13px] font-medium uppercase tracking-wider">{selectedDataset.type}</div>
				</div>
				<div>
					<div class="text-[11px] text-text-secondary mb-1">Rows</div>
					<div class="text-[13px] font-medium tabular-nums">
						{selectedDataset.rows.toLocaleString()}
					</div>
				</div>
				<div>
					<div class="text-[11px] text-text-secondary mb-1">Size</div>
					<div class="text-[13px] font-medium tabular-nums">{selectedDataset.size}</div>
				</div>
				<div>
					<div class="text-[11px] text-text-secondary mb-1">Status</div>
					<StatusBadge status={selectedDataset.status} />
				</div>
			</div>

			<Tabs
				active={datasets.panelTab}
				onchange={(id) => (datasets.panelTab = id as any)}
				tabs={[
					{ id: 'schema', label: 'Schema' },
					{ id: 'preview', label: 'Data Preview' },
					{ id: 'statistics', label: 'Statistics' },
					{ id: 'history', label: 'History' }
				]}
				class="px-2"
			/>

			<div class="flex-1 overflow-y-auto p-6">
				{#if datasets.panelTab === 'schema'}
					<div class="border border-border rounded-lg overflow-hidden">
						<table class="w-full text-left">
							<thead class="bg-surface-elevated border-b border-border">
								<tr>
									<th class="px-4 py-2 text-[12px] font-medium text-text-secondary">Column Name</th>
									<th class="px-4 py-2 text-[12px] font-medium text-text-secondary">Type</th>
									<th class="px-4 py-2 text-[12px] font-medium text-text-secondary">Nullable</th>
									<th class="px-4 py-2 text-[12px] font-medium text-text-secondary">Unique</th>
								</tr>
							</thead>
							<tbody>
								{#each selectedDataset.columns as col}
									<tr class="border-b border-border/50 last:border-0">
										<td class="px-4 py-2.5 text-[13px] font-medium text-text-primary">{col.name}</td
										>
										<td class="px-4 py-2.5 text-[12px] font-mono text-indigo">{col.type}</td>
										<td class="px-4 py-2.5 text-[13px] text-text-secondary"
											>{col.nullable ? 'Yes' : 'No'}</td
										>
										<td class="px-4 py-2.5 text-[13px] text-text-secondary">{col.unique}%</td>
									</tr>
								{:else}
									<tr>
										<td colspan="4" class="px-4 py-8 text-center text-muted text-[13px]">
											No schema information available for this dataset type.
										</td>
									</tr>
								{/each}
							</tbody>
						</table>
					</div>
				{:else if datasets.panelTab === 'preview'}
					{#if selectedDataset.columns.length > 0}
						<DatasetTable columns={selectedDataset.columns} />
					{:else}
						<EmptyState
							icon={IconDatabase}
							title="No Preview Available"
							description="Data preview is only available for structured datasets that have been fully processed."
						/>
					{/if}
				{:else}
					<div class="flex items-center justify-center h-48 text-muted text-[13px]">
						Content for {datasets.panelTab} will appear here.
					</div>
				{/if}
			</div>
		</div>
	{/if}

	<svelte:fragment slot="footer">
		<div class="flex justify-between items-center w-full">
			<Button variant="danger" size="sm">Delete</Button>
			<div class="flex gap-2">
				<Button variant="secondary" size="sm">Export</Button>
				<Button variant="primary" size="sm">Query Data</Button>
			</div>
		</div>
	</svelte:fragment>
</Drawer>
