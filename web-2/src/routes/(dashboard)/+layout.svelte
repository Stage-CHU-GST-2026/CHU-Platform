<script lang="ts">
	import * as Sidebar from "$lib/components/ui/sidebar/index.js";
	import AppSidebar from "$lib/components/dashboard/app-sidebar.svelte";
	import { Button } from "$lib/components/ui/button";
	import { toggleMode } from "mode-watcher";
	import Sun from "@lucide/svelte/icons/sun";
	import Moon from "@lucide/svelte/icons/moon";
	import type { LayoutData } from "./$types";

	interface Props {
		data: LayoutData;
		children: any;
	}

	let { data, children }: Props = $props();

	// Reactive conversation history list from server load
	let conversations = $derived(data.conversations || []);
</script>

<!-- FIXED SCREEN LAYOUT: h-screen w-screen overflow-hidden -->
<Sidebar.Provider class="h-screen w-screen overflow-hidden flex flex-row bg-background">
	<!-- App Sidebar fixed on the left -->
	<AppSidebar {conversations} />

	<!-- Main Content Area: fixed viewport height, overflow-hidden flex flex-col -->
	<Sidebar.Inset class="flex-1 h-full overflow-hidden flex flex-col min-w-0 bg-background">
		<!-- Top Header Bar -->
		<header class="h-14 shrink-0 border-b border-border px-4 flex items-center justify-between bg-card/50 backdrop-blur-xs">
			<div class="flex items-center gap-3">
				<Sidebar.Trigger class="size-8" />
				<span class="text-sm font-medium text-muted-foreground">CHU Platform</span>
			</div>

			<div class="flex items-center gap-2">
				<Button
					type="button"
					variant="ghost"
					size="icon"
					onclick={toggleMode}
					aria-label="Toggle theme"
					class="size-8 rounded-lg"
				>
					<Sun class="size-4 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
					<Moon class="absolute size-4 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
				</Button>
			</div>
		</header>

		<!-- Main Page View: full height container allowing per-page scroll control -->
		<main class="flex-1 h-full overflow-hidden flex flex-col min-h-0 min-w-0 bg-background">
			{@render children()}
		</main>
	</Sidebar.Inset>
</Sidebar.Provider>
