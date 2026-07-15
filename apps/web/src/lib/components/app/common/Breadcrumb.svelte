<script lang="ts">
	import { IconChevronRight } from '@tabler/icons-svelte';

	export interface BreadcrumbItem {
		label: string;
		href?: string;
	}

	interface Props {
		items: BreadcrumbItem[];
		class?: string;
	}

	let { items, class: className = '' } = $props();
</script>

<nav aria-label="Breadcrumb" class={className}>
	<ol class="flex items-center text-[13px]">
		{#each items as item, i}
			<li class="flex items-center">
				{#if item.href && i < items.length - 1}
					<a
						href={item.href}
						class="text-text-secondary hover:text-text-primary transition-colors rounded-sm"
					>
						{item.label}
					</a>
				{:else}
					<span class="text-text-primary font-medium" aria-current="page">
						{item.label}
					</span>
				{/if}

				{#if i < items.length - 1}
					<IconChevronRight size={14} class="mx-1 text-muted" />
				{/if}
			</li>
		{/each}
	</ol>
</nav>
