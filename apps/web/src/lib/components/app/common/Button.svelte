<script lang="ts">
	import type { Snippet, Component } from 'svelte';
	import { IconLoader2 } from '@tabler/icons-svelte';

	interface Props {
		variant?: 'primary' | 'secondary' | 'ghost' | 'danger' | 'outline' | 'success';
		size?: 'sm' | 'md' | 'lg' | 'icon';
		type?: 'button' | 'submit' | 'reset';
		disabled?: boolean;
		loading?: boolean;
		class?: string;
		icon?: Component<any>;
		iconRight?: Component<any>;
		onclick?: (e: MouseEvent) => void;
		children?: Snippet;
		'aria-label'?: string;
	}

	let {
		variant = 'primary',
		size = 'md',
		type = 'button',
		disabled = false,
		loading = false,
		class: className = '',
		icon: Icon,
		iconRight: IconRight,
		onclick,
		children,
		'aria-label': ariaLabel
	} = $props();

	const variants = {
		primary: 'bg-accent text-white hover:bg-accent/90 active:bg-accent/95 shadow-sm border border-transparent',
		secondary: 'bg-surface-elevated text-text-primary border border-border/80 hover:bg-surface-hover hover:border-border',
		ghost: 'bg-transparent text-text-secondary hover:bg-surface-hover hover:text-text-primary border border-transparent',
		danger: 'bg-danger/15 text-danger border border-danger/30 hover:bg-danger/25 active:bg-danger/30',
		outline: 'bg-transparent border border-border text-text-primary hover:bg-surface-hover hover:border-text-secondary',
		success: 'bg-success/15 text-success border border-success/30 hover:bg-success/25'
	};

	const sizes = {
		sm: 'py-2 px-3.5 text-xs font-semibold rounded-md gap-2',
		md: 'py-2.5 px-5 text-sm font-semibold rounded-lg gap-2.5',
		lg: 'py-3.5 px-7 text-base font-bold rounded-xl gap-3',
		icon: 'h-10 w-10 p-0 flex justify-center items-center rounded-lg'
	};

	let iconSize = $derived(size === 'sm' ? 16 : size === 'lg' ? 20 : 18);
</script>

<button
	{type}
	class="inline-flex items-center justify-center whitespace-nowrap cursor-pointer select-none transition-all duration-150 ease-out active:scale-[0.98] disabled:opacity-40 disabled:cursor-not-allowed disabled:pointer-events-none shrink-0 {variants[
		variant
	]} {sizes[size]} {className}"
	disabled={disabled || loading}
	{onclick}
	aria-label={ariaLabel}
>
	{#if loading}
		<IconLoader2 class="animate-spin shrink-0" size={iconSize} />
	{:else if Icon}
		<Icon class="shrink-0" size={iconSize} />
	{/if}

	{#if children}
		<span class="inline-flex items-center justify-center gap-2 whitespace-nowrap {loading && size === 'icon' ? 'opacity-0' : ''}">
			{@render children()}
		</span>
	{/if}

	{#if IconRight && !loading}
		<IconRight class="shrink-0" size={iconSize} />
	{/if}
</button>
