import type { Toast } from '$lib/types';
import type { Artifact } from '$lib/api/chat';

class AppState {
    sidebarCollapsed = $state(false);
    _artifactOpen = $state(false);
    activeArtifacts = $state<Artifact[]>([]);
    _activeArtifactTabId = $state<string>('overview');
    _openArtifactTabs = $state<string[]>([]);
    theme = $state<'dark' | 'light'>('dark');
    cmdPaletteOpen = $state(false);
    activeRoute = $state('/dashboard');
    toasts = $state<Toast[]>([]);

    constructor() {
        if (typeof window !== 'undefined') {
            const savedArtifactOpen = localStorage.getItem('app-artifactOpen');
            if (savedArtifactOpen !== null) {
                this._artifactOpen = savedArtifactOpen === 'true';
            }
            
            const savedTabId = localStorage.getItem('app-activeArtifactTabId');
            if (savedTabId) {
                this._activeArtifactTabId = savedTabId;
            }
            
            const savedTabs = localStorage.getItem('app-openArtifactTabs');
            if (savedTabs) {
                try {
                    this._openArtifactTabs = JSON.parse(savedTabs);
                } catch (e) {}
            }
        }
    }

    get activeArtifactTabId() { return this._activeArtifactTabId; }
    set activeArtifactTabId(val: string) {
        this._activeArtifactTabId = val;
        if (typeof window !== 'undefined') {
            localStorage.setItem('app-activeArtifactTabId', val);
        }
    }

    get openArtifactTabs() { return this._openArtifactTabs; }
    set openArtifactTabs(val: string[]) {
        this._openArtifactTabs = val;
        if (typeof window !== 'undefined') {
            localStorage.setItem('app-openArtifactTabs', JSON.stringify(val));
        }
    }

    get artifactOpen() {
        return this._artifactOpen;
    }

    set artifactOpen(value: boolean) {
        this._artifactOpen = value;
        if (typeof window !== 'undefined') {
            localStorage.setItem('app-artifactOpen', String(value));
        }
    }

    get sidebarWidth() {
        return this.sidebarCollapsed ? 'var(--sidebar-collapsed-width)' : 'var(--sidebar-width)';
    }

    get artifactWidth() {
        return this.artifactOpen ? 'var(--artifact-width)' : '0px';
    }

    toggleSidebar() {
        this.sidebarCollapsed = !this.sidebarCollapsed;
    }

    toggleArtifact() {
        this.artifactOpen = !this.artifactOpen;
    }

    openCommandPalette() {
        this.cmdPaletteOpen = true;
    }

    closeCommandPalette() {
        this.cmdPaletteOpen = false;
    }

    toggleTheme() {
        this.theme = this.theme === 'dark' ? 'light' : 'dark';
        if (typeof document !== 'undefined') {
            document.documentElement.classList.toggle('dark', this.theme === 'dark');
            document.documentElement.classList.toggle('light', this.theme === 'light');
        }
    }

    addToast(toast: Omit<Toast, 'id'>) {
        const id = crypto.randomUUID();
        this.toasts = [...this.toasts, { ...toast, id }];
        setTimeout(() => this.dismissToast(id), 4000);
    }

    dismissToast(id: string) {
        this.toasts = this.toasts.filter((t) => t.id !== id);
    }
}

export const app = new AppState();
