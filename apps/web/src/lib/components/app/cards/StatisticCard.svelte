<script lang="ts">
	import type { Component } from 'svelte';
	import Card from './Card.svelte';
	import { IconArrowUpRight, IconArrowDownRight, IconMinus } from '@tabler/icons-svelte';

	interface Props {
		label: string;
		value: string | number;
		delta?: string;
		trend?: 'up' | 'down' | 'stable';
		icon?: Component<any>;
		suffix?: string;
		class?: string;
	}

	let { label, value, delta, trend, icon: Icon, suffix, class: className = '' } = $props();

	const trendColors = {
		up: 'text-success bg-success/10',
		down: 'text-danger bg-danger/10',
		stable: 'text-muted bg-surface-elevated'
	};

	const trendIcons = {
		up: IconArrowUpRight,
		down: IconArrowDownRight,
		stable: IconMinus
	};
</script>

<Card padding="md" class={className}>
	<div class="flex items-center justify-between mb-3">
		<h3 class="text-[13px] font-medium text-text-secondary">{label}</h3>
		{#if Icon}
			<div class="text-muted">
				<Icon size={18} />
			</div>
		{/if}
	</div>

	<div class="flex items-baseline gap-2">
		<span class="text-[24px] font-semibold tracking-tight text-text-primary tabular-nums"
			>{value}</span
		>
		{#if suffix}
			<span class="text-[14px] text-text-secondary">{suffix}</span>
		{/if}
	</div>

	{#if delta && trend}
		{@const TrendIcon = trendIcons[trend]}
		<div class="flex items-center gap-1.5 mt-3">
			<span
				class="inline-flex items-center gap-0.5 px-1.5 py-0.5 rounded text-[11px] font-medium {trendColors[
					trend
				]}"
			>
				<TrendIcon size={12} />
				{delta}
			</span>
			<span class="text-[11px] text-text-secondary">vs previous</span>
		</div>
	{/if}
</Card>
