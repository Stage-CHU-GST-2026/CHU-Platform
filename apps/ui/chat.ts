/**
 * Chat API service — connects the UI to the Data Analyst agent backend.
 *
 * The development Vite proxy forwards /api → http://localhost:10000/api
 */

const API_BASE = "/api/v1";

export interface ChatMessage {
    role: "user" | "assistant";
    content: string;
}

export interface ThreadInfo {
    threadId: string;
}

/** Response type for the streaming callback */
export interface StreamCallbacks {
    onToken: (token: string) => void;
    onDone: () => void;
    onError: (error: Error) => void;
}

/**
 * Create a new conversation thread.
 */
export async function createThread(): Promise<ThreadInfo> {
    const res = await fetch(`${API_BASE}/chat/new`, { method: "POST" });
    if (!res.ok) {
        throw new Error(`Failed to create thread: ${res.status}`);
    }
    const data = await res.json();
    return { threadId: data.thread_id };
}

/**
 * Send a message and stream the assistant response via SSE.
 *
 * Returns the thread_id (useful on first message when none was set).
 */
export async function sendMessage(
    message: string,
    threadId: string | undefined,
    callbacks: StreamCallbacks
): Promise<string> {
    const res = await fetch(`${API_BASE}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            message,
            ...(threadId ? { thread_id: threadId } : {}),
        }),
    });

    if (!res.ok) {
        throw new Error(`Chat request failed: ${res.status}`);
    }

    const reader = res.body?.getReader();
    if (!reader) {
        throw new Error("No response body stream");
    }

    const decoder = new TextDecoder();
    let buffer = "";
    let resolvedThreadId = threadId ?? "";

    // These must live OUTSIDE the read loop: an SSE event's "event:" and
    // "data:" lines can be split across two separate reader.read() chunks,
    // since chunk boundaries have nothing to do with SSE event boundaries.
    // Resetting them per-chunk (as the old code did) silently drops any
    // event that happens to straddle a chunk boundary.
    let currentEvent = "";
    let dataLines: string[] = [];

    try {
        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });

            // Parse SSE events from the buffer
            const lines = buffer.split("\n");
            buffer = lines.pop() ?? ""; // keep incomplete line in buffer

            for (const rawLine of lines) {
                // sse_starlette uses \r\n as its default line separator.
                // Splitting on \n alone leaves a trailing \r on every line,
                // which means the blank-line event boundary never matches "".
                // Strip the trailing \r here so both \r\n and \n streams work.
                const line = rawLine.replace(/\r$/, "");

                if (line.startsWith("event: ")) {
                    currentEvent = line.slice(7).trim();
                } else if (line.startsWith("data:")) {
                    // SSE allows multiple "data:" lines per event; per spec they're
                    // joined with "\n". Handle both "data: x" and bare "data:".
                    dataLines.push(line.startsWith("data: ") ? line.slice(6) : line.slice(5));
                } else if (line.startsWith(":")) {
                    // Comment line (e.g. ": ping ...") — ignore.
                    continue;
                } else if (line === "") {
                    // Empty line = end of event
                    const currentData = dataLines.join("\n");
                    if (currentEvent === "thread_id" && currentData) {
                        resolvedThreadId = currentData;
                    } else if (currentEvent === "token" && dataLines.length > 0) {
                        callbacks.onToken(currentData);
                    } else if (currentEvent === "step_token" && dataLines.length > 0) {
                        // Live tokens streamed during each execution step.
                        callbacks.onToken(currentData);
                    } else if (currentEvent === "image" && currentData) {
                        // Append a markdown image so MessageResponse renders it inline.
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

    return resolvedThreadId;
}

/**
 * Fetch the full message history for a thread.
 */
export async function getHistory(threadId: string): Promise<ChatMessage[]> {
    const res = await fetch(`${API_BASE}/chat/${encodeURIComponent(threadId)}/history`);
    if (!res.ok) {
        throw new Error(`Failed to fetch history: ${res.status}`);
    }
    const data = await res.json();
    return (data.messages ?? []).map((m: { role: string; content: string }) => ({
        role: m.role as "user" | "assistant",
        content: m.content,
    }));
}

/**
 * Delete a thread session.
 */
export async function deleteThread(threadId: string): Promise<void> {
    await fetch(`${API_BASE}/chat/${encodeURIComponent(threadId)}`, {
        method: "DELETE",
    });
}