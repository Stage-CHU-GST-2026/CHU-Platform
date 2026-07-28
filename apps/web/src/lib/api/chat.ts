/**
 * Chat API service — connects the UI to the CHU Platform analytics backend.
 *
 * Uses the conversation-based REST API (persistent, DB-backed).
 * The development Vite proxy forwards /api → http://localhost:10000/api
 */

const API_BASE = "/api/v1";

// ── Types ─────────────────────────────────────────────────────────────────────

export const PLAN_MIME_TYPE = "application/vnd.chu.execution-plan+json";

export interface ConversationSummary {
    id: string;
    title: string | null;
    created_at: string;
    updated_at: string;
    message_count: number;
    artifact_count?: number;
}

export interface Artifact {
    id: string;
    conversation_id: string;
    filename: string;
    mime_type: string;
    file_size: number;
    url: string;
    created_at: string;
    /** Optional fields for plan artifacts (from create_plan tool). */
    title?: string;
    description?: string;
}

export interface ToolEvidence {
    id?: string;
    message_id?: number;
    conversation_id?: string;
    step_id?: number | null;
    tool_name: string;
    tool_call_id?: string | null;
    parameters?: Record<string, any> | null;
    result: string;
    status: 'success' | 'error' | string;
    execution_time_ms?: number | null;
    created_at?: string;
}

export interface ChatMessage {
    id: number;
    role: "user" | "assistant";
    content: string;
    created_at: string;
    tool_evidences?: ToolEvidence[];
}

export interface Conversation {
    id: string;
    title: string | null;
    created_at: string;
    updated_at: string;
    messages: ChatMessage[];
    artifacts: Artifact[];
}

export interface StreamCallbacks {
    onToken: (token: string) => void;
    onArtifact: (artifact: Artifact) => void;
    /** Called when the orchestrator generates an execution plan. */
    onPlan?: (plan: PlanData) => void;
    /** Called when a tool evidence record is emitted. */
    onToolEvidence?: (evidence: ToolEvidence) => void;
    /** Called when a step starts executing. */
    onStepStarted?: (step: PlanStepData) => void;
    /** Called with progress updates within a step. */
    onStepUpdate?: (message: string) => void;
    /** Called when a step finishes executing. */
    onStepFinished?: (stepId: number) => void;
    onDone: () => void;
    onError: (error: Error) => void;
}


/** Structured plan data from the orchestrator. */
export interface PlanData {
    plan_title: string;
    steps: PlanStepData[];
}

/** A single step in the execution plan. */
export interface PlanStepData {
    id: number;
    title: string;
    description: string;
    tool_hint: string;
}

// ── Conversation CRUD ─────────────────────────────────────────────────────────

/**
 * List all conversations, most recently updated first.
 */
export async function listConversations(
    limit = 50,
    offset = 0
): Promise<ConversationSummary[]> {
    const res = await fetch(`${API_BASE}/conversations?limit=${limit}&offset=${offset}`);
    if (!res.ok) throw new Error(`Failed to list conversations: ${res.status}`);
    return res.json();
}

/**
 * Create a new conversation. Title is optional — auto-generated from first message if omitted.
 */
export async function createConversation(title?: string): Promise<Conversation> {
    const res = await fetch(`${API_BASE}/conversations`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(title ? { title } : {}),
    });
    if (!res.ok) throw new Error(`Failed to create conversation: ${res.status}`);
    return res.json();
}

/**
 * Get a specific conversation by ID
 */
export async function getConversation(id: string): Promise<Conversation> {
    const res = await fetch(`${API_BASE}/conversations/${encodeURIComponent(id)}?include_artifacts=true`);
    if (!res.ok) throw new Error(`Failed to get conversation: ${res.status}`);
    return res.json();
}

/**
 * List artifacts for a specific conversation
 */
export async function listArtifacts(conversationId: string, limit = 50, offset = 0): Promise<Artifact[]> {
    const res = await fetch(`${API_BASE}/artifacts?conversation_id=${encodeURIComponent(conversationId)}&limit=${limit}&offset=${offset}`);
    if (!res.ok) throw new Error(`Failed to list artifacts: ${res.status}`);
    return res.json();
}

/**
 * Fetch the execution plan JSON from a plan artifact.
 * Returns null if the artifact is not a plan or the fetch fails.
 */
export async function fetchPlanFromArtifact(artifact: Artifact): Promise<PlanData | null> {
    if (artifact.mime_type !== PLAN_MIME_TYPE) return null;
    try {
        // Use the /artifacts/{id}/file endpoint — the static /charts/ path
        // does not serve .json files reliably (it is optimised for images).
        const res = await fetch(`${API_BASE}/artifacts/${encodeURIComponent(artifact.id)}/file`);
        if (!res.ok) return null;
        return await res.json();
    } catch {
        return null;
    }
}

