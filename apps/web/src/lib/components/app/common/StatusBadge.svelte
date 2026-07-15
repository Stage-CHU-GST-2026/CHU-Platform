<script lang="ts">
	import type { AgentStatus } from '$lib/types';
	import { IconLoader2 } from '@tabler/icons-svelte';

	interface Props {
		status: AgentStatus | 'draft' | 'ready' | 'indexed' | 'failed' | 'published';
		class?: string;
	}

	let { status, class: className = '' } = $props();

	const configs = {
		active: { label: 'Active', dotClass: 'bg-success', wrapperClass: 'bg-success/10 text-success' },
		idle: { label: 'Idle', dotClass: 'bg-muted', wrapperClass: 'bg-muted/10 text-muted' },
		error: { label: 'Error', dotClass: 'bg-danger', wrapperClass: 'bg-danger/10 text-danger' },
		failed: { label: 'Failed', dotClass: 'bg-danger', wrapperClass: 'bg-danger/10 text-danger' },
		processing: {
			label: 'Processing',
			icon: IconLoader2,
			wrapperClass: 'bg-warning/10 text-warning'
		},
		draft: { label: 'Draft', dotClass: 'bg-muted', wrapperClass: 'bg-muted/10 text-muted' },
		ready: { label: 'Ready', dotClass: 'bg-accent', wrapperClass: 'bg-accent/10 text-accent' },
		indexed: {
			label: 'Indexed',
			dotClass: 'bg-success',
			wrapperClass: 'bg-success/10 text-success'
		},
		published: {
			label: 'Published',
			dotClass: 'bg-accent',
			wrapperClass: 'bg-accent/10 text-accent'
		}
	};

	let config = $derived(configs[status as keyof typeof configs] || configs.idle);
</script>

<span
	class="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[11px] font-medium border border-current/20 {config.wrapperClass} {className}"
>
	{#if config.icon}
		<config.icon size={12} class="animate-spin" />
	{:else if config.dotClass}
		<span class="w-1.5 h-1.5 rounded-full {config.dotClass}"></span>
	{/if}
	{config.label}
</span>
