<script lang="ts">
    import Dialog from './Dialog.svelte';
    import Button from './Button.svelte';

    interface Props {
        open: boolean;
        title: string;
        description: string;
        confirmLabel?: string;
        cancelLabel?: string;
        variant?: 'danger' | 'default';
        onConfirm: () => void;
        onCancel: () => void;
    }

    let { 
        open, 
        title, 
        description, 
        confirmLabel = 'Confirm', 
        cancelLabel = 'Cancel', 
        variant = 'default',
        onConfirm, 
        onCancel 
    } = $props();
</script>

<Dialog {open} {title} {description} onclose={onCancel} width="max-w-md">
    <svelte:fragment slot="footer">
        <Button variant="ghost" onclick={onCancel}>{cancelLabel}</Button>
        <Button variant={variant === 'danger' ? 'danger' : 'primary'} onclick={onConfirm}>{confirmLabel}</Button>
    </svelte:fragment>
</Dialog>
