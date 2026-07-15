<script lang="ts">
    interface Props {
        name: string;
        src?: string;
        size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
        class?: string;
    }

    let { name, src, size = 'md', class: className = '' } = $props();

    const sizes = {
        xs: 'w-6 h-6 text-[10px]',
        sm: 'w-8 h-8 text-[11px]',
        md: 'w-10 h-10 text-[13px]',
        lg: 'w-12 h-12 text-[16px]',
        xl: 'w-16 h-16 text-[20px]'
    };

    let initials = $derived(
        name
            .split(' ')
            .map(n => n[0])
            .join('')
            .toUpperCase()
            .substring(0, 2)
    );

    // Generate a consistent color based on the name string
    let bgColors = [
        'bg-blue/20 text-blue',
        'bg-indigo/20 text-indigo',
        'bg-success/20 text-success',
        'bg-warning/20 text-warning',
        'bg-danger/20 text-danger',
        'bg-teal-500/20 text-teal-500',
        'bg-purple-500/20 text-purple-500',
        'bg-pink-500/20 text-pink-500'
    ];
    
    let colorIndex = $derived.by(() => {
        let hash = 0;
        for (let i = 0; i < name.length; i++) {
            hash = name.charCodeAt(i) + ((hash << 5) - hash);
        }
        return Math.abs(hash) % bgColors.length;
    });
</script>

<div class="relative shrink-0 inline-flex items-center justify-center rounded-full overflow-hidden {sizes[size]} {className}">
    {#if src}
        <img {src} alt={name} class="w-full h-full object-cover" />
    {:else}
        <div class="w-full h-full flex items-center justify-center font-semibold {bgColors[colorIndex]}">
            {initials}
        </div>
    {/if}
</div>
