<script lang="ts">
	import { mockKnowledgeDocs } from '$lib/mock';
	import PageHeader from '$lib/components/app/layout/PageHeader.svelte';
	import Toolbar from '$lib/components/app/data/Toolbar.svelte';
	import FilterBar from '$lib/components/app/data/FilterBar.svelte';
	import SearchBar from '$lib/components/app/data/SearchBar.svelte';
	import Button from '$lib/components/app/common/Button.svelte';
	import ContentGrid from '$lib/components/app/layout/ContentGrid.svelte';
	import KnowledgeCard from '$lib/components/app/cards/KnowledgeCard.svelte';
	import EmptyState from '$lib/components/app/common/EmptyState.svelte';
	import { IconPlus, IconBooks } from '@tabler/icons-svelte';

	let search = $state('');
	let filters = $state([
		{
			id: 'type',
			label: 'Type',
			value: 'all',
			options: [
				{ label: 'All Types', value: 'all' },
				{ label: 'PDF', value: 'pdf' },
				{ label: 'DOCX', value: 'docx' },
				{ label: 'TXT', value: 'txt' }
			]
		}
	]);

	let docs = $derived.by(() => {
		let filtered = [...mockKnowledgeDocs];
		if (search) {
			filtered = filtered.filter((d) => d.name.toLowerCase().includes(search.toLowerCase()));
		}
		return filtered;
	});
</script>

<svelte:head>
	<title>Knowledge Base | CHU Analytics</title>
</svelte:head>

<div class="p-8 max-w-7xl mx-auto h-full flex flex-col">
	<PageHeader
		title="Knowledge Base"
		subtitle="Manage documents, guidelines, and literature indexed for AI reference."
	>
		<Button variant="primary" icon={IconPlus}>Upload Document</Button>
	</PageHeader>

	<Toolbar>
		<SearchBar bind:value={search} placeholder="Search documents..." class="w-64" />
		<div class="w-px h-6 bg-border mx-2"></div>
		<FilterBar bind:filters />
	</Toolbar>

	<div class="flex-1 mt-6">
		{#if docs.length === 0}
			<EmptyState
				icon={IconBooks}
				title="No documents found"
				description="Upload medical guidelines, policies, or research papers to build your knowledge base."
				class="mt-8"
			>
				<Button variant="primary" icon={IconPlus}>Upload Document</Button>
			</EmptyState>
		{:else}
			<ContentGrid columns={3} gap="lg">
				{#each docs as doc}
					<KnowledgeCard {doc} />
				{/each}
			</ContentGrid>
		{/if}
	</div>
</div>
