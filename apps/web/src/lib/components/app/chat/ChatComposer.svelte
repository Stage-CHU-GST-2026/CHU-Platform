<script lang="ts">
	import {
		IconChevronDown,
		IconArrowUp,
		IconSquare,
		IconDatabase,
		IconX,
		IconCheck,
		IconSearch,
		IconPlus
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

<div class="composer {focused ? 'composer-focused' : ''} {size === 'large' ? '!rounded-2xl !p-3 shadow-lg border border-border/90' : ''}">
	<!-- Attached Dataset Context Pill (Only rendered when a dataset is active) -->
	{#if selectedDataset}
		<div class="flex items-center gap-2 px-1 pt-0.5 pb-1">
			<div
				class="inline-flex items-center gap-2 px-2.5 py-1 rounded-lg bg-surface/90 border border-accent/35 text-xs font-sans text-text-primary shadow-xs transition-all"
			>
				<div class="w-5 h-5 rounded-md bg-accent/15 flex items-center justify-center text-accent shrink-0">
					<IconDatabase size={13} stroke={2} />
				</div>
				<span class="font-semibold text-text-primary truncate max-w-64">{selectedDataset.original_filename}</span>
				{#if selectedDataset.rows || selectedDataset.columns}
					<span class="text-[11px] font-mono text-text-secondary/80 border-l border-border/60 pl-2">
						{selectedDataset.rows?.toLocaleString() ?? '?'} rows &middot; {selectedDataset.columns ?? '?'} cols
					</span>
				{/if}
				<button
					onclick={clearDataset}
					class="ml-1 p-0.5 rounded text-muted hover:text-danger hover:bg-danger/10 transition-colors cursor-pointer"
					title={t(m.chat_remove_dataset)}
					aria-label="Remove dataset"
				>
					<IconX size={13} stroke={2} />
				</button>
			</div>
		</div>
	{/if}

	<!-- Main Textarea -->
	<textarea
		bind:this={textareaEl}
		bind:value={input}
		class="w-full bg-transparent text-text-primary placeholder-text-secondary/50 resize-none focus:outline-none focus:ring-0 border-0 shadow-none disabled:opacity-40 {size === 'large'
			? 'px-2.5 pt-2 pb-1 text-[15.5px] leading-relaxed min-h-[52px] max-h-56'
			: 'px-2 pt-1.5 pb-1 text-[14.5px] leading-relaxed min-h-[36px] max-h-44'} overflow-y-auto"
		placeholder={selectedDataset
			? `Ask anything about "${selectedDataset.original_filename}"...`
			: t(m.chat_placeholder_default)}
		rows={size === 'large' ? 2 : 1}
		disabled={isStreaming}
		onkeydown={handleKeydown}
		oninput={resizeTextarea}
		onfocus={() => (focused = true)}
		onblur={() => (focused = false)}></textarea>

	<!-- Bottom Action Toolbar -->
	<div class="flex items-center justify-between w-full px-1 pt-1 pb-0.5">
		<!-- Left side: Dataset Picker Button & Keyboard Hint -->
		<div class="flex items-center gap-2">
			<div class="relative">
				<!-- Minimalist Dataset Trigger Button -->
				<button
					onclick={toggleDatasetPicker}
					class="w-7.5 h-7.5 rounded-lg flex items-center justify-center transition-all cursor-pointer border disabled:opacity-30 {selectedDataset
						? 'bg-accent/15 border-accent/40 text-accent hover:bg-accent/25 shadow-xs'
						: 'bg-surface/60 hover:bg-surface border-border/70 text-text-secondary hover:text-text-primary'}"
					aria-label="Attach dataset"
					disabled={isStreaming}
					title={selectedDataset ? `Dataset attached: ${selectedDataset.original_filename} (click to change)` : t(m.chat_attach_dataset)}
				>
					<IconDatabase size={15} stroke={1.8} class={selectedDataset ? 'text-accent' : 'text-text-secondary'} />
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
						class="absolute bottom-full left-0 mb-2.5 w-84 max-h-80 flex flex-col rounded-xl border border-border bg-surface-elevated/95 backdrop-blur-xl shadow-2xl z-50 overflow-hidden font-sans"
						role="listbox"
						aria-label="Available datasets"
					>
						<!-- Header with Search Input -->
						<div class="p-3 border-b border-border/80 bg-surface/70 flex flex-col gap-2">
							<div class="flex items-center justify-between px-0.5">
								<span class="text-[11px] font-bold text-text-secondary uppercase tracking-wider">{t(m.chat_select_dataset)}</span>
								<span class="text-[11px] font-mono text-muted">{availableDatasets.length} ready</span>
							</div>
							<div class="relative w-full">
								<input
									type="text"
									bind:value={datasetSearchQuery}
									placeholder={t(m.chat_search_datasets)}
									class="w-full bg-surface-elevated border border-border/80 rounded-lg px-2.5 py-1.5 pl-8 text-xs text-text-primary placeholder-muted focus:outline-none focus:border-accent"
								/>
								<IconSearch size={14} class="absolute left-2.5 top-2 text-muted" />
							</div>
						</div>

						<!-- Dataset List -->
						<div class="overflow-y-auto flex-1 divide-y divide-border/30">
							{#if loadingDatasets}
								<div class="p-6 text-center text-xs text-muted font-mono">Loading datasets...</div>
							{:else if filteredAvailableDatasets.length === 0}
								<div class="p-6 text-center text-xs text-muted">
									No matching datasets found.
									<a href="/dashboard/datasets" class="block mt-1.5 text-accent font-semibold hover:underline">Upload new dataset &rarr;</a>
								</div>
							{:else}
								{#each filteredAvailableDatasets as ds}
									<button
										class="w-full flex items-center justify-between px-3.5 py-2.5 text-left hover:bg-surface-hover transition-colors cursor-pointer group {selectedDataset?.id === ds.id ? 'bg-accent/10' : ''}"
										onclick={() => selectDataset(ds)}
										role="option"
										aria-selected={selectedDataset?.id === ds.id}
									>
										<div class="flex items-center gap-2.5 min-w-0">
											<div class="w-7 h-7 rounded-lg bg-surface border border-border/80 flex items-center justify-center text-accent shrink-0">
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
			<span class="hidden sm:inline text-[11px] text-muted/50 font-mono select-none ml-1"
				>Shift + Enter for new line</span
			>
		</div>

		<!-- Right side: Send / Stop Action Button -->
		<div class="flex items-center gap-2">
			{#if isStreaming}
				<button
					onclick={handleStop}
					class="flex items-center justify-center gap-1.5 px-3 h-8 rounded-xl bg-danger/10 border border-danger/30 text-danger hover:bg-danger/20 transition-all cursor-pointer text-xs font-semibold"
					aria-label="Stop generating"
				>
					<IconSquare size={12} stroke={2.5} fill="currentColor" />
					<span>Stop</span>
				</button>
			{:else}
				<button
					onclick={onsubmit}
					disabled={!hasText}
					class="flex items-center justify-center w-8 h-8 rounded-xl transition-all duration-200 cursor-pointer {hasText
						? 'bg-accent text-black hover:scale-105 active:scale-95 shadow-md shadow-accent/25'
						: 'bg-surface-elevated text-muted/40 cursor-not-allowed opacity-40'}"
					aria-label="Send message"
				>
					<IconArrowUp size={18} stroke={2.5} />
				</button>
			{/if}
		</div>
	</div>
</div>
