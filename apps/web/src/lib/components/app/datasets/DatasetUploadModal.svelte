<script lang="ts">
	import { uploadDataset } from '$lib/api/datasets';
	import type { DatasetUploadResponse } from '$lib/api/datasets';
	import { clickOutside, trapFocus } from '../common/actions';
	import { IconX, IconRefresh } from '@tabler/icons-svelte';

	let { open = $bindable(false), onUploaded }: { open: boolean; onUploaded?: (res: DatasetUploadResponse) => void } = $props();

	let isDragging = $state(false);
	let selectedFile = $state<File | null>(null);
	let isUploading = $state(false);
	let error = $state<string | null>(null);
	let successMsg = $state<string | null>(null);
	let fileInputRef: HTMLInputElement;

	const ALLOWED_EXTENSIONS = ['.csv', '.tsv', '.xlsx', '.xls', '.parquet', '.json', '.feather'];
	const MAX_SIZE_MB = 500;

	function close() {
		if (isUploading) return;
		open = false;
		reset();
	}

	function reset() {
		selectedFile = null;
		error = null;
		successMsg = null;
		isUploading = false;
		if (fileInputRef) fileInputRef.value = '';
	}

	function validateFile(file: File): boolean {
		error = null;
		const ext = '.' + file.name.split('.').pop()?.toLowerCase();
		if (!ALLOWED_EXTENSIONS.includes(ext)) {
			error = `Unsupported file type '${ext}'. Allowed formats: ${ALLOWED_EXTENSIONS.join(', ')}`;
			return false;
		}

		if (file.size > MAX_SIZE_MB * 1024 * 1024) {
			error = `File size exceeds ${MAX_SIZE_MB} MB limit. File is ${(file.size / (1024 * 1024)).toFixed(1)} MB.`;
			return false;
		}

		return true;
	}

	function handleFileSelect(e: Event) {
		const target = e.target as HTMLInputElement;
		if (target.files && target.files[0]) {
			const file = target.files[0];
			if (validateFile(file)) {
				selectedFile = file;
			}
		}
	}

	function handleDrop(e: DragEvent) {
		e.preventDefault();
		isDragging = false;
		if (e.dataTransfer?.files && e.dataTransfer.files[0]) {
			const file = e.dataTransfer.files[0];
			if (validateFile(file)) {
				selectedFile = file;
			}
		}
	}

	function handleDragOver(e: DragEvent) {
		e.preventDefault();
		isDragging = true;
	}

	function handleDragLeave(e: DragEvent) {
		e.preventDefault();
		isDragging = false;
	}

	async function startUpload() {
		if (!selectedFile || isUploading) return;
		isUploading = true;
		error = null;
		successMsg = null;

		try {
			const response = await uploadDataset(selectedFile);
			successMsg = response.message || 'File uploaded successfully — processing in background.';
			onUploaded?.(response);
			setTimeout(() => {
				close();
			}, 1000);
		} catch (err: any) {
			error = err?.message || 'Failed to upload dataset. Please try again.';
		} finally {
			isUploading = false;
		}
	}

	function formatBytes(bytes: number): string {
		if (bytes === 0) return '0 B';
		const k = 1024;
		const sizes = ['B', 'KB', 'MB', 'GB'];
		const i = Math.floor(Math.log(bytes) / Math.log(k));
		const val = (bytes / Math.pow(k, i)).toFixed(1);
		return val + ' ' + sizes[i];
	}

	function handleKeydown(e: KeyboardEvent) {
		if (open && e.key === 'Escape' && !isUploading) {
			close();
		}
	}
</script>

<svelte:window onkeydown={handleKeydown} />