/**
 * Update the title of a conversation.
 */
export async function updateConversation(id: string, title: string): Promise<Conversation> {
    const res = await fetch(`${API_BASE}/conversations/${encodeURIComponent(id)}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title }),
    });
    if (!res.ok) throw new Error(`Failed to update conversation: ${res.status}`);
    return res.json();
}

/**
 * Delete a conversation and all its messages.
 */
export async function deleteConversation(id: string): Promise<void> {
    await fetch(`${API_BASE}/conversations/${encodeURIComponent(id)}`, {
        method: "DELETE",
    });
}

// ── SSE Streaming ─────────────────────────────────────────────────────────────

/**
 * Send a message inside an existing conversation and stream the assistant response via SSE.
 *
 * Both the user message and the complete assistant response are automatically
 * saved to the database by the backend.
 */
export async function sendMessage(
    conversationId: string,
    message: string,
    callbacks: StreamCallbacks,
    datasetPath?: string
): Promise<void> {
    const res = await fetch(
        `${API_BASE}/conversations/${encodeURIComponent(conversationId)}/chat`,
        {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                message,
                ...(datasetPath ? { dataset_path: datasetPath } : {}),
            }),
        }
    );

    if (!res.ok) {
        throw new Error(`Chat request failed: ${res.status}`);
    }

    const reader = res.body?.getReader();
    if (!reader) throw new Error("No response body stream");

    const decoder = new TextDecoder();
    let buffer = "";
    let currentEvent = "";
    let dataLines: string[] = [];

    try {
        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });

            const lines = buffer.split("\n");
            buffer = lines.pop() ?? "";

            for (const rawLine of lines) {
                const line = rawLine.replace(/\r$/, "");

                if (line.startsWith("event: ")) {
                    currentEvent = line.slice(7).trim();
                } else if (line.startsWith("data:")) {
                    dataLines.push(line.startsWith("data: ") ? line.slice(6) : line.slice(5));
                } else if (line.startsWith(":")) {
                    // Comment / ping line — ignore
                    continue;
                } else if (line === "") {
                    // End of SSE event
                    const currentData = dataLines.join("\n");

                    if (currentEvent === "token" && dataLines.length > 0) {
                        callbacks.onToken(currentData);
                    } else if (currentEvent === "step_token" && dataLines.length > 0) {
                        // Route live step text to the step card (onStepUpdate),
                        // NOT to the main message bubble (onToken). This prevents
                        // duplication: step text is shown transiently in the active
                        // step card; only the final synthesis goes into the message.
                        callbacks.onStepUpdate?.(currentData);
                    } else if (currentEvent === "image" && currentData) {
                        callbacks.onStepUpdate?.(`\n\n![chart](${currentData})\n\n`);
                    } else if (currentEvent === "artifact" && currentData) {
                        try {
                            const artifact = JSON.parse(currentData);
                            callbacks.onArtifact(artifact);
                        } catch (e) {
                            console.warn("Failed to parse artifact event", e);
                        }
                    } else if (currentEvent === "plan" && currentData) {
                        try {
                            const plan = JSON.parse(currentData);
                            callbacks.onPlan?.(plan);
                        } catch (e) {
                            console.warn("Failed to parse plan event", e);
                        }
                    } else if (currentEvent === "tool_evidence" && currentData) {
                        try {
                            const evidence = JSON.parse(currentData);
                            callbacks.onToolEvidence?.(evidence);
                        } catch (e) {
                            console.warn("Failed to parse tool_evidence event", e);
                        }
                    } else if (currentEvent === "step_started" && currentData) {

                        try {
                            const step = JSON.parse(currentData);
                            callbacks.onStepStarted?.(step);
                        } catch (e) {
                            console.warn("Failed to parse step_started event", e);
                        }
                    } else if (currentEvent === "step_update" && currentData) {
                        callbacks.onStepUpdate?.(currentData);
                    } else if (currentEvent === "step_finished" && currentData) {
                        try {
                            const data = JSON.parse(currentData);
                            callbacks.onStepFinished?.(data.id);
                        } catch (e) {
                            console.warn("Failed to parse step_finished event", e);
                        }
                    } else if (currentEvent === "done") {
                        callbacks.onDone();
                    }

                    currentEvent = "";
                    dataLines = [];
                }
            }
        }
    } catch (err) {
        callbacks.onError(err instanceof Error ? err : new Error(String(err)));
    }
}