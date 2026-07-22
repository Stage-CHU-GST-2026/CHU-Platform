<script lang="ts">
	import { settings } from '$lib/state/settings.svelte';
	import PageHeader from '$lib/components/app/layout/PageHeader.svelte';
	import Button from '$lib/components/app/common/Button.svelte';
	import Input from '$lib/components/app/common/Input.svelte';
	import Tabs from '$lib/components/app/common/Tabs.svelte';
	import Section from '$lib/components/app/layout/Section.svelte';
	import Card from '$lib/components/app/cards/Card.svelte';
	import {
		IconCheck,
		IconDeviceFloppy,
		IconSettings,
		IconPalette,
		IconRobot
	} from '@tabler/icons-svelte';

	let saving = $state(false);

	async function handleSave() {
		saving = true;
		await settings.save();
		saving = false;
	}
</script>

<svelte:head>
	<title>Settings | CHU Analytics</title>
</svelte:head>

<div class="p-8 max-w-5xl mx-auto h-full flex flex-col">
	<PageHeader
		title="Settings"
		subtitle="Manage your workspace preferences, appearance, and AI model configurations."
	>
		<Button variant="primary" loading={saving} onclick={handleSave}>
			{#if settings.saved && !saving}
				<IconCheck size={16} class="mr-2" /> Saved
			{:else}
				<IconDeviceFloppy size={16} class="mr-2" /> Save Changes
			{/if}
		</Button>
	</PageHeader>

	<div class="flex flex-col md:flex-row gap-8 mt-4">
		<!-- Sidebar Navigation -->
		<div class="w-full md:w-56 shrink-0">
			<nav class="flex flex-col gap-1">
				<button
					class="w-full flex items-center gap-3 px-3 py-2 rounded-md text-[13px] font-medium transition-colors {settings.activeSection ===
					'general'
						? 'bg-surface-elevated text-text-primary'
						: 'text-text-secondary hover:bg-surface-hover hover:text-text-primary'}"
					onclick={() => (settings.activeSection = 'general')}
				>
					<IconSettings
						size={18}
						class={settings.activeSection === 'general' ? 'text-accent' : 'text-muted'}
					/>
					General
				</button>
				<button
					class="w-full flex items-center gap-3 px-3 py-2 rounded-md text-[13px] font-medium transition-colors {settings.activeSection ===
					'appearance'
						? 'bg-surface-elevated text-text-primary'
						: 'text-text-secondary hover:bg-surface-hover hover:text-text-primary'}"
					onclick={() => (settings.activeSection = 'appearance')}
				>
					<IconPalette
						size={18}
						class={settings.activeSection === 'appearance' ? 'text-accent' : 'text-muted'}
					/>
					Appearance
				</button>
				<button
					class="w-full flex items-center gap-3 px-3 py-2 rounded-md text-[13px] font-medium transition-colors {settings.activeSection ===
					'ai'
						? 'bg-surface-elevated text-text-primary'
						: 'text-text-secondary hover:bg-surface-hover hover:text-text-primary'}"
					onclick={() => (settings.activeSection = 'ai')}
				>
					<IconRobot
						size={18}
						class={settings.activeSection === 'ai' ? 'text-accent' : 'text-muted'}
					/>
					AI Models
				</button>
			</nav>
		</div>

		<!-- Settings Content -->
		<div class="flex-1 max-w-2xl">
			{#if settings.activeSection === 'general'}
				<Section title="General Settings" class="mb-8">
					<Card padding="lg">
						<div class="flex flex-col gap-6">
							<Input
								label="Workspace Name"
								bind:value={settings.general.workspaceName}
								hint="This name will be displayed in the sidebar."
							/>

							<div class="grid grid-cols-2 gap-6">
								<div class="flex flex-col gap-1.5">
									<label class="text-[13px] font-medium text-text-primary">Language</label>
									<select
										class="w-full h-9 bg-surface border border-border rounded-md text-[13px] text-text-primary px-3 hover:border-muted focus:border-accent focus:ring-1 focus:ring-accent/50 outline-none transition-colors appearance-none"
									>
										<option value="en" selected={settings.general.language === 'en'}>English</option
										>
										<option value="fr" selected={settings.general.language === 'fr'}
											>Français</option
										>
										<option value="es" selected={settings.general.language === 'es'}>Español</option
										>
									</select>
								</div>
								<div class="flex flex-col gap-1.5">
									<label class="text-[13px] font-medium text-text-primary">Timezone</label>
									<select
										class="w-full h-9 bg-surface border border-border rounded-md text-[13px] text-text-primary px-3 hover:border-muted focus:border-accent focus:ring-1 focus:ring-accent/50 outline-none transition-colors appearance-none"
									>
										<option value="UTC" selected={settings.general.timezone === 'UTC'}>UTC</option>
										<option value="UTC+1" selected={settings.general.timezone === 'UTC+1'}
											>Central European Time (CET)</option
										>
										<option value="EST" selected={settings.general.timezone === 'EST'}
											>Eastern Standard Time (EST)</option
										>
									</select>
								</div>
							</div>
						</div>
					</Card>
				</Section>
			{:else if settings.activeSection === 'appearance'}
				<Section title="Appearance" class="mb-8">
					<Card padding="lg">
						<div class="flex flex-col gap-6">
							<div class="flex flex-col gap-3">
								<label class="text-[13px] font-medium text-text-primary">Interface Density</label>
								<div class="grid grid-cols-2 gap-4">
									<!-- svelte-ignore a11y_click_events_have_key_events -->
									<!-- svelte-ignore a11y_no_static_element_interactions -->
									<div
										class="border rounded-lg p-4 cursor-pointer transition-colors {settings
											.appearance.density === 'comfortable'
											? 'border-accent bg-accent/5'
											: 'border-border bg-surface hover:border-muted'}"
										onclick={() => (settings.appearance.density = 'comfortable')}
									>
										<div class="flex items-center gap-2 mb-2">
											<div
												class="w-4 h-4 rounded-full border flex items-center justify-center {settings
													.appearance.density === 'comfortable'
													? 'border-accent text-accent'
													: 'border-muted'}"
											>
												{#if settings.appearance.density === 'comfortable'}<div
														class="w-2 h-2 rounded-full bg-accent"
													></div>{/if}
											</div>
											<span class="text-[13px] font-medium text-text-primary">Comfortable</span>
										</div>
										<div class="flex flex-col gap-3 pl-6">
											<div class="h-2 w-full bg-border rounded"></div>
											<div class="h-2 w-3/4 bg-border rounded"></div>
										</div>
									</div>
									<!-- svelte-ignore a11y_click_events_have_key_events -->
									<!-- svelte-ignore a11y_no_static_element_interactions -->
									<div
										class="border rounded-lg p-4 cursor-pointer transition-colors {settings
											.appearance.density === 'compact'
											? 'border-accent bg-accent/5'
											: 'border-border bg-surface hover:border-muted'}"
										onclick={() => (settings.appearance.density = 'compact')}
									>
										<div class="flex items-center gap-2 mb-2">
											<div
												class="w-4 h-4 rounded-full border flex items-center justify-center {settings
													.appearance.density === 'compact'
													? 'border-accent text-accent'
													: 'border-muted'}"
											>
												{#if settings.appearance.density === 'compact'}<div
														class="w-2 h-2 rounded-full bg-accent"
													></div>{/if}
											</div>
											<span class="text-[13px] font-medium text-text-primary">Compact</span>
										</div>
										<div class="flex flex-col gap-2 pl-6">
											<div class="h-2 w-full bg-border rounded"></div>
											<div class="h-2 w-3/4 bg-border rounded"></div>
										</div>
									</div>
								</div>
							</div>
						</div>
					</Card>
				</Section>
			{:else if settings.activeSection === 'ai'}
				<Section title="AI Models" class="mb-8">
					<Card padding="lg">
						<div class="flex flex-col gap-6">
							<div class="flex flex-col gap-1.5">
								<label class="text-[13px] font-medium text-text-primary"
									>Default Language Model</label
								>
								<select
									class="w-full h-9 bg-surface border border-border rounded-md text-[13px] text-text-primary px-3 hover:border-muted focus:border-accent focus:ring-1 focus:ring-accent/50 outline-none transition-colors appearance-none"
								>
									<option
										value="claude-3.5-sonnet"
										selected={settings.aiModels.defaultModel === 'claude-3.5-sonnet'}
										>Claude 3.5 Sonnet (Recommended)</option
									>
									<option value="gpt-4o" selected={settings.aiModels.defaultModel === 'gpt-4o'}
										>GPT-4o</option
									>
									<option
										value="gemini-1.5-pro"
										selected={settings.aiModels.defaultModel === 'gemini-1.5-pro'}
										>Gemini 1.5 Pro</option
									>
								</select>
								<span class="text-[12px] text-text-secondary mt-1"
									>This model will be used by default for all agents unless specifically overridden.</span
								>
							</div>

							<div>
								<div class="flex justify-between items-center mb-2">
									<label class="text-[13px] font-medium text-text-primary">Temperature</label>
									<span class="text-[13px] tabular-nums text-text-secondary"
										>{settings.aiModels.temperature}</span
									>
								</div>
								<input
									type="range"
									min="0"
									max="1"
									step="0.1"
									bind:value={settings.aiModels.temperature}
									class="w-full accent-accent h-1.5 bg-surface-elevated rounded-lg appearance-none cursor-pointer"
								/>
								<div class="flex justify-between items-center mt-1 text-[11px] text-muted">
									<span>Precise</span>
									<span>Creative</span>
								</div>
							</div>
						</div>
					</Card>
				</Section>
			{/if}
		</div>
	</div>
</div>
