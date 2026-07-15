<script lang="ts">
    import { app } from '$lib/state/app.svelte';
    import { page } from '$app/stores';
    import { goto } from '$app/navigation';
    import { onMount } from 'svelte';
    import SidebarItem from './SidebarItem.svelte';
    import { listConversations, deleteConversation, createConversation } from '$lib/api/chat';
    import type { ConversationSummary } from '$lib/api/chat';
    import { conversationRefreshTick } from '$lib/stores/conversations';
    import {
        IconPlus,
        IconLayoutDashboard,
        IconSun,
        IconMoon,
        IconMessages,
        IconTrash,
        IconLoader2
    } from '@tabler/icons-svelte';

    const currentPath = $derived($page.url.pathname);
    const activeConvId = $derived($page.url.searchParams.get('id'));

    let conversations = $state<ConversationSummary[]>([]);
    let loading = $state(false);

    async function load() {
        try {
            loading = true;
            conversations = await listConversations(50);
        } catch (e) {
            // silently fail — API may not be up
        } finally {
            loading = false;
        }
    }

    onMount(load);

    // Re-fetch whenever the conversation page signals a new conversation was created
    $effect(() => {
        const _ = $conversationRefreshTick;
        load();
    });

    async function newConversation() {
        const conv = await createConversation();
        await load();
        goto(`/dashboard/conversation?id=${conv.id}`);
    }

    async function handleDelete(e: MouseEvent, id: string) {
        e.preventDefault();
        e.stopPropagation();
        await deleteConversation(id);
        conversations = conversations.filter(c => c.id !== id);
        // If we deleted the active conversation, go back to dashboard
        if (activeConvId === id) goto('/dashboard/conversation');
    }

    function formatRelativeTime(dateStr: string): string {
        const diff = Date.now() - new Date(dateStr).getTime();
        const mins = Math.floor(diff / 60000);
        if (mins < 1) return 'just now';
        if (mins < 60) return `${mins}m ago`;
        const hrs = Math.floor(mins / 60);
        if (hrs < 24) return `${hrs}h ago`;
        const days = Math.floor(hrs / 24);
        if (days < 7) return `${days}d ago`;
        return new Date(dateStr).toLocaleDateString();
    }
</script>

<aside class="sidebar bg-sidebar border-r border-border flex flex-col z-[var(--z-sidebar)]">
    <!-- Header: New Conversation button -->
    <div class="py-3 px-3 shrink-0 transition-all border-b border-border-subtle">
        <button
            class="w-full flex items-center h-6 px-2 rounded-md transition-all text-text-secondary cursor-pointer border border-border-subtle hover:bg-surface-hover hover:text-text-primary"
            class:justify-center={app.sidebarCollapsed}
            onclick={newConversation}
        >
            <IconPlus size={16} stroke={2} class={app.sidebarCollapsed ? '' : 'mr-2'} />
            {#if !app.sidebarCollapsed}
                <span class="text-[13px] font-medium whitespace-nowrap">New Conversation</span>
            {/if}
        </button>
    </div>

    <!-- Nav -->
    <nav class="flex-1 overflow-y-auto py-3 px-3 flex flex-col gap-0.5" role="navigation" aria-label="Main navigation">
        <SidebarItem href="/dashboard" icon={IconLayoutDashboard} label="Dashboard" {currentPath} />

        {#if !app.sidebarCollapsed}
            <!-- Conversations section -->
            <div class="mt-3 mb-1 px-2">
                <span class="text-[11px] font-semibold uppercase tracking-wider text-muted">Conversations</span>
            </div>

            {#if loading}
                <div class="flex items-center gap-2 px-2 py-1.5 text-muted">
                    <IconLoader2 size={13} class="animate-spin" />
                    <span class="text-[12px]">Loading…</span>
                </div>
            {:else if conversations.length === 0}
                <div class="px-2 py-1.5 text-[12px] text-muted italic">No conversations yet</div>
            {:else}
                {#each conversations as conv (conv.id)}
                    {@const isActive = conv.id === activeConvId}
                    <a
                        href="/dashboard/conversation?id={conv.id}"
                        class="group relative flex items-center gap-2 rounded-md px-2 py-1.5 transition-colors text-[13px] cursor-pointer
                               {isActive
                                   ? 'bg-surface text-text-primary'
                                   : 'text-text-secondary hover:bg-surface-hover hover:text-text-primary'}"
                    >
                        <IconMessages size={13} stroke={1.5} class="shrink-0 opacity-60" />
                        <span class="flex-1 min-w-0 truncate leading-tight">
                            {conv.title ?? 'New conversation'}
                        </span>
                        <!-- Delete button (shows on hover) -->
                        <button
                            class="shrink-0 opacity-0 group-hover:opacity-100 p-0.5 rounded hover:text-danger transition-all"
                            onclick={(e) => handleDelete(e, conv.id)}
                            aria-label="Delete conversation"
                        >
                            <IconTrash size={12} stroke={1.5} />
                        </button>
                    </a>
                {/each}
            {/if}
        {/if}
    </nav>

    <!-- Footer -->
    <div class="p-3 flex flex-col gap-1 shrink-0">
        <button
            class="group flex items-center h-6 px-2 rounded-md transition-all text-text-secondary cursor-pointer relative w-full hover:bg-surface-hover hover:text-text-primary"
            onclick={() => app.toggleTheme()}
            aria-label="Toggle theme"
        >
            <div class="flex items-center justify-center shrink-0 w-5 h-5">
                {#if app.theme === 'dark'}
                    <IconSun size={16} />
                {:else}
                    <IconMoon size={16} />
                {/if}
            </div>
            {#if !app.sidebarCollapsed}
                <span class="ml-3 text-[13px] font-medium whitespace-nowrap overflow-hidden truncate">
                    {app.theme === 'dark' ? 'Light Mode' : 'Dark Mode'}
                </span>
            {/if}
        </button>
    </div>
</aside>

<style>
    .sidebar {
        grid-area: sidebar;
        height: 100vh;
        overflow: hidden;
        transition: width var(--transition-slow);
    }
</style>
