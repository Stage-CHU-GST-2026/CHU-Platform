import type { Dataset } from '$lib/types';
import { mockDatasets } from '$lib/mock';

class DatasetsState {
    all = $state<Dataset[]>(mockDatasets);
    selected = $state<Dataset | null>(null);
    sortCol = $state<keyof Dataset>('name');
    sortDir = $state<'asc' | 'desc'>('asc');
    page = $state(1);
    pageSize = $state(20);
    search = $state('');
    panelTab = $state<'schema' | 'preview' | 'statistics' | 'history'>('schema');

    get sorted(): Dataset[] {
        let items = [...this.all];
        if (this.search) {
            items = items.filter(d => d.name.toLowerCase().includes(this.search.toLowerCase()));
        }
        items.sort((a, b) => {
            const valA = a[this.sortCol];
            const valB = b[this.sortCol];
            if (valA < valB) return this.sortDir === 'asc' ? -1 : 1;
            if (valA > valB) return this.sortDir === 'asc' ? 1 : -1;
            return 0;
        });
        return items;
    }

    get paginated(): Dataset[] {
        const start = (this.page - 1) * this.pageSize;
        return this.sorted.slice(start, start + this.pageSize);
    }

    get total() {
        return this.all.length;
    }

    get totalPages() {
        return Math.ceil(this.total / this.pageSize);
    }

    sort(col: keyof Dataset) {
        if (this.sortCol === col) {
            this.sortDir = this.sortDir === 'asc' ? 'desc' : 'asc';
        } else {
            this.sortCol = col;
            this.sortDir = 'asc';
        }
    }
}

export const datasets = new DatasetsState();
