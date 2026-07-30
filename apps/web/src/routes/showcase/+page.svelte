<script lang="ts">
	import { onMount } from 'svelte';

	// Component Imports
	import Button from '$lib/components/app/common/Button.svelte';
	import Input from '$lib/components/app/common/Input.svelte';
	import Dropdown from '$lib/components/app/common/Dropdown.svelte';
	import StatusBadge from '$lib/components/app/common/StatusBadge.svelte';
	import ProgressIndicator from '$lib/components/app/common/ProgressIndicator.svelte';
	import Tabs from '$lib/components/app/common/Tabs.svelte';
	import FileUploader from '$lib/components/app/common/FileUploader.svelte';
	import Dialog from '$lib/components/app/common/Dialog.svelte';
	import Avatar from '$lib/components/app/common/Avatar.svelte';
	import Breadcrumb from '$lib/components/app/common/Breadcrumb.svelte';
	import EmptyState from '$lib/components/app/common/EmptyState.svelte';
	import Skeleton from '$lib/components/app/common/Skeleton.svelte';
	import DatasetTable from '$lib/components/app/data/DatasetTable.svelte';
	import Pagination from '$lib/components/app/data/Pagination.svelte';

	// Chat & Cards
	import ChatComposer from '$lib/components/app/chat/ChatComposer.svelte';
	import ChatBubble from '$lib/components/app/chat/ChatBubble.svelte';
	import ChartCard from '$lib/components/app/cards/ChartCard.svelte';
	import DatasetMetricsBanner from '$lib/components/app/datasets/DatasetMetricsBanner.svelte';
	import DatasetUploadModal from '$lib/components/app/datasets/DatasetUploadModal.svelte';

	// Icons
	import {
		IconDatabase,
		IconSparkles,
		IconPlus,
		IconTrash,
		IconDownload,
		IconRefresh,
		IconCheck,
		IconX,
		IconSearch,
		IconFilter,
		IconChartBar,
		IconTable,
		IconFileAnalytics,
		IconMessages,
		IconExternalLink,
		IconArrowRight,
		IconBrain,
		IconCloudUpload
	} from '@tabler/icons-svelte';

	// State variables for interactive demos
	let demoInputVal = $state('patient_records_q2.csv');
	let demoTextareaVal = $state('I want to analyze the correlation between systolic blood pressure and BMI across patient age groups.');
	let demoDropdownVal = $state('vitals');
	let demoTabVal = $state('preview');
	let showUploadModal = $state(false);
	let showDemoDialog = $state(false);

	let demoPage = $state(1);
	let demoSortCol = $state('sys_bp');
	let demoSortDir = $state<'asc' | 'desc'>('desc');

	const demoTableColumns = [
		{ name: 'patient_id', type: 'string' as const, sample: ['PT-10842', 'PT-10843', 'PT-10844', 'PT-10845', 'PT-10846'] },
		{ name: 'sys_bp', type: 'number' as const, sample: [138, 122, 145, 118, 150] },
		{ name: 'dia_bp', type: 'number' as const, sample: [88, 79, 92, 76, 95] },
		{ name: 'glucose', type: 'number' as const, sample: [104, 96, 142, null, 110] },
		{ name: 'recorded_at', type: 'date' as const, sample: ['2026-07-28', '2026-07-29', '2026-07-29', '2026-07-30', '2026-07-30'] },
		{ name: 'high_risk', type: 'boolean' as const, sample: [true, false, true, false, true] }
	];

	let demoDatasets = $state([
		{
			id: 'ds-1',
			original_filename: 'patient_records_q2.csv',
			file_size: 4520000,
			status: 'ready' as const,
			rows: 12430,
			columns: 18,
			error_message: null,
			created_at: new Date().toISOString()
		},
		{
			id: 'ds-2',
			original_filename: 'lab_results_history.json',
			file_size: 18400000,
			status: 'processing' as const,
			rows: 84120,
			columns: 32,
			error_message: null,
			created_at: new Date(Date.now() - 3600000).toISOString()
		},
		{
			id: 'ds-3',
			original_filename: 'er_logs_2026.csv',
			file_size: 920000,
			status: 'error' as const,
			rows: null,
			columns: null,
			error_message: 'Invalid CSV header delimiter',
			created_at: new Date(Date.now() - 86400000).toISOString()
		}
	]);

	const dropdownOptions = [
		{ value: 'vitals', label: 'Clinical / Vitals', icon: IconSparkles },
		{ value: 'labs', label: 'Lab Results', icon: IconFileAnalytics },
		{ value: 'demographics', label: 'Demographics', icon: IconTable },
		{ value: 'identifiers', label: 'Identifiers & Metadata', icon: IconDatabase }
	];

	const demoTabs = [
		{ id: 'preview', label: 'Data Preview', icon: IconTable },
		{ id: 'schema', label: 'Schema & Profiling', icon: IconFileAnalytics, badge: '18' },
		{ id: 'stats', label: 'Statistical Summary', icon: IconChartBar },
		{ id: 'semantics', label: 'Semantic Mapping', icon: IconSparkles, badge: 'AI' }
	];
