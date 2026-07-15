<script lang="ts">
    import { marked } from 'marked';
    import { browser } from '$app/environment';
    import { IconChevronDown, IconPlus, IconMicrophone, IconSparkles, IconUser } from '@tabler/icons-svelte';

    // Configure marked for clean output
    marked.setOptions({ breaks: true, gfm: true });

    async function renderMd(content: string): Promise<string> {
        const html = marked.parse(content) as string;
        if (browser) {
            const DOMPurify = (await import('dompurify')).default;
            return DOMPurify.sanitize(html, {
                ADD_TAGS: ['img'],
                ADD_ATTR: ['src', 'alt', 'title', 'href', 'target', 'rel']
            });
        }
        return html;
    }

    let messages = $state([
        {
            role: 'user',
            content: 'Can you analyze the patient admission trends in our latest Q2 dataset and give me a summary with key insights?'
        },
        {
            role: 'agent',
            content: `Sure! Here's a summary of the **Q2 Patient Admission Trends** based on the latest export:

## Key Metrics

| Metric | Q1 | Q2 | Change |
|---|---|---|---|
| Total Admissions | 4,821 | 5,340 | +10.8% |
| Emergency Admissions | 1,203 | 1,489 | +23.8% |
| Avg. Stay (days) | 4.2 | 3.9 | -7.1% |
| Readmission Rate | 8.3% | 7.6% | -8.4% |

## Key Insights

1. **Emergency admissions spiked** by nearly 24%, likely correlated with the seasonal flu wave in April-May. Cross-referencing with the respiratory diagnosis codes confirms this.

2. **Average length of stay decreased** from 4.2 to 3.9 days — a positive efficiency gain, likely due to the new discharge protocols introduced in March.

3. **Readmission rates improved**, dropping from 8.3% to 7.6%. This is a strong indicator that post-care follow-up programs are working.

4. **Cardiology and Orthopedics** departments saw the highest volume growth (+18% and +15% respectively).

## Recommendations

- Increase emergency bed capacity or staffing ahead of Q3, given the trend.
- Investigate outlier cases where stay > 7 days to find further efficiency opportunities.
- Expand the follow-up program to the top 3 readmission-prone departments.

> **Note:** This analysis is based on aggregate data only. Individual patient records were not accessed.`
        },
        {
            role: 'user',
            content: 'Great! Can you generate a quick Python snippet to visualize the admissions trend over time?'
        },
        {
            role: 'agent',
            content: `Of course! Here's a simple \`matplotlib\` snippet to visualize monthly admissions:

\`\`\`python
import matplotlib.pyplot as plt
import pandas as pd

# Sample data (replace with your actual export)
data = {
    'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
    'Admissions': [1580, 1620, 1621, 1720, 1780, 1840],
    'Emergency': [390, 405, 408, 480, 510, 499],
}

df = pd.DataFrame(data)

fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(df['Month'], df['Admissions'], marker='o', label='Total', linewidth=2, color='#1db954')
ax.plot(df['Month'], df['Emergency'], marker='s', label='Emergency', linewidth=2, color='#f0555c', linestyle='--')

ax.set_title('Q2 Patient Admissions Trend', fontsize=14, fontweight='bold')
ax.set_xlabel('Month')
ax.set_ylabel('Admissions')
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('q2_admissions.png', dpi=150)
plt.show()
\`\`\`

Run this with your actual data loaded into the \`data\` dict (or from a \`pd.read_csv()\` call) and you'll get a clean trend chart saved as \`q2_admissions.png\`.

Want me to adapt this to pull directly from your database export?`
        },
        {
            role: 'user',
            content: 'Yes please! Also show me what the output chart typically looks like.'
        },
        {
            role: 'agent',
            content: `Sure! Here's what a typical air quality / time-series output chart looks like from pandas + matplotlib — very similar to what your admissions chart will produce:

![Pandas time-series chart example](https://pandas.pydata.org/docs/_images/04_airqual_quick.png)

*Example from the [pandas documentation](https://pandas.pydata.org/docs/getting_started/intro_tutorials/04_plotting.html) — shows a multi-line time-series plot, exactly the pattern we're using.*

---

Here's the adapted version that pulls directly from your database export file:

\`\`\`python
import pandas as pd
import matplotlib.pyplot as plt

# Load directly from your CSV export
df = pd.read_csv('chu_admissions_q2.csv', parse_dates=['date'])
df = df.set_index('date').resample('M').sum()

fig, axes = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

df['total_admissions'].plot(ax=axes[0], color='#1db954', linewidth=2, marker='o', label='Total')
axes[0].set_title('Monthly Total Admissions')
axes[0].set_ylabel('Count')
axes[0].legend()
axes[0].grid(alpha=0.2)

df['emergency_admissions'].plot(ax=axes[1], color='#f0555c', linewidth=2, marker='s', linestyle='--', label='Emergency')
axes[1].set_title('Monthly Emergency Admissions')
axes[1].set_ylabel('Count')
axes[1].legend()
axes[1].grid(alpha=0.2)

plt.tight_layout()
plt.savefig('chu_q2_report.png', dpi=150, bbox_inches='tight')
plt.show()
\`\`\`

> **Tip:** Make sure your CSV has at minimum a \`date\`, \`total_admissions\`, and \`emergency_admissions\` column. Run \`df.dtypes\` first to confirm the schema.`
        },
        {
            role: 'user',
            content: 'Perfect. Now can you outline the full data pipeline we need to set up for automated weekly reporting?'
        },
        {
            role: 'agent',
            content: `Great question. Here's a full outline of the **Automated Weekly Reporting Pipeline** for CHU Analytics:

---

## Architecture Overview

\`\`\`
[Database]  →  [ETL Job]  →  [Data Lake]  →  [Analysis Engine]  →  [Report Generator]  →  [Distribution]
  PostgreSQL     Airflow       S3 / MinIO       pandas / dbt          Jinja2 / PDF           Email / Slack
\`\`\`

---

## Phase 1 — Data Extraction

- **Source:** PostgreSQL \`admissions\`, \`patients\`, \`departments\` tables
- **Tool:** Apache Airflow DAG scheduled every **Monday at 06:00**
- **Steps:**
  1. Connect via \`psycopg2\` with read-only credentials
  2. Run parameterized SQL for the trailing 7-day window
  3. Validate row counts and null rates
  4. Write raw parquet to \`s3://chu-datalake/raw/YYYY-WW/\`

## Phase 2 — Transformation

Use **dbt** models to produce clean, tested aggregations:

| Model | Description | Grain |
|---|---|---|
| \`stg_admissions\` | Cleaned admission records | 1 row / admission |
| \`fct_weekly_admissions\` | Aggregated by week + dept | 1 row / week / dept |
| \`fct_readmissions\` | Patients readmitted within 30d | 1 row / patient |
| \`dim_departments\` | Department reference data | 1 row / dept |

## Phase 3 — Report Generation

\`\`\`python
from jinja2 import Environment, FileSystemLoader
import pdfkit

env = Environment(loader=FileSystemLoader('templates/'))
template = env.get_template('weekly_report.html')

html = template.render(
    week=week_label,
    total=df['total_admissions'].sum(),
    emergency_pct=emergency_rate,
    top_dept=df.groupby('dept')['admissions'].sum().idxmax(),
    chart_path='charts/weekly_trend.png'
)

pdfkit.from_string(html, f'reports/CHU_Weekly_{week_label}.pdf')
\`\`\`

## Phase 4 — Distribution

- ✅ Email via **SendGrid API** to department heads
- ✅ Post summary card to **Slack** \`#analytics\` channel
- ✅ Upload PDF to **SharePoint** document library
- ⬜ Interactive dashboard link (in progress)

---

> **Reference:** See the [Airflow DAG documentation](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/dags.html) and [dbt best practices guide](https://docs.getdbt.com/guides/best-practices) for implementation details.`
        },
        {
            role: 'user',
            content: 'What are the risks and how do we mitigate them?'
        },
        {
            role: 'agent',
            content: `Here's a risk assessment for the pipeline:

## Risk Matrix

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| DB connection failure | Medium | High | Retry logic + alerting |
| Schema drift | Low | High | dbt schema tests on every run |
| Stale data in report | Low | Medium | Freshness checks + SLA alerts |
| PII exposure in exports | Low | Critical | Column-level masking + audit log |
| Pipeline lag > 2h | Medium | Medium | Airflow SLA miss callbacks |

---

## Mitigation Strategies

### 1. Resilient Connections
\`\`\`python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def fetch_admissions(conn, week_start: str):
    ...
\`\`\`

### 2. Data Quality Gates

Run these dbt tests before any report generates:

- \`not_null\` on \`admission_id\`, \`patient_id\`, \`dept_code\`
- \`accepted_values\` for \`admission_type\` in \`['emergency', 'elective', 'transfer']\`
- \`relationships\` between \`fct_admissions\` → \`dim_departments\`

### 3. PII Handling

> ⚠️ **Critical:** Patient \`name\`, \`DOB\`, and \`NIN\` fields must **never** appear in exported CSVs or reports. Use the \`anonymize()\` transformer in the ETL step.

All columns are masked at extraction time:

\`\`\`sql
SELECT
    md5(patient_id::text) AS patient_hash,  -- anonymized
    admission_date,
    dept_code,
    admission_type,
    length_of_stay_days
FROM admissions
WHERE admission_date >= :week_start
\`\`\`

---

*Last reviewed: Q2 2026 · Owner: CHU Analytics Team · Status: **In Review***`
        }
    ]);

