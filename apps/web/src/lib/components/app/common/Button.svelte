<script lang="ts">
	import type { Snippet, Component } from 'svelte';
	import { IconLoader2 } from '@tabler/icons-svelte';

	interface Props {
		variant?: 'primary' | 'secondary' | 'ghost' | 'danger' | 'outline';
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
		primary: 'bg-accent text-white hover:brightness-110 active:brightness-90',
		secondary: 'bg-surface-elevated text-text-primary border border-border hover:bg-surface-hover',
		ghost: 'bg-transparent text-text-secondary hover:text-text-primary hover:bg-surface-hover',
		danger: 'bg-danger text-white hover:brightness-110 active:brightness-90',
		outline: 'bg-transparent border border-border text-text-primary hover:bg-surface-hover'
	};

	const sizes = {
		sm: 'h-8 px-3 text-[12px]',
		md: 'h-9 px-4 text-[13px]',
		lg: 'h-11 px-6 text-[14px]',
		icon: 'h-9 w-9 p-0 flex justify-center'
	};
</script>

<button
	{type}
	class="inline-flex items-center justify-center font-medium transition-all rounded-md active:scale-[0.98] disabled:pointer-events-none disabled:opacity-50 {variants[
		variant
	]} {sizes[size]} {className}"
	{disabled}
	{onclick}
	aria-label={ariaLabel}
>
	{#if loading}
		<IconLoader2 class="animate-spin {children ? 'mr-2' : ''}" size={size === 'sm' ? 14 : 16} />
	{:else if Icon}
		<Icon class={children ? 'mr-2' : ''} size={size === 'sm' ? 14 : 16} />
	{/if}

	{#if children && !loading && size === 'icon' && false}
		<!-- Prevent rendering children if size is icon and no specific layout requested, but allow generally -->
	{/if}

	{#if children}
		<span class:opacity-0={loading && size === 'icon'}>
			{@render children()}
		</span>
	{/if}

	{#if IconRight && !loading}
		<IconRight class="ml-2" size={size === 'sm' ? 14 : 16} />
	{/if}
</button>
