export type AgentStatus = 'active' | 'idle' | 'error' | 'processing';

export type Agent = {
    id: string;
    name: string;
    description: string;
    icon: string;
    status: AgentStatus;
    capabilities: string[];
    formats: string[];
    workload: number;
    queue: number;
    avgExecutionTime: string;
    health: number;
    tools: string[];
    category: string;
    lastRun: string;
};

export type MessageRole = 'user' | 'assistant' | 'system' | 'tool';

export type Artifact = {
    id: string;
    type: 'table' | 'code' | 'chart' | 'file' | 'report';
    title: string;
    content: string;
    language?: string;
};

export type Citation = { ref: number; source: string; excerpt: string; url?: string };

export type Message = {
    id: string;
    role: MessageRole;
    content: string;
    timestamp: string;
    thinking?: boolean;
    citations?: Citation[];
    artifacts?: Artifact[];
    toolName?: string;
    toolStatus?: 'running' | 'done' | 'error';
};

export type Conversation = {
    id: string;
    title: string;
    agentId: string;
    messages: Message[];
    createdAt: string;
    updatedAt: string;
    status: 'active' | 'archived' | 'draft';
    pinned?: boolean;
};

export type ColumnType = 'string' | 'number' | 'boolean' | 'date' | 'null';

export type DatasetColumn = {
    name: string;
    type: ColumnType;
    nullable: boolean;
    unique: number;
    sample: string[];
};

export type Dataset = {
    id: string;
    name: string;
    type: 'tabular' | 'text' | 'fhir' | 'hl7' | 'dicom';
    rows: number;
    size: string;
    quality: number;
    status: 'ready' | 'processing' | 'failed';
    updatedAt: string;
    columns: DatasetColumn[];
};

export type Report = {
    id: string;
    title: string;
    agentId: string;
    authorName: string;
    authorAvatar?: string;
    summary: string;
    content: string;
    tags: string[];
    status: 'draft' | 'published';
    type: string;
    datasetId?: string;
    createdAt: string;
};

export type KnowledgeDoc = {
    id: string;
    name: string;
    type: string;
    tags: string[];
    embeddingStatus: 'indexed' | 'processing' | 'failed' | 'draft';
    lastIndexed: string;
    chunks: number;
    size: string;
};

export type NotificationType = 'info' | 'success' | 'warning' | 'error';

export type Notification = {
    id: string;
    title: string;
    body: string;
    type: NotificationType;
    read: boolean;
    timestamp: string;
    action?: { label: string; href: string };
};

export type Toast = {
    id: string;
    title: string;
    description?: string;
    type: NotificationType;
    duration?: number;
};
