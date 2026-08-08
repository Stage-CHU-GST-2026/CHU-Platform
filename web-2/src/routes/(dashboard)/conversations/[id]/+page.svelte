<script lang="ts">
	import * as PromptInput from "$lib/components/ai-elements/prompt-input";
	import ChatContainer from "$lib/components/chat/chat-container.svelte";
	import PromptCheckpoints, {
		type CheckpointItem,
	} from "$lib/components/chat/prompt-checkpoints.svelte";
	import * as Conversation from "$lib/components/ai-elements/conversation";
	import * as Message from "$lib/components/ai-elements/message";
	import * as ChainOfThought from "$lib/components/ai-elements/chain-of-thought";
	import * as Select from "$lib/components/ui/select";
	import { Button } from "$lib/components/ui/button";
	import { Input } from "$lib/components/ui/input";
	import MessageSquare from "@lucide/svelte/icons/message-square";
	import Sparkles from "@lucide/svelte/icons/sparkles";
	import Database from "@lucide/svelte/icons/database";
	import X from "@lucide/svelte/icons/x";
	import Search from "@lucide/svelte/icons/search";
	import { sendChatMessageStream, type ConversationDetail } from "$lib/api/conversations";
	import { listDatasets, type DatasetSummary } from "$lib/api/datasets";
	import { fetchPlanFromArtifact } from "$lib/api/artifacts";
	import { BACKEND_API_URL } from "$lib/api/client";
	import { cn } from "$lib/utils";
	import { goto, invalidateAll } from "$app/navigation";
	import { page } from "$app/state";
	import { onMount, tick } from "svelte";
	import type { PageData } from "./$types";

	interface Props {
		data: PageData;
	}

	let { data }: Props = $props();

	let conversation = $derived(data.conversation as ConversationDetail);
	let scrollContainerRef = $state<HTMLDivElement | null>(null);

	// Dataset Attachment state (Matching apps/web 1:1 logic + shadcn-svelte Select)
	let selectedDataset = $state<DatasetSummary | null>(null);
	let availableDatasets = $state<DatasetSummary[]>([]);
	let loadingDatasets = $state(false);
	let datasetSearchQuery = $state("");
	let loadedConversationId = $state<string | null>(null);
	let historicalPlanSteps = $state<ReasoningStepItem[]>([]);

	// Restore linked dataset from conversation on initial load (matching apps/web loadConversation)
	$effect(() => {
		const currentId = conversation?.id;
		if (currentId && currentId !== loadedConversationId) {
			loadedConversationId = currentId;
			if (conversation.dataset_id && conversation.dataset_name) {
				selectedDataset = {
					id: conversation.dataset_id,
					original_filename: conversation.dataset_name,
					filepath: "",
					file_size: 0,
					rows: null,
					columns: null,
					status: "ready",
					created_at: "",
					updated_at: ""
				};
			} else {
				selectedDataset = null;
			}
		}
	});

	// Restore reasoning plan steps for historical messages (matching apps/web)
	$effect(() => {
		const artifacts = conversation.artifacts || [];
		const planArtifact = artifacts.find(
			(a) => a.mime_type.includes("plan") || a.filename.includes("plan")
		);
		if (planArtifact) {
			fetchPlanFromArtifact(planArtifact).then((planData) => {
				if (planData && planData.steps) {
					historicalPlanSteps = planData.steps.map((s) => ({
						id: s.id,
						name: s.title || s.name || `Step ${s.id}`,
						description: s.description || "",
						status: "complete",
					}));
				}
			});
		} else {
			historicalPlanSteps = [];
		}
	});

	let filteredDatasets = $derived.by(() => {
		if (!datasetSearchQuery.trim()) return availableDatasets;
		const q = datasetSearchQuery.toLowerCase();
		return availableDatasets.filter((d) =>
			d.original_filename.toLowerCase().includes(q)
		);
	});

	async function loadDatasets() {
		loadingDatasets = true;
		try {
			const res = await listDatasets({ limit: 100, status_filter: "ready" });
			if (res.ok && res.data) {
				availableDatasets = res.data;
			} else {
				availableDatasets = [];
			}
		} catch (err) {
			console.error("Failed to load datasets:", err);
			availableDatasets = [];
		} finally {
			loadingDatasets = false;
		}
	}

	function handleSelectValue(val: string) {
		if (!val || val === "none") {
			selectedDataset = null;
		} else {
			const found = availableDatasets.find((d) => d.id === val);
			if (found) selectedDataset = found;
		}
	}

	function clearDataset() {
		selectedDataset = null;
	}

	function scrollToBottom(behavior: ScrollBehavior = "smooth") {
		if (scrollContainerRef) {
			scrollContainerRef.scrollTo({
				top: scrollContainerRef.scrollHeight,
				behavior,
			});
		}
	}

	interface AttachmentItem {
		type: "file";
		url?: string;
		mediaType: string;
		filename: string;
	}

	export interface ToolEvidenceItem {
		tool_name: string;
		input?: any;
		output?: any;
	}

	export interface ReasoningStepItem {
		id: number;
		name: string;
		description?: string;
		status?: "complete" | "active" | "pending";
		evidences?: ToolEvidenceItem[];
	}

	interface ConversationTurn {
		id: string;
		key: string;
		userPrompt: string;
		userAttachments?: AttachmentItem[];
		assistantResponse?: string;
		turnNumber: number;
		isStreaming?: boolean;
		steps?: ReasoningStepItem[];
		evidences?: ToolEvidenceItem[];
	}

	// Dynamic turns state derived from server conversation & live streaming additions
	let activeStreamingTurn = $state<ConversationTurn | null>(null);

	let turns = $derived.by<ConversationTurn[]>(() => {
		const rawMessages = conversation.messages || [];
		const result: ConversationTurn[] = [];
		let turnIndex = 1;

		for (let i = 0; i < rawMessages.length; i++) {
			const msg = rawMessages[i];
			if (msg.role === "user") {
				const assistantMsg = rawMessages[i + 1]?.role === "assistant" ? rawMessages[i + 1] : undefined;
				const isLastTurn = i >= rawMessages.length - 2;
				result.push({
					id: `cp-${msg.id || i}`,
					key: `msg-${msg.id || i}`,
					userPrompt: msg.content,
					assistantResponse: assistantMsg?.content || "",
					turnNumber: turnIndex++,
					steps: isLastTurn && historicalPlanSteps.length > 0 ? historicalPlanSteps : undefined
				});
				if (assistantMsg) i++; // skip assistant msg since it was paired
			}
		}

		if (activeStreamingTurn) {
			result.push(activeStreamingTurn);
		}

		return result;
	});

	// Auto-scroll to bottom smoothly when new turns arrive
	let previousTurnCount = $state(0);
	$effect(() => {
		const currentCount = turns.length;
		if (currentCount > previousTurnCount) {
			previousTurnCount = currentCount;
			tick().then(() => {
				scrollToBottom("smooth");
			});
		}
	});

	onMount(() => {
		tick().then(() => {
			scrollToBottom("auto");
		});

		// Check for initial query draft param from /conversations/new
		const initialQuery = page.url.searchParams.get("q");
		if (initialQuery) {
			const cleanUrl = page.url.pathname;
			goto(cleanUrl, { replaceState: true, noScroll: true }).then(() => {
				handleSubmit({ text: initialQuery }, new Event("submit") as SubmitEvent);
			});
		}
	});

	// Extract user prompts into checkpoints for the right-side outline panel
	let checkpoints = $derived<CheckpointItem[]>(
		turns.map((t) => ({
			id: t.id,
			title: t.userPrompt,
			number: t.turnNumber,
		}))
	);

	let activeCheckpointId = $state<string>("");

	// IntersectionObserver for dynamic scroll spying on user checkpoints
	$effect(() => {
		if (checkpoints.length === 0) return;

		if (!activeCheckpointId && checkpoints.length > 0) {
			activeCheckpointId = checkpoints[0].id;
		}

		const observer = new IntersectionObserver(
			(entries) => {
				for (const entry of entries) {
					if (entry.isIntersecting) {
						activeCheckpointId = entry.target.id;
					}
				}
			},
			{
				root: null,
				rootMargin: "-10% 0px -70% 0px",
				threshold: 0,
			}
		);

		checkpoints.forEach((cp) => {
			const el = document.getElementById(cp.id);
			if (el) observer.observe(el);
		});

		return () => observer.disconnect();
	});

	let abortController: AbortController | null = null;

	async function handleSubmit(messageInput: { text?: string }, event: SubmitEvent) {
		const userQuery = messageInput?.text?.trim() || "";
		if (!userQuery) return;

		const turnId = `cp-stream-${Date.now()}`;

		activeStreamingTurn = {
			id: turnId,
			key: turnId,
			userPrompt: userQuery,
			assistantResponse: "",
			turnNumber: turns.length + 1,
			isStreaming: true,
			steps: [],
			evidences: []
		};

		await tick();
		scrollToBottom("smooth");

		abortController = new AbortController();

		try {
			const datasetPath = selectedDataset?.filepath || selectedDataset?.id;
			const res = await sendChatMessageStream(conversation.id, {
				message: userQuery,
				...(datasetPath ? { dataset_path: datasetPath } : {})
			});

			if (!res.ok || !res.body) {
				activeStreamingTurn.assistantResponse = "Failed to communicate with the assistant API server.";
				activeStreamingTurn.isStreaming = false;
				activeStreamingTurn = null;
				return;
			}

			const reader = res.body.getReader();
			const decoder = new TextDecoder();
			let buffer = "";
			let currentEventType = "token";
			let dataLines: string[] = [];

			while (true) {
				const { done, value } = await reader.read();
				if (done) break;

				buffer += decoder.decode(value, { stream: true });

				const lines = buffer.split("\n");
				buffer = lines.pop() ?? "";

				for (const rawLine of lines) {
					const line = rawLine.replace(/\r$/, "");

					if (line.startsWith("event: ")) {
						currentEventType = line.slice(7).trim();
					} else if (line.startsWith("event:")) {
						currentEventType = line.slice(6).trim();
					} else if (line.startsWith("data:")) {
						dataLines.push(line.startsWith("data: ") ? line.slice(6) : line.slice(5));
					} else if (line.startsWith(":")) {
						continue;
					} else if (line === "") {
						if (dataLines.length > 0) {
							const currentData = dataLines.join("\n");
							dataLines = [];

							if (currentEventType === "token") {
								if (activeStreamingTurn) {
									activeStreamingTurn.assistantResponse += currentData;
									scrollToBottom("smooth");
								}
							} else if (currentEventType === "step_token" || currentEventType === "step_update") {
								if (activeStreamingTurn?.steps) {
									const activeStep = activeStreamingTurn.steps.find((s) => s.status === "active")
										|| activeStreamingTurn.steps[activeStreamingTurn.steps.length - 1];
									if (activeStep) {
										activeStep.description = (activeStep.description || "") + currentData;
									}
								}
								scrollToBottom("smooth");
							} else if (currentEventType === "plan") {
								try {
									const plan = JSON.parse(currentData);
									if (plan && plan.steps && activeStreamingTurn) {
										activeStreamingTurn.steps = plan.steps.map((s: any) => ({
											id: s.id,
											name: s.name || s.title || `Step ${s.id}`,
											description: s.description || "",
											status: "pending",
											evidences: []
										}));
									}
								} catch (e) {
									console.warn("Failed to parse plan event:", e);
								}
							} else if (currentEventType === "step_started") {
								try {
									const stepData = JSON.parse(currentData);
									if (activeStreamingTurn) {
										if (!activeStreamingTurn.steps) activeStreamingTurn.steps = [];
										const existing = activeStreamingTurn.steps.find((s) => s.id === stepData.id);
										if (existing) {
											existing.status = "active";
										} else {
											activeStreamingTurn.steps.push({
												id: stepData.id,
												name: stepData.name || `Step ${stepData.id}`,
												description: stepData.description || "",
												status: "active",
												evidences: []
											});
										}
									}
								} catch (e) {
									console.warn("Failed to parse step_started event:", e);
								}
							} else if (currentEventType === "step_finished") {
								try {
									const stepData = JSON.parse(currentData);
									const stepId = typeof stepData === "object" ? stepData.id : stepData;
									if (activeStreamingTurn?.steps) {
										const step = activeStreamingTurn.steps.find((s) => s.id === stepId);
										if (step) {
											step.status = "complete";
										}
									}
								} catch (e) {
									console.warn("Failed to parse step_finished event:", e);
								}
							} else if (currentEventType === "tool_evidence") {
								try {
									const evidence = JSON.parse(currentData);
									if (activeStreamingTurn) {
										if (!activeStreamingTurn.evidences) activeStreamingTurn.evidences = [];
										activeStreamingTurn.evidences.push(evidence);

										const activeStep = activeStreamingTurn.steps?.find((s) => s.status === "active");
										if (activeStep) {
											if (!activeStep.evidences) activeStep.evidences = [];
											activeStep.evidences.push(evidence);
										}
									}
								} catch (e) {
									console.warn("Failed to parse tool_evidence event:", e);
								}
							} else if (currentEventType === "image") {
								const imageUrl = currentData.startsWith("http")
									? currentData
									: `${BACKEND_API_URL}${currentData}`;
								if (activeStreamingTurn) {
									const activeStep = activeStreamingTurn.steps?.find((s) => s.status === "active")
										|| activeStreamingTurn.steps?.[activeStreamingTurn.steps.length - 1];

									if (activeStep) {
										activeStep.description = (activeStep.description || "") + `\n\n![Generated Chart](${imageUrl})\n\n`;
									} else {
										activeStreamingTurn.assistantResponse += `\n\n![Generated Chart](${imageUrl})\n\n`;
									}
									scrollToBottom("smooth");
								}
							} else if (currentEventType === "done") {
								if (activeStreamingTurn) {
									activeStreamingTurn.isStreaming = false;
									if (activeStreamingTurn.steps) {
										activeStreamingTurn.steps.forEach((s) => (s.status = "complete"));
									}
								}
							}
						}
					}
				}
			}

			if (dataLines.length > 0) {
				const currentData = dataLines.join("\n");
				if (currentEventType === "token" && activeStreamingTurn) {
					activeStreamingTurn.assistantResponse += currentData;
				}
			}

			// Smooth transition: mark streaming as done, fetch updated server messages, THEN clear activeStreamingTurn
			if (activeStreamingTurn) {
				activeStreamingTurn.isStreaming = false;
			}
			await invalidateAll();
			await tick();
			activeStreamingTurn = null;
		} catch (err: any) {
			if (err.name !== "AbortError") {
				if (activeStreamingTurn) {
					activeStreamingTurn.assistantResponse += `\n\n*Error streaming response: ${err.message}*`;
					activeStreamingTurn.isStreaming = false;
				}
				activeStreamingTurn = null;
			}
		} finally {
			abortController = null;
		}
	}

	function handleStop() {
		if (abortController) {
			abortController.abort();
			abortController = null;
		}
		if (activeStreamingTurn) {
			activeStreamingTurn.isStreaming = false;
			activeStreamingTurn = null;
		}
	}
