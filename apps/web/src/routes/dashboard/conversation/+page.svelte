<script lang="ts">
	import { marked } from 'marked';
	import { browser } from '$app/environment';
	import { tick, onMount } from 'svelte';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import {
		sendMessage,
		createConversation,
		getConversation,
		listArtifacts,
		fetchPlanFromArtifact,
		PLAN_MIME_TYPE,
		type ChatMessage,
		type PlanData,
		type Artifact,
		type ToolEvidence
	} from '$lib/api/chat';
	import { convo } from '$lib/state/conversations.svelte';
	import { app } from '$lib/state/app.svelte';
	import { getPromptLanguageInstruction } from '$lib/i18n';
	import { IconSparkles, IconDatabase } from '@tabler/icons-svelte';
	import { listDatasets } from '$lib/api/datasets';
	import type { DatasetSummary } from '$lib/api/datasets';
	import ChatLoadingState from '$lib/components/app/chat/ChatLoadingState.svelte';
	import ChatEmptyState from '$lib/components/app/chat/ChatEmptyState.svelte';
	import ChatBubble from '$lib/components/app/chat/ChatBubble.svelte';
	import ChatComposer from '$lib/components/app/chat/ChatComposer.svelte';
	import PlanCard from '$lib/components/app/chat/PlanCard.svelte';

	// ── State ────────────────────────────────────────────────────────────
	interface Message {
		role: 'user' | 'assistant';
		content: string;
		streaming?: boolean;
		artifact?: Artifact;
		plan?: PlanData;
		completedSteps?: Set<number>;
		activeStepId?: number | null;
		stepMessages?: Record<number, string>; // persistent per-step content
		evidences?: ToolEvidence[];
	}


	let messages = $state<Message[]>([]);
	let conversationId = $state<string | null>(null);
	let input = $state('');
	let isStreaming = $state(false);
	let isLoading = $state(false);
	let error = $state<string | null>(null);
	let selectedDataset = $state<DatasetSummary | null>(null);

	function stripLanguageInstruction(text: string): string {
		if (!text) return '';
		return text
			.replace(/\n\n\(Please answer in (French \/ Veuillez répondre en français|English)\)/gi, '')
			.replace(/\n\n\(answer in (fr\/en|fr|en|French|English)\)/gi, '')
			.trim();
	}

	// ── Helpers ─────────────────────────────────────────────────────────
	/** Force Svelte 5 to notice a deep mutation by touching the array.
	 *  Svelte 5 proxies detect property writes on array elements, but
	 *  only if they go through the proxied reference.  As a safety net,
	 *  we reassign the array to itself after deep mutations — this is
	 *  a no-op identity-wise but tells the Svelte runtime to re-check. */
	function touch() {
		messages = messages;
	}

	let scrollEl = $state<HTMLDivElement | null>(null);
	let isAutoScrolling = $state(true);

	function onScroll(e: Event) {
		const target = e.target as HTMLElement;
		const isAtBottom = Math.abs(target.scrollHeight - target.clientHeight - target.scrollTop) < 50;
		isAutoScrolling = isAtBottom;
	}

	function scrollToBottom() {
		if (scrollEl && isAutoScrolling) {
			scrollEl.scrollTop = scrollEl.scrollHeight;
		}
	}

	// ── Load history when ?id changes ─────────────────────────────────
	async function loadConversation(id: string) {
		isLoading = true;
		error = null;
		try {
			const conv = await getConversation(id);
			conversationId = id;

			// Restore linked dataset if the conversation has one
			if (conv.dataset_id && conv.dataset_name) {
				selectedDataset = {
					id: conv.dataset_id,
					original_filename: conv.dataset_name,
					file_size: null,
					mime_type: '',
					status: 'ready',
					rows: null,
					columns: null,
					error_message: null,
					created_at: '',
					updated_at: ''
				};
			}

			// Build message list from stored messages
			const loaded: Message[] = conv.messages.map((m: ChatMessage) => ({
				role: m.role as 'user' | 'assistant',
				content: m.content,
				evidences: m.tool_evidences || []
			}));


			// ── Reconstruct execution plan — attach it to the last assistant message ──
			const planArtifact = (conv.artifacts || []).find(
				(a: Artifact) => a.mime_type === PLAN_MIME_TYPE
			);
			if (planArtifact) {
				const plan = await fetchPlanFromArtifact(planArtifact);
				if (plan) {
					// Find the last assistant message and embed the plan there.
					for (let i = loaded.length - 1; i >= 0; i--) {
						if (loaded[i].role === 'assistant') {
							loaded[i].plan = plan;
							loaded[i].completedSteps = new Set(plan.steps.map((s) => s.id));
							loaded[i].activeStepId = null;
							loaded[i].activeStepMessage = '';
							break;
						}
					}
				}
			}

			messages = loaded;
			app.activeArtifacts = conv.artifacts || [];
			await tick();
			scrollToBottom();
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to load conversation';
		} finally {
			isLoading = false;
		}
	}

	// Re-load when URL ?id param changes (e.g. clicking a different conversation)
	$effect(() => {
		const id = $page.url.searchParams.get('id');
		const q = $page.url.searchParams.get('q');
		const draft = $page.url.searchParams.get('draft');

		if (id && id !== conversationId) {
			messages = [];
			conversationId = id;
			loadConversation(id).then(() => {
				if (draft) {
					input = draft;
					goto(`/dashboard/conversation?id=${id}`, { replaceState: true });
				} else if (q) {
					input = q;
					goto(`/dashboard/conversation?id=${id}`, { replaceState: true });
					submit();
				}
			});
		} else if (!id && conversationId) {
			messages = [];
			conversationId = null;
		}
	});

	// ── Proceed with a plan ────────────────────────────────────────────
	async function proceedWithPlan(artifact: Artifact) {
		if (isStreaming) return;
		input = `Proceed with the plan from ${artifact.filename}`;
		await tick();
		submit();
	}

	function regenerate(index: number) {
		if (isStreaming || index === 0) return;
		// Find the previous user message
		const prevMsg = messages[index - 1];
		if (prevMsg && prevMsg.role === 'user') {
			input = prevMsg.content;
			submit();
		}
	}

	// ── Send message ───────────────────────────────────────────────────
	async function submit() {
		const text = input.trim();
		if (!text || isStreaming) return;

		error = null;
		input = '';
		await tick();

		// Push user bubble
		messages.push({ role: 'user', content: text });

		// Single assistant slot — plan data will be set inline on this same message.
		const streamIdx = messages.length;
		messages.push({
			role: 'assistant',
			content: '',
			streaming: true,
			plan: undefined,
			completedSteps: new Set<number>(),
			activeStepId: null,
			stepMessages: {},
			evidences: []
		});

		isStreaming = true;
		isAutoScrolling = true;
		await tick();
		scrollToBottom();

		try {
			if (!conversationId) {
				// If a dataset is selected, link it to the conversation
				const conv = await createConversation(
					selectedDataset ? `Dataset: ${selectedDataset.original_filename}` : undefined,
					selectedDataset?.id
				);
				conversationId = conv.id;
				goto(`/dashboard/conversation?id=${conv.id}`, { replaceState: true, noScroll: true });
				convo.refresh();
			}

			const backendPrompt = `${text}${getPromptLanguageInstruction()}`;
			await sendMessage(conversationId, backendPrompt, {
				onToken(token) {
					if (streamIdx < messages.length) {
						messages[streamIdx].content += token;
						touch();
					}
					scrollToBottom();
				},
				onArtifact(artifact) {
					const a = {
						...artifact,
						id: artifact.id || crypto.randomUUID(),
						conversation_id: artifact.conversation_id || conversationId || '',
						created_at: artifact.created_at || new Date().toISOString()
					};
					app.activeArtifacts = [...app.activeArtifacts, a];
					messages.push({ role: 'assistant', content: '', artifact: a, streaming: false });
					touch();
				},
				onPlan(plan) {
					// Embed the plan directly in the streaming message — no separate row.
					if (streamIdx < messages.length) {
						messages[streamIdx].plan = plan;
						messages[streamIdx].completedSteps = new Set();
						touch();
						scrollToBottom();
					}
				},
				onToolEvidence(evidence) {
					if (streamIdx < messages.length) {
						const m = messages[streamIdx];
						m.evidences = [...(m.evidences || []), evidence];
						touch();
						scrollToBottom();
					}
				},
				onStepStarted(step) {
					if (streamIdx >= messages.length) return;
					messages[streamIdx].activeStepId = step.id;
					touch();
					scrollToBottom();
				},
				onStepUpdate(msgText) {
					if (streamIdx >= messages.length) return;
					const m = messages[streamIdx];
					const sid = m.activeStepId;
					console.log('[StepUpdate] sid=', sid, 'text=', msgText?.slice(0, 40));
					if (sid == null) return;
					// Create a NEW object so Svelte's proxy detects the change.
					const prev = m.stepMessages ?? {};
					messages[streamIdx].stepMessages = {
						...prev,
						[sid]: (prev[sid] ?? '') + msgText
					};
					touch();
					scrollToBottom();
				},
				onStepFinished(stepId) {
					if (streamIdx >= messages.length) return;
					const m = messages[streamIdx];
					m.completedSteps = new Set([...(m.completedSteps ?? []), stepId]);
					if (m.activeStepId === stepId) {
						m.activeStepId = null;
					}
					touch();
					scrollToBottom();
				},
				async onDone() {
					if (streamIdx < messages.length) {
						const m = messages[streamIdx];
						m.streaming = false;
						if (m.plan) {
							m.completedSteps = new Set(m.plan.steps.map((s) => s.id));
							m.activeStepId = null;
						}
					}
					isStreaming = false;
					touch();
					convo.refresh();
					if (conversationId) {
						try {
							app.activeArtifacts = await listArtifacts(conversationId);
						} catch (err) {
							console.error('Failed to load artifacts', err);
						}
					}
				},
				onError(err) {
					if (streamIdx < messages.length) {
						messages[streamIdx].streaming = false;
						messages[streamIdx].content =
							messages[streamIdx].content || '_Error receiving response._';
					}
					touch();
					error = err.message;
					isStreaming = false;
				}
			});

			if (isStreaming) {
				if (streamIdx < messages.length) messages[streamIdx].streaming = false;
				touch();
				isStreaming = false;
			}
		} catch (err) {
			if (streamIdx < messages.length) messages[streamIdx].streaming = false;
			touch();
			error = err instanceof Error ? err.message : 'Unknown error';
			isStreaming = false;
		}
	}
