# Frontend Enhancement Plan — CHU Platform

**Audit date: 2026-07-21 · Branch: `feature/planing-frontend`**

---

## Executive Summary

The CHU Platform frontend is a **SvelteKit 5 + Tailwind CSS 4** application with a well-articulated dark-first design philosophy, a comprehensive design system document (`apps/ui/design-system.html`), and ~40 custom components. The visual language favours data clarity — true black sidebar, near-black canvases, restrained use of accent colour. CSS custom properties, a Tailwind v4 `@theme` block, type scale, spacing rhythm, and light/dark mode support are all in place.

However, an audit reveals **significant distance between the documented design system and its implementation in code**. The design system document describes a green accent (#1DB954), while the live CSS uses a muted blue (#0a66c2). Several components use hardcoded values where theme tokens exist. Legacy patterns (`button.css` `@layer components`, duplicate state directories) sit alongside modern patterns (Svelte 5 runes, Tailwind v4 `@theme`). No test infrastructure exists.

This plan is organised into **seven phases**, ordered by dependency. Each phase delivers independently reviewable value; earlier phases unblock later ones.

---

## Phase 0 — Design Token Consolidation & Colour Resolution

**Severity: Critical** · **Effort: 1–2 days** · **Depends on: Nothing**

### Problem

The design-system.html and live CSS define incompatible colour systems:

| Token | Design System Doc | Live CSS (layout.css) |
|---|---|---|
| Primary accent | #1DB954 (green) | #0a66c2 (blue) |
| Focus ring colour | #1DB954 (inferred) | #0a66c2 (blue) |
| `--color-blue` / `--blue` | #1DB954 (green labelled blue) | #0a66c2 (actual blue) |

The design doc calls the accent `--blue: #1DB954` — a green hue used as the product's primary action colour. The live CSS uses `--color-blue: #0a66c2` — a genuine blue. The live app does not match the documented design intent.

Additionally, the design doc defines `--space-7` (48px) and `--space-9` (96px) in its spacing scale, but these are missing from the `@theme` block in `layout.css`.

### Resolution

1. **Resolve the accent colour.** Choose one: adopt the design doc's green (#1DB954 → `--color-accent`) as the product accent, or update the design doc to reflect the current blue. **Recommendation:** adopt the green — it has better contrast against dark backgrounds, it is distinct from the AI-indigo (#8D87FF), and it differentiates from every other analytics tool's blue.

2. **Normalise naming.** All accent tokens live under `--color-accent`. Rename `--color-blue` to `--color-accent` in `layout.css`. Keep `--color-blue` as a deprecated alias for backward compatibility.

3. **Add missing spacing tokens.** Add `--spacing-7: 48px` and `--spacing-9: 96px` to the `@theme` block.

4. **Extract a canonical token file.** Move token definitions from `layout.css` to `src/lib/css/tokens.css`. Import it from `layout.css`. This makes the token file importable by tests, the design-system doc, and future build tools.

---

## Phase 1 — Legacy Extirpation

**Severity: High** · **Effort: 2–3 days** · **Depends on: Phase 0**

### Problems

1. **`button.css` uses Tailwind v3 `@layer components`**, while the project runs Tailwind v4. The `Button.svelte` component already uses Tailwind utility classes directly (correct for v4). The `@layer components` layer is silently ignored by Tailwind v4, making `button.css` dead code.

2. **Duplicate state directory.** `src/lib/state/` (Svelte 5 rune-based classes) and `src/lib/stores/` (legacy stores) coexist. The legacy `conversations.ts` store is referenced by Sidebar.svelte via `$conversationRefreshTick`.

3. **Duplicate API client.** `src/lib/api/chat.ts` (active) and `src/lib/services/chat.ts` (unused) both exist.

4. **Legacy routes** `(legacy)/legacy/` occupy a parallel route group with their own layout.

### Resolution

1. **Delete `button.css`.** Verify all button styles in `Button.svelte` cover the required variants. If any class from `button.css` is still used outside `Button.svelte`, inline the Tailwind utilities.

2. **Consolidate state.** Migrate the legacy `conversationRefreshTick` store into `conversations.svelte.ts` as a Svelte 5 rune. Delete `src/lib/stores/`.

3. **Delete `src/lib/services/chat.ts`.** Update any remaining imports.

4. **Archive legacy routes.** Move `(legacy)/` content into `_archive/legacy-routes/` for reference, or delete if confirmed unused by real users.

---

## Phase 2 — Design System Fidelity Pass

**Severity: High** · **Effort: 4–5 days** · **Depends on: Phase 0**

### Components That Diverge from the Design System

1. **TopBar.svelte uses hardcoded colors:**
   - `bg-[#0a0a0a]` → should reference `bg-surface-elevated`
   - `border-[#1f1f1f]` → should be `border-border`
   - `text-gray-400` / `text-gray-600` → should reference theme text tokens
   - The "Artifacts" toggle uses `bg-[#141414]` and `bg-[#2a2a2a]` — direct hex values

2. **ChatComposer radius mismatch:**
   - Design doc specifies `--radius-sm: 8px` for input containers
   - ChatComposer uses `rounded-[14px]` — an undocumented radius
   - **Fix:** use `rounded-radius-sm` (8px) or `rounded-radius-md` (12px)

3. **Gradient headline on dashboard pages:**
   - The hero headline uses `bg-gradient-to-br from-text-primary via-text-primary to-text-secondary bg-clip-text text-transparent`
   - Gradient headlines are a recognised AI-generated-UX tell
   - **Fix:** solid ink, weight-only heading (font-weight 900, tighter tracking)

4. **Primary button hover shifts from blue to green:**
   - Resting: `bg-accent` → resolves to #0a66c2 (blue)
   - Hover: `hover:bg-[#1ED760]` → bright green
   - The button changes semantic colour on hover — disorienting
   - **Fix:** hover should lighten or desaturate the accent (e.g., `filter: brightness(1.15)`), not shift to a different hue

5. **Spacing audit:**
   - The design doc specifies an 8pt rhythm: 4, 8, 12, 16, 20, 24, 32, 40, 48, 64, 96px
   - Components use arbitrary values like `py-[10px]` (10px — not in the scale)
   - Audit all padding/margin values against the documented scale

6. **Animation values:**
   - Design doc: `--transition-base: 150ms cubic-bezier(0.4, 0, 0.2, 1)`
   - Button.svelte uses `duration-150 ease-out` — close but `ease-out` maps to `cubic-bezier(0, 0, 0.2, 1)`, which differs from the design token
   - **Fix:** reference `var(--transition-base)` or register the exact easing as a Tailwind utility

7. **Missing `--space-7` (48px) and `--space-9` (96px):**
   - Referenced in the backward-compatible `:root` aliases in layout.css
   - But missing from the `@theme` block, so cannot be used via Tailwind spacing utilities

### Implementation

For each component in `src/lib/components/app/`, audit:
- All colour values reference theme tokens (`var(--color-*)` or Tailwind theme classes)
- All radii reference the documented scale
- All spacing values adhere to the 8pt rhythm
- All typography uses the documented type scale
- All animation durations/easings use the transition tokens

---

## Phase 3 — Component Library Maturation

**Severity: Medium** · **Effort: 5–7 days** · **Depends on: Phase 2**

### Missing Components

| Component | Priority | Justification |
|---|---|---|
| **Select** (`Select.svelte`) | High | Native `<select>` used in design doc but no styled component exists. Needed for settings and filter bars. |
| **Switch/Toggle** (`Switch.svelte`) | High | Referenced in design patterns. Needed for settings toggles. |
| **Accordion** (`Accordion.svelte`) | Medium | Would simplify settings sidebar and dataset column details. |
| **FormField** (`FormField.svelte`) | Medium | Wraps label + input + error + hint consistently. Currently hand-built in each form. |
| **Combobox** (`Combobox.svelte`) | Medium | Required for dataset picker and model selector. |
| **NotificationBanner** (`NotificationBanner.svelte`) | Low | For system-level alerts (API down, maintenance mode). |

### Component Quality Standards

Every interactive component must implement **8 states**:
- default · hover · `:focus-visible` · `:active` · disabled · loading · error · success

For the existing `Button.svelte`:
- **Error state:** missing. A button that triggers a failed action should show an error appearance while keeping the action available.
- **Success state:** missing. A brief success appearance after a save/submit completes.

### Component Documentation

Create a `COMPONENTS.md` in `apps/web/` that catalogs:
- Component name and file path
- Props interface
- Accepted variants/sizes
- Current state coverage
- Known gaps

---

## Phase 4 — Accessibility & Responsive Audit

**Severity: High** · **Effort: 3–4 days** · **Depends on: Phase 2**

### Accessibility

Current state: some `aria-*` attributes exist (Dialog, Dropdown, Tabs, Sidebar). No systematic coverage.

1. **Keyboard navigation audit:**
   - Chat composer: Enter sends, Shift+Enter newline — correct.
   - Execution plan: steps are buttons with `onclick` but no keyboard-documented shortcut.
   - All interactive elements need visible focus rings (partially done via `:focus-visible` in layout.css).

2. **Colour contrast audit:**
   - `--color-muted: #6A6A6A` on `--color-bg: #121212` → contrast ratio ~4.2:1 (passes WCAG AA for text > 18px, fails AA for normal text)
   - Caption text (12px) at this contrast would fail WCAG AA
   - **Fix:** lighten `--color-muted` to ~#888888 for dark mode (~5.5:1 on #121212)

3. **Screen reader audit:**
   - Streaming chat messages need `aria-live="polite"` regions
   - Toast notifications need `role="status"` and `aria-live="assertive"`
   - The Command Palette should have `role="combobox"` with proper `aria-activedescendant`

4. **Reduced motion:**
   - Already partially supported via `prefers-reduced-motion: reduce` in design-system.html
   - Not yet ported to the app's actual `layout.css`
   - **Fix:** add the `prefers-reduced-motion` media query to `layout.css`

### Responsive

1. **Sidebar:** currently 260px fixed width. On mobile (< 768px), collapse into a drawer with a hamburger trigger.
2. **Conversation pages:** `max-w-[1024px]` constraint works well. Verify at 320px:
   - Chat bubbles widen to `max-w-[88%]` (vs current `max-w-[72%]`)
   - Composer expands to full width
   - Model selector replaced with an inline select
3. **Settings page:** already responsive (`grid-cols-1 md:grid-cols-[220px_1fr]`). Verify on 375px.
4. **DatasetTable:** add `overflow-x-auto` wrapper.

---

## Phase 5 — Performance & Architecture

**Severity: Medium** · **Effort: 4–5 days** · **Depends on: Phase 0, Phase 1**

### Performance

1. **Markdown rendering on server:**
   - `ChatBubble.svelte` and `ExecutionPlan.svelte` both import `marked` and `DOMPurify` dynamically in the browser
   - For initial page load (conversation history), pre-render markdown on the server and pass HTML to the client
   - Use `marked` only for live streaming tokens client-side

2. **Bundle optimisation:**
   - Tabler Icons are imported individually — correct pattern. Verify no barrel imports.
   - `marked` (~35 KB) and `DOMPurify` (~25 KB) are significant. Dynamic import pattern (`import('dompurify')`) is correct — verify consistent usage.
   - SvelteKit's filesystem routing already handles route-based code splitting. Verify in the build output.

### Architecture

1. **API layer consolidation:**
   - Extract shared API types to `src/lib/api/types.ts`
   - Create `src/lib/api/datasets.ts`, `src/lib/api/agents.ts` as the codebase grows

2. **State pattern standardisation:**
   - All state files use the Svelte 5 class-with-runes pattern — this is correct and should be the single convention
   - Remove the `touch()` workaround in conversation page; use Svelte 5 proxied arrays properly

3. **Error boundary:**
   - Create `+error.svelte` at the root layout level
   - Optionally add an `<ErrorBoundary>` wrapper component for per-section error catching

4. **Settings persistence:**
   - The `SettingsState.save()` method uses a mock `setTimeout`. Wire it to an actual API endpoint.

---

## Phase 6 — New Pages & Features

**Severity: Low–Medium** · **Effort: 5–8 days per page** · **Depends on: Phase 2, Phase 3**

The type definitions and legacy routes reference pages that do not yet exist in the new dashboard:

| Page | Route | Key Components |
|---|---|---|
| Dataset Library | `/dashboard/datasets` | `DatasetTable`, `FileUploader`, new `Select` |
| Knowledge Base | `/dashboard/knowledge` | `KnowledgeCard`, new search/filter patterns |
| Reports | `/dashboard/reports` | `ReportCard`, pagination |
| Agent Hub | `/dashboard/agents` | `AgentCard`, `StatusBadge` |
| Data Explorer | `/dashboard/explorer` | `PaneGroup`, `DatasetTable`, charts |
| 404 Page | no match | Branded not-found, consistent with dark-first system |

Each page follows the pattern established by existing dashboard pages: `PageHeader` → content → standardised loading/empty/error states.

---

## Phase 7 — Testing Infrastructure

**Severity: Medium** · **Effort: 3–4 days** · **Depends on: Phase 2, Phase 3**

No testing framework is currently configured. This is a blocking gap for any refactoring work.

1. **Add Vitest** (`vitest`, `@sveltejs/vite-plugin-svelte` for component testing)
2. **Write tests for core components** (Button, Dialog, Input, Tabs — the most-used UI primitives)
3. **Write tests for the SSE parser** (the most complex client-side logic)
4. **Set up accessibility assertions** (vitest-axe or similar)
5. **Add a `test` script** to `package.json`

---

## Implementation Roadmap

```
Week 1 ── Phase 0 (Token consolidation)               [1–2 days]
           Phase 1 (Legacy removal)                    [2–3 days]
Week 2 ── Phase 2 (Design fidelity pass)               [4–5 days]
Week 3 ── Phase 3 (Component library maturation)       [5–7 days]
Week 4 ── Phase 4 (Accessibility + responsive)         [3–4 days]
           Phase 5 (Performance + architecture)        [4–5 days]
Week 5   Phase 6 (New pages)                            [per page]
          + Phase 7 (Testing infrastructure)           [3–4 days]
```

**Phases 0–2 are prerequisite** before any new feature work. The colour token inconsistency affects every component and every new page — resolving it early prevents compounding technical debt.

---

## Key Audit Findings Summary

### What passes (38 design quality gates)
- Dark-first philosophy consistently applied ✓
- Inter + JetBrains Mono type pairing ✓
- 8pt spacing rhythm (mostly) ✓
- Motion: purposeful, no decorative bounce ✓
- `:focus-visible` rings defined ✓
- Border-first elevation hierarchy ✓
- Components use aria attributes selectively ✓
- Toast system with role="alert" ✓
- Skeleton loading with aria-hidden ✓

### What needs attention (20 gates)
| Area | Issue | Fix |
|---|---|---|
| Colour | Green accent in design doc, blue accent in live CSS | Resolve to one |
| Gradient headline | Dashboard hero uses `bg-clip-text text-transparent` | Solid ink, weight-only |
| Button hover | Resting blue → hover green (semantic colour shift) | Brightness shift only |
| Hardcoded colors | TopBar uses `#0a0a0a`, `#1f1f1f`, `#262626` directly | Reference theme tokens |
| Undocumented radius | ChatComposer `rounded-[14px]` | Use `rounded-radius-md` |
| Muted contrast | #6A6A6A fails WCAG AA for small text | Lighten to ~#888888 |
| Reduced motion | Media query exists in design doc, not in app CSS | Port to layout.css |
| Missing `--space-7`, `--space-9` | Missing from `@theme` block | Add both |
| Legacy button.css | Tailwind v3 pattern on Tailwind v4 | Delete, verify Button.svelte |

---

*Audit methodology: Hallmark 58-gate slop test combined with the CHU Platform's own six design principles (Data is the hero, White space is functional, Motion is purposeful, Typography first, Color is information, Borders before shadows). Each component in `src/lib/components/app/`, each route in `src/routes/`, and each CSS/token file was reviewed against both frameworks.*
