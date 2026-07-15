<script lang="ts">
	import type { KnowledgeDoc } from '$lib/types';
	import Card from './Card.svelte';
	import StatusBadge from '../common/StatusBadge.svelte';
	import ProgressIndicator from '../common/ProgressIndicator.svelte';
	import Button from '../common/Button.svelte';
	import {
		IconFileText,
		IconFileTypography,
		IconFileDescription,
		IconHeartRateMonitor,
		IconDots
	} from '@tabler/icons-svelte';

	interface Props {
		doc: KnowledgeDoc;
		class?: string;
	}

	let { doc, class: className = '' } = $props();

	function getFileIcon(type: string) {
		const t = type.toUpperCase();
		if (t === 'PDF') return IconFileText;
		if (t === 'DOCX') return IconFileTypography;
		if (t === 'TXT') return IconFileDescription;
		if (t === 'HL7' || t === 'FHIR') return IconHeartRateMonitor;
		return IconFileText;
	}

	const FileIcon = $derived(getFileIcon(doc.type));

	function formatDate(dateStr: string) {
		const d = new Date(dateStr);
		return d.toLocaleDateString('en-US', {
			month: 'short',
			day: 'numeric',
			hour: '2-digit',
			minute: '2-digit'
		});
	}
</script>

<Card hoverable class={className}>
	<div class="flex items-start gap-3 mb-4">
		<div
			class="w-10 h-10 rounded bg-surface-elevated flex items-center justify-center text-accent shrink-0"
		>
			<FileIcon size={20} />
		</div>
		<div class="flex-1 min-w-0 pt-0.5">
			<h3 class="text-[13px] font-semibold text-text-primary truncate">{doc.name}</h3>
			<div class="flex flex-wrap gap-1 mt-1.5">
				<span class="text-[10px] font-bold text-accent uppercase tracking-wider">{doc.type}</span>
				{#each doc.tags.slice(0, 2) as tag}
					<span class="text-[10px] text-text-secondary px-1.5 bg-surface-elevated rounded"
						>{tag}</span
					>
				{/each}
			</div>
		</div>
	</div>

	<div class="mb-4 bg-surface-elevated p-3 rounded-md border border-border">
		<div class="flex items-center justify-between mb-2 text-[11px]">
			<span class="font-medium text-text-secondary">Embedding</span>
			<StatusBadge status={doc.embeddingStatus} class="scale-90 origin-right" />
		</div>

		{#if doc.embeddingStatus === 'indexed'}
			<ProgressIndicator value={100} showValue={false} barClass="bg-success" />
			<div class="mt-1.5 text-[11px] text-text-secondary flex justify-between">
				<span>{doc.chunks.toLocaleString()} chunks</span>
				<span>{doc.size}</span>
			</div>
		{:else if doc.embeddingStatus === 'processing'}
			<ProgressIndicator value={45} showValue={false} barClass="bg-warning" />
			<div class="mt-1.5 text-[11px] text-text-secondary">Processing...</div>
		{:else if doc.embeddingStatus === 'failed'}
			<ProgressIndicator value={100} showValue={false} barClass="bg-danger" />
			<div class="mt-1.5 text-[11px] text-danger">Failed to extract text</div>
		{:else}
			<ProgressIndicator value={0} showValue={false} />
			<div class="mt-1.5 text-[11px] text-muted">Waiting...</div>
		{/if}
	</div>

	<div class="flex items-center justify-between pt-3">
		<span class="text-[10px] text-muted">Updated: {formatDate(doc.lastIndexed)}</span>
		<div class="flex gap-1">
			<Button variant="ghost" size="sm">Preview</Button>
			<Button variant="ghost" size="icon"><IconDots size={16} /></Button>
		</div>
	</div>
</Card>
