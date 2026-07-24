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
		primary: 'bg-accent text-[#0A0A0A] hover:brightness-[1.12] active:brightness-[0.95]',
		secondary: 'bg-surface text-text-primary border border-border hover:bg-surface-hover',
		ghost: 'bg-transparent text-text-secondary hover:bg-surface-hover hover:text-text-primary',
		danger: 'bg-danger/10 text-danger border border-danger/20 hover:bg-danger/20',
		outline: 'bg-transparent border border-border text-text-primary hover:bg-surface'
	};

	const sizes = {
		sm: 'py-[7px] px-[14px] text-[12.5px]',
		md: 'py-[10px] px-[22px] text-[13.5px]',
		lg: 'py-[12px] px-[28px] text-[15px]',
		icon: 'h-[38px] w-[38px] p-0 flex justify-center items-center'
	};
</script>

<button
	{type}
	class="inline-flex items-center justify-center font-medium tracking-normal transition-all duration-150 ease-out rounded-lg disabled:pointer-events-none disabled:opacity-50 {variants[
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
