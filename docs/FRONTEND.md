# Frontend Subsystem Documentation - CHU-Platform

CHU-Platform features two frontend applications:
1. **Primary Frontend (`apps/web`)**: Built with **SvelteKit 5** and **Svelte 5 Runes**, providing a responsive UI with real-time SSE stream visualization, dataset management, and interactive Plotly chart rendering.
2. **Component Library (`apps/ui`)**: Reusable UI primitives and design components.
3. **Legacy Frontend (`web-2`)**: Earlier prototype build (Svelte 4 / Vite).

---

## 1. Primary SvelteKit Web Application (`apps/web`)

### Tech Stack
- **Framework**: SvelteKit 5 (Svelte 5)
- **Styling**: TailwindCSS
- **Build Tool**: Vite
- **Package Manager**: Bun / npm

### Route Architecture (`apps/web/src/routes/`)
- `+layout.svelte`: Global navigation bar, sidebar layout, theme providers, and notification toasts.
- `+page.svelte`: Landing dashboard showing dataset stats, recent conversations, and quick uploads.
- `datasets/`: Dataset management page (file dropzone, schema viewer, column profiling).
- `chat/` / `conversations/[id]`: Interactive chat interface with SSE stream listeners, markdown rendering, tool call accordion step displays, and Plotly chart containers.
- `categories/`: Semantic category hierarchy management interface.

---

## 2. Server-Sent Events (SSE) Integration

The chat client uses an event stream subscriber to consume real-time updates from `POST /api/chat/stream`:

```typescript
// Svelte 5 Rune State Management
let messages = $state<Message[]>([]);
let isStreaming = $state(false);

async function sendMessage(prompt: string) {
  isStreaming = true;
  const response = await fetch('/api/chat/stream', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ conversation_id: currentId, prompt })
  });

  const reader = response.body?.getReader();
  // Consume chunked SSE events (token, tool_call, artifact, done)
}
```

---

## 3. Chart & Artifact Rendering

- Plotly charts are dynamically hydrated using `plotly.js-dist-min` inside responsive container wrappers.
- Generated static file artifacts (CSV exports, PNG summaries) display preview cards with direct download triggers (`GET /api/artifacts/{id}`).

---

## 4. Legacy Web Application (`web-2`)
- **Status**: Retained for backward compatibility and reference testing.
- **Tech Stack**: Svelte 4, Vite, Vanilla CSS.
- **Recommendation**: New features should strictly target `apps/web`.
