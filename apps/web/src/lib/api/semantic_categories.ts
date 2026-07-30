/**
 * Semantic Categories API client — interfaces and functions for managing
 * domain category definitions stored in the database.
 * Base route: /api/v1/semantic-categories
 */

const API_BASE = "/api/v1";

// ── Types ─────────────────────────────────────────────────────────────

export interface SemanticCategory {
    id: string;
    name: string;
    label: string;
    color: string | null;
    description: string | null;
    sort_order: number;
    created_at: string;
    updated_at: string;
}

export interface SemanticCategoryCreate {
    /** Short machine-friendly key — lowercase letters, digits, underscores and hyphens only. */
    name: string;
    label: string;
    color?: string | null;
    description?: string | null;
    sort_order?: number;
}

export interface SemanticCategoryUpdate {
    label?: string | null;
    color?: string | null;
    description?: string | null;
    sort_order?: number | null;
}

// ── Fetch helpers ─────────────────────────────────────────────────────

async function handleResponse<T>(res: Response, context: string): Promise<T> {
    if (!res.ok) {
        let detail = `${context}: HTTP ${res.status}`;
        try {
            const err = await res.json();
            if (err.detail) detail = err.detail;
        } catch {}
        throw new Error(detail);
    }
    return res.json();
}

// ── API Functions ─────────────────────────────────────────────────────

/**
 * List all semantic categories, ordered by sort_order then name.
 */
export async function listSemanticCategories(): Promise<SemanticCategory[]> {
    const res = await fetch(`${API_BASE}/semantic-categories`);
    return handleResponse(res, "Failed to load semantic categories");
}

/**
 * Get a single semantic category by ID.
 */
export async function getSemanticCategory(id: string): Promise<SemanticCategory> {
    const res = await fetch(`${API_BASE}/semantic-categories/${encodeURIComponent(id)}`);
    return handleResponse(res, "Failed to load semantic category");
}

/**
 * Create a new semantic category.
 */
export async function createSemanticCategory(
    payload: SemanticCategoryCreate
): Promise<SemanticCategory> {
    const res = await fetch(`${API_BASE}/semantic-categories`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
    });
    return handleResponse(res, "Failed to create semantic category");
}

/**
 * Partially update a semantic category (PATCH semantics — only included
 * fields are changed). Note: the `name` field cannot be changed after creation.
 */
export async function updateSemanticCategory(
    id: string,
    payload: SemanticCategoryUpdate
): Promise<SemanticCategory> {
    const res = await fetch(`${API_BASE}/semantic-categories/${encodeURIComponent(id)}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
    });
    return handleResponse(res, "Failed to update semantic category");
}

/**
 * Delete a semantic category by ID.
 * Note: existing mappings referencing this category's name are not automatically
 * updated — reassign those rows before deleting.
 */
export async function deleteSemanticCategory(id: string): Promise<void> {
    const res = await fetch(`${API_BASE}/semantic-categories/${encodeURIComponent(id)}`, {
        method: "DELETE",
    });
    if (!res.ok) {
        let detail = `Failed to delete semantic category: HTTP ${res.status}`;
        try {
            const err = await res.json();
            if (err.detail) detail = err.detail;
        } catch {}
        throw new Error(detail);
    }
}
