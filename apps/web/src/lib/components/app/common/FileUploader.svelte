<script lang="ts">
	import { IconCloudUpload, IconFile, IconX } from '@tabler/icons-svelte';
	import ProgressIndicator from './ProgressIndicator.svelte';
	import Button from './Button.svelte';

	interface Props {
		accept?: string;
		multiple?: boolean;
		onupload?: (files: File[]) => void;
		class?: string;
	}

	let { accept, multiple = false, onupload, class: className = '' } = $props();

	let isDragging = $state(false);
	let files = $state<{ file: File; progress: number }[]>([]);
	let fileInput: HTMLInputElement;

	function handleDragEnter(e: DragEvent) {
		e.preventDefault();
		isDragging = true;
	}

	function handleDragLeave(e: DragEvent) {
		e.preventDefault();
		isDragging = false;
	}

	function handleDrop(e: DragEvent) {
		e.preventDefault();
		isDragging = false;

		if (e.dataTransfer?.files) {
			addFiles(Array.from(e.dataTransfer.files));
		}
	}

	function handleFileChange(e: Event) {
		const target = e.target as HTMLInputElement;
		if (target.files) {
			addFiles(Array.from(target.files));
		}
	}

	function addFiles(newFiles: File[]) {
		const toAdd = multiple ? newFiles : [newFiles[0]];
		files = [...files, ...toAdd.map((f) => ({ file: f, progress: 0 }))];
		simulateUpload();
	}

	function removeFile(index: number) {
		files = files.filter((_, i) => i !== index);
	}

	function simulateUpload() {
		files.forEach((f, i) => {
			if (f.progress === 100) return;

			let p = 0;
			const interval = setInterval(() => {
				p += Math.random() * 20;
				if (p >= 100) {
					p = 100;
					clearInterval(interval);

					// Check if all done
					if (files.every((file) => file.progress === 100)) {
						onupload?.(files.map((f) => f.file));
					}
				}

				files = files.map((file, idx) => (idx === i ? { ...file, progress: p } : file));
			}, 200);
		});
	}

	function formatSize(bytes: number) {
		if (bytes === 0) return '0 B';
		const k = 1024;
		const sizes = ['B', 'KB', 'MB', 'GB'];
		const i = Math.floor(Math.log(bytes) / Math.log(k));
		return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
	}
</script>

<div class="flex flex-col gap-4 {className}">
	<!-- svelte-ignore a11y_no_static_element_interactions -->
	<div
		class="border-2 border-dashed rounded-lg p-8 flex flex-col items-center justify-center text-center transition-colors cursor-pointer"
		class:border-accent={isDragging}
		class:bg-accent={isDragging}
		class:bg-opacity-5={isDragging}
		class:border-border={!isDragging}
		class:bg-surface={!isDragging}
		class:hover:border-muted={!isDragging}
		ondragenter={handleDragEnter}
		ondragover={handleDragEnter}
		ondragleave={handleDragLeave}
		ondrop={handleDrop}
		onclick={() => fileInput.click()}
		onkeydown={(e) => e.key === 'Enter' && fileInput.click()}
	>
		<input
			bind:this={fileInput}
			type="file"
			{accept}
			{multiple}
			class="hidden"
			onchange={handleFileChange}
		/>

		<div
			class="w-12 h-12 rounded-full bg-surface-elevated flex items-center justify-center text-muted mb-4 pointer-events-none"
		>
			<IconCloudUpload size={24} />
		</div>

		<p class="text-[13px] font-medium text-text-primary mb-1 pointer-events-none">
			Click to upload or drag and drop
		</p>
		<p class="text-[12px] text-text-secondary pointer-events-none">
			{accept ? `Supports ${accept}` : 'Any file type supported'}
		</p>
	</div>

	{#if files.length > 0}
		<div class="flex flex-col gap-2">
			{#each files as { file, progress }, i}
				<div class="bg-surface border border-border rounded-md p-3 flex items-center gap-3">
					<div class="text-muted shrink-0">
						<IconFile size={20} />
					</div>

					<div class="flex-1 min-w-0">
						<div class="flex justify-between items-center mb-1">
							<span class="text-[13px] font-medium text-text-primary truncate mr-2"
								>{file.name}</span
							>
							<span class="text-[11px] text-text-secondary shrink-0">{formatSize(file.size)}</span>
						</div>
						<ProgressIndicator
							value={progress}
							showValue={false}
							barClass={progress === 100 ? 'bg-success' : 'bg-accent'}
						/>
					</div>

					<button
						class="text-muted hover:text-danger transition-colors p-1 shrink-0"
						onclick={(e) => {
							e.stopPropagation();
							removeFile(i);
						}}
						aria-label="Remove file"
					>
						<IconX size={16} />
					</button>
				</div>
			{/each}
		</div>
	{/if}
</div>
