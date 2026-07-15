<script lang="ts">
	import Card from './Card.svelte';
	import Button from '../common/Button.svelte';
	import {
		IconChartBar,
		IconChartLine,
		IconChartScatter,
		IconTable,
		IconDots
	} from '@tabler/icons-svelte';

	interface Props {
		title: string;
		type: 'bar' | 'line' | 'scatter' | 'heatmap' | 'table';
		datasetName: string;
		agentName: string;
		createdAt: string;
		class?: string;
	}

	let { title, type, datasetName, agentName, createdAt, class: className = '' } = $props();

	const TypeIcon = {
		bar: IconChartBar,
		line: IconChartLine,
		scatter: IconChartScatter,
		heatmap: IconChartBar,
		table: IconTable
	}[type];
</script>

<Card hoverable class="flex flex-col h-full {className}" padding="none">
	<!-- SVG Placeholder for chart -->
	<div
		class="h-40 bg-surface-elevated flex items-center justify-center border-b border-border relative overflow-hidden group"
	>
		<div
			class="absolute top-2 left-2 z-10 px-2 py-1 rounded bg-surface/80 backdrop-blur border border-border flex items-center gap-1.5 text-[10px] font-medium text-text-primary uppercase tracking-wider"
		>
			<TypeIcon size={12} class="text-accent" />
			{type}
		</div>

		<!-- Subtle visual patterns based on chart type -->
		<div
			class="absolute inset-0 opacity-20 transition-opacity group-hover:opacity-40 flex items-center justify-center"
		>
			{#if type === 'bar'}
				<div class="flex items-end gap-2 h-20 w-3/4">
					<div class="w-full bg-accent h-[40%] rounded-t-sm"></div>
					<div class="w-full bg-accent h-[70%] rounded-t-sm"></div>
					<div class="w-full bg-accent h-[50%] rounded-t-sm"></div>
					<div class="w-full bg-accent h-[90%] rounded-t-sm"></div>
					<div class="w-full bg-accent h-[60%] rounded-t-sm"></div>
				</div>
			{:else if type === 'line'}
				<svg
					width="80%"
					height="80%"
					viewBox="0 0 100 50"
					preserveAspectRatio="none"
					stroke="var(--color-accent)"
					stroke-width="2"
					fill="none"
				>
					<path d="M0,40 L20,30 L40,35 L60,15 L80,25 L100,5" stroke-linejoin="round" />
				</svg>
			{:else if type === 'scatter'}
				<div class="w-3/4 h-3/4 relative">
					<div class="absolute w-1.5 h-1.5 bg-accent rounded-full left-[10%] top-[80%]"></div>
					<div class="absolute w-1.5 h-1.5 bg-accent rounded-full left-[20%] top-[60%]"></div>
					<div class="absolute w-1.5 h-1.5 bg-accent rounded-full left-[35%] top-[70%]"></div>
					<div class="absolute w-1.5 h-1.5 bg-accent rounded-full left-[45%] top-[40%]"></div>
					<div class="absolute w-1.5 h-1.5 bg-accent rounded-full left-[60%] top-[50%]"></div>
					<div class="absolute w-1.5 h-1.5 bg-accent rounded-full left-[75%] top-[20%]"></div>
					<div class="absolute w-1.5 h-1.5 bg-accent rounded-full left-[85%] top-[30%]"></div>
				</div>
			{:else if type === 'table'}
				<div class="w-3/4 h-3/4 flex flex-col gap-2">
					<div class="w-full h-1 bg-border rounded"></div>
					<div class="w-full h-1 bg-border/50 rounded"></div>
					<div class="w-full h-1 bg-border/50 rounded"></div>
					<div class="w-full h-1 bg-border/50 rounded"></div>
				</div>
			{/if}
		</div>
	</div>

	<div class="p-4 flex flex-col flex-1">
		<h3 class="text-[14px] font-semibold text-text-primary mb-3 line-clamp-2 leading-snug">
			{title}
		</h3>

		<div class="flex flex-col gap-1.5 text-[11px] text-text-secondary mt-auto mb-4">
			<div class="flex justify-between">
				<span>Dataset:</span>
				<span class="text-text-primary truncate ml-2 max-w-[60%]">{datasetName}</span>
			</div>
			<div class="flex justify-between">
				<span>Agent:</span>
				<span class="text-text-primary truncate ml-2 max-w-[60%]">{agentName}</span>
			</div>
		</div>

		<div class="flex items-center justify-between pt-3 border-t border-border mt-auto">
			<span class="text-[10px] text-muted">{createdAt}</span>
			<div class="flex gap-1">
				<Button variant="ghost" size="sm">View</Button>
				<Button variant="ghost" size="icon"><IconDots size={16} /></Button>
			</div>
		</div>
	</div>
</Card>
