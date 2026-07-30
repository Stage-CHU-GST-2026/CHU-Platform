<script lang="ts">
	import { onMount } from 'svelte';
	import Button from '$lib/components/app/common/Button.svelte';
	import {
		listSemanticCategories,
		createSemanticCategory,
		updateSemanticCategory,
		deleteSemanticCategory
	} from '$lib/api/semantic_categories';
	import type {
		SemanticCategory
	} from '$lib/api/semantic_categories';
	import {
		IconArrowLeft,
		IconPlus,
		IconPencil,
		IconTrash,
		IconRefresh,
		IconTag,
		IconCheck,
		IconX,
		IconInfoCircle,
		IconSearch,
		IconFilter,
		IconFolderCheck,
		IconClock,
		IconHash
	} from '@tabler/icons-svelte';

	let categories = $state<SemanticCategory[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);
	let successMsg = $state<string | null>(null);

	// Search & Filter State
	let searchQuery = $state('');

	// Create Modal / Form State
	let showCreateModal = $state(false);
	let isSubmitting = $state(false);
	let newCatName = $state('');
	let newCatLabel = $state('');
	let newCatColor = $state('#3b82f6');
	let newCatDesc = $state('');
	let newCatSort = $state(0);
	let formError = $state<string | null>(null);

	// Edit Modal / Form State
	let editingCat = $state<SemanticCategory | null>(null);
	let editCatLabel = $state('');
	let editCatColor = $state('#3b82f6');
	let editCatDesc = $state('');
	let editCatSort = $state(0);

	// Delete Modal State
	let deletingCat = $state<SemanticCategory | null>(null);
	let isDeleting = $state(false);

	// Preset color palette for category badges
	const PRESET_COLORS = [
		{ hex: '#3b82f6', label: 'Blue' },
		{ hex: '#10b981', label: 'Emerald' },
		{ hex: '#8b5cf6', label: 'Purple' },
		{ hex: '#f59e0b', label: 'Amber' },
		{ hex: '#ef4444', label: 'Red' },
		{ hex: '#ec4899', label: 'Pink' },
		{ hex: '#06b6d4', label: 'Cyan' },
		{ hex: '#6b7280', label: 'Gray' }
	];

	async function fetchCategories() {
		loading = true;
		error = null;
		try {
			categories = await listSemanticCategories();
		} catch (err: any) {
			error = err?.message || 'Failed to load semantic categories.';
		} finally {
			loading = false;
		}
	}

	onMount(() => {
		fetchCategories();
	});

	let filteredCategories = $derived.by(() => {
		if (!searchQuery.trim()) return categories;
		const q = searchQuery.toLowerCase();
		return categories.filter(
			(c) =>
				c.name.toLowerCase().includes(q) ||
				c.label.toLowerCase().includes(q) ||
				(c.description && c.description.toLowerCase().includes(q))
		);
	});

	function openCreateModal() {
		newCatName = '';
		newCatLabel = '';
		newCatColor = '#3b82f6';
		newCatDesc = '';
		newCatSort = categories.length * 10;
		formError = null;
		showCreateModal = true;
	}

	async function handleCreate() {
		if (!newCatName.trim() || !newCatLabel.trim()) {
			formError = 'Category key and display label are required.';
			return;
		}

		const keyPattern = /^[a-z0-9_-]+$/;
		if (!keyPattern.test(newCatName.trim())) {
			formError = 'Category key must contain only lowercase letters, numbers, hyphens, or underscores.';
			return;
		}

		isSubmitting = true;
		formError = null;

		try {
			const created = await createSemanticCategory({
				name: newCatName.trim().toLowerCase(),
				label: newCatLabel.trim(),
				color: newCatColor,
				description: newCatDesc.trim() || null,
				sort_order: newCatSort
			});
			showCreateModal = false;
			successMsg = `Category "${created.label}" created successfully.`;
			setTimeout(() => (successMsg = null), 3000);
			await fetchCategories();
		} catch (err: any) {
			formError = err?.message || 'Failed to create category.';
		} finally {
			isSubmitting = false;
		}
	}

	function openEditModal(cat: SemanticCategory) {
		editingCat = cat;
		editCatLabel = cat.label;
		editCatColor = cat.color || '#3b82f6';
		editCatDesc = cat.description || '';
		editCatSort = cat.sort_order;
		formError = null;
	}

	async function handleUpdate() {
		if (!editingCat) return;
		if (!editCatLabel.trim()) {
			formError = 'Display label is required.';
			return;
		}

		isSubmitting = true;
		formError = null;

		try {
			const updated = await updateSemanticCategory(editingCat.id, {
				label: editCatLabel.trim(),
				color: editCatColor,
				description: editCatDesc.trim() || null,
				sort_order: editCatSort
			});
			editingCat = null;
			successMsg = `Category "${updated.label}" updated successfully.`;
			setTimeout(() => (successMsg = null), 3000);
			await fetchCategories();
		} catch (err: any) {
			formError = err?.message || 'Failed to update category.';
		} finally {
			isSubmitting = false;
		}
	}

	async function handleDelete() {
		if (!deletingCat || isDeleting) return;
		isDeleting = true;

		try {
			await deleteSemanticCategory(deletingCat.id);
			const label = deletingCat.label;
			deletingCat = null;
			successMsg = `Category "${label}" deleted successfully.`;
			setTimeout(() => (successMsg = null), 3000);
			await fetchCategories();
		} catch (err: any) {
			alert(err?.message || 'Failed to delete category.');
		} finally {
			isDeleting = false;
		}
	}
