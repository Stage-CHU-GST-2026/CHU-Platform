<script lang="ts">
	import { IconChevronDown, IconChevronRight, IconCheck } from '@tabler/icons-svelte';
	import type { PlanData, PlanStepData } from '$lib/api/chat';
	import { marked } from 'marked';
	import { browser } from '$app/environment';

	interface Props {
		plan: PlanData;
		completedSteps: Set<number>;
		activeStepId: number | null;
		stepMessages: Record<number, string>;
	}

	let { plan, completedSteps, activeStepId, stepMessages }: Props = $props();

	// Configure marked for clean output
	marked.setOptions({ breaks: true, gfm: true });

	let DOMPurify: any = null;
	if (browser) {
		import('dompurify').then((module) => {
			DOMPurify = module.default;
		});
	}

	function renderMd(text: string): string {
		if (!text) return '';
		const html = marked.parse(text) as string;
		if (browser && DOMPurify) {
			return DOMPurify.sanitize(html, {
				ADD_TAGS: ['img', 'table', 'th', 'td', 'tr', 'thead', 'tbody'],
				ADD_ATTR: ['src', 'alt', 'title', 'href', 'target', 'rel']
			});
		}
		return html;
	}

	// Steps the user has explicitly toggled closed (active steps) or open (done steps)
	let closedByUser = $state(new Set<number>());
	let openedByUser = $state(new Set<number>());

	function toggleStep(id: number) {
		// console.log('[toggleStep] id=', id, 'stepMessages=', stepMessages, 'openedByUser=', openedByUser);
		const status = stepStatus(plan.steps.find((s) => s.id === id)!);
		if (status === 'active') {
			if (closedByUser.has(id)) {
				closedByUser = new Set([...closedByUser].filter((x) => x !== id));
			} else {
				closedByUser = new Set([...closedByUser, id]);
			}
		} else {
			if (openedByUser.has(id)) {
				openedByUser = new Set([...openedByUser].filter((x) => x !== id));
			} else {
				openedByUser = new Set([...openedByUser, id]);
			}
		}
	}

	function isStepExpanded(step: PlanStepData): boolean {
		const status = stepStatus(step);
		if (status === 'active') {
			// Open by default unless user explicitly closed it
			return !closedByUser.has(step.id);
		}
		// Done/pending: closed by default unless user opened it
		return openedByUser.has(step.id);
	}

	// Auto-expand while running, auto-collapse when done
	const allDone = $derived(plan.steps.every((s: PlanStepData) => completedSteps.has(s.id)));
	let expanded = $state(true);

	$effect(() => {
		if (allDone) {
			// Small delay so the user sees the last step complete before collapsing
			const t = setTimeout(() => (expanded = false), 900);
			return () => clearTimeout(t);
		} else {
			expanded = true;
		}
	});

	function stepStatus(step: PlanStepData): 'pending' | 'active' | 'done' {
		if (completedSteps.has(step.id)) return 'done';
		if (activeStepId === step.id) return 'active';
		return 'pending';
	}

	const completedCount = $derived(completedSteps.size);
	const totalCount = $derived(plan.steps.length);
</script>

