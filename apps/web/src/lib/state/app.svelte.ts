import type { Toast } from '$lib/types';

class AppState {
    sidebarCollapsed = $state(false);
    artifactOpen = $state(false);
    theme = $state<'dark' | 'light'>('dark');
    cmdPaletteOpen = $state(false);
    activeRoute = $state('/dashboard');
    toasts = $state<Toast[]>([]);

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
