<script lang="ts">
	import { marked } from 'marked';
	import { browser } from '$app/environment';
	import ExecutionPlan from './ExecutionPlan.svelte';
	import type { PlanData } from '$lib/api/chat';
	import { IconCopy, IconRefresh, IconCheck } from '@tabler/icons-svelte';

	interface Props {
		role: 'user' | 'assistant';
		content: string;
		streaming?: boolean;
		// Plan data — only set on assistant messages that ran the orchestrator
		plan?: PlanData;
		completedSteps?: Set<number>;
		activeStepId?: number | null;
		stepMessages?: Record<number, string>;
		onregenerate?: () => void;
	}

	let {
		role,
		content,
		streaming = false,
		plan,
		completedSteps = new Set(),
		activeStepId = null,
		stepMessages = {},
		onregenerate
	}: Props = $props();

	// Configure marked for clean output
	marked.setOptions({ breaks: true, gfm: true });

	let DOMPurify: any = null;
	if (browser) {
		import('dompurify').then((module) => {
			DOMPurify = module.default;
		});
	}

	function renderMd(text: string): string {
		const html = marked.parse(text) as string;
		if (browser && DOMPurify) {
			return DOMPurify.sanitize(html, {
				ADD_TAGS: ['img', 'table', 'th', 'td', 'tr', 'thead', 'tbody'],
				ADD_ATTR: ['src', 'alt', 'title', 'href', 'target', 'rel']
			});
		}
		return html;
	}

	let tokens = $derived(content ? marked.lexer(content) : []);

	const hasPlan = $derived(!!plan);
	const hasContent = $derived(!!content);

	let copied = $state(false);
	function copyText() {
		if (!browser) return;
		navigator.clipboard.writeText(content);
		copied = true;
		setTimeout(() => (copied = false), 2000);
	}
</script>

<div class="msg-row {role} group">

	<div class="msg-bubble {role}">
		{#if role === 'user'}
			<div class="whitespace-pre-wrap">{content}</div>
		{:else}
			<!-- Assistant meta line -->
			<div class="msg-meta hidden md:flex">
				<span class="font-medium text-text-primary text-[13px] tracking-normal">Data Analyst Agent</span>
			</div>

			<!-- Execution plan block (sits at the top of the bubble) -->
			{#if plan}
				<ExecutionPlan {plan} {completedSteps} {activeStepId} {stepMessages} />
				<!-- Divider only shown once content starts streaming in -->
				{#if hasContent}
					<div class="plan-divider"></div>
				{/if}
			{/if}

			<!-- Streamed content -->
			{#if !content && streaming && !hasPlan}
				<!-- Typing indicator before first token (no plan) -->
				<span class="inline-flex gap-[5px] items-center h-5 mt-1">
					<span class="typing-dot" style="animation-delay: 0ms"></span>
					<span class="typing-dot" style="animation-delay: 160ms"></span>
					<span class="typing-dot" style="animation-delay: 320ms"></span>
				</span>
			{:else if content}
				<!-- Progressive markdown render -->
				<div class="prose-agent flex flex-col">
					{#each tokens as token, i (i)}
						<div class="md-block">
							{@html renderMd(token.raw)}
						</div>
					{/each}
					{#if streaming}
						<div class="mt-2 flex">
							<span class="inline-flex gap-[5px] items-center h-5 px-1">
								<span class="typing-dot" style="animation-delay: 0ms"></span>
								<span class="typing-dot" style="animation-delay: 160ms"></span>
								<span class="typing-dot" style="animation-delay: 320ms"></span>
							</span>
						</div>
					{/if}
				</div>
			{/if}

			<!-- Actions Bar -->
			{#if !streaming}
				<div
					class="flex items-center justify-start gap-1.5 mt-3 opacity-0 group-hover:opacity-100 transition-opacity"
				>
					<button
						class="w-7 h-7 flex items-center justify-center rounded-md text-muted hover:text-text-primary hover:bg-surface transition-colors"
						title="Copy response"
						onclick={copyText}
					>
						{#if copied}
							<IconCheck size={15} stroke={2} class="text-success" />
						{:else}
							<IconCopy size={15} stroke={1.5} />
						{/if}
					</button>
					{#if onregenerate}
						<button
							class="w-7 h-7 flex items-center justify-center rounded-md text-muted hover:text-text-primary hover:bg-surface transition-colors"
							title="Regenerate response"
							onclick={onregenerate}
						>
							<IconRefresh size={15} stroke={1.5} />
						</button>
					{/if}
				</div>
			{/if}
		{/if}
	</div>
</div>

<style>
	/* Typing indicator dots */
	.typing-dot {
		width: 5px;
		height: 5px;
		border-radius: 50%;
		background: var(--color-muted);
		animation: bounce-dot 1.2s ease-in-out infinite;
		display: inline-block;
	}

	@keyframes bounce-dot {
		0%,
		80%,
		100% {
			transform: translateY(0);
			opacity: 0.35;
		}
		40% {
			transform: translateY(-4px);
			opacity: 0.9;
		}
	}

	/* Separator between the thinking block and the synthesized response */
	.plan-divider {
		height: 1px;
		background: var(--color-border);
		opacity: 0.5;
		margin: 10px 0 12px;
	}
</style>
