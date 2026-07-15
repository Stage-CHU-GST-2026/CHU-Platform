<script lang="ts">
    import type { Component } from 'svelte';

    interface Props {
        type?: 'text' | 'password' | 'email' | 'number' | 'search';
        value?: string;
        label?: string;
        placeholder?: string;
        error?: string;
        hint?: string;
        disabled?: boolean;
        prefix?: Component<any>;
        suffix?: Component<any>;
        class?: string;
        id?: string;
    }

    let {
        type = 'text',
        value = $bindable(''),
        label,
        placeholder,
        error,
        hint,
        disabled = false,
        prefix: Prefix,
        suffix: Suffix,
        class: className = '',
        id = crypto.randomUUID()
    } = $props();
</script>

<div class="flex flex-col gap-1.5 {className}">
    {#if label}
        <label for={id} class="text-[13px] font-medium text-text-primary">
            {label}
        </label>
    {/if}
    
    <div class="relative flex items-center">
        {#if Prefix}
            <div class="absolute left-3 text-muted">
                <Prefix size={16} />
            </div>
        {/if}
        
        <input
            {id}
            {type}
            bind:value
            {placeholder}
            {disabled}
            class="w-full h-9 bg-canvas border rounded-md text-[13px] text-text-primary placeholder:text-muted transition-colors "
            class:border-border={!error}
            class:hover:border-muted={!error && !disabled}
            class:border-danger={!!error}
            class:focus:border-danger={!!error}
            class:pl-9={!!Prefix}
            class:pr-9={!!Suffix}
            class:px-3={!Prefix && !Suffix}
            class:opacity-50={disabled}
            class:cursor-not-allowed={disabled}
            aria-invalid={!!error}
            aria-describedby={error ? `${id}-error` : hint ? `${id}-hint` : undefined}
        />
        
        {#if Suffix}
            <div class="absolute right-3 text-muted">
                <Suffix size={16} />
            </div>
        {/if}
    </div>
    
    {#if error}
        <span id="{id}-error" class="text-[12px] text-danger">{error}</span>
    {:else if hint}
        <span id="{id}-hint" class="text-[12px] text-text-secondary">{hint}</span>
    {/if}
</div>
