<script lang="ts">
	import {
		IconChevronDown,
		IconPlus,
		IconMicrophone,
		IconSparkles,
		IconBrain,
		IconMessageCircle,
		IconArrowRight,
		IconSquare,
		IconDatabase,
		IconX,
		IconCheck
	} from '@tabler/icons-svelte';
	import Dropdown, { type DropdownItem } from '$lib/components/app/common/Dropdown.svelte';
	import { listDatasets } from '$lib/api/datasets';
	import type { DatasetSummary } from '$lib/api/datasets';

	interface Props {
		input?: string;
		isStreaming?: boolean;
		onsubmit?: () => void;
		selectedDataset?: DatasetSummary | null;
	}

	let {
		input = $bindable(''),
		isStreaming = false,
		onsubmit = () => {},
		selectedDataset = $bindable(null)
	} = $props<Props>();

	let textareaEl = $state<HTMLTextAreaElement | null>(null);
	let selectedModel = $state('Gemini');
	let focused = $state(false);
	let showDatasetPicker = $state(false);
	let availableDatasets = $state<DatasetSummary[]>([]);
	let loadingDatasets = $state(false);

	const modelItems: DropdownItem[] = [
		{ label: 'Gemini', icon: IconSparkles, action: () => (selectedModel = 'Gemini') },
		{ label: 'Claude', icon: IconBrain, action: () => (selectedModel = 'Claude') },
		{ label: 'ChatGPT', icon: IconMessageCircle, action: () => (selectedModel = 'ChatGPT') }
	];

	let hasText = $derived((input || '').trim().length > 0);

	export function resizeTextarea() {
		if (textareaEl) {
			textareaEl.style.height = 'auto';
			textareaEl.style.height = textareaEl.scrollHeight + 'px';
		}
	}

	function handleKeydown(e: KeyboardEvent) {
		if (e.key === 'Enter' && !e.shiftKey) {
			e.preventDefault();
			if (hasText && !isStreaming) onsubmit();
		}
	}

	function handleStop() {
		// Reload the page to stop the current stream — the backend
		// will detect the disconnected client and abort generation.
		window.location.reload();
	}

	async function toggleDatasetPicker() {
		if (showDatasetPicker) {
			showDatasetPicker = false;
			return;
		}
		loadingDatasets = true;
		showDatasetPicker = true;
		try {
			availableDatasets = await listDatasets(100, 0, 'ready');
		} catch (e) {
			console.error('Failed to load datasets', e);
			availableDatasets = [];
		} finally {
			loadingDatasets = false;
		}
	}

	function selectDataset(ds: DatasetSummary) {
		selectedDataset = ds;
		showDatasetPicker = false;
	}

	function clearDataset() {
		selectedDataset = null;
	}
</script>