</script>

<svelte:head>
	<title>Design System & Component Showcase | CHU Platform</title>
</svelte:head>

<!-- Shell Layout -->
<div class="grid min-h-screen lg:grid-cols-[16rem_1fr] bg-bg text-text-primary">
	<!-- Sidebar Navigation -->
	<aside class="sticky top-0 z-20 hidden h-screen overflow-y-auto border-r border-border bg-sidebar p-5 lg:block">
		<div class="mb-6 flex items-center gap-2.5 border-b border-border pb-4">
			<div class="w-7 h-7 rounded-lg bg-accent flex items-center justify-center text-white font-bold text-xs">
				DS
			</div>
			<div>
				<h1 class="text-sm font-bold tracking-tight text-text-primary">CHU Design System</h1>
				<p class="text-[11px] text-muted">Dark-first analytical UI</p>
			</div>
		</div>

		<nav class="space-y-6 text-xs font-medium">
			<div>
				<div class="px-2 mb-2 text-[10px] uppercase tracking-wider text-muted font-bold">
					Foundations
				</div>
				<div class="space-y-1 ">
					<a href="#colors" class="block px-2.5 py-1.5 rounded-md text-text-secondary hover:text-text-primary hover:bg-surface-hover transition-colors">Color Tokens</a>
					<a href="#typography" class="block px-2.5 py-1.5 rounded-md text-text-secondary hover:text-text-primary hover:bg-surface-hover transition-colors">Typography</a>
				</div>
			</div>

			<div>
				<div class="px-2 mb-2 text-[10px] uppercase tracking-wider text-muted font-bold">
					Core Components
				</div>
				<div class="space-y-1 ">
					<a href="#buttons" class="block px-2.5 py-1.5 rounded-md text-text-secondary hover:text-text-primary hover:bg-surface-hover transition-colors">Buttons & Triggers</a>
					<a href="#inputs" class="block px-2.5 py-1.5 rounded-md text-text-secondary hover:text-text-primary hover:bg-surface-hover transition-colors">Form Controls & Textarea</a>
					<a href="#dropdowns" class="block px-2.5 py-1.5 rounded-md text-text-secondary hover:text-text-primary hover:bg-surface-hover transition-colors">Dropdowns & Selects</a>
					<a href="#badges" class="block px-2.5 py-1.5 rounded-md text-text-secondary hover:text-text-primary hover:bg-surface-hover transition-colors">Badges & Status</a>
					<a href="#progress" class="block px-2.5 py-1.5 rounded-md text-text-secondary hover:text-text-primary hover:bg-surface-hover transition-colors">Progress & Skeletons</a>
					<a href="#tabs" class="block px-2.5 py-1.5 rounded-md text-text-secondary hover:text-text-primary hover:bg-surface-hover transition-colors">Tab Navigation</a>
				</div>
			</div>

			<div>
				<div class="px-2 mb-2 text-[10px] uppercase tracking-wider text-muted font-bold">
					Data & Cards
				</div>
				<div class="space-y-1 ">
					<a href="#cards" class="block px-2.5 py-1.5 rounded-md text-text-secondary hover:text-text-primary hover:bg-surface-hover transition-colors">Cards & KPI Banners</a>
					<a href="#tables" class="block px-2.5 py-1.5 rounded-md text-text-secondary hover:text-text-primary hover:bg-surface-hover transition-colors">Data Tables & Semantics</a>
					<a href="#modals" class="block px-2.5 py-1.5 rounded-md text-text-secondary hover:text-text-primary hover:bg-surface-hover transition-colors">Modals & Dialogs</a>
				</div>
			</div>

			<div>
				<div class="px-2 mb-2 text-[10px] uppercase tracking-wider text-muted font-bold">
					AI & Conversation
				</div>
				<div class="space-y-1 ">
					<a href="#chat" class="block px-2.5 py-1.5 rounded-md text-text-secondary hover:text-text-primary hover:bg-surface-hover transition-colors">Chat Composer & Messages</a>
					<a href="#uploader" class="block px-2.5 py-1.5 rounded-md text-text-secondary hover:text-text-primary hover:bg-surface-hover transition-colors">Dropzone File Uploader</a>
				</div>
			</div>
		</nav>
	</aside>

	<!-- Main Content Area -->
	<main class="p-6 lg:p-12 space-y-16 max-w-7xl mx-auto w-full">
		<!-- Page Banner -->
		<header class="border-b border-border pb-8">
			<div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-accent/15 border border-accent/30 text-accent text-xs font-semibold mb-3">
				<IconSparkles size={14} />
				<span>Design Tokens & UI Component Hub</span>
			</div>
			<h1 class="font-extrabold text-text-primary">
				Analytical Design System
			</h1>
			<p class="text-sm text-text-secondary mt-2 max-w-2xl">
				Unified showcase of reusable Svelte components, design tokens, typography, forms, data tables, modals, and AI conversation elements across the CHU platform.
			</p>
		</header>

		<!-- 1. COLOR TOKENS -->
		<section id="colors" class="space-y-6">
			<div>
				<h2>Color Tokens & Palette</h2>
				<p class="text-xs text-text-secondary mt-1">Enterprise dark-first surfaces and semantic color system.</p>
			</div>

			<div class="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-6 gap-4">
				<div class="p-3 rounded-lg border border-border bg-bg space-y-2">
					<div class="h-10 rounded bg-bg border border-border"></div>
					<div class="text-xs font-bold text-text-primary">bg-bg</div>
					<div class="text-[10px] text-muted">#090d11</div>
				</div>
				<div class="p-3 rounded-lg border border-border bg-surface space-y-2">
					<div class="h-10 rounded bg-surface border border-border"></div>
					<div class="text-xs font-bold text-text-primary">bg-surface</div>
					<div class="text-[10px] text-muted">#181e28</div>
				</div>
				<div class="p-3 rounded-lg border border-border bg-surface-elevated space-y-2">
					<div class="h-10 rounded bg-surface-elevated border border-border"></div>
					<div class="text-xs font-bold text-text-primary">surface-elevated</div>
					<div class="text-[10px] text-muted">#1c2331</div>
				</div>
				<div class="p-3 rounded-lg border border-border bg-accent/20 space-y-2">
					<div class="h-10 rounded bg-accent"></div>
					<div class="text-xs font-bold text-text-primary">bg-accent</div>
					<div class="text-[10px] text-muted">#2563eb</div>
				</div>
				<div class="p-3 rounded-lg border border-border bg-success/20 space-y-2">
					<div class="h-10 rounded bg-success"></div>
					<div class="text-xs font-bold text-text-primary">bg-success</div>
					<div class="text-[10px] text-muted">#10b981</div>
				</div>
				<div class="p-3 rounded-lg border border-border bg-warning/20 space-y-2">
					<div class="h-10 rounded bg-warning"></div>
					<div class="text-xs font-bold text-text-primary">bg-warning</div>
					<div class="text-[10px] text-muted">#f59e0b</div>
				</div>
			</div>
		</section>

		<!-- 2. TYPOGRAPHY & HEADING HIERARCHY -->
		<section id="typography" class="space-y-6">
			<div>
				<h2>Typography & Heading Hierarchy</h2>
				<p class="text-xs text-text-secondary mt-1">Headings h1–h6 in Cormorant Garamond serif and body text in Inter sans-serif.</p>
			</div>

			<div class="bg-surface border border-border rounded-xl p-6 space-y-6">
				<div class="space-y-1">
					<div class="text-[10px] text-accent font-bold uppercase">h1 Heading — 2.75rem (44px)</div>
					<h1>Header 1: Cormorant Garamond Title</h1>
				</div>

				<div class="space-y-1 border-t border-border/50 pt-4">
					<div class="text-[10px] text-accent font-bold uppercase">h2 Heading — 2.2rem (35px)</div>
					<h2>Header 2: Analytical Section Title</h2>
				</div>

				<div class="space-y-1 border-t border-border/50 pt-4">
					<div class="text-[10px] text-accent font-bold uppercase">h3 Heading — 1.75rem (28px)</div>
					<h3>Header 3: Dataset Component Panel</h3>
				</div>

				<div class="space-y-1 border-t border-border/50 pt-4">
					<div class="text-[10px] text-accent font-bold uppercase">h4 Heading — 1.4rem (22px)</div>
					<h4>Header 4: Sub-panel & Metric Title</h4>
				</div>

				<div class="space-y-1 border-t border-border/50 pt-4">
					<div class="text-[10px] text-accent font-bold uppercase">h5 Heading — 1.2rem (19px)</div>
					<h5>Header 5: Card & Action Group Heading</h5>
				</div>

				<div class="space-y-1 border-t border-border/50 pt-4">
					<div class="text-[10px] text-accent font-bold uppercase">h6 Heading — 1.05rem (17px)</div>
					<h6>Header 6: Small Section Label Heading</h6>
				</div>

				<div class="border-t border-border/50 pt-4 space-y-2">
					<div class="text-[10px] text-muted font-bold uppercase">Standard Application Body Text (Inter)</div>
					<p class="text-sm text-text-primary leading-relaxed">
						This standard paragraph is rendered in <strong class="text-accent font-semibold">Inter</strong> sans-serif font family. It is optimized for high readability in dense data analysis workflows, form fields, and chat streams.
					</p>
				</div>
			</div>
		</section>

		<!-- 2. BUTTONS -->
		<section id="buttons" class="space-y-6">
			<div>
				<h2>Buttons & Action Triggers</h2>
				<p class="text-xs text-text-secondary mt-1">Generous sizing, icon compositions, left/right icon placements, and state variants.</p>
			</div>

			<div class="bg-surface border border-border rounded-xl p-6 space-y-6">
				<!-- Standard Variants -->
				<div class="space-y-3">
					<div class="text-xs uppercase text-muted font-bold">Standard Variants</div>
					<div class="flex flex-wrap items-center gap-3">
						<Button variant="primary">Primary Action</Button>
						<Button variant="secondary">Secondary Action</Button>
						<Button variant="outline">Outline Action</Button>
						<Button variant="ghost">Ghost Button</Button>
						<Button variant="danger">Delete / Danger</Button>
						<Button variant="success">Success / Verified</Button>
					</div>
				</div>

				<!-- Left Icon Composition -->
				<div class="space-y-3 border-t border-border/50 pt-5">
					<div class="text-xs uppercase text-muted font-bold">Left Icon Compositions</div>
					<div class="flex flex-wrap items-center gap-3">
						<Button variant="primary" icon={IconPlus}>Upload Dataset</Button>
						<Button variant="secondary" icon={IconSparkles}>Auto-Detect Semantics</Button>
						<Button variant="outline" icon={IconDownload}>Export Results</Button>
						<Button variant="danger" icon={IconTrash}>Delete Record</Button>
						<Button variant="success" icon={IconCheck}>Confirm Changes</Button>
					</div>
				</div>

				<!-- Right Icon Composition -->
				<div class="space-y-3 border-t border-border/50 pt-5">
					<div class="text-xs uppercase text-muted font-bold">Right Icon Compositions</div>
					<div class="flex flex-wrap items-center gap-3">
						<Button variant="primary" iconRight={IconArrowRight}>Start Analysis</Button>
						<Button variant="secondary" iconRight={IconExternalLink}>Open Documentation</Button>
						<Button variant="outline" iconRight={IconFilter}>Apply Filters</Button>
					</div>
				</div>

				<!-- Icon-Only Buttons -->
				<div class="space-y-3 border-t border-border/50 pt-5">
					<div class="text-xs uppercase text-muted font-bold">Icon-Only Action Buttons</div>
					<div class="flex flex-wrap items-center gap-3">
						<Button variant="primary" size="icon" icon={IconPlus} aria-label="Add item" />
						<Button variant="secondary" size="icon" icon={IconSearch} aria-label="Search" />
						<Button variant="outline" size="icon" icon={IconDownload} aria-label="Download" />
						<Button variant="ghost" size="icon" icon={IconRefresh} aria-label="Refresh" />
						<Button variant="danger" size="icon" icon={IconTrash} aria-label="Delete" />
					</div>
				</div>

				<!-- Sizes (sm, md, lg) -->
				<div class="space-y-3 border-t border-border/50 pt-5">
					<div class="text-xs uppercase text-muted font-bold">Sizes (sm, md, lg)</div>
					<div class="flex flex-wrap items-center gap-3">
						<Button variant="primary" size="sm" icon={IconPlus}>Small (sm)</Button>
						<Button variant="primary" size="md" icon={IconPlus}>Medium (md)</Button>
						<Button variant="primary" size="lg" icon={IconPlus}>Large (lg)</Button>
					</div>
				</div>

				<!-- Loading & Disabled States -->
				<div class="space-y-3 border-t border-border/50 pt-5">
					<div class="text-xs uppercase text-muted font-bold">Loading & Disabled States</div>
					<div class="flex flex-wrap items-center gap-3">
						<Button variant="primary" loading>Running Query…</Button>
						<Button variant="secondary" loading>Processing…</Button>
						<Button variant="outline" disabled icon={IconDatabase}>Disabled Action</Button>
						<Button variant="danger" disabled icon={IconTrash}>Disabled Danger</Button>
					</div>
				</div>
			</div>
		</section>

		<!-- 3. FORM CONTROLS & TEXTAREA -->
		<section id="inputs" class="space-y-6">
			<div>
				<h2>Form Controls & Textarea</h2>
				<p class="text-xs text-text-secondary mt-1">Text inputs, textareas, search inputs, labels, and error messages.</p>
			</div>

			<div class="bg-surface border border-border rounded-xl p-6 grid grid-cols-1 md:grid-cols-2 gap-6">
				<!-- Input Fields -->
				<div class="space-y-4">
					<Input
						label="Dataset Name"
						bind:value={demoInputVal}
						placeholder="Enter dataset name…"
						helperText="Standard dataset filename with extension."
					/>

					<Input
						label="Search Filter"
						placeholder="Search columns or cell values…"
						type="search"
					/>

					<Input
						label="Invalid Input Example"
						value="invalid_column_!@#"
						error="Column name contains invalid characters"
					/>

					<Input
						label="Disabled Input"
						value="read_only_system_parameter"
						disabled
					/>
				</div>

				<!-- Textarea & Checkbox Controls -->
				<div class="space-y-4">
					<div class="space-y-1.5">
						<label for="demo-textarea" class="block text-xs font-medium text-text-secondary">Analysis Prompt (Textarea)</label>
						<textarea
							id="demo-textarea"
							bind:value={demoTextareaVal}
							rows={4}
							placeholder="Type your analytical question or instructions…"
							class="w-full bg-surface-elevated border border-border rounded-lg p-3 text-sm text-text-primary placeholder:text-muted focus:outline-none focus:border-accent focus:ring-1 focus:ring-accent transition-colors"
						></textarea>
					</div>

					<div class="flex items-center gap-3 pt-2">
						<input type="checkbox" id="check-1" checked class="w-4 h-4 accent-accent cursor-pointer" />
						<label for="check-1" class="text-xs text-text-secondary cursor-pointer">Auto-detect column data types and null percentages</label>
					</div>
				</div>
			</div>
		</section>

		<!-- 4. DROPDOWNS & SELECTS -->
		<section id="dropdowns" class="space-y-6">
			<div>
				<h2>Dropdowns & Custom Selects</h2>
				<p class="text-xs text-text-secondary mt-1">Dropdown components, option items, and native selects.</p>
			</div>

			<div class="bg-surface border border-border rounded-xl p-6 grid grid-cols-1 md:grid-cols-2 gap-6">
				<div class="space-y-2">
					<span class="block text-xs font-medium text-text-secondary">Custom Component Dropdown</span>
					<Dropdown
						items={[
							{ label: 'Clinical / Vitals', icon: IconSparkles, action: () => (demoDropdownVal = 'vitals') },
							{ label: 'Lab Results', icon: IconFileAnalytics, action: () => (demoDropdownVal = 'labs') },
							{ label: 'Demographics', icon: IconTable, action: () => (demoDropdownVal = 'demographics') },
							{ separator: true, label: '' },
							{ label: 'Identifiers & Metadata', icon: IconDatabase, action: () => (demoDropdownVal = 'identifiers') }
						]}
					>
						{#snippet trigger()}
							<div class="px-4 py-2.5 rounded-lg bg-surface-elevated border border-border flex items-center justify-between gap-3 text-xs text-text-primary hover:border-accent transition-colors cursor-pointer min-w-[220px]">
								<span>{demoDropdownVal === 'vitals' ? 'Clinical / Vitals' : demoDropdownVal === 'labs' ? 'Lab Results' : demoDropdownVal === 'demographics' ? 'Demographics' : 'Identifiers & Metadata'}</span>
								<span class="text-muted text-[10px]">▼</span>
							</div>
						{/snippet}
					</Dropdown>
				</div>

				<div class="space-y-2">
					<span class="block text-xs font-medium text-text-secondary">Native Select</span>
					<select class="w-full bg-surface-elevated border border-border rounded-lg pl-3.5 pr-10 py-2 text-sm text-text-primary focus:outline-none focus:border-accent">
						<option>10 rows</option>
						<option>25 rows</option>
						<option>50 rows</option>
						<option>100 rows</option>
					</select>
				</div>
			</div>
		</section>

		<!-- 5. BADGES & STATUS -->
		<section id="badges" class="space-y-6">
			<div>
				<h2>Badges & Status Indicators</h2>
				<p class="text-xs text-text-secondary mt-1">Status badges, pulse indicators, format tags, and confidence badges.</p>
			</div>

			<div class="bg-surface border border-border rounded-xl p-6 space-y-6">
				<div class="space-y-3">
					<h3 class="text-xs uppercase text-muted font-bold">Dataset Status Badges</h3>
					<div class="flex flex-wrap items-center gap-3">
						<StatusBadge status="ready" label="Ready" />
						<StatusBadge status="processing" label="Processing" />
						<StatusBadge status="uploading" label="Uploading" />
						<StatusBadge status="error" label="Error" />
					</div>
				</div>

				<div class="space-y-3 border-t border-border/50 pt-5">
					<h3 class="text-xs uppercase text-muted font-bold">Format & Concept Tags</h3>
					<div class="flex flex-wrap items-center gap-2">
						<span class="px-2.5 py-1 rounded bg-surface-elevated border border-border text-accent text-xs font-bold ">CSV</span>
						<span class="px-2.5 py-1 rounded bg-surface-elevated border border-border text-accent text-xs font-bold ">PARQUET</span>
						<span class="px-2.5 py-1 rounded bg-surface-elevated border border-border text-accent text-xs font-bold ">JSON</span>
						<span class="px-2.5 py-1 rounded-full bg-success/15 text-success text-xs font-semibold">98% Confidence</span>
					</div>
				</div>
			</div>
		</section>

		<!-- 6. PROGRESS & SKELETONS -->
		<section id="progress" class="space-y-6">
			<div>
				<h2>Progress & Loading States</h2>
				<p class="text-xs text-text-secondary mt-1">Progress bars, spinners, and skeleton loaders.</p>
			</div>

			<div class="bg-surface border border-border rounded-xl p-6 grid grid-cols-1 md:grid-cols-2 gap-6">
				<div class="space-y-4">
					<h3 class="text-xs uppercase text-muted font-bold">Progress Indicators</h3>
					<ProgressIndicator value={45} showValue />
					<ProgressIndicator value={100} showValue barClass="bg-success" />
				</div>

				<div class="space-y-4">
					<h3 class="text-xs uppercase text-muted font-bold">Skeleton Loading Blocks</h3>
					<div class="space-y-2">
						<Skeleton class="h-4 w-3/4" />
						<Skeleton class="h-4 w-1/2" />
						<Skeleton class="h-10 w-full" />
					</div>
				</div>
			</div>
		</section>

		<!-- 7. TABS -->
		<section id="tabs" class="space-y-6">
			<div>
				<h2>Tab Navigation</h2>
				<p class="text-xs text-text-secondary mt-1">Interactive tab component with badges and icons.</p>
			</div>

			<div class="bg-surface border border-border rounded-xl p-6">
				<Tabs tabs={demoTabs} bind:activeTab={demoTabVal} />
				<div class="mt-4 p-4 rounded bg-surface-elevated text-xs text-muted">
					Active Tab State: <span class="text-accent font-bold">{demoTabVal}</span>
				</div>
			</div>
		</section>

		<!-- 8. CARDS & KPI BANNERS -->
		<section id="cards" class="space-y-6">
			<div>
				<h2>Cards & KPI Banners</h2>
				<p class="text-xs text-text-secondary mt-1">Dataset metrics banner, chart cards, and metric widgets.</p>
			</div>

			<div class="space-y-6">
				<DatasetMetricsBanner datasets={demoDatasets} />

				<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
					<ChartCard
						title="Systolic BP vs Patient Age"
						type="bar"
						datasetName="patient_records_q2.csv"
						agentName="Data Analyst Agent"
						createdAt="2m ago"
					/>
					<ChartCard
						title="Blood Glucose Distribution"
						type="line"
						datasetName="lab_results_history.json"
						agentName="Data Analyst Agent"
						createdAt="1h ago"
					/>
				</div>
			</div>
		</section>

		<!-- 9. DATA TABLES -->
		<section id="tables" class="space-y-6">
			<div>
				<h2>Data Tables & Semantic Mapping</h2>
				<p class="text-xs text-text-secondary mt-1">Full dataset data grid with type icons, sorting headers, pagination, and column semantic mapping.</p>
			</div>

			<div class="bg-surface border border-border rounded-xl p-6 space-y-8">
				<!-- DatasetTable Component -->
				<div class="space-y-3">
					<div class="flex items-center justify-between">
						<h3 class="text-sm font-bold text-text-primary ">Dataset Table Component (Type Badges & Sorting)</h3>
						<span class="text-xs text-muted">Click column header to sort</span>
					</div>

					<DatasetTable
						columns={demoTableColumns}
						sortCol={demoSortCol}
						sortDir={demoSortDir}
						onsort={(col) => {
							if (demoSortCol === col) {
								demoSortDir = demoSortDir === 'asc' ? 'desc' : 'asc';
							} else {
								demoSortCol = col;
								demoSortDir = 'asc';
							}
						}}
					/>

					<Pagination page={demoPage} totalPages={12} onchange={(p) => (demoPage = p)} />
				</div>

				<!-- Semantic Concept Mapping Table -->
				<div class="space-y-3 border-t border-border/50 pt-6">
					<h3 class="text-sm font-bold text-text-primary ">Semantic Concept Mapping Table</h3>

					<div class="border border-border rounded-xl overflow-hidden bg-surface w-full shadow-xs">
						<table class="w-full text-left text-sm border-collapse">
							<thead>
								<tr class="bg-surface-elevated text-xs text-text-primary uppercase font-bold tracking-wider border-b border-border">
									<th class="px-5 py-4">Raw Column</th>
									<th class="px-5 py-4">Type</th>
									<th class="px-5 py-4">Semantic Concept / Business Term</th>
									<th class="px-5 py-4">Category</th>
									<th class="px-5 py-4">Unit / Format</th>
									<th class="px-5 py-4 text-right">AI Confidence</th>
								</tr>
							</thead>
							<tbody class="text-text-secondary divide-y divide-border/40">
								<tr class="hover:bg-surface-hover/60 transition-colors">
									<td class="px-5 py-4 font-bold text-text-primary text-sm">LAB_004</td>
									<td class="px-5 py-4"><span class="px-2.5 py-1 rounded bg-surface-elevated border border-border text-accent text-xs font-semibold ">int64</span></td>
									<td class="px-5 py-4 ">
										<div class="flex items-center gap-2.5">
											<input type="text" value="Systolic Blood Pressure" class="bg-surface-elevated border border-border/80 rounded-lg px-3.5 py-2 text-sm font-medium text-text-primary focus:outline-none focus:border-accent focus:ring-1 focus:ring-accent shadow-xs w-80 transition-colors" />
										</div>
									</td>
									<td class="px-5 py-4"><span class="px-3 py-1 rounded-full border text-xs font-semibold capitalize bg-indigo/15 border-indigo/30 text-indigo">Vitals</span></td>
									<td class="px-5 py-4 text-sm text-text-secondary ">mmHg</td>
									<td class="px-5 py-4 text-right"><span class="px-2.5 py-1 rounded text-xs font-semibold bg-success/15 border border-success/30 text-success">98%</span></td>
								</tr>
								<tr class="hover:bg-surface-hover/60 transition-colors">
									<td class="px-5 py-4 font-bold text-text-primary text-sm">RES_01</td>
									<td class="px-5 py-4"><span class="px-2.5 py-1 rounded bg-surface-elevated border border-border text-accent text-xs font-semibold ">float64</span></td>
									<td class="px-5 py-4 ">
										<div class="flex items-center gap-2.5">
											<input type="text" value="Patient Respiration Rate" class="bg-surface-elevated border border-border/80 rounded-lg px-3.5 py-2 text-sm font-medium text-text-primary focus:outline-none focus:border-accent focus:ring-1 focus:ring-accent shadow-xs w-80 transition-colors" />
										</div>
									</td>
									<td class="px-5 py-4"><span class="px-3 py-1 rounded-full border text-xs font-semibold capitalize bg-indigo/15 border-indigo/30 text-indigo">Vitals</span></td>
									<td class="px-5 py-4 text-sm text-text-secondary ">breaths/min</td>
									<td class="px-5 py-4 text-right"><span class="px-2.5 py-1 rounded text-xs font-semibold bg-success/15 border border-success/30 text-success">96%</span></td>
								</tr>
							</tbody>
						</table>
					</div>
				</div>
			</div>
		</section>

		<!-- 10. MODALS & DIALOGS -->
		<section id="modals" class="space-y-6">
			<div>
				<h2>Modals & Dialogs</h2>
				<p class="text-xs text-text-secondary mt-1">Modal triggers with backdrop overlays.</p>
			</div>

			<div class="bg-surface border border-border rounded-xl p-6 flex flex-wrap items-center gap-4">
				<Button variant="primary" onclick={() => (showUploadModal = true)}>
					<IconCloudUpload size={16} />
					<span>Open Dataset Upload Modal</span>
				</Button>

				<Button variant="secondary" onclick={() => (showDemoDialog = true)}>
					<span>Open Demo Confirmation Dialog</span>
				</Button>
			</div>
		</section>

		<!-- 11. CHAT COMPONENT -->
		<section id="chat" class="space-y-6">
			<div>
				<h2>Chat Composer & Messages</h2>
				<p class="text-xs text-text-secondary mt-1">Full AI conversational composer and chat bubble interface.</p>
			</div>

			<div class="bg-surface border border-border rounded-xl p-6 space-y-6">
				<div class="space-y-4">
					<ChatBubble role="user" content="Analyze correlation between BMI and fasting blood glucose levels in patient_records_q2.csv" timestamp="10:42 AM" />
					<ChatBubble role="assistant" content="I analyzed the dataset **patient_records_q2.csv** (12,430 rows). There is a moderate positive correlation (r = 0.48) between BMI and fasting glucose." timestamp="10:43 AM" />
				</div>

				<div class="border-t border-border pt-6">
					<h3 class="text-xs uppercase text-muted font-bold mb-3">Live Chat Composer Component</h3>
					<ChatComposer onSendMessage={(msg) => alert(`Sent message: ${msg}`)} />
				</div>
			</div>
		</section>

		<!-- 12. DROPZONE FILE UPLOADER -->
		<section id="uploader" class="space-y-6">
			<div>
				<h2>Dropzone File Uploader</h2>
				<p class="text-xs text-text-secondary mt-1">Interactive file upload dropzone component.</p>
			</div>

			<div class="bg-surface border border-border rounded-xl p-6">
				<FileUploader accept=".csv,.xlsx,.parquet,.json" />
			</div>
		</section>
	</main>
</div>

<!-- Modal Demos -->
<DatasetUploadModal bind:open={showUploadModal} />

<Dialog open={showDemoDialog} title="Confirmation Required" description="Are you sure you want to proceed with dataset transformation?" onclose={() => (showDemoDialog = false)}>
	<p class="text-sm text-text-secondary">This action will trigger an automated AI schema profiling job in the background.</p>
	{#snippet footer()}
		<Button variant="secondary" onclick={() => (showDemoDialog = false)}>Cancel</Button>
		<Button variant="primary" onclick={() => (showDemoDialog = false)}>Proceed</Button>
	{/snippet}
</Dialog>
