<svelte:head>
	<title>Design System — Analytical Workspace</title>
</svelte:head>

<!-- ===== LAYOUT SHELL ===== -->
<div class="grid min-h-screen lg:grid-cols-[15rem_1fr]">
	<!-- SIDEBAR -->
	<aside
		class="sticky top-0 z-10 hidden h-screen overflow-y-auto border-r border-border bg-sidebar p-6 lg:block"
	>
		<div class="mb-3 flex items-center gap-[10px] border-b border-border pb-5">
			<div class="size-6 shrink-0 rounded-full bg-blue"></div>
			<span class="text-[13.5px] font-semibold tracking-tight">Analytical Workspace</span>
		</div>

		<div class="mb-6">
			<div class="mb-2 px-2 text-[11px] font-semibold uppercase tracking-wider text-muted">
				Foundations
			</div>
			<a
				href="#colors"
				class="mb-[2px] block rounded-radius-sm px-2 py-[7px] text-[13.5px] text-text-secondary no-underline transition-colors hover:bg-surface hover:text-text-primary"
				>Color</a
			>
			<a
				href="#typography"
				class="mb-[2px] block rounded-radius-sm px-2 py-[7px] text-[13.5px] text-text-secondary no-underline transition-colors hover:bg-surface hover:text-text-primary"
				>Typography</a
			>
			<a
				href="#shape"
				class="mb-[2px] block rounded-radius-sm px-2 py-[7px] text-[13.5px] text-text-secondary no-underline transition-colors hover:bg-surface hover:text-text-primary"
				>Shape &amp; elevation</a
			>
			<a
				href="#motion"
				class="mb-[2px] block rounded-radius-sm px-2 py-[7px] text-[13.5px] text-text-secondary no-underline transition-colors hover:bg-surface hover:text-text-primary"
				>Motion</a
			>
		</div>

		<div class="mb-6">
			<div class="mb-2 px-2 text-[11px] font-semibold uppercase tracking-wider text-muted">
				Components
			</div>
			<a
				href="#buttons"
				class="mb-[2px] block rounded-radius-sm px-2 py-[7px] text-[13.5px] text-text-secondary no-underline transition-colors hover:bg-surface hover:text-text-primary"
				>Buttons</a
			>
			<a
				href="#badges"
				class="mb-[2px] block rounded-radius-sm px-2 py-[7px] text-[13.5px] text-text-secondary no-underline transition-colors hover:bg-surface hover:text-text-primary"
				>Badges</a
			>
			<a
				href="#inputs"
				class="mb-[2px] block rounded-radius-sm px-2 py-[7px] text-[13.5px] text-text-secondary no-underline transition-colors hover:bg-surface hover:text-text-primary"
				>Inputs</a
			>
			<a
				href="#cards"
				class="mb-[2px] block rounded-radius-sm px-2 py-[7px] text-[13.5px] text-text-secondary no-underline transition-colors hover:bg-surface hover:text-text-primary"
				>Cards &amp; KPIs</a
			>
			<a
				href="#table"
				class="mb-[2px] block rounded-radius-sm px-2 py-[7px] text-[13.5px] text-text-secondary no-underline transition-colors hover:bg-surface hover:text-text-primary"
				>Tables</a
			>
			<a
				href="#charts"
				class="mb-[2px] block rounded-radius-sm px-2 py-[7px] text-[13.5px] text-text-secondary no-underline transition-colors hover:bg-surface hover:text-text-primary"
				>Data visualization</a
			>
			<a
				href="#ai"
				class="mb-[2px] block rounded-radius-sm px-2 py-[7px] text-[13.5px] text-text-secondary no-underline transition-colors hover:bg-surface hover:text-text-primary"
				>AI presence</a
			>
		</div>

		<div class="mb-6">
			<div class="mb-2 px-2 text-[11px] font-semibold uppercase tracking-wider text-muted">
				Patterns
			</div>
			<a
				href="#context-bar"
				class="mb-[2px] block rounded-radius-sm px-2 py-[7px] text-[13.5px] text-text-secondary no-underline transition-colors hover:bg-surface hover:text-text-primary"
				>Dataset context bar</a
			>
			<a
				href="#timeline"
				class="mb-[2px] block rounded-radius-sm px-2 py-[7px] text-[13.5px] text-text-secondary no-underline transition-colors hover:bg-surface hover:text-text-primary"
				>Tool execution timeline</a
			>
			<a
				href="#conversation"
				class="mb-[2px] block rounded-radius-sm px-2 py-[7px] text-[13.5px] text-text-secondary no-underline transition-colors hover:bg-surface hover:text-text-primary"
				>Conversation</a
			>
			<a
				href="#prompts"
				class="mb-[2px] block rounded-radius-sm px-2 py-[7px] text-[13.5px] text-text-secondary no-underline transition-colors hover:bg-surface hover:text-text-primary"
				>Quick prompts</a
			>
			<a
				href="#upload"
				class="mb-[2px] block rounded-radius-sm px-2 py-[7px] text-[13.5px] text-text-secondary no-underline transition-colors hover:bg-surface hover:text-text-primary"
				>Dataset upload</a
			>
			<a
				href="#explorer"
				class="mb-[2px] block rounded-radius-sm px-2 py-[7px] text-[13.5px] text-text-secondary no-underline transition-colors hover:bg-surface hover:text-text-primary"
				>Data explorer</a
			>
		</div>

		<div class="mb-6">
			<div class="mb-2 px-2 text-[11px] font-semibold uppercase tracking-wider text-muted">
				Reference
			</div>
			<a
				href="#principles"
				class="mb-[2px] block rounded-radius-sm px-2 py-[7px] text-[13.5px] text-text-secondary no-underline transition-colors hover:bg-surface hover:text-text-primary"
				>Principles</a
			>
		</div>
	</aside>

	<!-- ===== MAIN ===== -->
	<main class="pb-40">
		<!-- HERO -->
		<section
			class="border-b border-border bg-[radial-gradient(ellipse_900px_400px_at_15%_0%,rgba(29,185,84,0.07),transparent_60%)] px-5 py-12 lg:px-16 lg:py-24"
		>
			<div
				class="mb-6 inline-flex items-center gap-2 rounded-full border border-border bg-surface px-3 py-[6px] text-xs font-mono text-text-secondary shadow-shadow-sm"
			>
				<span class="size-[6px] rounded-full bg-success"></span>
				v1.0 — Dark-first design system
			</div>

			<h1
				class="mb-5 max-w-[780px] text-[2rem] font-black leading-[1.05] tracking-tighter lg:text-[3.5rem]"
			>
				The interface exists&nbsp;to support&nbsp;thinking.
			</h1>
			<p class="mb-9 max-w-[620px] text-[17px] leading-relaxed text-text-secondary">
				A calm, focused environment where data is the primary content and AI acts as an invisible
				expert. Every pixel here exists for a reason — nothing competes with the user's data.
			</p>

			<div class="mb-8 flex gap-3">
				<button
					class="inline-flex cursor-pointer appearance-none items-center gap-2 rounded-radius-btn border border-transparent bg-blue px-[22px] py-[10px] text-[13.5px] font-bold text-[#0A0A0A] font-ui shadow-shadow-sm shadow-[inset_0_1px_0_rgba(255,255,255,0.12)] transition-all duration-[0.16s] ease-[cubic-bezier(.4,0,.2,1)] active:scale-[0.97] hover:translate-y-[-1px] hover:bg-[#1ED760] hover:shadow-shadow-md hover:shadow-[inset_0_1px_0_rgba(255,255,255,0.14)]"
					>Explore components</button
				>
				<button
					class="inline-flex cursor-pointer appearance-none items-center gap-2 rounded-radius-btn border border-border bg-surface-elevated px-[22px] py-[10px] text-[13.5px] font-bold text-text-primary font-ui transition-all duration-[0.16s] ease-[cubic-bezier(.4,0,.2,1)] active:scale-[0.97] hover:translate-y-[-1px] hover:border-[#3E3E3E] hover:bg-[#2E2E2E] hover:shadow-shadow-sm"
					>Read the philosophy</button
				>
			</div>

			<div
				class="grid max-w-[760px] grid-cols-2 overflow-hidden rounded-radius-md border border-border lg:grid-cols-4"
				style="gap:1px; background:var(--color-border)"
			>
				<div class="bg-canvas px-5 py-4">
					<div class="font-mono text-[22px] font-medium tracking-tight">6</div>
					<div class="mt-1 text-xs text-muted">Core colors</div>
				</div>
				<div class="bg-canvas px-5 py-4">
					<div class="font-mono text-[22px] font-medium tracking-tight">8px</div>
					<div class="mt-1 text-xs text-muted">Base radius</div>
				</div>
				<div class="bg-canvas px-5 py-4">
					<div class="font-mono text-[22px] font-medium tracking-tight">2</div>
					<div class="mt-1 text-xs text-muted">Typefaces</div>
				</div>
				<div class="bg-canvas px-5 py-4">
					<div class="font-mono text-[22px] font-medium tracking-tight">0</div>
					<div class="mt-1 text-xs text-muted">Gradients as decoration</div>
				</div>
			</div>
		</section>

		<!-- PRINCIPLES -->
		<section id="principles" class="border-b border-border px-5 py-12 lg:px-16 lg:py-24">
			<div class="mb-7 max-w-[720px]">
				<div class="mb-[10px] font-mono text-[11px] uppercase tracking-wider text-blue">
					Philosophy
				</div>
				<h2 class="m-0 mb-[10px] text-[22px] font-extrabold tracking-tight">
					Six principles, one discipline
				</h2>
				<p class="m-0 text-[14.5px] leading-relaxed text-text-secondary">
					The system is dark-first because analysts, engineers, and researchers already live in dark
					environments — IDEs, terminals, notebooks. This is a natural extension of that world, not
					a stylistic choice.
				</p>
			</div>

			<div class="grid gap-5 md:grid-cols-2 lg:grid-cols-3">
				{#each ['Data is the hero', 'White space is functional', 'Motion is purposeful', 'Typography first', 'Color is information', 'Borders before shadows'] as principle, i}
					<div
						class="rounded-radius-md border border-border bg-canvas p-5 transition-shadow hover:shadow-shadow-sm"
					>
						<span
							class="mb-[14px] inline-flex items-center gap-[6px] rounded-full bg-blue/13 px-[9px] py-[4px] text-[11.5px] font-mono font-medium tracking-wide text-blue"
						>
							{'0' + (i + 1).toString().slice(-2)}
						</span>
						<div class="text-sm font-semibold tracking-tight">{principle}</div>
						<p class="mt-2 text-[14.5px] leading-relaxed text-text-secondary">
							{i === 0
								? 'Charts, tables, and statistics receive visual emphasis. The interface fades into the background.'
								: ''}
							{i === 1
								? 'Spacing separates thoughts, not decorates pages. Every section is given room to breathe.'
								: ''}
							{i === 2
								? 'Animation communicates state — dataset uploaded, chart updated — never personality.'
								: ''}
							{i === 3
								? 'Most of the app is text. It must be readable, consistent, and comfortable for long sessions.'
								: ''}
							{i === 4
								? 'Blue means action, purple means AI, green means success. Everything else stays neutral.'
								: ''}
							{i === 5
								? 'Hierarchy comes from surface contrast and thin borders. Shadows are a last resort.'
								: ''}
						</p>
					</div>
				{/each}
			</div>
		</section>

		<!-- COLOR -->
		<section id="colors" class="border-b border-border px-5 py-12 lg:px-16 lg:py-24">
			<div class="mb-7 max-w-[720px]">
				<div class="mb-[10px] font-mono text-[11px] uppercase tracking-wider text-blue">
					Foundations / 01
				</div>
				<h2 class="m-0 mb-[10px] text-[22px] font-extrabold tracking-tight">Color</h2>
				<p class="m-0 text-[14.5px] leading-relaxed text-text-secondary">
					True black sidebar, near-black canvas — the interface recedes so a single confident accent
					can carry every action. Everything else stays neutral grey, several shades deep instead of
					one flat surface.
				</p>
			</div>

			<div class="mb-8 grid grid-cols-[repeat(auto-fill,minmax(160px,1fr))] gap-4">
				{#each [{ name: 'Background', hex: '#121212', usage: 'App-level base layer' }, { name: 'Canvas', hex: '#181818', usage: 'Content area background' }, { name: 'Surface', hex: '#1A1A1A', usage: 'Cards, panels, table headers' }, { name: 'Elevated surface', hex: '#282828', usage: 'Popovers, active states' }, { name: 'Sidebar', hex: '#000000', usage: 'Navigation chrome' }, { name: 'Border', hex: '#2A2A2A', usage: 'Hairline dividers' }] as swatch}
					<div
						class="overflow-hidden rounded-radius-md border border-border bg-canvas transition-shadow hover:-translate-y-0.5 hover:shadow-shadow-md"
					>
						<div class="h-[72px]" style="background:{swatch.hex}"></div>
						<div class="px-4 py-3">
							<div class="mb-[2px] text-[13px] font-medium">{swatch.name}</div>
							<div class="font-mono text-[11.5px] text-muted">{swatch.hex}</div>
							<div class="mt-[6px] text-[11px] leading-relaxed text-text-secondary">
								{swatch.usage}
							</div>
						</div>
					</div>
				{/each}
			</div>

			<div class="grid grid-cols-[repeat(auto-fill,minmax(160px,1fr))] gap-4">
				{#each [{ name: 'Primary green', hex: '#1DB954', usage: 'Actions — buttons, links, focus' }, { name: 'Accent indigo', hex: '#8D87FF', usage: 'AI — reserved exclusively' }, { name: 'Success', hex: '#34D399', usage: 'Positive deltas, confirmations' }, { name: 'Warning', hex: '#F0A23E', usage: 'Needs attention, not urgent' }, { name: 'Danger', hex: '#F0555C', usage: 'Errors, destructive actions' }, { name: 'Primary text', hex: '#FFFFFF', usage: 'Headlines, body copy' }] as swatch}
					<div
						class="overflow-hidden rounded-radius-md border border-border bg-canvas transition-shadow hover:-translate-y-0.5 hover:shadow-shadow-md"
					>
						<div class="h-[72px]" style="background:{swatch.hex}"></div>
						<div class="px-4 py-3">
							<div class="mb-[2px] text-[13px] font-medium">{swatch.name}</div>
							<div class="font-mono text-[11.5px] text-muted">{swatch.hex}</div>
							<div class="mt-[6px] text-[11px] leading-relaxed text-text-secondary">
								{swatch.usage}
							</div>
						</div>
					</div>
				{/each}
			</div>
		</section>

		<!-- TYPOGRAPHY -->
		<section id="typography" class="border-b border-border px-5 py-12 lg:px-16 lg:py-24">
			<div class="mb-7 max-w-[720px]">
				<div class="mb-[10px] font-mono text-[11px] uppercase tracking-wider text-blue">
					Foundations / 02
				</div>
				<h2 class="m-0 mb-[10px] text-[22px] font-extrabold tracking-tight">Typography</h2>
				<p class="m-0 text-[14.5px] leading-relaxed text-text-secondary">
					Inter carries the interface. JetBrains Mono carries numbers — metrics, code, timestamps —
					anything that benefits from fixed-width alignment.
				</p>
			</div>

			<div>
				{#each [{ name: 'Title / SemiBold', meta: '32px · -0.02em', style: 'font-size:32px; font-weight:600; letter-spacing:-0.02em;', text: 'Quarterly revenue analysis' }, { name: 'Heading / SemiBold', meta: '22px · -0.01em', style: 'font-size:22px; font-weight:600; letter-spacing:-0.01em;', text: 'Cohort retention by channel' }, { name: 'Subheading / Medium', meta: '15px', style: 'font-size:15px; font-weight:500;', text: 'Panel and card titles' }, { name: 'Body / Regular', meta: '13.5px · 1.6 line-height', style: 'font-size:13.5px; color:var(--color-text-secondary); line-height:1.6; max-width:480px;', text: 'Body copy stays quiet and legible across long analytical sessions, never competing with the data it describes.' }, { name: 'Caption / Regular', meta: '12px', style: 'font-size:12px; color:var(--color-muted);', text: 'Last updated 4 minutes ago' }, { name: 'Mono / Numbers', meta: 'JetBrains Mono', style: 'font-family:var(--font-mono); font-size:20px; letter-spacing:-0.02em;', text: '$482,190.24' }, { name: 'Mono / Code', meta: '13px', style: '', text: 'code' }] as type}
					<div class="flex items-baseline gap-7 border-b border-border py-5 last:border-b-0">
						<div class="w-40 shrink-0 font-mono text-[11.5px] leading-relaxed text-muted">
							<span class="mb-[2px] block text-text-secondary">{type.name}</span>
							{type.meta}
						</div>
						{#if type.name === 'Mono / Code'}
							<code
								class="inline-block rounded border border-border bg-surface px-[6px] py-[1px] font-mono text-xs text-text-secondary"
								>SELECT revenue FROM q3 WHERE region = 'EMEA'</code
							>
						{:else}
							<div class="text-text-primary" style={type.style}>{type.text}</div>
						{/if}
					</div>
				{/each}
			</div>
		</section>

		<!-- SHAPE & ELEVATION -->
		<section id="shape" class="border-b border-border px-5 py-12 lg:px-16 lg:py-24">
			<div class="mb-7 max-w-[720px]">
				<div class="mb-[10px] font-mono text-[11px] uppercase tracking-wider text-blue">
					Foundations / 03
				</div>
				<h2 class="m-0 mb-[10px] text-[22px] font-extrabold tracking-tight">
					Shape &amp; elevation
				</h2>
				<p class="m-0 text-[14.5px] leading-relaxed text-text-secondary">
					Everything feels engineered. Radii are modest and consistent. Hierarchy still comes from
					surface contrast and hairline borders first.
				</p>
			</div>

			<div class="mb-5 grid gap-5 md:grid-cols-2 lg:grid-cols-3">
				{#each [{ label: 'Radius — 8px', radius: 'rounded-radius-sm', desc: 'Buttons, inputs, small controls' }, { label: 'Radius — 12px', radius: 'rounded-radius-md', desc: 'Cards and panels' }, { label: 'Radius — 16px', radius: 'rounded-radius-lg', desc: 'Dialogs and modals' }] as item}
					<div class="rounded-radius-md border border-border bg-canvas p-5">
						<div class="mb-[14px] h-14 w-full bg-surface-elevated {item.radius}"></div>
						<div class="text-[13px] font-semibold tracking-tight">{item.label}</div>
						<div class="mt-1 text-xs leading-relaxed text-text-secondary">{item.desc}</div>
					</div>
				{/each}
			</div>

			<div class="mb-5 grid gap-5 md:grid-cols-2 lg:grid-cols-3">
				{#each [{ label: 'Level 0 — Canvas', bg: 'bg-canvas', desc: 'Base content background' }, { label: 'Level 1 — Surface', bg: 'bg-surface', desc: 'Resting panels' }, { label: 'Level 2 — Elevated', bg: 'bg-surface-elevated', desc: 'Active / hovered / focused — border + soft shadow' }] as item}
					<div
						class="rounded-radius-md border border-border {item.bg} p-[18px] {item.label ===
						'Level 2 — Elevated'
							? 'shadow-shadow-md'
							: ''}"
					>
						<div class="mb-[6px] text-[13px] font-semibold tracking-tight">{item.label}</div>
						<div class="text-xs leading-relaxed text-text-secondary">{item.desc}</div>
					</div>
				{/each}
			</div>

			<div class="grid gap-5 md:grid-cols-2 lg:grid-cols-3">
				{#each [{ label: 'Shadow — sm', shadow: 'shadow-shadow-sm', desc: 'Resting hover, composer, active nav' }, { label: 'Shadow — md', shadow: 'shadow-shadow-md', desc: 'Elevated panels, AI presence, focused composer' }, { label: 'Shadow — lg', shadow: 'shadow-shadow-lg', desc: 'Dialogs, dropdowns, floating above content' }] as item}
					<div class="rounded-radius-md border border-border bg-canvas p-5 {item.shadow}">
						<div class="mb-[6px] text-[13px] font-semibold tracking-tight">{item.label}</div>
						<div class="text-xs leading-relaxed text-text-secondary">{item.desc}</div>
					</div>
				{/each}
			</div>

			<div class="mb-6 mt-12">
				<h2 class="mb-[10px] text-base font-extrabold tracking-tight">Spacing scale</h2>
				<p class="text-[14.5px] leading-relaxed text-text-secondary">
					An 8-point rhythm, one step looser than before — room for data to breathe without turning
					into empty luxury.
				</p>
			</div>

			<div class="max-w-[520px]">
				{#each [{ block: 'w-[4px]', var: '--spacing-1 · 4px', desc: 'Icon-to-label gaps' }, { block: 'w-[8px]', var: '--spacing-2 · 8px', desc: 'Chip and badge padding' }, { block: 'w-[12px]', var: '--spacing-3 · 12px', desc: 'Input padding, tight stacks' }, { block: 'w-[16px]', var: '--spacing-4 · 16px', desc: 'Panel internal padding' }, { block: 'w-[24px]', var: '--spacing-5 · 24px', desc: 'Grid gaps, panel padding' }, { block: 'w-[32px]', var: '--spacing-6 · 32px', desc: 'Nav groups, hero actions' }, { block: 'w-[48px]', var: '--spacing-7 · 48px', desc: 'Section head margins' }, { block: 'w-[64px]', var: '--spacing-8 · 64px', desc: 'Section horizontal padding' }, { block: 'w-[96px]', var: '--spacing-9 · 96px', desc: 'Section vertical padding' }] as space}
					<div class="flex items-center gap-5 border-b border-border py-3 last:border-b-0">
						<div class="h-4 shrink-0 rounded-[3px] bg-blue {space.block}"></div>
						<div class="w-[120px] font-mono text-xs text-text-secondary">{space.var}</div>
						<div class="text-xs text-muted">{space.desc}</div>
					</div>
				{/each}
			</div>
		</section>

		<!-- MOTION -->
		<section id="motion" class="border-b border-border px-5 py-12 lg:px-16 lg:py-24">
			<div class="mb-7 max-w-[720px]">
				<div class="mb-[10px] font-mono text-[11px] uppercase tracking-wider text-blue">
					Foundations / 04
				</div>
				<h2 class="m-0 mb-[10px] text-[22px] font-extrabold tracking-tight">Motion</h2>
				<p class="m-0 text-[14.5px] leading-relaxed text-text-secondary">
					Animation communicates state, never personality. Nothing bounces. Nothing spins forever.
				</p>
			</div>

			<div class="flex items-center gap-6 rounded-radius-md border border-border bg-canvas p-5">
				<div class="flex items-center gap-[10px]">
					<div class="size-2 rounded-full bg-success animate-pulse-fade"></div>
					<span class="text-[13px] text-text-secondary">Live query running</span>
				</div>
				<div class="flex items-center gap-3">
					<span class="font-mono text-[12.5px] text-muted">Analysis 68%</span>
					<div
						class="h-[6px] w-[220px] overflow-hidden rounded-full border border-border bg-surface-elevated"
					>
						<div class="h-full w-[68%] rounded-full bg-blue transition-[width] duration-400"></div>
					</div>
				</div>
			</div>
		</section>

		<!-- BUTTONS -->
		<section id="buttons" class="border-b border-border px-5 py-12 lg:px-16 lg:py-24">
			<div class="mb-7 max-w-[720px]">
				<div class="mb-[10px] font-mono text-[11px] uppercase tracking-wider text-blue">
					Components / 01
				</div>
				<h2 class="m-0 mb-[10px] text-[22px] font-extrabold tracking-tight">Buttons</h2>
				<p class="m-0 text-[14.5px] leading-relaxed text-text-secondary">
					One primary action per view. Softer, rounder corners and a tactile press give the
					interface a warmer, more conversational feel.
				</p>
			</div>

			<div class="mb-[18px] flex flex-wrap items-center gap-3">
				<button
					class="inline-flex cursor-pointer appearance-none items-center gap-2 rounded-radius-btn border border-transparent bg-blue px-[22px] py-[10px] text-[13.5px] font-bold text-[#0A0A0A] font-ui shadow-shadow-sm shadow-[inset_0_1px_0_rgba(255,255,255,0.12)] transition-all duration-[0.16s] ease-[cubic-bezier(.4,0,.2,1)] active:scale-[0.97] hover:translate-y-[-1px] hover:bg-[#1ED760] hover:shadow-shadow-md hover:shadow-[inset_0_1px_0_rgba(255,255,255,0.14)]"
					>Run analysis</button
				>
				<button
					class="inline-flex cursor-pointer appearance-none items-center gap-2 rounded-radius-btn border border-border bg-surface-elevated px-[22px] py-[10px] text-[13.5px] font-bold text-text-primary font-ui transition-all duration-[0.16s] ease-[cubic-bezier(.4,0,.2,1)] active:scale-[0.97] hover:translate-y-[-1px] hover:border-[#3E3E3E] hover:bg-[#2E2E2E] hover:shadow-shadow-sm"
					>Export data</button
				>
				<button
					class="inline-flex cursor-pointer appearance-none items-center gap-2 rounded-radius-btn border border-transparent bg-transparent px-[22px] py-[10px] text-[13.5px] font-bold text-text-secondary font-ui transition-all duration-[0.16s] ease-[cubic-bezier(.4,0,.2,1)] active:scale-[0.97] hover:translate-y-[-1px] hover:bg-surface hover:text-text-primary"
					>Cancel</button
				>
				<button
					class="inline-flex cursor-pointer appearance-none items-center gap-2 rounded-radius-btn border border-danger/26 bg-danger/13 px-[22px] py-[10px] text-[13.5px] font-bold text-[#FF9498] font-ui transition-all duration-[0.16s] ease-[cubic-bezier(.4,0,.2,1)] active:scale-[0.97] hover:translate-y-[-1px] hover:bg-danger/20 hover:shadow-shadow-sm"
					>Delete dataset</button
				>
			</div>
			<div class="flex flex-wrap items-center gap-3">
				<button
					class="inline-flex cursor-pointer appearance-none items-center gap-2 rounded-radius-btn border border-transparent bg-blue px-[14px] py-[7px] text-[12.5px] font-bold text-[#0A0A0A] font-ui shadow-shadow-sm shadow-[inset_0_1px_0_rgba(255,255,255,0.12)] transition-all duration-[0.16s] ease-[cubic-bezier(.4,0,.2,1)] active:scale-[0.97] hover:translate-y-[-1px] hover:bg-[#1ED760] hover:shadow-shadow-md hover:shadow-[inset_0_1px_0_rgba(255,255,255,0.14)]"
					>Apply filter</button
				>
				<button
					class="inline-flex cursor-pointer appearance-none items-center gap-2 rounded-radius-btn border border-border bg-surface-elevated px-[14px] py-[7px] text-[12.5px] font-bold text-text-primary font-ui transition-all duration-[0.16s] ease-[cubic-bezier(.4,0,.2,1)] active:scale-[0.97] hover:translate-y-[-1px] hover:border-[#3E3E3E] hover:bg-[#2E2E2E] hover:shadow-shadow-sm"
					>Duplicate</button
				>
				<button
					class="inline-flex cursor-pointer appearance-none items-center gap-2 rounded-radius-btn border border-transparent bg-transparent px-[14px] py-[7px] text-[12.5px] font-bold text-text-secondary font-ui transition-all duration-[0.16s] ease-[cubic-bezier(.4,0,.2,1)] active:scale-[0.97] hover:translate-y-[-1px] hover:bg-surface hover:text-text-primary"
					>Reset</button
				>
			</div>
		</section>

		<!-- BADGES -->
		<section id="badges" class="border-b border-border px-5 py-12 lg:px-16 lg:py-24">
			<div class="mb-7 max-w-[720px]">
				<div class="mb-[10px] font-mono text-[11px] uppercase tracking-wider text-blue">
					Components / 02
				</div>
				<h2 class="m-0 mb-[10px] text-[22px] font-extrabold tracking-tight">Badges &amp; status</h2>
				<p class="m-0 text-[14.5px] leading-relaxed text-text-secondary">
					Color as information — never as ornament. Each hue maps to exactly one meaning across the
					entire product.
				</p>
			</div>

			<div class="flex flex-wrap items-center gap-3">
				<span
					class="inline-flex items-center gap-[6px] rounded-full bg-blue/13 px-[9px] py-[4px] text-[11.5px] font-mono font-medium tracking-wide text-blue"
					>Action</span
				>
				<span
					class="inline-flex items-center gap-[6px] rounded-full bg-indigo/15 px-[9px] py-[4px] text-[11.5px] font-mono font-medium tracking-wide text-indigo"
					>AI-assisted</span
				>
				<span
					class="inline-flex items-center gap-[6px] rounded-full bg-success/13 px-[9px] py-[4px] text-[11.5px] font-mono font-medium tracking-wide text-success"
					>Completed</span
				>
				<span
					class="inline-flex items-center gap-[6px] rounded-full bg-warning/14 px-[9px] py-[4px] text-[11.5px] font-mono font-medium tracking-wide text-warning"
					>Needs review</span
				>
				<span
					class="inline-flex items-center gap-[6px] rounded-full bg-danger/13 px-[9px] py-[4px] text-[11.5px] font-mono font-medium tracking-wide text-danger"
					>Failed</span
				>
				<span
					class="inline-flex items-center gap-[6px] rounded-full bg-surface-elevated px-[9px] py-[4px] text-[11.5px] font-mono font-medium tracking-wide text-text-secondary"
					>Draft</span
				>
			</div>
		</section>

		<!-- INPUTS -->
		<section id="inputs" class="border-b border-border px-5 py-12 lg:px-16 lg:py-24">
			<div class="mb-7 max-w-[720px]">
				<div class="mb-[10px] font-mono text-[11px] uppercase tracking-wider text-blue">
					Components / 03
				</div>
				<h2 class="m-0 mb-[10px] text-[22px] font-extrabold tracking-tight">
					Inputs &amp; filters
				</h2>
				<p class="m-0 text-[14.5px] leading-relaxed text-text-secondary">
					Form controls stay quiet — 8px radius, single hairline border, subtle blue on focus.
				</p>
			</div>

			<div class="max-w-[520px] rounded-radius-md border border-border bg-canvas p-5">
				<div class="mb-4">
					<label for="dataset" class="mb-[7px] block text-[12.5px] font-medium text-text-secondary"
						>Dataset</label
					>
					<input
						id="dataset"
						type="text"
						placeholder="Search datasets…"
						class="w-full appearance-none rounded-radius-sm border border-border bg-canvas px-3 py-[10px] font-ui text-[13.5px] text-text-primary transition-[border-color,box-shadow] duration-150 placeholder:text-muted focus:border-blue focus:shadow-[0_0_0_3px_rgba(29,185,84,0.15)] focus:outline-hidden"
					/>
				</div>
				<div class="mb-4">
					<label for="range" class="mb-[7px] block text-[12.5px] font-medium text-text-secondary"
						>Date range</label
					>
					<select
						id="range"
						class="w-full appearance-none rounded-radius-sm border border-border bg-canvas px-3 py-[10px] font-ui text-[13.5px] text-text-primary transition-[border-color,box-shadow] duration-150 focus:border-blue focus:shadow-[0_0_0_3px_rgba(29,185,84,0.15)] focus:outline-hidden"
					>
						<option>Last 7 days</option>
						<option>Last 30 days</option>
						<option>Quarter to date</option>
					</select>
				</div>
				<div class="flex items-center gap-[9px] text-[13px] text-text-secondary">
					<input type="checkbox" id="anomaly" checked class="size-[15px] accent-blue" />
					<label for="anomaly" class="m-0">Flag anomalies automatically</label>
				</div>
			</div>
		</section>

		<!-- CARDS / KPIs -->
		<section id="cards" class="border-b border-border px-5 py-12 lg:px-16 lg:py-24">
			<div class="mb-7 max-w-[720px]">
				<div class="mb-[10px] font-mono text-[11px] uppercase tracking-wider text-blue">
					Components / 04
				</div>
				<h2 class="m-0 mb-[10px] text-[22px] font-extrabold tracking-tight">
					Cards &amp; KPI panels
				</h2>
				<p class="m-0 text-[14.5px] leading-relaxed text-text-secondary">
					Each component lives inside a clearly defined container. The user should instantly
					understand what belongs together.
				</p>
			</div>

			<div class="grid gap-5 md:grid-cols-2 lg:grid-cols-3">
				<div
					class="rounded-radius-md border border-border bg-canvas p-5 transition-shadow hover:shadow-shadow-sm"
				>
					<div class="mt-[2px] text-xs text-muted">Total revenue</div>
					<div class="my-[4px] font-mono text-[30px] font-medium tracking-tight">$1.24M</div>
					<span class="inline-flex items-center gap-1 font-mono text-xs font-medium text-success"
						>▲ 12.4%</span
					>
				</div>
				<div
					class="rounded-radius-md border border-border bg-canvas p-5 transition-shadow hover:shadow-shadow-sm"
				>
					<div class="mt-[2px] text-xs text-muted">Active queries</div>
					<div class="my-[4px] font-mono text-[30px] font-medium tracking-tight">342</div>
					<span class="inline-flex items-center gap-1 font-mono text-xs font-medium text-danger"
						>▼ 3.1%</span
					>
				</div>
				<div
					class="rounded-radius-md border border-border bg-canvas p-5 transition-shadow hover:shadow-shadow-sm"
				>
					<div class="mt-[2px] text-xs text-muted">Model latency</div>
					<div class="my-[4px] font-mono text-[30px] font-medium tracking-tight">
						184<span class="text-[15px] text-muted">ms</span>
					</div>
					<span class="inline-flex items-center gap-1 font-mono text-xs font-medium text-success"
						>▲ 0.8%</span
					>
				</div>
			</div>
		</section>

		<!-- TABLE -->
		<section id="table" class="border-b border-border px-5 py-12 lg:px-16 lg:py-24">
			<div class="mb-7 max-w-[720px]">
				<div class="mb-[10px] font-mono text-[11px] uppercase tracking-wider text-blue">
					Components / 05
				</div>
				<h2 class="m-0 mb-[10px] text-[22px] font-extrabold tracking-tight">Tables</h2>
				<p class="m-0 text-[14.5px] leading-relaxed text-text-secondary">
					High information density, modeled after GitHub and Observable. Rows highlight on hover.
				</p>
			</div>

			<div class="overflow-hidden rounded-radius-md border border-border shadow-shadow-sm">
				<table class="w-full border-collapse">
					<thead>
						<tr class="border-b border-border bg-surface">
							<th
								class="px-4 py-3 text-left text-[11px] font-semibold uppercase tracking-wider text-muted"
								>Model</th
							>
							<th
								class="px-4 py-3 text-left text-[11px] font-semibold uppercase tracking-wider text-muted"
								>Requests</th
							>
							<th
								class="px-4 py-3 text-left text-[11px] font-semibold uppercase tracking-wider text-muted"
								>Avg. latency</th
							>
							<th
								class="px-4 py-3 text-left text-[11px] font-semibold uppercase tracking-wider text-muted"
								>Error rate</th
							>
							<th
								class="px-4 py-3 text-left text-[11px] font-semibold uppercase tracking-wider text-muted"
								>Status</th
							>
						</tr>
					</thead>
					<tbody>
						{#each [{ model: 'llama-3.1-70b', req: '18,204', lat: '142ms', err: '0.02%', status: 'Healthy', badge: 'badge-success' }, { model: 'mixtral-8x7b', req: '9,481', lat: '98ms', err: '0.11%', status: 'Healthy', badge: 'badge-success' }, { model: 'qwen-2.5-32b', req: '3,027', lat: '210ms', err: '1.84%', status: 'Degraded', badge: 'badge-warning' }, { model: 'phi-3-mini', req: '512', lat: '—', err: '100%', status: 'Offline', badge: 'badge-danger' }] as row}
							<tr class="border-b border-border transition-colors last:border-b-0 hover:bg-surface">
								<td class="px-4 py-[13px] text-[13px]">{row.model}</td>
								<td class="px-4 py-[13px] font-mono text-[12.5px] text-text-secondary">{row.req}</td
								>
								<td class="px-4 py-[13px] font-mono text-[12.5px] text-text-secondary">{row.lat}</td
								>
								<td class="px-4 py-[13px] font-mono text-[12.5px] text-text-secondary">{row.err}</td
								>
								<td class="px-4 py-[13px]">
									<span
										class="inline-flex items-center gap-[6px] rounded-full px-[9px] py-[4px] text-[11.5px] font-mono font-medium tracking-wide {row.badge ===
										'badge-success'
											? 'bg-success/13 text-success'
											: row.badge === 'badge-warning'
												? 'bg-warning/14 text-warning'
												: 'bg-danger/13 text-danger'}">{row.status}</span
									>
								</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
		</section>

		<!-- CHARTS -->
		<section id="charts" class="border-b border-border px-5 py-12 lg:px-16 lg:py-24">
			<div class="mb-7 max-w-[720px]">
				<div class="mb-[10px] font-mono text-[11px] uppercase tracking-wider text-blue">
					Components / 06
				</div>
				<h2 class="m-0 mb-[10px] text-[22px] font-extrabold tracking-tight">Data visualization</h2>
				<p class="m-0 text-[14.5px] leading-relaxed text-text-secondary">
					Minimal grid lines. Muted axes. One primary accent color. Highlight only what matters.
				</p>
			</div>

			<div class="grid gap-5 md:grid-cols-2">
				<div class="rounded-radius-md border border-border bg-canvas p-5">
					<div class="mb-4 flex items-center justify-between">
						<div>
							<div class="text-sm font-semibold tracking-tight">Requests per hour</div>
							<div class="mt-[2px] text-xs text-muted">Last 24 hours</div>
						</div>
					</div>
					<div class="mb-4 flex gap-4">
						<div class="flex items-center gap-[7px] text-xs text-text-secondary">
							<span class="size-2 rounded-[2px] bg-blue"></span>Requests
						</div>
						<div class="flex items-center gap-[7px] text-xs text-text-secondary">
							<span class="size-2 rounded-[2px] bg-indigo"></span>Forecast
						</div>
					</div>
					<svg viewBox="0 0 480 200" class="w-full h-[200px] overflow-visible">
						<g stroke="#2A2A2A" stroke-width="1">
							<line x1="0" y1="20" x2="480" y2="20" />
							<line x1="0" y1="70" x2="480" y2="70" />
							<line x1="0" y1="120" x2="480" y2="120" />
							<line x1="0" y1="170" x2="480" y2="170" />
						</g>
						<polyline
							fill="none"
							stroke="#8D87FF"
							stroke-width="2"
							stroke-dasharray="4 4"
							opacity="0.7"
							points="300,110 340,100 380,95 420,80 460,75"
						/>
						<polyline
							fill="none"
							stroke="#1DB954"
							stroke-width="2.5"
							points="0,140 40,130 80,150 120,110 160,120 200,90 240,100 280,85 300,110"
						/>
						<polygon
							fill="url(#areaFade_chart)"
							opacity="0.5"
							points="0,140 40,130 80,150 120,110 160,120 200,90 240,100 280,85 300,110 300,170 0,170"
						/>
						<defs>
							<linearGradient id="areaFade_chart" x1="0" y1="0" x2="0" y2="1">
								<stop offset="0%" stop-color="#1DB954" stop-opacity="0.25" />
								<stop offset="100%" stop-color="#1DB954" stop-opacity="0" />
							</linearGradient>
						</defs>
						<circle cx="280" cy="85" r="4" fill="#1DB954" stroke="#121212" stroke-width="2" />
					</svg>
				</div>

				<div class="rounded-radius-md border border-border bg-canvas p-5">
					<div class="mb-4 flex items-center justify-between">
						<div>
							<div class="text-sm font-semibold tracking-tight">Traffic by endpoint</div>
							<div class="mt-[2px] text-xs text-muted">Share of total requests</div>
						</div>
					</div>
					<div class="mt-2 flex flex-col gap-[14px]">
						{#each [{ label: '/v1/chat/completions', pct: 62, bar: 'bg-blue' }, { label: '/v1/embeddings', pct: 24, bar: 'bg-muted' }, { label: '/v1/models', pct: 9, bar: 'bg-muted' }, { label: '/v1/fine-tunes', pct: 5, bar: 'bg-warning' }] as bar}
							<div>
								<div class="mb-[6px] flex justify-between text-[12.5px]">
									<span class="text-text-secondary">{bar.label}</span>
									<span class="font-mono text-[12.5px] text-text-secondary">{bar.pct}%</span>
								</div>
								<div class="h-[6px] overflow-hidden rounded-full bg-surface-elevated">
									<div class="h-full rounded-full {bar.bar}" style="width:{bar.pct}%"></div>
								</div>
							</div>
						{/each}
					</div>
				</div>
			</div>
		</section>

		<!-- AI PRESENCE -->
		<section id="ai" class="border-b border-border px-5 py-12 lg:px-16 lg:py-24">
			<div class="mb-7 max-w-[720px]">
				<div class="mb-[10px] font-mono text-[11px] uppercase tracking-wider text-blue">
					Components / 07
				</div>
				<h2 class="m-0 mb-[10px] text-[22px] font-extrabold tracking-tight">AI presence</h2>
				<p class="m-0 text-[14.5px] leading-relaxed text-text-secondary">
					The AI is an expert collaborator, not the product. It appears when needed, analyzes,
					explains, then gets out of the way.
				</p>
			</div>

			<div
				class="max-w-[640px] rounded-radius-md border border-indigo/30 bg-canvas p-5 shadow-[0_8px_24px_-10px_rgba(141,135,255,0.18),var(--shadow-sm)]"
			>
				<div class="mb-3 inline-flex items-center gap-[7px] font-mono text-[11px] text-indigo">
					<span class="size-[6px] rounded-full bg-indigo"></span> AI insight
				</div>
				<p class="text-[13.5px] leading-relaxed text-text-primary">
					Error rate for <span
						class="rounded bg-indigo/15 px-[6px] py-[1px] font-mono text-xs text-indigo"
						>qwen-2.5-32b</span
					> increased sharply after the 14:00 deploy. Latency correlates with a spike in prompt length
					— consider reverting the context window change or scaling the batch size down.
				</p>
				<div class="mt-4 flex flex-wrap items-center gap-3">
					<button
						class="inline-flex cursor-pointer appearance-none items-center gap-2 rounded-radius-btn border border-border bg-surface-elevated px-[14px] py-[7px] text-[12.5px] font-bold text-text-primary font-ui transition-all duration-[0.16s] ease-[cubic-bezier(.4,0,.2,1)] active:scale-[0.97] hover:translate-y-[-1px] hover:border-[#3E3E3E] hover:bg-[#2E2E2E] hover:shadow-shadow-sm"
						>View trace</button
					>
					<button
						class="inline-flex cursor-pointer appearance-none items-center gap-2 rounded-radius-btn border border-transparent bg-transparent px-[14px] py-[7px] text-[12.5px] font-bold text-text-secondary font-ui transition-all duration-[0.16s] ease-[cubic-bezier(.4,0,.2,1)] active:scale-[0.97] hover:translate-y-[-1px] hover:bg-surface hover:text-text-primary"
						>Dismiss</button
					>
				</div>
			</div>
		</section>

		<!-- DATASET CONTEXT BAR -->
		<section id="context-bar" class="border-b border-border px-5 py-12 lg:px-16 lg:py-24">
			<div class="mb-7 max-w-[720px]">
				<div class="mb-[10px] font-mono text-[11px] uppercase tracking-wider text-blue">
					Patterns / 01
				</div>
				<h2 class="m-0 mb-[10px] text-[22px] font-extrabold tracking-tight">Dataset context bar</h2>
				<p class="m-0 text-[14.5px] leading-relaxed text-text-secondary">
					Persistent strip above the conversation. It answers the first question any analytical
					session needs: what data am I looking at, and is the agent doing anything right now.
				</p>
			</div>

			<div
				class="flex items-center justify-between gap-[10px] rounded-radius-md border border-border bg-canvas px-4 py-3 shadow-shadow-sm max-lg:flex-col max-lg:items-start"
			>
				<div class="flex items-center gap-[14px] max-sm:flex-col max-sm:items-start">
					<div class="flex items-center gap-[7px] text-[12.5px] text-text-secondary">
						<span class="size-[7px] rounded-[2px] bg-blue"></span> sales_2025.csv
					</div>
					<div class="h-[14px] w-px bg-border max-sm:hidden"></div>
					<div class="text-[12.5px] text-text-secondary">12,430 rows · 18 columns</div>
					<div class="h-[14px] w-px bg-border max-sm:hidden"></div>
					<div class="text-[12.5px] text-text-secondary">Updated 4m ago</div>
				</div>
				<div class="flex items-center gap-[7px] font-mono text-xs text-indigo">
					<span class="size-[7px] rounded-full bg-indigo animate-spinner"></span> Analyzing
				</div>
			</div>
		</section>

		<!-- TOOL EXECUTION TIMELINE -->
		<section id="timeline" class="border-b border-border px-5 py-12 lg:px-16 lg:py-24">
			<div class="mb-7 max-w-[720px]">
				<div class="mb-[10px] font-mono text-[11px] uppercase tracking-wider text-blue">
					Patterns / 02 — Signature component
				</div>
				<h2 class="m-0 mb-[10px] text-[22px] font-extrabold tracking-tight">
					Tool execution timeline
				</h2>
				<p class="m-0 text-[14.5px] leading-relaxed text-text-secondary">
					Replaces a silent "thinking…" state. Each LangGraph tool call becomes one row —
					high-level, never chain-of-thought.
				</p>
			</div>

			<div class="max-w-[560px] overflow-hidden rounded-radius-md border border-border bg-canvas">
				{#each [{ label: 'Reading dataset', marker: 'done', time: '0.4s' }, { label: 'Detecting schema', marker: 'done', time: '0.2s', detail: '18 columns · 4 numeric · 2 datetime · 12 categorical' }, { label: 'Running correlation analysis', marker: 'active', time: '1.1s', detail: 'revenue × region, revenue × discount_rate' }, { label: 'Generating visualization', marker: 'pending' }, { label: 'Preparing response', marker: 'pending' }] as step}
					<div class="flex items-start gap-3 border-b border-border px-4 py-[13px] last:border-b-0">
						{#if step.marker === 'done'}
							<div
								class="mt-[1px] flex size-[18px] shrink-0 items-center justify-center rounded-full bg-success/15 font-mono text-[10px] text-success"
							>
								✓
							</div>
						{:else if step.marker === 'active'}
							<div
								class="mt-[1px] flex size-[18px] shrink-0 items-center justify-center rounded-full bg-blue/15 font-mono text-[10px] text-blue shadow-[0_0_0_3px_rgba(29,185,84,0.12)]"
							>
								●
							</div>
						{:else}
							<div
								class="mt-[1px] flex size-[18px] shrink-0 items-center justify-center rounded-full border border-border bg-surface font-mono text-[10px] text-muted"
							>
								3
							</div>
						{/if}
						<div class="flex-1">
							<div class="flex items-center justify-between text-[13px]">
								<span class={step.marker === 'pending' ? 'text-muted' : 'text-text-primary'}
									>{step.label}</span
								>
								{#if step.time}
									<span class="font-mono text-[11.5px] text-muted">{step.time}</span>
								{/if}
							</div>
							{#if step.detail}
								<div class="mt-[5px] font-mono text-xs leading-relaxed text-text-secondary">
									{step.detail}
								</div>
							{/if}
						</div>
					</div>
				{/each}
			</div>
		</section>

		<!-- CONVERSATION -->
		<section id="conversation" class="border-b border-border px-5 py-12 lg:px-16 lg:py-24">
			<div class="mb-7 max-w-[720px]">
				<div class="mb-[10px] font-mono text-[11px] uppercase tracking-wider text-blue">
					Patterns / 03
				</div>
				<h2 class="m-0 mb-[10px] text-[22px] font-extrabold tracking-tight">Conversation</h2>
				<p class="m-0 text-[14.5px] leading-relaxed text-text-secondary">
					Chat is the primary workspace, not a side panel — this is a conversational analysis tool
					first.
				</p>
			</div>

			<div class="mb-5 flex max-w-[640px] flex-col gap-5">
				<div class="flex justify-end">
					<div
						class="max-w-[72%] rounded-radius-md border border-border bg-surface-elevated px-4 py-4 text-[13.5px] leading-relaxed shadow-shadow-sm"
						style="border-bottom-right-radius:4px"
					>
						Show me a summary of sales_2025.csv
					</div>
				</div>
				<div class="flex">
					<div
						class="max-w-[72%] rounded-radius-md border border-border bg-canvas px-4 py-4 text-[13.5px] leading-relaxed"
						style="border-bottom-left-radius:4px"
					>
						<div class="mb-2 flex items-center gap-2 font-mono text-[11px] text-muted">
							Data Analyst Agent · 2.3s
						</div>
						The dataset contains<strong>12,430 rows</strong> and <strong>18 columns</strong>. Here's
						the overview:
						<table class="my-3 w-full border-collapse text-xs">
							<thead>
								<tr>
									<th>Column</th>
									<th>Type</th>
									<th>Nulls</th>
									<th>Unique</th>
								</tr>
							</thead>
							<tbody>
								<tr
									><td>date</td><td class="font-mono text-[12.5px] text-text-secondary">datetime</td
									><td class="font-mono text-[12.5px] text-text-secondary">0</td><td
										class="font-mono text-[12.5px] text-text-secondary">456</td
									></tr
								>
								<tr
									><td>revenue</td><td class="font-mono text-[12.5px] text-text-secondary">float</td
									><td class="font-mono text-[12.5px] text-text-secondary">23</td><td
										class="font-mono text-[12.5px] text-text-secondary">1,200</td
									></tr
								>
								<tr
									><td>region</td><td class="font-mono text-[12.5px] text-text-secondary">string</td
									><td class="font-mono text-[12.5px] text-text-secondary">0</td><td
										class="font-mono text-[12.5px] text-text-secondary">5</td
									></tr
								>
							</tbody>
						</table>
						<div class="mt-3 flex gap-2">
							<button
								class="inline-flex cursor-pointer appearance-none items-center gap-2 rounded-radius-btn border border-border bg-surface-elevated px-[14px] py-[7px] text-[12.5px] font-bold text-text-primary font-ui transition-all duration-[0.16s] ease-[cubic-bezier(.4,0,.2,1)] active:scale-[0.97] hover:translate-y-[-1px] hover:border-[#3E3E3E] hover:bg-[#2E2E2E] hover:shadow-shadow-sm"
								>View chart</button
							>
							<button
								class="inline-flex cursor-pointer appearance-none items-center gap-2 rounded-radius-btn border border-transparent bg-transparent px-[14px] py-[7px] text-[12.5px] font-bold text-text-secondary font-ui transition-all duration-[0.16s] ease-[cubic-bezier(.4,0,.2,1)] active:scale-[0.97] hover:translate-y-[-1px] hover:bg-surface hover:text-text-primary"
								>Export</button
							>
							<button
								class="inline-flex cursor-pointer appearance-none items-center gap-2 rounded-radius-btn border border-transparent bg-transparent px-[14px] py-[7px] text-[12.5px] font-bold text-text-secondary font-ui transition-all duration-[0.16s] ease-[cubic-bezier(.4,0,.2,1)] active:scale-[0.97] hover:translate-y-[-1px] hover:bg-surface hover:text-text-primary"
								>Explore</button
							>
						</div>
					</div>
				</div>
			</div>

			<div
				class="flex max-w-[640px] items-center gap-2 rounded-radius-md border border-border bg-canvas px-4 py-[10px] shadow-shadow-sm transition-shadow focus-within:border-blue focus-within:shadow-shadow-md"
			>
				<input
					type="text"
					placeholder="Ask something about your dataset…"
					class="flex-1 bg-transparent font-ui text-[13.5px] text-text-primary outline-none placeholder:text-muted"
				/>
				<button
					class="inline-flex cursor-pointer appearance-none items-center gap-2 rounded-radius-btn border border-transparent bg-blue px-[14px] py-[7px] text-[12.5px] font-bold text-[#0A0A0A] font-ui shadow-shadow-sm shadow-[inset_0_1px_0_rgba(255,255,255,0.12)] transition-all duration-[0.16s] ease-[cubic-bezier(.4,0,.2,1)] active:scale-[0.97] hover:translate-y-[-1px] hover:bg-[#1ED760] hover:shadow-shadow-md hover:shadow-[inset_0_1px_0_rgba(255,255,255,0.14)]"
					>Send</button
				>
			</div>
		</section>

		<!-- QUICK PROMPTS -->
		<section id="prompts" class="border-b border-border px-5 py-12 lg:px-16 lg:py-24">
			<div class="mb-7 max-w-[720px]">
				<div class="mb-[10px] font-mono text-[11px] uppercase tracking-wider text-blue">
					Patterns / 04
				</div>
				<h2 class="m-0 mb-[10px] text-[22px] font-extrabold tracking-tight">Quick prompts</h2>
				<p class="m-0 text-[14.5px] leading-relaxed text-text-secondary">
					Lower the cost of the first question. Shown above the composer on an empty thread or after
					a dataset upload.
				</p>
			</div>

			<div class="flex flex-wrap items-center gap-3">
				{#each ['Summarize this dataset', 'Chart revenue by region', 'Find outliers', 'Correlation between price and sales'] as prompt}
					<div
						class="inline-flex cursor-default items-center gap-2 rounded-full border border-border bg-canvas px-4 py-2 text-[12.5px] text-text-secondary transition-colors hover:border-blue hover:text-text-primary hover:shadow-shadow-sm"
					>
						<span class="font-mono text-[11px] text-muted">
							{prompt === 'Summarize this dataset'
								? '▤'
								: prompt === 'Chart revenue by region'
									? '▥'
									: prompt === 'Find outliers'
										? '◈'
										: '∿'}
						</span>
						{prompt}
					</div>
				{/each}
			</div>
		</section>

		<!-- UPLOAD -->
		<section id="upload" class="border-b border-border px-5 py-12 lg:px-16 lg:py-24">
			<div class="mb-7 max-w-[720px]">
				<div class="mb-[10px] font-mono text-[11px] uppercase tracking-wider text-blue">
					Patterns / 05
				</div>
				<h2 class="m-0 mb-[10px] text-[22px] font-extrabold tracking-tight">Dataset upload</h2>
				<p class="m-0 text-[14.5px] leading-relaxed text-text-secondary">
					The dropzone is quiet until it matters — a hairline dash, not an illustration.
				</p>
			</div>

			<div
				class="max-w-[520px] rounded-radius-md border border-dashed border-border bg-canvas px-5 py-7 text-center transition-colors hover:border-blue hover:bg-blue/[3%] hover:shadow-shadow-sm"
			>
				<div
					class="mx-auto mb-4 flex size-9 items-center justify-center rounded-radius-sm border border-border bg-surface-elevated font-mono text-sm text-blue"
				>
					↑
				</div>
				<div class="mb-1 text-[13.5px] font-medium">Drop a dataset here, or browse</div>
				<div class="text-xs text-muted">CSV, Excel, JSON, or Parquet · up to 100MB</div>
			</div>
		</section>

		<!-- DATA EXPLORER -->
		<section id="explorer" class="border-b border-border px-5 py-12 lg:px-16 lg:py-24">
			<div class="mb-7 max-w-[720px]">
				<div class="mb-[10px] font-mono text-[11px] uppercase tracking-wider text-blue">
					Patterns / 06
				</div>
				<h2 class="m-0 mb-[10px] text-[22px] font-extrabold tracking-tight">
					Data explorer split view
				</h2>
				<p class="m-0 text-[14.5px] leading-relaxed text-text-secondary">
					Opens beside the conversation for the professional-workspace phase of the roadmap.
				</p>
			</div>

			<div
				class="grid min-h-[320px] grid-cols-1 overflow-hidden rounded-radius-md border border-border shadow-shadow-sm md:grid-cols-[1fr_1.5fr]"
				style="gap:1px; background:var(--color-border)"
			>
				<div class="bg-canvas p-4">
					<div class="mb-4 flex items-center justify-between">
						<div class="text-[13px] font-semibold tracking-tight">Columns</div>
						<span
							class="inline-flex items-center gap-[6px] rounded-full bg-surface-elevated px-[9px] py-[4px] text-[11.5px] font-mono font-medium tracking-wide text-text-secondary"
							>18</span
						>
					</div>
					{#each [{ name: 'date', w: 92 }, { name: 'revenue', w: 78, bar: 'bg-blue' }, { name: 'region', w: 40 }, { name: 'discount_rate', w: 22, bar: 'bg-warning' }] as col}
						<div
							class="flex items-center justify-between border-b border-border py-[9px] text-[12.5px] last:border-b-0"
						>
							<span>{col.name}</span>
							<div class="h-[5px] w-20 overflow-hidden rounded-full bg-surface-elevated">
								<span
									class="block h-full rounded-full {col.bar ?? 'bg-blue'}"
									style="width:{col.w}%"
								></span>
							</div>
						</div>
					{/each}
				</div>
				<div class="bg-canvas p-4">
					<div class="mb-4 flex items-center justify-between">
						<div class="text-[13px] font-semibold tracking-tight">Revenue by region</div>
						<span
							class="inline-flex items-center gap-[6px] rounded-full bg-blue/13 px-[9px] py-[4px] text-[11.5px] font-mono font-medium tracking-wide text-blue"
							>Chart</span
						>
					</div>
					<svg viewBox="0 0 400 160" class="w-full h-40">
						<g stroke="#2A2A2A" stroke-width="1">
							<line x1="0" y1="10" x2="400" y2="10" />
							<line x1="0" y1="60" x2="400" y2="60" />
							<line x1="0" y1="110" x2="400" y2="110" />
							<line x1="0" y1="150" x2="400" y2="150" />
						</g>
						<rect x="20" y="50" width="48" height="100" fill="#1DB954" />
						<rect x="100" y="70" width="48" height="80" fill="#1DB954" opacity="0.75" />
						<rect x="180" y="95" width="48" height="55" fill="#1DB954" opacity="0.55" />
						<rect x="260" y="115" width="48" height="35" fill="#1DB954" opacity="0.4" />
					</svg>
				</div>
			</div>
		</section>

		<!-- FOOTER -->
		<div
			class="flex items-center justify-between px-5 py-7 font-mono text-[12.5px] text-muted lg:px-16 lg:py-8"
		>
			<div>analytical-workspace / design-system</div>
			<div>dark-first · v1.1 — conversational patterns</div>
		</div>
	</main>
</div>