</script>

<svelte:head>
	<title>Active Conversation | CHU Platform</title>
	<meta name="description" content="Chat with the Data Analyst Agent to analyze your data." />
</svelte:head>

<div class="absolute inset-0 flex flex-col bg-canvas">
	<!-- Chat History Area -->
	<div
		class="flex-1 overflow-y-auto flex flex-col items-center px-4 md:px-8"
		bind:this={scrollEl}
		onscroll={onScroll}
	>
		<div class="w-full max-w-[1024px] pt-8 pb-6 conversation">
			<!-- Loading state -->
			{#if isLoading}
				<ChatLoadingState />

				<!-- Empty state -->
			{:else if messages.length === 0}
				<ChatEmptyState />
			{/if}

			{#each messages as msg, i}
				{#if msg.artifact}
					<PlanCard planArtifact={msg.artifact} onproceed={() => proceedWithPlan(msg.artifact!)} />
				{:else}
					<ChatBubble
						role={msg.role}
						content={msg.role === 'user' ? stripLanguageInstruction(msg.content) : msg.content}
						streaming={msg.streaming}
						plan={msg.plan}
						completedSteps={msg.completedSteps ?? new Set()}
						activeStepId={msg.activeStepId ?? null}
						stepMessages={msg.stepMessages ?? {}}
						evidences={msg.evidences ?? []}
						onregenerate={msg.role === 'assistant' && i > 0 ? () => regenerate(i) : undefined}
					/>
				{/if}
			{/each}

			<!-- Error banner -->
			{#if error}
				<div
					class="w-full mt-3 rounded-xl border border-danger/30 bg-danger/8 px-4 py-3 text-[12.5px] text-danger flex items-center gap-2 shadow-sm"
				>
					<span class="font-semibold">Error:</span>
					{error}
				</div>
			{/if}
		</div>
	</div>

	<!-- Pinned Input Area -->
	<div
		class="w-full px-4 pb-4 pt-2.5 flex justify-center shrink-0 border-t border-border-subtle bg-canvas"
	>
		<ChatComposer bind:input {isStreaming} onsubmit={submit} bind:selectedDataset />
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

	/* ── Scoped prose styles for agent markdown output ── */
	.prose-agent :global(h1),
	.prose-agent :global(h2),
	.prose-agent :global(h3),
	.prose-agent :global(h4) {
		font-family: 'Cormorant Garamond', serif;
		color: var(--color-text-primary);
		font-weight: 700;
		letter-spacing: -0.02em;
		margin-top: 1.4em;
		margin-bottom: 0.45em;
		line-height: 1.3;
	}
	.prose-agent :global(h1) {
		font-size: 1.85em;
	}
	.prose-agent :global(h2) {
		font-size: 1.6em;
	}
	.prose-agent :global(h3) {
		font-size: 1.35em;
	}
	.prose-agent :global(h4) {
		font-size: 1.2em;
		font-weight: 700;
	}

	.prose-agent :global(p) {
		margin: 0.55em 0;
		color: var(--color-text-primary);
	}

	.prose-agent :global(p:first-child) {
		margin-top: 0;
	}

	.prose-agent :global(ul) {
		list-style-type: disc;
	}

	.prose-agent :global(ol) {
		list-style-type: decimal;
	}

	.prose-agent :global(ul),
	.prose-agent :global(ol) {
		padding-left: 1.35em;
		margin: 0.55em 0;
		color: var(--color-text-primary);
	}

	.prose-agent :global(li) {
		margin: 0.3em 0;
		line-height: 1.6;
	}

	.prose-agent :global(code) {
		background: var(--color-surface-elevated);
		color: var(--color-text-secondary);
		padding: 0.1em 0.38em;
		border-radius: 5px;
		font-family: var(--font-mono);
		font-size: 0.84em;
		border: 1px solid var(--color-border);
		letter-spacing: 0;
	}

	.prose-agent :global(pre) {
		background: var(--color-surface-elevated);
		border: 1px solid var(--color-border-subtle);
		border-radius: 10px;
		padding: 0.9em 1.1em;
		overflow-x: auto;
		margin: 0.85em 0;
	}

	.prose-agent :global(pre code) {
		background: transparent;
		border: none;
		padding: 0;
		color: var(--color-text-primary);
		font-size: 0.9em;
		letter-spacing: 0;
	}

	.prose-agent :global(table) {
		width: 100%;
		border-collapse: collapse;
		margin: 1.25em 0;
		font-size: 0.95em;
	}

	.prose-agent :global(th) {
		color: var(--color-text-secondary);
		font-weight: 600;
		text-align: left;
		padding: 0.75em 0.5em;
		border-bottom: 1.5px solid var(--color-border);
		font-size: 0.9em;
		letter-spacing: 0.01em;
	}

	.prose-agent :global(td) {
		padding: 0.6em 0.5em;
		border-bottom: 1px solid var(--color-border-subtle);
		color: var(--color-text-primary);
		font-size: 0.95em;
	}

	.prose-agent :global(blockquote) {
		border-left: 2px solid var(--color-accent);
		margin: 0.85em 0;
		padding: 0.5em 1em;
		background: color-mix(in srgb, var(--color-accent) 6%, transparent);
		border-radius: 0 8px 8px 0;
		color: var(--color-text-primary);
		font-size: 0.92em;
	}

	.prose-agent :global(strong),
	.prose-agent :global(b) {
		color: var(--color-text-primary);
		font-weight: 650;
	}

	.prose-agent :global(a) {
		color: var(--color-text-secondary);
		text-decoration: underline;
		text-underline-offset: 2px;
		text-decoration-thickness: 1px;
	}

	.prose-agent :global(img) {
		max-width: 100%;
		border-radius: 10px;
		border: 1px solid var(--color-border);
		margin: 0.85em 0;
		display: block;
	}

	.prose-agent :global(hr) {
		border: none;
		height: 1px;
		background: var(--color-border);
		opacity: 0.5;
		margin: 1.4em 0;
		color: transparent; /* Fix for tailwind color: inherit */
	}

	.prose-agent :global(em) {
		color: var(--color-text-primary);
		font-style: italic;
		opacity: 0.85;
	}
</style>