</script>

<ChatContainer bind:scrollContainerRef={scrollContainerRef}>
	<!-- Conversation Root & Content -->
	<Conversation.Root style="height: auto" class="max-w-6xl w-full mx-auto px-6">
		<Conversation.Content class="gap-10">
			{#if turns.length === 0}
				<Conversation.EmptyState
					description="Ask questions about datasets, request chart generation, or inspect metrics."
					title="Start a conversation"
				>
					{#snippet icon()}
						<MessageSquare class="size-6 text-primary" />
					{/snippet}
				</Conversation.EmptyState>
			{:else}
				{#each turns as turn, index (turn.id)}
					<!-- Conversation Turn: User prompt on top, assistant response below -->
					<div
						id={turn.id}
						class={cn(
							"flex flex-col gap-4 scroll-mt-14 transition-all",
							index === turns.length - 1
								? "min-h-[45vh] pb-24"
								: "pb-8 border-b border-border/30"
						)}
					>
						<!-- User prompt on top -->
						<Message.Root from="user">
							{#if turn.userAttachments && turn.userAttachments.length > 0}
								<Message.Attachments class="mb-2">
									{#each turn.userAttachments as att}
										<Message.Attachment data={att} />
									{/each}
								</Message.Attachments>
							{/if}
							<Message.Content>
								<div class="whitespace-pre-wrap font-medium">
									{turn.userPrompt}
								</div>
							</Message.Content>
						</Message.Root>

						<!-- Assistant response directly below -->
						{#if turn.assistantResponse || turn.isStreaming || (turn.steps && turn.steps.length > 0)}
							<Message.Root from="assistant" class="min-h-[80px]">
								<Message.Content>
									<!-- Standard Clean Chain of Thought Reasoning Steps -->
									{#if turn.steps && turn.steps.length > 0}
										<div class="mb-3">
											<ChainOfThought.Root defaultOpen={turn.isStreaming}>
												<ChainOfThought.Header />
												<ChainOfThought.Content>
													{#each turn.steps as step (step.id)}
														<ChainOfThought.Step
															label={step.name}
															status={step.status || "complete"}
														>
															{#if step.description}
																<div class="mt-1 text-xs">
																	<Message.Response
																		content={step.description}
																		class="text-xs [&_p]:my-1 [&_p]:leading-relaxed [&_h1]:text-sm [&_h2]:text-xs [&_h3]:text-xs [&_pre]:my-2 [&_table]:my-2 [&_img]:my-3 font-normal text-muted-foreground"
																	/>
																</div>
															{/if}
														</ChainOfThought.Step>
													{/each}
												</ChainOfThought.Content>
											</ChainOfThought.Root>
										</div>
									{/if}

									{#if turn.assistantResponse}
										<Message.Response content={turn.assistantResponse} />
									{:else if turn.isStreaming && (!turn.steps || turn.steps.length === 0)}
										<div class="flex items-center gap-2 text-xs text-muted-foreground animate-pulse py-2">
											<Sparkles class="size-4 animate-spin text-primary" />
											Assistant is thinking...
										</div>
									{/if}
								</Message.Content>
							</Message.Root>
						{/if}
					</div>
				{/each}
			{/if}
		</Conversation.Content>
		<Conversation.ScrollButton />
	</Conversation.Root>

	<!-- Prompt bar sticky toolbar at the bottom: ALWAYS FLOATING OVER CONVERSATION -->
	{#snippet prompt()}
		<div class="w-full max-w-5xl mx-auto px-4 flex flex-col gap-2">
			<!-- Attached Dataset Pill -->
			{#if selectedDataset}
				<div class="flex items-center gap-2 px-1">
					<div class="inline-flex items-center gap-2 px-3 py-1.5 rounded-xl bg-primary/10 border border-primary/25 text-xs font-medium text-foreground shadow-xs backdrop-blur-md">
						<Database class="size-3.5 text-primary shrink-0" />
						<span class="font-semibold truncate max-w-xs">{selectedDataset.original_filename}</span>
						{#if selectedDataset.rows || selectedDataset.columns}
							<span class="text-[11px] font-mono text-muted-foreground border-l border-border/60 pl-2">
								{selectedDataset.rows?.toLocaleString() ?? '?'} rows &middot; {selectedDataset.columns ?? '?'} cols
							</span>
						{/if}
						<button
							type="button"
							onclick={clearDataset}
							class="ml-1 p-0.5 rounded-md text-muted-foreground hover:text-destructive hover:bg-destructive/10 transition-colors cursor-pointer"
							title="Remove dataset"
						>
							<X class="size-3.5" />
						</button>
					</div>
				</div>
			{/if}

			<PromptInput.Root class="p-2 shadow-2xl border border-border/60 bg-background/95 backdrop-blur-xl rounded-2xl" onSubmit={handleSubmit}>
				<PromptInput.Body>
					<PromptInput.Textarea placeholder={selectedDataset ? `Ask anything about "${selectedDataset.original_filename}"...` : "Ask a question or request a chart visualization..."} />
				</PromptInput.Body>
				<PromptInput.Toolbar class="justify-between">
					<!-- Shadcn-Svelte Select Dataset Selector with Search Input -->
					<Select.Root
						type="single"
						value={selectedDataset?.id || "none"}
						onValueChange={handleSelectValue}
						onOpenChange={(open) => {
							if (open) {
								datasetSearchQuery = "";
								if (availableDatasets.length === 0) loadDatasets();
							}
						}}
					>
						<Select.Trigger class="w-auto min-w-[160px] h-8 gap-2 rounded-lg bg-background/80 backdrop-blur-sm border-border/70 text-xs font-medium cursor-pointer">
							<Database class="size-3.5 text-primary shrink-0" />
							<span class="truncate max-w-[140px]">
								{selectedDataset ? selectedDataset.original_filename : "Attach Dataset"}
							</span>
						</Select.Trigger>
						<Select.Content class="w-80 max-h-80 z-50 p-0 overflow-hidden">
							<!-- Search Input Box inside Select Content -->
							<div class="p-2 border-b border-border/60 bg-muted/40 sticky top-0 z-10">
								<div class="relative w-full">
									<Input
										type="text"
										placeholder="Search datasets..."
										bind:value={datasetSearchQuery}
										class="h-8 text-xs pl-8 bg-background"
										onclick={(e) => e.stopPropagation()}
										onkeydown={(e) => e.stopPropagation()}
									/>
									<Search class="absolute left-2.5 top-2.5 size-3.5 text-muted-foreground" />
								</div>
							</div>

							<Select.Group class="p-1">
								<Select.GroupHeading class="text-[11px] font-bold text-muted-foreground uppercase px-2 py-1.5">
									Available Datasets
								</Select.GroupHeading>

								{#if selectedDataset}
									<Select.Item value="none" label="None (Detach dataset)" class="text-xs text-muted-foreground italic">
										None (Detach dataset)
									</Select.Item>
								{/if}

								{#if loadingDatasets}
									<div class="p-4 text-center text-xs text-muted-foreground">Loading datasets...</div>
								{:else if filteredDatasets.length === 0}
									<div class="p-4 text-center text-xs text-muted-foreground">
										No matching datasets found.
									</div>
								{:else}
									{#each filteredDatasets as ds (ds.id)}
										<Select.Item value={ds.id} label={ds.original_filename} class="text-xs flex items-center justify-between py-2">
											<div class="flex flex-col min-w-0">
												<span class="truncate font-semibold">{ds.original_filename}</span>
												<span class="text-[10px] text-muted-foreground font-mono">
													{ds.rows?.toLocaleString() ?? '?'} rows &middot; {ds.columns ?? '?'} cols
												</span>
											</div>
										</Select.Item>
									{/each}
								{/if}
							</Select.Group>
						</Select.Content>
					</Select.Root>

					<PromptInput.Submit onStop={handleStop} />
				</PromptInput.Toolbar>
			</PromptInput.Root>
		</div>
	{/snippet}
</ChatContainer>

<!-- Prompt Checkpoints Outline Panel on the Right Side -->
<PromptCheckpoints checkpoints={checkpoints} bind:activeId={activeCheckpointId} />
