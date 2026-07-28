<script lang="ts">
	import {
		IconTools,
		IconChevronDown,
		IconChevronRight,
		IconCheck,
		IconAlertCircle,
		IconClock,
		IconCopy,
		IconCode,
		IconFileText
	} from '@tabler/icons-svelte';
	import type { ToolEvidence } from '$lib/api/chat';
	import { browser } from '$app/environment';
	import Prism from 'prismjs';
	import 'prismjs/components/prism-json';
	import 'prismjs/components/prism-python';
	import 'prismjs/components/prism-sql';
	import 'prismjs/components/prism-markdown';

	interface Props {
		evidences: ToolEvidence[];
	}

	let { evidences = [] }: Props = $props();

	let isMainExpanded = $state(false);
	let expandedItems = $state(new Set<number>());
	let activeTab = $state<Record<number, 'params' | 'result'>>({});
	let copiedId = $state<string | null>(null);

	const totalDuration = $derived(
		evidences.reduce((sum, item) => sum + (item.execution_time_ms || 0), 0)
	);

	const hasErrors = $derived(
		evidences.some((item) => item.status === 'error')
	);

	function toggleMain() {
		isMainExpanded = !isMainExpanded;
	}

	function toggleItem(index: number) {
		const next = new Set(expandedItems);
		if (next.has(index)) {
			next.delete(index);
		} else {
			next.add(index);
		}
		expandedItems = next;
	}

	function setTab(index: number, tab: 'params' | 'result') {
		activeTab = { ...activeTab, [index]: tab };
	}

	function formatParams(params?: any): string {
		if (!params) return 'No parameters passed';

		// If params object contains { raw: "{\"path\": ...}" }, unwrap and parse raw
		if (typeof params === 'object' && params !== null && 'raw' in params && typeof params.raw === 'string') {
			const rawStr = params.raw.trim();
			try {
				const parsed = JSON.parse(rawStr);
				if (parsed && typeof parsed === 'object' && Object.keys(parsed).length > 0) {
					return JSON.stringify(parsed, null, 2);
				}
			} catch {
				// If raw string contains concatenated JSON objects, extract the last valid JSON object
				const matches = rawStr.match(/\{[^{}]*\}/g);
				if (matches && matches.length > 0) {
					for (let i = matches.length - 1; i >= 0; i--) {
						try {
							const obj = JSON.parse(matches[i]);
							if (obj && typeof obj === 'object' && Object.keys(obj).length > 0) {
								return JSON.stringify(obj, null, 2);
							}
						} catch {
							// skip
						}
					}

				}
			}
		}

		if (typeof params === 'string') {
			try {
				const parsed = JSON.parse(params);
				if (parsed && typeof parsed === 'object' && Object.keys(parsed).length > 0) {
					return JSON.stringify(parsed, null, 2);
				}
			} catch {
				return params.trim() || 'No parameters passed';
			}
		}

		if (typeof params === 'object' && params !== null && Object.keys(params).length > 0) {
			return JSON.stringify(params, null, 2);
		}

		return 'No parameters passed';
	}


	function formatDuration(ms?: number | null): string {
		if (ms == null || ms < 0) return '';
		if (ms === 0) return '0ms';
		if (ms < 1000) return `${ms}ms`;
		if (ms < 60000) {
			const secs = (ms / 1000).toFixed(1);
			return secs.endsWith('.0') ? `${Math.round(ms / 1000)}s` : `${secs}s`;
		}
		const mins = Math.floor(ms / 60000);
		const remainingSecs = Math.round((ms % 60000) / 1000);
		return remainingSecs > 0 ? `${mins}m ${remainingSecs}s` : `${mins}m`;
	}

	function highlightCode(code: string, language = 'json'): string {
		if (!browser || !code || code === 'No parameters passed' || code === 'No output returned') {
			return code;
		}
		try {
			const lang = language.toLowerCase();
			const grammar = Prism.languages[lang] || Prism.languages.json || Prism.languages.clike;
			return Prism.highlight(code, grammar, lang);
		} catch {
			return code;
		}
	}

	function copyToClipboard(text: string, id: string) {
		if (!browser) return;
		navigator.clipboard.writeText(text);
		copiedId = id;
		setTimeout(() => (copiedId = null), 2000);
	}
</script>

