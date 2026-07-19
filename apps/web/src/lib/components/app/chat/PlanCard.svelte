<script lang="ts">
	import { IconClipboardList, IconChevronRight, IconCheck } from '@tabler/icons-svelte';
	import { app } from '$lib/state/app.svelte';
	import type { Artifact } from '$lib/api/chat';

	interface Props {
		planArtifact: Artifact;
		onproceed?: () => void;
	}

	let { planArtifact, onproceed = () => {} } = $props<Props>();

	function openPlan() {
		// Ensure the artifact is in activeArtifacts
		const exists = app.activeArtifacts.find((a) => a.id === planArtifact.id);
		if (!exists) {
			app.activeArtifacts = [...app.activeArtifacts, planArtifact];
		}

		if (!app.openArtifactTabs.includes(planArtifact.id)) {
			app.openArtifactTabs = [...app.openArtifactTabs, planArtifact.id];
		}
		app.activeArtifactTabId = planArtifact.id;
		app.artifactOpen = true;
	}
</script>

<div class="msg-row assistant my-2">
	<div class="w-full">
		<!-- Assistant meta styling -->
		<div class="msg-meta mb-2">
			<span>Project Manager Agent</span>
			<span>·</span>
			<span>done</span>
		</div>

		<!-- Matching the standard assistant bubble styles -->
		<div
			class="msg-bubble assistant !p-0 !max-w-[85%] overflow-hidden flex flex-col transition-shadow"
		>
			<div class="flex items-start gap-4 p-5">
				<div
					class="w-10 h-10 rounded-lg bg-surface-elevated border border-border flex items-center justify-center shrink-0 text-accent"
				>
					<IconClipboardList size={22} stroke={1.5} />
				</div>

				<div class="flex-1 flex flex-col pt-0.5">
					<h3 class="text-text-primary font-semibold text-[15px] mb-1 tracking-tight">
						{planArtifact.title || planArtifact.filename}
					</h3>
					<p class="text-text-secondary text-[14px] leading-relaxed mb-4 max-w-[95%]">
						{planArtifact.description ||
							'A detailed plan has been created. Review it and let me know if we should proceed.'}
					</p>

					<div class="flex items-center gap-3 self-start">
						<button class="btn btn-primary shadow-sm !text-white" onclick={onproceed}>
							<span>Proceed</span>
							<IconCheck size={16} stroke={2} />
						</button>

						<button onclick={openPlan} class="btn btn-secondary shadow-sm">
							<span>View Plan</span>
							<IconChevronRight size={16} stroke={2} />
						</button>
					</div>
				</div>
			</div>

			<div
				class="bg-surface px-5 py-2.5 border-t border-border-subtle flex items-center justify-between"
			>
				<span class="text-muted text-[12px] font-mono tracking-tight">{planArtifact.filename}</span>
				<span class="text-muted text-[12px]">{(planArtifact.file_size / 1024).toFixed(1)} KB</span>
			</div>
		</div>
	</div>
</div>