<div class="composer {focused ? 'composer-focused' : ''}">
	<!-- Selected dataset badge -->
	{#if selectedDataset}
		<div class="flex items-center gap-2 px-3 pt-2 pb-1">
			<div
				class="flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-accent/10 border border-accent/20 text-[12px] font-medium text-accent"
			>
				<IconDatabase size={13} stroke={1.5} />
				<span class="truncate max-w-50">{selectedDataset.original_filename}</span>
				<span class="text-muted">({selectedDataset.rows?.toLocaleString() ?? '?'} rows)</span>
				<button
					onclick={clearDataset}
					class="ml-1 p-0.5 rounded hover:bg-accent/20 transition-colors cursor-pointer"
					aria-label="Remove dataset"
				>
					<IconX size={12} stroke={2} />
				</button>
			</div>
		</div>
	{/if}

	<!-- Textarea at the top -->
	<textarea
		bind:this={textareaEl}
		bind:value={input}
		class="w-full bg-transparent text-text-primary placeholder-muted resize-none focus:outline-none focus:ring-0 border-0 shadow-none px-3 pt-2 text-[15.5px] leading-[1.7] min-h-[28px] max-h-48 overflow-y-auto disabled:opacity-40"
		placeholder={selectedDataset
			? `Ask about "${selectedDataset.original_filename}"...`
			: 'Ask anything...'}
		rows="1"
		disabled={isStreaming}
		onkeydown={handleKeydown}
		oninput={resizeTextarea}
		onfocus={() => (focused = true)}
		onblur={() => (focused = false)}></textarea>

	<!-- Toolbar row at the bottom -->
	<div class="flex items-center justify-between w-full px-1.5 pb-0.5">
		<!-- Left side: + button (dataset picker) & Model selector -->
		<div class="flex items-center gap-1 relative">
			<div class="relative">
				<button
					onclick={toggleDatasetPicker}
					class="w-8 h-8 flex items-center justify-center rounded-md hover:bg-surface-hover text-muted hover:text-text-secondary transition-colors shrink-0 cursor-pointer disabled:opacity-30 {selectedDataset
						? 'text-accent'
						: ''}"
					aria-label="Select dataset"
					disabled={isStreaming}
					title="Select dataset"
				>
					<IconDatabase size={16} stroke={2} />
				</button>

				<!-- Dataset picker dropdown -->
				{#if showDatasetPicker}
					<div
						class="absolute bottom-full left-0 mb-1 w-72 max-h-64 overflow-y-auto rounded-lg border border-border bg-surface-elevated shadow-lg z-50"
						role="listbox"
						aria-label="Available datasets"
					>
						<div
							class="px-3 py-2 text-[11px] font-semibold text-muted uppercase tracking-wider border-b border-border"
						>
							Select a dataset
						</div>
						{#if loadingDatasets}
							<div class="px-3 py-4 text-center text-[12px] text-muted">Loading datasets...</div>
						{:else if availableDatasets.length === 0}
							<div class="px-3 py-4 text-center text-[12px] text-muted">
								No ready datasets found.
								<a href="/dashboard/datasets" class="text-accent hover:underline">Upload one</a>
							</div>
						{:else}
							{#each availableDatasets as ds}
								<button
									class="w-full flex items-center gap-2.5 px-3 py-2.5 text-left text-[13px] hover:bg-surface-hover transition-colors cursor-pointer border-b border-border/30 last:border-0"
									onclick={() => selectDataset(ds)}
									role="option"
									aria-selected={selectedDataset?.id === ds.id}
								>
									<IconDatabase size={14} stroke={1.5} class="shrink-0 text-muted" />
									<div class="flex-1 min-w-0">
										<div class="font-medium text-text-primary truncate">{ds.original_filename}</div>
										<div class="text-[11px] text-muted">
											{ds.rows?.toLocaleString() ?? '?'} rows &middot; {ds.columns ?? '?'} cols
										</div>
									</div>
									{#if selectedDataset?.id === ds.id}
										<IconCheck size={14} stroke={2} class="text-accent shrink-0" />
									{/if}
								</button>
							{/each}
						{/if}
					</div>
				{/if}
			</div>

			<Dropdown items={modelItems} align="left" direction="up" width="w-48">
				{#snippet trigger()}
					<button
						class="flex items-center gap-1.5 px-2.5 h-8 rounded-md hover:bg-surface-hover text-muted hover:text-text-secondary transition-colors text-[12.5px] font-medium"
					>
						<IconSparkles size={14} stroke={1.5} />
						<span>{selectedModel}</span>
						<IconChevronDown size={12} stroke={2} class="opacity-40" />
					</button>
				{/snippet}
			</Dropdown>

			<!-- Hint text -->
			<span class="hidden sm:inline text-[11.5px] text-muted/50 ml-2 select-none"
				>Shift + Enter for new line</span
			>
		</div>

		<!-- Right side: Actions -->
		<div class="flex items-center gap-2">
			<button
				class="flex items-center justify-center w-8 h-8 rounded-md text-muted hover:text-text-secondary hover:bg-surface-hover transition-colors cursor-pointer"
				aria-label="Voice input"
			>
				<IconMicrophone size={16} stroke={1.5} />
			</button>

			{#if isStreaming}
				<button
					onclick={handleStop}
					class="flex items-center justify-center gap-1.5 px-3 h-8 rounded-lg bg-surface border border-border text-text-secondary hover:bg-surface-hover hover:text-danger transition-colors cursor-pointer text-[12.5px] font-medium"
					aria-label="Stop generating"
				>
					<IconSquare size={12} stroke={2} />
					Stop
				</button>
			{:else}
				<button
					onclick={onsubmit}
					disabled={!hasText}
					class="flex items-center justify-center w-8 h-8 rounded-lg transition-all duration-150 cursor-pointer {hasText
						? 'bg-accent text-black hover:brightness-[1.15] active:brightness-[0.95] shadow-sm'
						: 'bg-surface text-muted opacity-50 cursor-not-allowed'}"
					aria-label="Send message"
				>
					<IconArrowRight size={18} stroke={2} />
				</button>
			{/if}
		</div>
	</div>
</div>
