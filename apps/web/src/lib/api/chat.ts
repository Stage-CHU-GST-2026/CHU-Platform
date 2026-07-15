/**
 * Chat API service — connects the UI to the CHU Platform analytics backend.
 *
 * Uses the conversation-based REST API (persistent, DB-backed).
 * The development Vite proxy forwards /api → http://localhost:10000/api
 */

const API_BASE = "/api/v1";

// ── Types ─────────────────────────────────────────────────────────────────────

export interface ConversationSummary {
    id: string;
    title: string | null;
    created_at: string;
    updated_at: string;
    message_count: number;
}

export interface ChatMessage {
    id: number;
    role: "user" | "assistant";
    content: string;
    created_at: string;
}

export interface Conversation {
    id: string;
    title: string | null;
    created_at: string;
    updated_at: string;
    messages: ChatMessage[];
}

export interface StreamCallbacks {
    onToken: (token: string) => void;
    onDone: () => void;
    onError: (error: Error) => void;
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
 * Fetch a single conversation with its full message history.
 */
export async function getConversation(id: string): Promise<Conversation> {
    const res = await fetch(`${API_BASE}/conversations/${encodeURIComponent(id)}`);
    if (!res.ok) throw new Error(`Failed to get conversation: ${res.status}`);
    return res.json();
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
                    } else if (currentEvent === "image" && currentData) {
                        callbacks.onToken(`\n\n![chart](${currentData})\n\n`);
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