</script>

<div class="absolute inset-0 flex flex-col bg-canvas">
    <!-- Chat History Area -->
    <div class="flex-1 overflow-y-auto p-4 md:p-8 flex flex-col items-center">
        <div class="w-full max-w-[880px] flex flex-col gap-6 mt-4 pb-4">
            {#each messages as msg}
                {#if msg.role === 'user'}
                    <!-- User message -->
                    <div class="flex justify-end w-full">
                        <div class="flex items-end gap-3 max-w-[85%]">
                            <div class="bg-surface-elevated border border-border-subtle text-text-primary rounded-2xl rounded-br-sm px-4 py-3 text-[15px] leading-relaxed">
                                {msg.content}
                            </div>
                            <div class="w-7 h-7 rounded-full bg-surface-elevated border border-border flex items-center justify-center text-text-secondary shrink-0">
                                <IconUser size={14} stroke={1.5} />
                            </div>
                        </div>
                    </div>
                {:else}
                    <!-- Agent message -->
                    <div class="flex items-start gap-3 w-full">
                        <div class="w-7 h-7 rounded-full bg-surface-elevated border border-border flex items-center justify-center text-accent shrink-0 mt-1">
                            <IconSparkles size={14} stroke={1.5} />
                        </div>
                        <div class="flex-1 min-w-0 prose-agent text-[15px] leading-relaxed text-text-primary">
                            {#await renderMd(msg.content) then html}
                                {@html html}
                            {/await}
                        </div>
                    </div>
                {/if}
            {/each}
        </div>
    </div>

    <!-- Pinned Input Area -->
    <div class="w-full p-4 pb-6 flex justify-center shrink-0 border-t border-border-subtle">
        <div class="w-full max-w-[880px] bg-surface border border-border-subtle rounded-[14px] overflow-hidden flex items-center gap-2 px-3 shadow-sm focus-within:border-border transition-colors">
            
            <!-- Add button -->
            <button class="w-6 h-6 flex items-center justify-center rounded-md hover:bg-surface-hover text-text-secondary hover:text-text-primary transition-colors shrink-0" aria-label="Add attachment">
                <IconPlus size={16} stroke={2} />
            </button>

            <!-- Textarea (grows in the middle) -->
            <textarea 
                class="flex-1 bg-transparent text-text-primary placeholder-muted resize-none focus:outline-none focus:ring-0 border-0 shadow-none p-0 text-[14px] leading-relaxed max-h-36 overflow-y-auto py-3"
                placeholder="Ask anything, @ to mention, / for actions"
                rows="1"
                oninput={(e) => {
                    const target = e.currentTarget;
                    target.style.height = 'auto';
                    target.style.height = target.scrollHeight + 'px';
                }}
            ></textarea>

            <!-- Right side: model selector + mic -->
            <div class="flex items-center gap-1 shrink-0">
                <button class="flex items-center gap-1.5 px-2 h-6 rounded-md hover:bg-surface-hover text-text-secondary hover:text-text-primary transition-colors text-[12px] font-medium">
                    <IconSparkles size={13} stroke={1.5} />
                    Gemini 3.1 Pro
                    <IconChevronDown size={13} stroke={2} class="opacity-70" />
                </button>

                <button class="w-6 h-6 flex items-center justify-center rounded-full bg-surface-elevated hover:bg-border text-text-secondary hover:text-text-primary transition-colors" aria-label="Voice input">
                    <IconMicrophone size={15} stroke={1.5} />
                </button>
            </div>

        </div>
    </div>

</div>

<style>
    /* Scoped prose styles for agent markdown output */
    .prose-agent :global(h1),
    .prose-agent :global(h2),
    .prose-agent :global(h3) {
        color: var(--color-text-primary);
        font-weight: 600;
        margin-top: 1.2em;
        margin-bottom: 0.5em;
    }
    .prose-agent :global(h1) { font-size: 1.2em; }
    .prose-agent :global(h2) { font-size: 1.05em; }
    .prose-agent :global(h3) { font-size: 0.95em; }

    .prose-agent :global(p) {
        margin: 0.5em 0;
        color: var(--color-text-primary);
    }

    .prose-agent :global(ul),
    .prose-agent :global(ol) {
        padding-left: 1.4em;
        margin: 0.5em 0;
        color: var(--color-text-primary);
    }

    .prose-agent :global(li) {
        margin: 0.25em 0;
    }

    .prose-agent :global(code) {
        background: var(--color-surface-elevated);
        color: var(--color-accent);
        padding: 0.15em 0.4em;
        border-radius: 4px;
        font-family: var(--font-mono);
        font-size: 0.875em;
        border: 1px solid var(--color-border);
    }

    .prose-agent :global(pre) {
        background: var(--color-surface-elevated);
        border: 1px solid var(--color-border);
        border-radius: 10px;
        padding: 1em 1.2em;
        overflow-x: auto;
        margin: 0.75em 0;
    }

    .prose-agent :global(pre code) {
        background: transparent;
        border: none;
        padding: 0;
        color: var(--color-text-secondary);
        font-size: 0.85em;
    }

    .prose-agent :global(table) {
        width: 100%;
        border-collapse: collapse;
        margin: 0.75em 0;
        font-size: 0.9em;
    }

    .prose-agent :global(th) {
        background: var(--color-surface-elevated);
        color: var(--color-text-secondary);
        font-weight: 600;
        text-align: left;
        padding: 0.5em 0.75em;
        border: 1px solid var(--color-border);
        font-size: 0.85em;
    }

    .prose-agent :global(td) {
        padding: 0.45em 0.75em;
        border: 1px solid var(--color-border-subtle);
        color: var(--color-text-primary);
    }

    .prose-agent :global(tr:nth-child(even) td) {
        background: var(--color-surface);
    }

    .prose-agent :global(blockquote) {
        border-left: 3px solid var(--color-accent);
        margin: 0.75em 0;
        padding: 0.5em 1em;
        background: var(--color-surface);
        border-radius: 0 8px 8px 0;
        color: var(--color-text-secondary);
        font-size: 0.9em;
    }

    .prose-agent :global(strong) {
        color: var(--color-text-primary);
        font-weight: 600;
    }

    .prose-agent :global(a) {
        color: var(--color-accent);
        text-decoration: underline;
        text-underline-offset: 2px;
    }

    .prose-agent :global(img) {
        max-width: 100%;
        border-radius: 10px;
        border: 1px solid var(--color-border);
        margin: 0.75em 0;
        display: block;
    }

    .prose-agent :global(hr) {
        border: none;
        border-top: 1px solid var(--color-border-subtle);
        margin: 1.2em 0;
    }

    .prose-agent :global(em) {
        color: var(--color-text-secondary);
        font-style: italic;
    }
</style>
