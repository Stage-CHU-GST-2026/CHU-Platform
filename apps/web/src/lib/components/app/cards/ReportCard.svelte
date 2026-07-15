<script lang="ts">
	import type { Report } from '$lib/types';
	import Card from './Card.svelte';
	import Avatar from '../common/Avatar.svelte';
	import StatusBadge from '../common/StatusBadge.svelte';
	import Button from '../common/Button.svelte';
	import { IconDownload, IconShare, IconDots } from '@tabler/icons-svelte';

	interface Props {
		report: Report;
		class?: string;
	}

	let { report, class: className = '' } = $props();

	function formatDate(dateStr: string) {
		const d = new Date(dateStr);
		return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
	}
</script>

<Card hoverable class={className} padding="md">
	<div class="flex justify-between items-start mb-3">
		<h3 class="text-[14px] font-semibold text-text-primary line-clamp-1 flex-1 mr-3 leading-tight">
			{report.title}
		</h3>
		<StatusBadge status={report.status} />
	</div>

	<div class="flex items-center gap-2 mb-4">
		<Avatar name={report.authorName} src={report.authorAvatar} size="sm" />
		<div class="flex flex-col">
			<span class="text-[12px] font-medium text-text-primary leading-none">{report.authorName}</span
			>
			<span class="text-[11px] text-text-secondary mt-1">{formatDate(report.createdAt)}</span>
		</div>
	</div>

	<p class="text-[13px] text-text-secondary line-clamp-3 mb-4 flex-1">
		{report.summary}
	</p>

	<div class="flex flex-wrap gap-1.5 mb-5 mt-auto">
		{#each report.tags.slice(0, 3) as tag}
			<span
				class="px-2 py-0.5 rounded text-[11px] font-medium bg-surface-elevated text-text-secondary"
			>
				{tag}
			</span>
		{/each}
		{#if report.tags.length > 3}
			<span class="px-2 py-0.5 rounded text-[11px] font-medium bg-surface-elevated text-muted">
				+{report.tags.length - 3}
			</span>
		{/if}
	</div>

	<div class="flex items-center justify-between pt-4 border-t border-border mt-auto">
		<Button variant="secondary" size="sm" class="w-full mr-2">Preview</Button>
		<div class="flex gap-1">
			<Button variant="ghost" size="icon" aria-label="Download">
				<IconDownload size={16} />
			</Button>
			<Button variant="ghost" size="icon" aria-label="Share">
				<IconShare size={16} />
			</Button>
			<Button variant="ghost" size="icon" aria-label="More">
				<IconDots size={16} />
			</Button>
		</div>
	</div>
</Card>
