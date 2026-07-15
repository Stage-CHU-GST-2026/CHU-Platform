import type { Agent, Conversation, Dataset, Report, KnowledgeDoc, Notification } from '$lib/types';

export const mockAgents: Agent[] = [
    {
        id: '1',
        name: 'Clinical Data Analyzer',
        description: 'Analyzes structured clinical data and extracts insights.',
        icon: 'IconStethoscope',
        status: 'active',
        capabilities: ['Data Mining', 'Trend Analysis', 'Predictive Modeling'],
        formats: ['FHIR', 'HL7', 'CSV'],
        workload: 78,
        queue: 3,
        avgExecutionTime: '4.2s',
        health: 98,
        tools: ['SQL Database', 'FHIR API'],
        category: 'Analysis',
        lastRun: '3 mins ago'
    },
    {
        id: '2',
        name: 'Medical Knowledge Assistant',
        description: 'Answers questions based on indexed medical literature.',
        icon: 'IconBook',
        status: 'active',
        capabilities: ['Literature Review', 'Guideline Lookup', 'Differential Diagnosis'],
        formats: ['PDF', 'TXT'],
        workload: 45,
        queue: 1,
        avgExecutionTime: '1.5s',
        health: 100,
        tools: ['Vector Database', 'PubMed Search'],
        category: 'Knowledge',
        lastRun: '12 mins ago'
    },
    {
        id: '3',
        name: 'Report Generator',
        description: 'Drafts comprehensive reports from raw analytical results.',
        icon: 'IconReport',
        status: 'processing',
        capabilities: ['Summarization', 'Template Filling', 'Formatting'],
        formats: ['JSON', 'CSV'],
        workload: 92,
        queue: 8,
        avgExecutionTime: '12.4s',
        health: 85,
        tools: ['Document Service', 'PDF Export'],
        category: 'Reporting',
        lastRun: 'Just now'
    },
    {
        id: '4',
        name: 'Document Analyzer',
        description: 'Extracts entities and relationships from free-text documents.',
        icon: 'IconFileText',
        status: 'active',
        capabilities: ['NLP', 'Entity Extraction', 'Sentiment Analysis'],
        formats: ['PDF', 'DOCX', 'TXT'],
        workload: 31,
        queue: 0,
        avgExecutionTime: '2.8s',
        health: 99,
        tools: ['OCR', 'NLP Pipeline'],
        category: 'Document',
        lastRun: '1 hour ago'
    },
    {
        id: '5',
        name: 'Visualization Agent',
        description: 'Generates interactive charts and graphs from datasets.',
        icon: 'IconChartBar',
        status: 'idle',
        capabilities: ['Charting', 'Data Aggregation', 'Dashboard Design'],
        formats: ['CSV', 'JSON'],
        workload: 0,
        queue: 0,
        avgExecutionTime: '3.1s',
        health: 100,
        tools: ['Plotly', 'D3'],
        category: 'Analytics',
        lastRun: '4 hours ago'
    },
    {
        id: '6',
        name: 'Research Assistant',
        description: 'Gathers and synthesizes information for clinical research.',
        icon: 'IconMicroscope',
        status: 'active',
        capabilities: ['Synthesis', 'Fact Checking', 'Drafting'],
        formats: ['PDF', 'TXT'],
        workload: 12,
        queue: 0,
        avgExecutionTime: '5.5s',
        health: 100,
        tools: ['Web Search', 'Vector Database'],
        category: 'Research',
        lastRun: '2 hours ago'
    },
    {
        id: '7',
        name: 'SQL Analyst',
        description: 'Converts natural language questions into executable SQL queries.',
        icon: 'IconDatabase',
        status: 'idle',
        capabilities: ['Text-to-SQL', 'Query Optimization', 'Schema Understanding'],
        formats: ['Natural Language'],
        workload: 0,
        queue: 0,
        avgExecutionTime: '1.2s',
        health: 100,
        tools: ['Database Connection', 'Schema Registry'],
        category: 'Data',
        lastRun: 'Yesterday'
    },
    {
        id: '8',
        name: 'Audit & Compliance Reviewer',
        description: 'Checks documentation and logs for compliance with hospital policies.',
        icon: 'IconShieldCheck',
        status: 'error',
        capabilities: ['Rule Checking', 'Anomaly Detection', 'Log Analysis'],
        formats: ['CSV', 'JSON', 'HL7'],
        workload: 0,
        queue: 0,
        avgExecutionTime: 'N/A',
        health: 40,
        tools: ['Rules Engine'],
        category: 'Compliance',
        lastRun: '2 days ago'
    }
];

