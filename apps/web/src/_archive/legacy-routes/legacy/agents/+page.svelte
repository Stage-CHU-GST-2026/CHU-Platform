<script lang="ts">
	import { agents } from '$lib/state/agents.svelte';
	import PageHeader from '$lib/components/app/layout/PageHeader.svelte';
	import Toolbar from '$lib/components/app/data/Toolbar.svelte';
	import FilterBar from '$lib/components/app/data/FilterBar.svelte';
	import SearchBar from '$lib/components/app/data/SearchBar.svelte';
	import Button from '$lib/components/app/common/Button.svelte';
	import Tabs from '$lib/components/app/common/Tabs.svelte';
	import Section from '$lib/components/app/layout/Section.svelte';
	import ContentGrid from '$lib/components/app/layout/ContentGrid.svelte';
	import AgentCard from '$lib/components/app/cards/AgentCard.svelte';
	import EmptyState from '$lib/components/app/common/EmptyState.svelte';
	import { IconPlus, IconRobot } from '@tabler/icons-svelte';

	let filters = $state([
		{
			id: 'category',
			label: 'Category',
			value: 'all',
			options: [
				{ label: 'All Categories', value: 'all' },
				{ label: 'Analysis', value: 'analysis' },
				{ label: 'Knowledge', value: 'knowledge' },
				{ label: 'Reporting', value: 'reporting' }
			]
		},
		{
			id: 'sort',
			label: 'Sort by',
			value: 'name',
			options: [
				{ label: 'Name (A-Z)', value: 'name' },
				{ label: 'Workload', value: 'workload' },
				{ label: 'Status', value: 'status' }
			]
		}
	]);

	let activeTab = $state('all');
</script>

<svelte:head>
	<title>AI Agents | CHU Analytics</title>
</svelte:head>

<div class="p-8 max-w-7xl mx-auto h-full flex flex-col">
	<PageHeader
		title="AI Agents"
		subtitle="Manage and monitor specialized AI agents in your workspace."
	>
		<Button variant="primary" icon={IconPlus}>Create Agent</Button>
	</PageHeader>

	<Tabs
		active={activeTab}
		onchange={(id) => (activeTab = id)}
		class="mb-6"
		tabs={[
			{ id: 'all', label: `All Agents (${agents.all.length})` },
			{ id: 'active', label: 'Active' },
			{ id: 'idle', label: 'Idle' },
			{ id: 'error', label: 'Errors' }
		]}
	/>

	<Toolbar>
		<SearchBar bind:value={agents.searchQuery} placeholder="Search agents..." class="w-64" />
		<div class="w-px h-6 bg-border mx-2"></div>
		<FilterBar bind:filters />
	</Toolbar>

	<div class="flex-1 mt-4">
		{#if agents.filtered.length === 0}
			<EmptyState
				icon={IconRobot}
				title="No agents found"
				description="Try adjusting your search or filters to find what you're looking for."
				class="mt-8"
			>
				<Button variant="secondary" onclick={() => (agents.searchQuery = '')}>Clear Search</Button>
			</EmptyState>
		{:else}
			{#each Object.entries(agents.grouped) as [category, categoryAgents]}
				<Section title={category} class="mb-8">
					<ContentGrid columns={3} gap="lg">
						{#each categoryAgents as agent}
							<AgentCard {agent} />
						{/each}
					</ContentGrid>
				</Section>
			{/each}
		{/if}
	</div>
</div>
