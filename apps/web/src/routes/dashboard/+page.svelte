<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { listDatasets, type DatasetSummary } from '$lib/api/datasets';
	import { listConversations, createConversation, type ConversationSummary } from '$lib/api/chat';
	import { IconLoader2 } from '@tabler/icons-svelte';

	let datasets = $state<DatasetSummary[]>([]);
	let conversations = $state<ConversationSummary[]>([]);
	let isLoading = $state(true);
	let error = $state<string | null>(null);

	async function loadOverviewData() {
		isLoading = true;
		error = null;
		try {
			const [dsList, convList] = await Promise.all([
				listDatasets(20, 0),
				listConversations(20, 0)
			]);
			datasets = dsList;
			conversations = convList;
		} catch (err) {
			console.error('Failed to load overview data', err);
			error = err instanceof Error ? err.message : 'Failed to load overview data';
		} finally {
			isLoading = false;
		}
	}

	onMount(() => {
		loadOverviewData();
	});

	let totalRows = $derived.by(() => datasets.reduce((acc, d) => acc + (d.rows || 0), 0));
	let readyDatasets = $derived.by(() => datasets.filter((d) => d.status === 'ready'));
	let totalArtifacts = $derived.by(() => conversations.reduce((acc, c) => acc + (c.artifact_count || 0), 0));

	function formatBytes(bytes: number | null | undefined): string {
		if (!bytes) return '—';
		const k = 1024;
		const sizes = ['B', 'KB', 'MB', 'GB'];
		const i = Math.floor(Math.log(bytes) / Math.log(k));
		return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
	}

	function formatDate(dateStr: string): string {
		if (!dateStr) return '—';
		const date = new Date(dateStr);
		return date.toLocaleDateString(undefined, {
			month: 'short',
			day: 'numeric',
			hour: '2-digit',
			minute: '2-digit'
		});
	}

	async function startNewAnalysis(datasetId?: string, datasetName?: string) {
		try {
			const title = datasetName ? `Analysis: ${datasetName}` : undefined;
			const conv = await createConversation(title, datasetId);
			await goto(`/dashboard/conversation?id=${conv.id}`);
		} catch (err) {
			console.error('Failed to start conversation', err);
		}
	}
</script>

<svelte:head>
	<title>Overview | CHU Platform</title>
	<meta
		name="description"
		content="Platform overview, datasets status, and active AI analytics conversations."
	/>
</svelte:head>