{#if evidences && evidences.length > 0}
	<div class="evidence-container my-3 rounded-lg border border-border bg-surface-subtle/50 text-xs overflow-hidden">
		<!-- Main Header Bar -->
		<button
			type="button"
			class="w-full flex items-center justify-between px-3 py-2 text-left bg-surface hover:bg-surface-hover/80 transition-colors cursor-pointer select-none"
			onclick={toggleMain}
		>
			<div class="flex items-center gap-2">
				<IconTools size={15} class="text-primary" />
				<span class="font-semibold text-text-primary">
					Tool Evidence & Traceability
				</span>
				<span class="px-1.5 py-0.5 rounded-full bg-surface-subtle border border-border text-[10px] text-text-secondary font-mono">
					{evidences.length} {evidences.length === 1 ? 'tool' : 'tools'} used
				</span>
				{#if hasErrors}
					<span class="flex items-center gap-1 text-error text-[10px] bg-error/10 px-1.5 py-0.5 rounded-full border border-error/20">
						<IconAlertCircle size={12} />
						Error
					</span>
				{/if}
			</div>

			<div class="flex items-center gap-3">
				{#if totalDuration > 0}
					<span class="flex items-center gap-1 text-[11px] text-muted font-mono">
						<IconClock size={12} />
						{formatDuration(totalDuration)}
					</span>
				{/if}
				{#if isMainExpanded}
					<IconChevronDown size={15} class="text-muted" />
				{:else}
					<IconChevronRight size={15} class="text-muted" />
				{/if}
			</div>
		</button>


		<!-- Expanded Evidence List -->
		{#if isMainExpanded}
			<div class="border-t border-border p-2 space-y-2 bg-surface-dark/30">
				{#each evidences as item, i (item.id || i)}
					{@const isItemExpanded = expandedItems.has(i)}
					{@const currentTab = activeTab[i] || 'params'}
					{@const paramText = formatParams(item.parameters)}
					{@const resultText = item.result || 'No output returned'}

					<div class="rounded border border-border/80 bg-surface overflow-hidden">
						<!-- Item Header -->
						<button
							type="button"
							class="w-full flex items-center justify-between px-2.5 py-1.5 text-left hover:bg-surface-hover transition-colors cursor-pointer"
							onclick={() => toggleItem(i)}
						>
							<div class="flex items-center gap-2 min-w-0">
								{#if item.status === 'error'}
									<IconAlertCircle size={14} class="text-error flex-shrink-0" />
								{:else}
									<IconCheck size={14} class="text-success flex-shrink-0" />
								{/if}
								<span class="font-mono font-medium text-text-primary truncate">
									{item.tool_name}
								</span>
								{#if item.step_id}
									<span class="px-1.5 py-0.2 rounded text-[10px] bg-primary/10 text-primary border border-primary/20 font-mono">
										Step {item.step_id}
									</span>
								{/if}
							</div>

							<div class="flex items-center gap-2.5 flex-shrink-0">
								{#if item.execution_time_ms}
									<span class="text-[10px] text-muted font-mono">
										{formatDuration(item.execution_time_ms)}
									</span>
								{/if}
								{#if isItemExpanded}

									<IconChevronDown size={14} class="text-muted" />
								{:else}
									<IconChevronRight size={14} class="text-muted" />
								{/if}
							</div>
						</button>

						<!-- Item Details -->
						{#if isItemExpanded}
							<div class="border-t border-border/60 bg-surface-dark/60 p-2 text-[11px]">
								<!-- Tabs -->
								<div class="flex items-center justify-between border-b border-border/40 pb-1.5 mb-2">
									<div class="flex items-center gap-1">
										<button
											type="button"
											class="flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-medium transition-colors cursor-pointer {currentTab === 'params' ? 'bg-primary/20 text-primary font-semibold' : 'text-muted hover:text-text-primary'}"
											onclick={() => setTab(i, 'params')}
										>
											<IconCode size={12} />
											Parameters
										</button>
										<button
											type="button"
											class="flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-medium transition-colors cursor-pointer {currentTab === 'result' ? 'bg-primary/20 text-primary font-semibold' : 'text-muted hover:text-text-primary'}"
											onclick={() => setTab(i, 'result')}
										>
											<IconFileText size={12} />
											Result
										</button>
									</div>

									<button
										type="button"
										class="flex items-center gap-1 px-1.5 py-0.5 rounded text-muted hover:text-text-primary hover:bg-surface transition-colors cursor-pointer"
										title="Copy content"
										onclick={() => copyToClipboard(currentTab === 'params' ? paramText : resultText, `item-${i}-${currentTab}`)}
									>
										{#if copiedId === `item-${i}-${currentTab}`}
											<IconCheck size={12} class="text-success" />
											<span class="text-[10px] text-success">Copied</span>
										{:else}
											<IconCopy size={12} />
											<span class="text-[10px]">Copy</span>
										{/if}
									</button>
								</div>

								<!-- Tab Content with Prism syntax highlighting -->
								{#if currentTab === 'params'}
									<pre class="font-mono text-[11px] bg-surface-dark/90 p-2.5 rounded overflow-x-auto whitespace-pre-wrap max-h-48 border border-border/40 text-text-primary"><code>{@html highlightCode(paramText, 'json')}</code></pre>
								{:else}
									<pre class="font-mono text-[11px] bg-surface-dark/90 p-2.5 rounded overflow-x-auto whitespace-pre-wrap max-h-60 border border-border/40 text-text-primary"><code>{@html highlightCode(resultText, resultText.trim().startsWith('{') || resultText.trim().startsWith('[') ? 'json' : 'markdown')}</code></pre>
								{/if}
							</div>
						{/if}
					</div>
				{/each}
			</div>
		{/if}
	</div>
{/if}

<style>
	/* Prism syntax highlighting dark theme tokens */
	:global(.token.property) {
		color: #7ee787;
		font-weight: 500;
	}
	:global(.token.string) {
		color: #a5d6ff;
	}
	:global(.token.number) {
		color: #79c0ff;
	}
	:global(.token.boolean),
	:global(.token.null) {
		color: #ff7b72;
		font-weight: 600;
	}
	:global(.token.punctuation) {
		color: #8b949e;
	}
	:global(.token.operator) {
		color: #d2a8ff;
	}
	:global(.token.keyword) {
		color: #ff7b72;
	}
	:global(.token.function) {
		color: #d2a8ff;
	}
</style>