</script>

<svelte:head>
	<title>Semantic Categories | CHU Platform</title>
	<meta name="description" content="Manage domain classification categories for dataset column concept mappings." />
</svelte:head>

<div class="w-full h-full p-6 md:p-8 flex flex-col space-y-6 overflow-y-auto">
	<!-- Top Navigation Breadcrumbs & Actions Header -->
	<div class="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-border pb-5">
		<div class="space-y-1">
			<a
				href="/dashboard/settings"
				class="inline-flex items-center gap-2 text-xs font-semibold text-text-secondary hover:text-text-primary transition-colors mb-1"
			>
				<IconArrowLeft size={16} />
				<span>Back to Settings</span>
			</a>
			<div class="flex items-center gap-3">
				<div class="p-2.5 rounded-lg bg-surface-elevated border border-border/80 text-accent">
					<IconTag size={24} />
				</div>
				<div>
					<h1 class="text-2xl md:text-3xl font-bold tracking-tight text-text-primary">
						Semantic Categories
					</h1>
					<p class="text-sm text-text-secondary mt-0.5">
						Manage domain classification buckets stored in the database for dataset column mapping.
					</p>
				</div>
			</div>
		</div>

		<div class="flex items-center gap-3 shrink-0">
			<button
				class="p-2.5 rounded border border-border bg-surface hover:bg-surface-hover text-text-secondary hover:text-text-primary transition-colors cursor-pointer"
				onclick={fetchCategories}
				disabled={loading}
				aria-label="Reload categories"
				title="Reload categories"
			>
				<IconRefresh size={18} class={loading ? 'animate-spin' : ''} />
			</button>

			<Button variant="primary" icon={IconPlus} onclick={openCreateModal}>
				Add Category
			</Button>
		</div>
	</div>

	<!-- High-level Metric Summary Cards Banner -->
	<div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
		<div class="bg-surface border border-border/80 rounded-xl p-4 flex items-center justify-between shadow-xs">
			<div class="space-y-1">
				<span class="text-xs font-semibold uppercase tracking-wider text-muted">Total Categories</span>
				<div class="text-2xl font-bold text-text-primary font-mono">{categories.length}</div>
			</div>
			<div class="p-3 rounded-lg bg-surface-elevated text-accent border border-border/60">
				<IconFolderCheck size={22} />
			</div>
		</div>

		<div class="bg-surface border border-border/80 rounded-xl p-4 flex items-center justify-between shadow-xs">
			<div class="space-y-1">
				<span class="text-xs font-semibold uppercase tracking-wider text-muted">Filtered Categories</span>
				<div class="text-2xl font-bold text-text-primary font-mono">{filteredCategories.length}</div>
			</div>
			<div class="p-3 rounded-lg bg-surface-elevated text-success border border-border/60">
				<IconFilter size={22} />
			</div>
		</div>

		<div class="bg-surface border border-border/80 rounded-xl p-4 flex items-center justify-between shadow-xs">
			<div class="space-y-1">
				<span class="text-xs font-semibold uppercase tracking-wider text-muted">System Storage</span>
				<div class="text-xs font-bold text-text-primary font-mono flex items-center gap-1 mt-1">
					<span class="w-2 h-2 rounded-full bg-success"></span>
					Postgres JSONB / ORM
				</div>
			</div>
			<div class="p-3 rounded-lg bg-surface-elevated text-warning border border-border/60">
				<IconHash size={22} />
			</div>
		</div>
	</div>

	<!-- Search & Action Toolbar -->
	<div class="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-4 bg-surface border border-border/80 rounded-xl p-4 shadow-xs">
		<div class="relative max-w-md w-full">
			<IconSearch size={16} class="absolute left-3.5 top-1/2 -translate-y-1/2 text-muted" />
			<input
				bind:value={searchQuery}
				type="text"
				placeholder="Filter categories by name, label, or description..."
				class="w-full pl-10 pr-4 py-2 bg-surface-elevated border border-border/60 rounded-lg text-sm text-text-primary placeholder:text-muted focus:outline-none focus:border-accent font-sans"
			/>
		</div>

		<div class="text-xs font-mono text-muted shrink-0 text-right">
			Showing {filteredCategories.length} of {categories.length} entries
		</div>
	</div>

	<!-- Alert Banners -->
	{#if successMsg}
		<div class="p-4 rounded-xl bg-success/10 border border-success/20 text-success text-sm font-medium flex items-center justify-between shadow-xs animate-in fade-in">
			<div class="flex items-center gap-2">
				<IconCheck size={18} />
				<span>{successMsg}</span>
			</div>
		</div>
	{/if}

	{#if error}
		<div class="p-4 rounded-xl bg-danger/10 border border-danger/20 text-danger text-sm font-medium flex items-center justify-between">
			<div class="flex items-center gap-2">
				<IconInfoCircle size={18} />
				<span>{error}</span>
			</div>
			<button class="underline text-xs font-semibold" onclick={fetchCategories}>Try Again</button>
		</div>
	{/if}

	<!-- Full-Width High Density Datatable -->
	<div class="w-full flex-1">
		{#if loading}
			<div class="h-64 border border-border rounded-xl p-8 flex flex-col items-center justify-center text-center bg-surface/30 space-y-3">
				<IconRefresh size={24} class="animate-spin text-accent" />
				<p class="text-sm font-mono text-muted">Loading domain categories from database…</p>
			</div>
		{:else if filteredCategories.length === 0}
			<div class="h-64 border border-dashed border-border rounded-xl p-8 flex flex-col items-center justify-center text-center bg-surface/30 space-y-3">
				<IconTag size={32} class="text-muted" />
				<p class="text-sm font-sans font-semibold text-text-primary">
					{searchQuery ? 'No categories matching filter' : 'No categories configured'}
				</p>
				<p class="text-xs text-muted max-w-sm">
					{searchQuery ? `No category found matching "${searchQuery}".` : 'Create domain categories to classify dataset columns.'}
				</p>
				<Button variant="primary" size="sm" icon={IconPlus} onclick={openCreateModal}>
					Add New Category
				</Button>
			</div>
		{:else}
			<div class="border border-border/80 rounded-xl overflow-hidden bg-surface w-full shadow-xs">
				<div class="overflow-x-auto max-h-[65vh]">
					<table class="w-full text-left text-sm border-collapse">
						<thead>
							<tr class="bg-surface-elevated text-xs text-text-secondary uppercase font-semibold tracking-wider border-b border-border/60 sticky top-0 z-10">
								<th class="px-6 py-4 bg-surface-elevated">Category Label & Color Badge</th>
								<th class="px-6 py-4 bg-surface-elevated">Key (DB Identifier)</th>
								<th class="px-6 py-4 bg-surface-elevated">Description</th>
								<th class="px-6 py-4 text-center bg-surface-elevated">Sort Order</th>
								<th class="px-6 py-4 text-right bg-surface-elevated">Actions</th>
							</tr>
						</thead>
						<tbody class="text-text-secondary">
							{#each filteredCategories as cat (cat.id)}
								<tr class="hover:bg-surface-hover/50 transition-colors">
									<!-- Badge & Label -->
									<td class="px-6 py-4">
										<div class="flex items-center gap-3">
											<span
												class="w-3.5 h-3.5 rounded-full shrink-0 shadow-xs ring-2 ring-surface-elevated"
												style="background-color: {cat.color || '#3b82f6'}"
											></span>
											<span class="font-bold text-text-primary text-sm font-sans">
												{cat.label}
											</span>
										</div>
									</td>

									<!-- Machine Key -->
									<td class="px-6 py-4 font-mono text-xs text-accent">
										<span class="px-2.5 py-1 rounded bg-surface-elevated border border-border/60 font-mono font-medium">
											{cat.name}
										</span>
									</td>

									<!-- Description -->
									<td class="px-6 py-4 text-xs text-text-secondary max-w-xl font-sans leading-relaxed">
										{cat.description || '—'}
									</td>

									<!-- Sort Order -->
									<td class="px-6 py-4 text-center font-mono text-xs font-semibold">
										<span class="px-2.5 py-1 rounded bg-surface-elevated border border-border/40">
											{cat.sort_order}
										</span>
									</td>

									<!-- Actions -->
									<td class="px-6 py-4 text-right">
										<div class="flex items-center justify-end gap-2">
											<button
												class="p-1.5 rounded-lg text-text-secondary hover:text-text-primary hover:bg-surface-elevated transition-colors cursor-pointer"
												onclick={() => openEditModal(cat)}
												aria-label="Edit category"
												title="Edit category"
											>
												<IconPencil size={16} />
											</button>
											<button
												class="p-1.5 rounded-lg text-muted hover:text-danger hover:bg-danger/10 transition-colors cursor-pointer"
												onclick={() => (deletingCat = cat)}
												aria-label="Delete category"
												title="Delete category"
											>
												<IconTrash size={16} />
											</button>
										</div>
									</td>
								</tr>
							{/each}
						</tbody>
					</table>
				</div>

				<!-- Datatable Footer Bar -->
				<div class="flex items-center justify-between text-xs font-mono text-muted px-6 py-3 bg-surface-elevated border-t border-border/60">
					<span>Showing {filteredCategories.length} categories</span>
					<span>Storage: Database table <code>semantic_categories</code></span>
				</div>
			</div>
		{/if}
	</div>
</div>

<!-- Create Category Modal -->
{#if showCreateModal}
	<div class="fixed inset-0 z-50 bg-black/60 backdrop-blur-xs flex items-center justify-center p-4">
		<div class="bg-surface border border-border rounded-xl p-6 max-w-md w-full shadow-2xl space-y-5 animate-in fade-in zoom-in-95">
			<div class="flex items-center justify-between border-b border-border pb-3">
				<h3 class="text-lg font-bold text-text-primary">Add Semantic Category</h3>
				<button
					class="p-1 rounded text-muted hover:text-text-primary hover:bg-surface-hover"
					onclick={() => (showCreateModal = false)}
				>
					<IconX size={18} />
				</button>
			</div>

			{#if formError}
				<div class="p-3 rounded bg-danger/10 border border-danger/20 text-danger text-xs">
					{formError}
				</div>
			{/if}

			<div class="space-y-4 text-sm">
				<div>
					<label class="block text-xs font-semibold text-text-secondary uppercase tracking-wider mb-1">
						Display Label *
					</label>
					<input
						bind:value={newCatLabel}
						type="text"
						placeholder="e.g. Genomics & Sequencing"
						class="w-full px-3 py-2 bg-surface-elevated border border-border/60 rounded-md text-text-primary focus:border-accent focus:outline-none"
					/>
				</div>

				<div>
					<label class="block text-xs font-semibold text-text-secondary uppercase tracking-wider mb-1">
						Machine Key (name) *
					</label>
					<input
						bind:value={newCatName}
						type="text"
						placeholder="e.g. genomics"
						class="w-full px-3 py-2 bg-surface-elevated border border-border/60 rounded-md font-mono text-text-primary focus:border-accent focus:outline-none"
					/>
					<p class="text-[11px] text-muted mt-1">Immutable unique key used in column metadata (lowercase, no spaces).</p>
				</div>

				<div>
					<label class="block text-xs font-semibold text-text-secondary uppercase tracking-wider mb-1">
						Badge Color
					</label>
					<div class="flex items-center gap-2">
						<input
							type="color"
							bind:value={newCatColor}
							class="w-9 h-9 p-0.5 rounded border border-border/60 bg-surface-elevated cursor-pointer"
						/>
						<div class="flex flex-wrap items-center gap-1.5">
							{#each PRESET_COLORS as preset}
								<button
									class="w-6 h-6 rounded-full border transition-transform hover:scale-110 cursor-pointer {newCatColor === preset.hex ? 'border-text-primary ring-2 ring-accent/50' : 'border-transparent'}"
									style="background-color: {preset.hex}"
									onclick={() => (newCatColor = preset.hex)}
									title={preset.label}
								></button>
							{/each}
						</div>
					</div>
				</div>

				<div>
					<label class="block text-xs font-semibold text-text-secondary uppercase tracking-wider mb-1">
						Description
					</label>
					<textarea
						bind:value={newCatDesc}
						rows={2}
						placeholder="Optional description of this domain category..."
						class="w-full px-3 py-2 bg-surface-elevated border border-border/60 rounded-md text-text-primary focus:border-accent focus:outline-none"
					></textarea>
				</div>

				<div>
					<label class="block text-xs font-semibold text-text-secondary uppercase tracking-wider mb-1">
						Sort Order
					</label>
					<input
						bind:value={newCatSort}
						type="number"
						class="w-full px-3 py-2 bg-surface-elevated border border-border/60 rounded-md text-text-primary focus:border-accent focus:outline-none font-mono"
					/>
				</div>
			</div>

			<div class="flex items-center justify-end gap-3 pt-2">
				<Button variant="secondary" onclick={() => (showCreateModal = false)} disabled={isSubmitting}>
					Cancel
				</Button>
				<Button variant="primary" onclick={handleCreate} loading={isSubmitting} disabled={isSubmitting}>
					Create Category
				</Button>
			</div>
		</div>
	</div>
{/if}

<!-- Edit Category Modal -->
{#if editingCat}
	<div class="fixed inset-0 z-50 bg-black/60 backdrop-blur-xs flex items-center justify-center p-4">
		<div class="bg-surface border border-border rounded-xl p-6 max-w-md w-full shadow-2xl space-y-5 animate-in fade-in zoom-in-95">
			<div class="flex items-center justify-between border-b border-border pb-3">
				<div>
					<h3 class="text-lg font-bold text-text-primary">Edit Category</h3>
					<span class="text-xs font-mono text-accent">Key: {editingCat.name}</span>
				</div>
				<button
					class="p-1 rounded text-muted hover:text-text-primary hover:bg-surface-hover"
					onclick={() => (editingCat = null)}
				>
					<IconX size={18} />
				</button>
			</div>

			{#if formError}
				<div class="p-3 rounded bg-danger/10 border border-danger/20 text-danger text-xs">
					{formError}
				</div>
			{/if}

			<div class="space-y-4 text-sm">
				<div>
					<label class="block text-xs font-semibold text-text-secondary uppercase tracking-wider mb-1">
						Display Label *
					</label>
					<input
						bind:value={editCatLabel}
						type="text"
						class="w-full px-3 py-2 bg-surface-elevated border border-border/60 rounded-md text-text-primary focus:border-accent focus:outline-none"
					/>
				</div>

				<div>
					<label class="block text-xs font-semibold text-text-secondary uppercase tracking-wider mb-1">
						Badge Color
					</label>
					<div class="flex items-center gap-2">
						<input
							type="color"
							bind:value={editCatColor}
							class="w-9 h-9 p-0.5 rounded border border-border/60 bg-surface-elevated cursor-pointer"
						/>
						<div class="flex flex-wrap items-center gap-1.5">
							{#each PRESET_COLORS as preset}
								<button
									class="w-6 h-6 rounded-full border transition-transform hover:scale-110 cursor-pointer {editCatColor === preset.hex ? 'border-text-primary ring-2 ring-accent/50' : 'border-transparent'}"
									style="background-color: {preset.hex}"
									onclick={() => (editCatColor = preset.hex)}
									title={preset.label}
								></button>
							{/each}
						</div>
					</div>
				</div>

				<div>
					<label class="block text-xs font-semibold text-text-secondary uppercase tracking-wider mb-1">
						Description
					</label>
					<textarea
						bind:value={editCatDesc}
						rows={2}
						class="w-full px-3 py-2 bg-surface-elevated border border-border/60 rounded-md text-text-primary focus:border-accent focus:outline-none"
					></textarea>
				</div>

				<div>
					<label class="block text-xs font-semibold text-text-secondary uppercase tracking-wider mb-1">
						Sort Order
					</label>
					<input
						bind:value={editCatSort}
						type="number"
						class="w-full px-3 py-2 bg-surface-elevated border border-border/60 rounded-md text-text-primary focus:border-accent focus:outline-none font-mono"
					/>
				</div>
			</div>

			<div class="flex items-center justify-end gap-3 pt-2">
				<Button variant="secondary" onclick={() => (editingCat = null)} disabled={isSubmitting}>
					Cancel
				</Button>
				<Button variant="primary" onclick={handleUpdate} loading={isSubmitting} disabled={isSubmitting}>
					Save Changes
				</Button>
			</div>
		</div>
	</div>
{/if}

<!-- Delete Confirmation Modal -->
{#if deletingCat}
	<div class="fixed inset-0 z-50 bg-black/60 backdrop-blur-xs flex items-center justify-center p-4">
		<div class="bg-surface border border-border rounded-xl p-6 max-w-md w-full shadow-2xl space-y-4">
			<div class="flex items-center justify-between border-b border-border pb-3">
				<h3 class="text-lg font-bold text-text-primary">Delete Category</h3>
				<button
					class="p-1 rounded text-muted hover:text-text-primary hover:bg-surface-hover"
					onclick={() => (deletingCat = null)}
				>
					<IconX size={18} />
				</button>
			</div>

			<p class="text-sm text-text-secondary">
				Are you sure you want to delete category <strong class="text-text-primary">"{deletingCat.label}"</strong> (<code class="text-accent font-mono text-xs">{deletingCat.name}</code>)?
			</p>

			<div class="flex items-center justify-end gap-3 pt-2">
				<Button variant="secondary" onclick={() => (deletingCat = null)} disabled={isDeleting}>
					Cancel
				</Button>
				<Button variant="danger" onclick={handleDelete} loading={isDeleting} disabled={isDeleting}>
					Delete Category
				</Button>
			</div>
		</div>
	</div>
{/if}