{#if open}
	<div
		class="fixed inset-0 z-[var(--z-modal)] bg-black/60 backdrop-blur-xs flex items-center justify-center p-4 animate-in fade-in duration-150"
		role="presentation"
	>
		<div
			class="bg-surface border border-border rounded-lg shadow-xl w-full max-w-xl min-h-[520px] max-h-[85vh] flex flex-col overflow-hidden animate-in zoom-in-95 duration-150"
			role="dialog"
			aria-modal="true"
			aria-labelledby="upload-modal-title"
			use:clickOutside={close}
			use:trapFocus={open}
			tabindex="-1"
		>
			<!-- Header with Icon-Only Close Button -->
			<div class="flex items-center justify-between px-6 py-5 border-b border-border bg-surface-elevated shrink-0">
				<div>
					<h3 id="upload-modal-title" class="text-base font-semibold text-text-primary">
						Upload Dataset
					</h3>
					<p class="text-sm text-muted mt-0.5">Maximum file size: 500 MB</p>
				</div>

				<button
					class="p-1.5 rounded text-muted hover:text-text-primary hover:bg-surface-hover transition-colors cursor-pointer"
					onclick={close}
					disabled={isUploading}
					aria-label="Close dialog"
					title="Close"
				>
					<IconX size={20} />
				</button>
			</div>

			<!-- Body with Taller Spacing and Taller Dropzone -->
			<div class="p-6 flex-1 flex flex-col gap-5 overflow-y-auto">
				{#if error}
					<div class="p-4 rounded-md bg-danger/10 border border-danger/20 text-danger text-sm font-medium shrink-0">
						{error}
					</div>
				{/if}

				{#if successMsg}
					<div class="p-4 rounded-md bg-success/10 border border-success/20 text-success text-sm font-medium shrink-0">
						{successMsg}
					</div>
				{/if}

				<!-- Taller Dropzone area -->
				<div
					class="border border-dashed rounded-lg flex-1 min-h-[260px] p-8 flex flex-col items-center justify-center text-center transition-all cursor-pointer {isDragging
						? 'border-accent bg-accent/5'
						: selectedFile
							? 'border-success/60 bg-success/5'
							: 'border-border hover:border-text-secondary hover:bg-surface-hover/30'}"
					onaria-droptarget={handleDrop}
					ondragover={handleDragOver}
					ondragleave={handleDragLeave}
					ondrop={handleDrop}
					onclick={() => !isUploading && fileInputRef?.click()}
					role="button"
					tabindex="0"
					onkeydown={(e) => (e.key === 'Enter' || e.key === ' ') && !isUploading && fileInputRef?.click()}
				>
					<input
						bind:this={fileInputRef}
						type="file"
						accept={ALLOWED_EXTENSIONS.join(',')}
						class="hidden"
						onchange={handleFileSelect}
						disabled={isUploading}
					/>

					{#if selectedFile}
						<span class="text-sm font-mono font-semibold text-text-primary max-w-full truncate px-4">
							{selectedFile.name}
						</span>
						<span class="text-xs font-mono text-muted mt-1.5">
							{formatBytes(selectedFile.size)}
						</span>
						<button
							type="button"
							class="mt-4 text-sm text-accent hover:underline font-semibold"
							onclick={(e) => {
								e.stopPropagation();
								reset();
							}}
							disabled={isUploading}
						>
							Select different file
						</button>
					{:else}
						<p class="text-base font-medium text-text-primary">
							Drag and drop dataset file here, or <span class="text-accent underline font-semibold">browse</span>
						</p>
						<p class="text-xs text-muted mt-2">
							Accepted formats: CSV, TSV, XLSX, XLS, Parquet, JSON, Feather
						</p>
					{/if}
				</div>

				<!-- Formats list -->
				<div class="flex flex-wrap items-center gap-2 pt-1 shrink-0">
					<span class="text-xs text-muted font-mono font-medium mr-1">Formats:</span>
					{#each ALLOWED_EXTENSIONS as ext}
						<span class="text-xs font-mono font-semibold px-2.5 py-1 rounded bg-surface-elevated border border-border text-text-secondary">
							{ext}
						</span>
					{/each}
				</div>
			</div>

			<!-- Footer -->
			<div class="px-6 py-4 bg-surface-elevated border-t border-border flex items-center justify-end gap-3 shrink-0">
				<button
					type="button"
					class="px-4 py-2 rounded border border-border text-sm font-medium text-text-secondary hover:text-text-primary hover:bg-surface-hover transition-colors cursor-pointer"
					onclick={close}
					disabled={isUploading}
				>
					Cancel
				</button>

				<button
					type="button"
					class="px-5 py-2 rounded bg-accent text-white hover:bg-accent-hover text-sm font-semibold shadow-xs transition-colors cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
					onclick={startUpload}
					disabled={!selectedFile || isUploading}
				>
					{isUploading ? 'Uploading…' : 'Upload & Process'}
				</button>
			</div>
		</div>
	</div>
{/if}
