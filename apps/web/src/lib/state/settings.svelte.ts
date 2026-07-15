class SettingsState {
    activeSection = $state('general');
    saved = $state(false);

    general = $state({
        workspaceName: 'CHU Analytics',
        language: 'en',
        timezone: 'UTC+1',
        dateFormat: 'DD/MM/YYYY'
    });

    appearance = $state({
        density: 'comfortable' as 'comfortable' | 'compact',
        fontSize: 'md'
    });

    aiModels = $state({
        defaultModel: 'claude-3.5-sonnet',
        temperature: 0.7,
        maxTokens: 4096,
        responseStyle: 'professional'
    });

    async save() {
        this.saved = true;
        await new Promise((resolve) => setTimeout(resolve, 800));
        this.saved = false;
    }
}

export const settings = new SettingsState();
