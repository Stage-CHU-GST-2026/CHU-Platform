<script lang="ts">
	import { agents } from '$lib/state/agents.svelte';
	import PageHeader from '$lib/components/app/layout/PageHeader.svelte';
	import Section from '$lib/components/app/layout/Section.svelte';
	import ContentGrid from '$lib/components/app/layout/ContentGrid.svelte';
	import Button from '$lib/components/app/common/Button.svelte';
	import StatisticCard from '$lib/components/app/cards/StatisticCard.svelte';
	import AgentCard from '$lib/components/app/cards/AgentCard.svelte';
	import ChartCard from '$lib/components/app/cards/ChartCard.svelte';
	import { IconPlus, IconStethoscope, IconReport, IconDatabase } from '@tabler/icons-svelte';

	// Get active agents
	let activeAgents = $derived(
		agents.all.filter((a) => a.status === 'active' || a.status === 'processing').slice(0, 3)
	);
</script>

<svelte:head>
	<title>Dashboard | CHU Analytics</title>
</svelte:head>

<div class="p-8 max-w-7xl mx-auto">
	<PageHeader
		title="Workspace Overview"
		subtitle="Monitor AI agents, recent analyses, and system health."
	>
		<Button variant="primary" icon={IconPlus}>New Analysis</Button>
	</PageHeader>

	<Section>
		<ContentGrid columns={4} gap="md">
			<StatisticCard label="Total Agents" value={agents.all.length} icon={IconStethoscope} />
			<StatisticCard label="Active Tasks" value="14" delta="12%" trend="up" icon={IconReport} />
			<StatisticCard
				label="Data Processed"
				value="1.2"
				suffix="TB"
				delta="5%"
				trend="up"
				icon={IconDatabase}
			/>
			<StatisticCard label="System Health" value="98%" delta="Stable" trend="stable" />
		</ContentGrid>
	</Section>

	<Section title="Active Agents" contentClass="mt-4">
		{#snippet action()}
			<Button variant="ghost" size="sm" onclick={() => (window.location.href = '/agents')}
				>View All</Button
			>
		{/snippet}
		<ContentGrid columns={3} gap="lg">
			{#each activeAgents as agent}
				<AgentCard {agent} />
			{/each}
		</ContentGrid>
	</Section>

	<Section title="Recent Visualizations" contentClass="mt-4">
		<ContentGrid columns={3} gap="lg">
			<ChartCard
				title="Q2 Patient Admission Trends"
				type="bar"
				datasetName="patient_records_q2.csv"
				agentName="Clinical Data Analyzer"
				createdAt="2 hours ago"
			/>
			<ChartCard
				title="Lab Results Anomaly Detection"
				type="scatter"
				datasetName="lab_results_history.json"
				agentName="Medical Knowledge Assistant"
				createdAt="Yesterday"
			/>
			<ChartCard
				title="ER Wait Times Forecast"
				type="line"
				datasetName="er_logs_2026.csv"
				agentName="Predictive Modeler"
				createdAt="2 days ago"
			/>
		</ContentGrid>
	</Section>
</div>