<!-- Claude-style thinking block — lives inside the assistant bubble -->
<div class="thinking-block">
	<!-- Trigger row -->
	<button class="trigger" onclick={() => (expanded = !expanded)} aria-expanded={expanded}>
		<span class="trigger-label">
			{#if !allDone}
				{activeStepId != null
					? (plan.steps.find((s) => s.id === activeStepId)?.title ?? 'Working…')
					: 'Planning…'}
			{:else}
				{plan.plan_title || 'Execution complete'}
			{/if}
		</span>

		<!-- Progress badge -->
		{#if !allDone && totalCount > 0}
			<span class="progress-badge">{completedCount}/{totalCount}</span>
		{:else if allDone}
			<span class="done-badge">
				<IconCheck size={10} stroke={2.5} />
				done
			</span>
		{/if}

		<!-- Chevron -->
		<span class="chevron" class:rotated={expanded}>
			<IconChevronRight size={13} stroke={2} />
		</span>
	</button>

	<!-- Collapsible step log -->
	{#if expanded}
		<div class="step-log">
			<div class="step-track">
				{#each plan.steps as step (step.id)}
					{@const status = stepStatus(step)}
					{@const stepExpanded = isStepExpanded(step)}

					<div class="step-row" class:active={status === 'active'} class:done={status === 'done'}>
						<!-- Timeline node -->
						<div class="node-col">
							{#if status === 'done'}
								<span class="node-done"><IconCheck size={9} stroke={3} /></span>
							{:else if status === 'active'}
								<span class="node-active" aria-hidden="true"></span>
							{:else}
								<span class="node-pending"></span>
							{/if}
						</div>

						<!-- Content -->
						<div class="step-content">
							<button
								class="step-title-btn"
								class:muted={status === 'pending'}
								onclick={() => toggleStep(step.id)}
								disabled={!stepMessages[step.id] && status === 'pending'}
							>
								<span class="step-title">{step.title}</span>
								{#if stepMessages[step.id] || status === 'active'}
									<span class="step-toggle-icon">
										{#if stepExpanded}
											<IconChevronDown size={14} />
										{:else}
											<IconChevronRight size={14} />
										{/if}
									</span>
								{/if}
							</button>

							{#if stepExpanded && stepMessages[step.id]}
								<div class="step-message prose-agent md-small">
									{@html renderMd(stepMessages[step.id])}
								</div>
							{:else if status === 'done'}
								<p class="step-desc done-desc">{step.description}</p>
							{:else if status === 'pending' || (status === 'active' && !stepMessages[step.id])}
								<p class="step-desc">{step.description}</p>
							{/if}
						</div>
					</div>
				{/each}
			</div>
		</div>
	{/if}
</div>

<style>
	/* ── Container ─────────────────────────────────────────────────────── */
	.thinking-block {
		margin: 0 0 4px;
	}

	/* ── Trigger button ────────────────────────────────────────────────── */
	.trigger {
		display: inline-flex;
		align-items: center;
		gap: 7px;
		padding: 5px 10px 5px 7px;
		border-radius: 8px;
		border: 1px solid var(--color-border-subtle);
		background: transparent;
		cursor: pointer;
		color: var(--color-text-secondary);
		font-size: 12.5px;
		font-family: var(--font-ui);
		line-height: 1;
		transition:
			background 120ms ease,
			color 120ms ease;
		user-select: none;
		width: auto;
		max-width: 100%;
	}

	.trigger:hover {
		background: var(--color-surface);
		color: var(--color-text-primary);
	}

	.trigger-label {
		font-weight: 500;
		letter-spacing: -0.01em;
		flex: 1;
		min-width: 0;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
		text-align: left;
	}

	.progress-badge {
		flex-shrink: 0;
		font-size: 10.5px;
		font-family: var(--font-mono);
		color: var(--color-muted);
		background: var(--color-surface-elevated);
		border: 1px solid var(--color-border);
		border-radius: 999px;
		padding: 1px 7px;
		letter-spacing: 0.02em;
	}

	.done-badge {
		flex-shrink: 0;
		display: inline-flex;
		align-items: center;
		gap: 4px;
		font-size: 10.5px;
		font-family: var(--font-mono);
		color: var(--color-success);
		background: color-mix(in srgb, var(--color-success) 10%, transparent);
		border: 1px solid color-mix(in srgb, var(--color-success) 20%, transparent);
		border-radius: 999px;
		padding: 1px 7px;
	}

	.chevron {
		flex-shrink: 0;
		display: flex;
		align-items: center;
		color: var(--color-muted);
		transition: transform 180ms cubic-bezier(0.4, 0, 0.2, 1);
	}

	.chevron.rotated {
		transform: rotate(90deg);
	}

	/* ── Step log ──────────────────────────────────────────────────────── */
	.step-log {
		margin-top: 6px;
		padding-left: 7px;
		animation: fade-in 160ms ease both;
	}

	.step-track {
		display: flex;
		flex-direction: column;
		border-left: 1.5px solid var(--color-border-subtle);
		padding-left: 14px;
		gap: 0;
	}

	/* ── Individual step ───────────────────────────────────────────────── */
	.step-row {
		display: flex;
		align-items: flex-start;
		gap: 10px;
		padding: 5px 0;
		position: relative;
		transition: opacity 150ms ease;
	}

	.step-row.active {
		opacity: 1;
	}

	.step-row:not(.active):not(.done) {
		opacity: 0.45;
	}

	/* Node column */
	.node-col {
		display: flex;
		align-items: center;
		justify-content: center;
		width: 16px;
		flex-shrink: 0;
		margin-top: 3px;
		/* Pull the dot to overlap the left border */
		margin-left: -22px;
		z-index: 1;
	}

	.node-pending {
		display: block;
		width: 6px;
		height: 6px;
		border-radius: 50%;
		background: var(--color-border);
	}

	.node-active {
		display: block;
		width: 8px;
		height: 8px;
		border-radius: 50%;
		background: var(--color-accent);
		box-shadow: 0 0 0 3px color-mix(in srgb, var(--color-accent) 20%, transparent);
		animation: pulse-node 1.4s ease-in-out infinite;
	}

	.node-done {
		display: flex;
		align-items: center;
		justify-content: center;
		width: 14px;
		height: 14px;
		border-radius: 50%;
		background: color-mix(in srgb, var(--color-success) 18%, transparent);
		color: var(--color-success);
		margin-left: -4px;
	}

	/* Step content */
	.step-content {
		flex: 1;
		min-width: 0;
		padding-top: 1px;
	}

	.step-title-btn {
		display: flex;
		align-items: center;
		justify-content: space-between;
		width: 100%;
		text-align: left;
		background: transparent;
		border: none;
		padding: 0;
		cursor: pointer;
	}

	.step-title-btn:disabled {
		cursor: default;
	}

	.step-title {
		display: block;
		font-size: 12.5px;
		font-weight: 500;
		color: var(--color-text-primary);
		letter-spacing: -0.01em;
		line-height: 1.4;
	}

	.step-title-btn.muted .step-title {
		color: var(--color-text-secondary);
	}

	.step-toggle-icon {
		color: var(--color-muted);
		display: flex;
		align-items: center;
	}

	.step-message {
		margin: 5px 0 0;
		background: color-mix(in srgb, var(--color-surface-elevated) 50%, transparent);
		border: 1px solid var(--color-border-subtle);
		border-radius: 8px;
		padding: 8px 12px;
	}

	/* Scale down the markdown for the step logs */
	.md-small :global(*) {
		font-size: 11.5px !important;
	}
	.md-small :global(h1),
	.md-small :global(h2),
	.md-small :global(h3),
	.md-small :global(h4) {
		margin-top: 0.8em !important;
		margin-bottom: 0.3em !important;
	}
	.md-small :global(table) {
		margin: 0.5em 0 !important;
	}
	.md-small :global(th),
	.md-small :global(td) {
		padding: 0.3em 0.4em !important;
	}
	.md-small :global(pre) {
		padding: 0.5em !important;
		margin: 0.5em 0 !important;
	}

	.step-desc {
		margin: 2px 0 0;
		font-size: 11.5px;
		color: var(--color-muted);
		line-height: 1.45;
	}

	.step-desc.done-desc {
		color: var(--color-text-secondary);
		opacity: 0.7;
	}

	/* ── Animations ────────────────────────────────────────────────────── */
	@keyframes spin {
		to {
			transform: rotate(360deg);
		}
	}

	@keyframes pulse-node {
		0%,
		100% {
			box-shadow: 0 0 0 3px color-mix(in srgb, var(--color-accent) 20%, transparent);
		}
		50% {
			box-shadow: 0 0 0 5px color-mix(in srgb, var(--color-accent) 8%, transparent);
		}
	}

	@keyframes fade-in {
		from {
			opacity: 0;
			transform: translateY(-4px);
		}
		to {
			opacity: 1;
			transform: translateY(0);
		}
	}
</style>
