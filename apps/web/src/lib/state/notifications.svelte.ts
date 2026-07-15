import type { Notification } from '$lib/types';
import { mockNotifications } from '$lib/mock';

class NotificationsState {
    items = $state<Notification[]>(mockNotifications);
    panelOpen = $state(false);

    get unreadCount() {
        return this.items.filter((n) => !n.read).length;
    }

    markRead(id: string) {
        this.items = this.items.map((n) => (n.id === id ? { ...n, read: true } : n));
    }

    markAllRead() {
        this.items = this.items.map((n) => ({ ...n, read: true }));
    }

    dismiss(id: string) {
        this.items = this.items.filter((n) => n.id !== id);
    }

    togglePanel() {
        this.panelOpen = !this.panelOpen;
    }
}

export const notifications = new NotificationsState();