<div class="w-full h-full p-6 md:p-8 flex flex-col space-y-6 overflow-y-auto bg-bg">
	<!-- Page Header -->
	<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-border/80 pb-6">
		<div class="space-y-1.5">
			<h1 class="text-3xl sm:text-4xl font-semibold tracking-tight text-text-primary">
				Platform Overview
			</h1>
			<p class="text-sm sm:text-base text-text-secondary">
				Summary of connected datasets, data volume, and AI analytics workflows.
			</p>
		</div>
		<div class="flex items-center gap-2.5 shrink-0">
			<a
				href="/dashboard/datasets"
				class="inline-flex items-center px-4 py-2.5 rounded-lg bg-surface-elevated border border-border/80 text-sm font-semibold text-text-primary hover:bg-surface-hover hover:border-accent transition-colors"
			>
				Upload Dataset
			</a>
			<a
				href="/dashboard/new-chat"
				class="inline-flex items-center px-4 py-2.5 rounded-lg bg-accent text-black font-semibold text-sm hover:brightness-110 transition-all shadow-xs"
			>
				Start AI Analysis
			</a>
		</div>
	</div>

	<!-- Error state banner -->
	{#if error}
		<div class="p-4 rounded-xl border border-danger/40 bg-danger/10 text-danger text-sm flex items-center justify-between">
			<span>{error}</span>
			<button
				onclick={loadOverviewData}
				class="px-3 py-1.5 rounded bg-danger/20 hover:bg-danger/30 font-semibold cursor-pointer text-xs"
			>
				Retry
			</button>
		</div>
	{/if}

	<!-- Overview KPI Grid -->
	<div class="grid grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-5">
		<!-- Datasets Card -->
		<div class="p-5 rounded-xl border border-border/80 bg-surface shadow-xs space-y-2">
			<span class="text-xs sm:text-sm font-semibold uppercase tracking-wider text-text-secondary">Total Datasets</span>
			<div class="flex items-baseline justify-between pt-1">
				<span class="text-3xl sm:text-4xl font-bold font-mono text-text-primary">
					{isLoading ? '—' : datasets.length}
				</span>
				{#if !isLoading && datasets.length > 0}
					<span class="text-xs font-mono text-muted">
						{readyDatasets.length} ready
					</span>
				{/if}
			</div>
		</div>

		<!-- Processed Rows Card -->
		<div class="p-5 rounded-xl border border-border/80 bg-surface shadow-xs space-y-2">
			<span class="text-xs sm:text-sm font-semibold uppercase tracking-wider text-text-secondary">Total Data Rows</span>
			<div class="flex items-baseline justify-between pt-1">
				<span class="text-3xl sm:text-4xl font-bold font-mono text-text-primary">
					{isLoading ? '—' : totalRows.toLocaleString()}
				</span>
				<span class="text-xs font-mono text-muted">rows index</span>
			</div>
		</div>

		<!-- Conversations Card -->
		<div class="p-5 rounded-xl border border-border/80 bg-surface shadow-xs space-y-2">
			<span class="text-xs sm:text-sm font-semibold uppercase tracking-wider text-text-secondary">AI Conversations</span>
			<div class="flex items-baseline justify-between pt-1">
				<span class="text-3xl sm:text-4xl font-bold font-mono text-text-primary">
					{isLoading ? '—' : conversations.length}
				</span>
				<span class="text-xs font-mono text-muted">active sessions</span>
			</div>
		</div>

		<!-- Artifacts Card -->
		<div class="p-5 rounded-xl border border-border/80 bg-surface shadow-xs space-y-2">
			<span class="text-xs sm:text-sm font-semibold uppercase tracking-wider text-text-secondary">Generated Reports</span>
			<div class="flex items-baseline justify-between pt-1">
				<span class="text-3xl sm:text-4xl font-bold font-mono text-text-primary">
					{isLoading ? '—' : totalArtifacts}
				</span>
				<span class="text-xs font-mono text-muted">artifacts</span>
			</div>
		</div>
	</div>

	<!-- Main Content Section: Datasets & Conversations -->
	<div class="grid grid-cols-1 lg:grid-cols-3 gap-6 sm:gap-8">
		<!-- Left: Recent Datasets Overview (2 Cols) -->
		<div class="lg:col-span-2 space-y-3.5">
			<div class="flex items-center justify-between">
				<h2 class="text-sm sm:text-base uppercase font-bold text-text-primary tracking-wider">
					Recent Datasets
				</h2>
				<a
					href="/dashboard/datasets"
					class="text-sm text-accent font-semibold hover:underline"
				>
					View All ({datasets.length}) &rarr;
				</a>
			</div>

			<div class="border border-border/80 rounded-xl overflow-hidden bg-surface shadow-xs">
				{#if isLoading}
					<div class="p-10 text-center text-sm text-muted font-mono flex items-center justify-center gap-2">
						<IconLoader2 size={18} class="animate-spin text-accent" />
						<span>Loading dataset inventory...</span>
					</div>
				{:else if datasets.length === 0}
					<div class="p-10 text-center space-y-3.5">
						<div class="space-y-1">
							<p class="text-base font-semibold text-text-primary">No datasets found</p>
							<p class="text-sm text-text-secondary">Upload a CSV or Excel file to begin data profiling and analysis.</p>
						</div>
						<a
							href="/dashboard/datasets"
							class="inline-flex items-center px-4 py-2 rounded-lg bg-accent text-black font-semibold text-sm hover:brightness-110 transition-all"
						>
							Upload First Dataset
						</a>
					</div>
				{:else}
					<div class="overflow-x-auto">
						<table class="w-full text-left text-sm font-mono border-collapse">
							<thead>
								<tr class="bg-surface-elevated text-xs uppercase font-bold text-text-primary border-b border-border/80">
									<th class="px-5 py-3.5">Dataset Name</th>
									<th class="px-5 py-3.5">Status</th>
									<th class="px-5 py-3.5">Rows & Cols</th>
									<th class="px-5 py-3.5">Size</th>
									<th class="px-5 py-3.5 text-right">Actions</th>
								</tr>
							</thead>
							<tbody class="text-text-secondary divide-y divide-border/40">
								{#each datasets.slice(0, 6) as ds}
									<tr class="hover:bg-surface-hover/60 transition-colors">
										<!-- Filename -->
										<td class="px-5 py-3.5 font-sans font-bold text-text-primary text-sm">
											<a
												href="/dashboard/datasets/{ds.id}"
												class="hover:text-accent transition-colors truncate max-w-[240px] block"
											>
												{ds.original_filename}
											</a>
										</td>

										<!-- Status Badge -->
										<td class="px-5 py-3.5">
											{#if ds.status === 'ready'}
												<span class="inline-flex items-center px-2.5 py-1 rounded bg-success/10 text-success text-xs font-semibold border border-success/20">
													Ready
												</span>
											{:else if ds.status === 'processing' || ds.status === 'uploading'}
												<span class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded bg-warning/10 text-warning text-xs font-semibold border border-warning/20">
													<IconLoader2 size={12} class="animate-spin" />
													Processing
												</span>
											{:else}
												<span class="inline-flex items-center px-2.5 py-1 rounded bg-danger/10 text-danger text-xs font-semibold border border-danger/20">
													Error
												</span>
											{/if}
										</td>

										<!-- Dimensions -->
										<td class="px-5 py-3.5 font-medium text-sm">
											{ds.rows?.toLocaleString() ?? '—'} rows &middot; {ds.columns ?? '—'} cols
										</td>

										<!-- Size -->
										<td class="px-5 py-3.5 text-muted text-sm">
											{formatBytes(ds.file_size)}
										</td>

										<!-- Actions -->
										<td class="px-5 py-3.5 text-right">
											<div class="inline-flex items-center gap-2 justify-end">
												<a
													href="/dashboard/datasets/{ds.id}"
													class="px-3 py-1.5 rounded bg-surface-elevated border border-border/80 text-xs font-sans font-semibold text-text-primary hover:border-accent hover:text-accent transition-colors"
												>
													Details
												</a>
												<button
													onclick={() => startNewAnalysis(ds.id, ds.original_filename)}
													class="px-3 py-1.5 rounded bg-accent/10 border border-accent/30 text-xs font-sans font-semibold text-accent hover:bg-accent/20 transition-colors cursor-pointer"
												>
													Analyze
												</button>
											</div>
										</td>
									</tr>
								{/each}
							</tbody>
						</table>
					</div>
				{/if}
			</div>
		</div>

		<!-- Right: Recent AI Conversations (1 Col) -->
		<div class="space-y-3.5">
			<div class="flex items-center justify-between">
				<h2 class="text-sm sm:text-base uppercase font-bold text-text-primary tracking-wider">
					Recent Conversations
				</h2>
				<a
					href="/dashboard/new-chat"
					class="text-sm text-accent font-semibold hover:underline"
				>
					New Chat &rarr;
				</a>
			</div>

			<div class="border border-border/80 rounded-xl overflow-hidden bg-surface shadow-xs">
				{#if isLoading}
					<div class="p-10 text-center text-sm text-muted font-mono flex items-center justify-center gap-2">
						<IconLoader2 size={18} class="animate-spin text-accent" />
						<span>Loading conversations...</span>
					</div>
				{:else if conversations.length === 0}
					<div class="p-10 text-center space-y-3.5">
						<div class="space-y-1">
							<p class="text-sm font-semibold text-text-primary">No active conversations</p>
							<p class="text-xs text-text-secondary">Start an AI analysis turn to query and model your dataset.</p>
						</div>
						<a
							href="/dashboard/new-chat"
							class="inline-flex items-center px-3.5 py-2 rounded-lg bg-accent text-black font-semibold text-sm hover:brightness-110 transition-all"
						>
							Start New Chat
						</a>
					</div>
				{:else}
					<div class="divide-y divide-border/40 max-h-[420px] overflow-y-auto">
						{#each conversations.slice(0, 6) as conv}
							<a
								href="/dashboard/conversation?id={conv.id}"
								class="p-4 block hover:bg-surface-hover/60 transition-colors space-y-2 group"
							>
								<div class="flex items-center justify-between gap-2">
									<h3 class="text-sm font-bold text-text-primary truncate group-hover:text-accent transition-colors font-sans">
										{conv.title || 'Untitled Analysis'}
									</h3>
									<span class="text-xs font-mono text-muted shrink-0">
										{formatDate(conv.updated_at)}
									</span>
								</div>

								<div class="flex items-center justify-between text-xs text-text-secondary font-mono">
									{#if conv.dataset_name}
										<span class="text-accent font-semibold truncate max-w-[200px]">
											{conv.dataset_name}
										</span>
									{:else}
										<span class="text-muted">General Query</span>
									{/if}
									<span class="text-muted">{conv.message_count} msg</span>
								</div>
							</a>
						{/each}
					</div>
				{/if}
			</div>
		</div>
	</div>
</div>
