<script lang="ts">
	import { mockReports } from '$lib/mock';
	import PageHeader from '$lib/components/app/layout/PageHeader.svelte';
	import Toolbar from '$lib/components/app/data/Toolbar.svelte';
	import FilterBar from '$lib/components/app/data/FilterBar.svelte';
	import SearchBar from '$lib/components/app/data/SearchBar.svelte';
	import Button from '$lib/components/app/common/Button.svelte';
	import ContentGrid from '$lib/components/app/layout/ContentGrid.svelte';
	import ReportCard from '$lib/components/app/cards/ReportCard.svelte';
	import EmptyState from '$lib/components/app/common/EmptyState.svelte';
	import { IconPlus, IconReportAnalytics } from '@tabler/icons-svelte';

	let search = $state('');
	let filters = $state([
		{
			id: 'status',
			label: 'Status',
			value: 'all',
			options: [
				{ label: 'All Statuses', value: 'all' },
				{ label: 'Published', value: 'published' },
				{ label: 'Draft', value: 'draft' }
			]
		}
	]);

	let reports = $derived.by(() => {
		let filtered = [...mockReports];
		if (search) {
			filtered = filtered.filter(
				(r) =>
					r.title.toLowerCase().includes(search.toLowerCase()) ||
					r.summary.toLowerCase().includes(search.toLowerCase())
			);
		}
		return filtered;
	});
</script>

<svelte:head>
	<title>Reports | CHU Analytics</title>
</svelte:head>

<div class="p-8 max-w-7xl mx-auto h-full flex flex-col">
	<PageHeader
		title="Reports"
		subtitle="AI-generated insights, summaries, and comprehensive analytical reports."
	>
		<Button variant="primary" icon={IconPlus}>Generate Report</Button>
	</PageHeader>

	<Toolbar>
		<SearchBar bind:value={search} placeholder="Search reports..." class="w-64" />
		<div class="w-px h-6 bg-border mx-2"></div>
		<FilterBar bind:filters />
	</Toolbar>

	<div class="flex-1 mt-6">
		{#if reports.length === 0}
			<EmptyState
				icon={IconReportAnalytics}
				title="No reports found"
				description="Use the Report Generator agent or click below to create your first report."
				class="mt-8"
			>
				<Button variant="primary" icon={IconPlus}>Generate Report</Button>
			</EmptyState>
		{:else}
			<ContentGrid columns={3} gap="lg">
				{#each reports as report}
					<ReportCard {report} />
				{/each}
			</ContentGrid>
		{/if}
	</div>
</div>