export const mockConversations: Conversation[] = [
    {
        id: 'c1',
        title: 'Patient Admission Trends',
        agentId: '1', // Clinical Data Analyzer
        createdAt: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString(),
        updatedAt: new Date(Date.now() - 1000 * 60 * 30).toISOString(),
        status: 'active',
        pinned: true,
        messages: [
            {
                id: 'm1',
                role: 'user',
                content: 'Can you show me the patient admission trends for the last quarter?',
                timestamp: new Date(Date.now() - 1000 * 60 * 45).toISOString()
            },
            {
                id: 'm2',
                role: 'assistant',
                content: 'I have analyzed the admission data for Q2 2026. Overall admissions increased by 4.2% compared to Q1.',
                timestamp: new Date(Date.now() - 1000 * 60 * 44).toISOString(),
                artifacts: [
                    {
                        id: 'a1',
                        type: 'chart',
                        title: 'Admissions Q2',
                        content: 'bar_chart_data'
                    }
                ]
            }
        ]
    },
    {
        id: 'c2',
        title: 'Lab Results Interpretation',
        agentId: '2',
        createdAt: new Date(Date.now() - 1000 * 60 * 60 * 24).toISOString(),
        updatedAt: new Date(Date.now() - 1000 * 60 * 60 * 24).toISOString(),
        status: 'archived',
        messages: []
    }
];

export const mockDatasets: Dataset[] = [
    {
        id: 'd1',
        name: 'patient_records_q2.csv',
        type: 'tabular',
        rows: 1245000,
        size: '245 MB',
        quality: 94,
        status: 'ready',
        updatedAt: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString(),
        columns: [
            { name: 'patient_id', type: 'string', nullable: false, unique: 100, sample: ['P1029', 'P9382'] },
            { name: 'admission_date', type: 'date', nullable: false, unique: 80, sample: ['2026-04-01', '2026-04-02'] },
            { name: 'diagnosis_code', type: 'string', nullable: true, unique: 15, sample: ['I10', 'E11.9'] }
        ]
    },
    {
        id: 'd2',
        name: 'lab_results_history.json',
        type: 'tabular',
        rows: 8500000,
        size: '1.2 GB',
        quality: 88,
        status: 'processing',
        updatedAt: new Date(Date.now() - 1000 * 60 * 30).toISOString(),
        columns: []
    }
];

export const mockReports: Report[] = [
    {
        id: 'r1',
        title: 'Q2 Hospital Throughput Analysis',
        agentId: '3',
        authorName: 'Dr. Sarah Jenkins',
        summary: 'A comprehensive review of ER wait times, admission delays, and discharge rates for Q2 2026.',
        content: '# Q2 Throughput Analysis\n\n...',
        tags: ['Quarterly', 'Throughput', 'ER'],
        status: 'published',
        type: 'Summary',
        createdAt: new Date(Date.now() - 1000 * 60 * 60 * 24 * 2).toISOString()
    }
];

export const mockKnowledgeDocs: KnowledgeDoc[] = [
    {
        id: 'k1',
        name: 'Standard Treatment Guidelines 2026.pdf',
        type: 'PDF',
        tags: ['Guidelines', 'Clinical'],
        embeddingStatus: 'indexed',
        lastIndexed: new Date(Date.now() - 1000 * 60 * 60 * 24 * 5).toISOString(),
        chunks: 1247,
        size: '4.2 MB'
    },
    {
        id: 'k2',
        name: 'New Compliance Protocols.docx',
        type: 'DOCX',
        tags: ['Policy', 'Compliance'],
        embeddingStatus: 'processing',
        lastIndexed: new Date(Date.now()).toISOString(),
        chunks: 0,
        size: '1.1 MB'
    }
];

export const mockNotifications: Notification[] = [
    {
        id: 'n1',
        title: 'Dataset Indexed',
        body: 'patient_records_q2.csv is now ready for analysis.',
        type: 'success',
        read: false,
        timestamp: new Date(Date.now() - 1000 * 60 * 5).toISOString()
    },
    {
        id: 'n2',
        title: 'Report Generated',
        body: 'Q2 Hospital Throughput Analysis has been finalized.',
        type: 'info',
        read: true,
        timestamp: new Date(Date.now() - 1000 * 60 * 60 * 48).toISOString()
    }
];
