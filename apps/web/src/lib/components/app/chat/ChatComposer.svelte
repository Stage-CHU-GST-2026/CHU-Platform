<script lang="ts">
	import {
		IconChevronDown,
		IconArrowRight,
		IconSquare,
		IconDatabase,
		IconX,
		IconCheck,
		IconSearch
	} from '@tabler/icons-svelte';
	import { listDatasets } from '$lib/api/datasets';
	import type { DatasetSummary } from '$lib/api/datasets';
	import { t, m } from '$lib/i18n';

	interface Props {
		input?: string;
		isStreaming?: boolean;
		onsubmit?: () => void;
		selectedDataset?: DatasetSummary | null;
		showModelSelector?: boolean;
		showMicrophone?: boolean;
		size?: 'default' | 'large';
	}

	let {
		input = $bindable(''),
		isStreaming = false,
		onsubmit = () => {},
		selectedDataset = $bindable(null),
		showModelSelector = false,
		showMicrophone = false,
		size = 'default'
	} = $props<Props>();

	let textareaEl = $state<HTMLTextAreaElement | null>(null);
	let focused = $state(false);
	let showDatasetPicker = $state(false);
	let availableDatasets = $state<DatasetSummary[]>([]);
	let loadingDatasets = $state(false);
	let datasetSearchQuery = $state('');

	let hasText = $derived((input || '').trim().length > 0);

	let filteredAvailableDatasets = $derived.by(() => {
		if (!datasetSearchQuery.trim()) return availableDatasets;
		const q = datasetSearchQuery.toLowerCase();
		return availableDatasets.filter((d) => d.original_filename.toLowerCase().includes(q));
	});

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
		window.location.reload();
	}

	async function toggleDatasetPicker() {
		if (showDatasetPicker) {
			showDatasetPicker = false;
			return;
		}
		loadingDatasets = true;
		showDatasetPicker = true;
		datasetSearchQuery = '';
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

<div class="composer {focused ? 'composer-focused' : ''} {size === 'large' ? '!rounded-2xl !p-2.5 !shadow-md border border-border/90' : ''}">
	<!-- Selected dataset badge -->
	{#if selectedDataset}
		<div class="flex items-center gap-2 px-2 pt-1 pb-0.5">
			<div
				class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-surface-elevated border border-accent/40 text-xs font-sans text-text-primary shadow-xs"
			>
				<IconDatabase size={13} stroke={1.8} class="text-accent shrink-0" />
				<span class="font-bold text-text-primary truncate max-w-64">{selectedDataset.original_filename}</span>
				<span class="text-[11px] font-mono text-muted border-l border-border/80 pl-2">
					{selectedDataset.rows?.toLocaleString() ?? '?'} rows &middot; {selectedDataset.columns ?? '?'} cols
				</span>
				<button
					onclick={clearDataset}
					class="ml-1 p-0.5 rounded text-muted hover:text-danger hover:bg-danger/10 transition-colors cursor-pointer"
					title={t(m.chat_remove_dataset)}
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
		class="w-full bg-transparent text-text-primary placeholder-muted resize-none focus:outline-none focus:ring-0 border-0 shadow-none disabled:opacity-40 {size === 'large'
			? 'px-3 pt-2 pb-1 text-[15px] md:text-[16px] leading-[1.5] min-h-[52px] max-h-52'
			: 'px-2.5 pt-1 pb-1 text-[14.5px] leading-[1.5] min-h-[22px] max-h-44'} overflow-y-auto"
		placeholder={selectedDataset
			? `Ask about "${selectedDataset.original_filename}"...`
			: t(m.chat_placeholder_default)}
		rows={size === 'large' ? 2 : 1}
		disabled={isStreaming}
		onkeydown={handleKeydown}
		oninput={resizeTextarea}
		onfocus={() => (focused = true)}
		onblur={() => (focused = false)}></textarea>

	<!-- Toolbar row at the bottom -->
	<div class="flex items-center justify-between w-full px-1 pb-0.5">
		<!-- Left side: Dataset Picker Chip -->
		<div class="flex items-center gap-1.5 relative">
			<div class="relative">
				<!-- Interactive Dataset Chip Button -->
				<button
					onclick={toggleDatasetPicker}
					class="inline-flex items-center gap-1.5 px-2 h-7 rounded-md text-[12px] font-medium transition-all cursor-pointer border disabled:opacity-30 {selectedDataset
						? 'bg-accent/15 border-accent/30 text-accent font-semibold shadow-xs'
						: 'bg-surface-elevated/60 hover:bg-surface-hover border-border/80 text-text-secondary hover:text-text-primary'}"
					aria-label="Select dataset"
					disabled={isStreaming}
					title="Attach dataset context"
				>
					<IconDatabase size={13} stroke={1.8} class={selectedDataset ? 'text-accent' : 'text-muted'} />
					<span class="truncate max-w-44 font-sans">
						{selectedDataset ? selectedDataset.original_filename : t(m.chat_attach_dataset)}
					</span>
					<IconChevronDown size={12} stroke={2} class="opacity-50 shrink-0" />
				</button>

				<!-- Dataset Picker Popup -->
				{#if showDatasetPicker}
					<!-- Backdrop overlay to dismiss on click outside -->
					<div
						class="fixed inset-0 z-40"
						onclick={() => (showDatasetPicker = false)}
						aria-hidden="true"
					></div>

					<div
						class="absolute bottom-full left-0 mb-2 w-80 max-h-80 flex flex-col rounded-xl border border-border bg-surface-elevated shadow-xl z-50 overflow-hidden font-sans"
						role="listbox"
						aria-label="Available datasets"
					>
						<!-- Header with Search Input -->
						<div class="p-2.5 border-b border-border/80 bg-surface flex flex-col gap-2">
							<div class="flex items-center justify-between px-1">
								<span class="text-xs font-bold text-text-primary uppercase tracking-wider">{t(m.chat_select_dataset)}</span>
								<span class="text-[11px] font-mono text-muted">{availableDatasets.length} ready</span>
							</div>
							<div class="relative w-full">
								<input
									type="text"
									bind:value={datasetSearchQuery}
									placeholder={t(m.chat_search_datasets)}
									class="w-full bg-surface-elevated border border-border/80 rounded-md px-2.5 py-1.5 pl-8 text-xs text-text-primary placeholder-muted focus:outline-none focus:border-accent"
								/>
								<IconSearch size={14} class="absolute left-2.5 top-2 text-muted" />
							</div>
						</div>

						<!-- Dataset List -->
						<div class="overflow-y-auto flex-1 divide-y divide-border/40">
							{#if loadingDatasets}
								<div class="p-6 text-center text-xs text-muted font-mono">Loading datasets...</div>
							{:else if filteredAvailableDatasets.length === 0}
								<div class="p-6 text-center text-xs text-muted">
									No matching datasets found.
									<a href="/dashboard/datasets" class="block mt-1 text-accent font-semibold hover:underline">Upload new dataset &rarr;</a>
								</div>
							{:else}
								{#each filteredAvailableDatasets as ds}
									<button
										class="w-full flex items-center justify-between px-3.5 py-2.5 text-left hover:bg-surface-hover/80 transition-colors cursor-pointer group {selectedDataset?.id === ds.id ? 'bg-accent/10' : ''}"
										onclick={() => selectDataset(ds)}
										role="option"
										aria-selected={selectedDataset?.id === ds.id}
									>
										<div class="flex items-center gap-2.5 min-w-0">
											<div class="w-7 h-7 rounded-md bg-surface border border-border/80 flex items-center justify-center text-accent shrink-0">
												<IconDatabase size={14} />
											</div>
											<div class="min-w-0">
												<div class="text-xs font-bold text-text-primary truncate group-hover:text-accent transition-colors">
													{ds.original_filename}
												</div>
												<div class="text-[11px] font-mono text-muted">
													{ds.rows?.toLocaleString() ?? '?'} rows &middot; {ds.columns ?? '?'} cols
												</div>
											</div>
										</div>
										{#if selectedDataset?.id === ds.id}
											<IconCheck size={16} class="text-accent shrink-0" />
										{/if}
									</button>
								{/each}
							{/if}
						</div>
					</div>
				{/if}
			</div>

			<!-- Hint text -->
			<span class="hidden sm:inline text-[11px] text-muted/50 ml-1.5 select-none"
				>Shift + Enter for new line</span
			>
		</div>

		<!-- Right side: Actions -->
		<div class="flex items-center gap-2">
			{#if isStreaming}
				<button
					onclick={handleStop}
					class="flex items-center justify-center gap-1.5 px-2.5 h-7 rounded-md bg-surface border border-border text-text-secondary hover:bg-surface-hover hover:text-danger transition-colors cursor-pointer text-[11.5px] font-medium"
					aria-label="Stop generating"
				>
					<IconSquare size={11} stroke={2} />
					Stop
				</button>
			{:else}
				<button
					onclick={onsubmit}
					disabled={!hasText}
					class="flex items-center justify-center w-7 h-7 rounded-md transition-all duration-150 cursor-pointer {hasText
						? 'bg-accent text-black hover:brightness-[1.15] active:brightness-[0.95] shadow-xs'
						: 'bg-surface text-muted opacity-50 cursor-not-allowed'}"
					aria-label="Send message"
				>
					<IconArrowRight size={16} stroke={2} />
				</button>
			{/if}
		</div>
	</div>
</div>
