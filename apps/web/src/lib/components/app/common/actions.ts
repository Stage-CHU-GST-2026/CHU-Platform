export function clickOutside(node: HTMLElement, callback: () => void) {
    const handleClick = (event: MouseEvent) => {
        if (node && !node.contains(event.target as Node) && !event.defaultPrevented) {
            callback();
        }
    };

    document.addEventListener('click', handleClick, true);

    return {
        destroy() {
            document.removeEventListener('click', handleClick, true);
        }
    };
}

export function trapFocus(node: HTMLElement, active: boolean = true) {
    let previousFocus: HTMLElement | null = null;

    const handleKeydown = (e: KeyboardEvent) => {
        if (!active) return;
        
        if (e.key === 'Tab') {
            const focusableElements = node.querySelectorAll(
                'a[href], button:not([disabled]), textarea:not([disabled]), input[type="text"]:not([disabled]), input[type="radio"]:not([disabled]), input[type="checkbox"]:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex="-1"])'
            );
            
            const firstElement = focusableElements[0] as HTMLElement;
            const lastElement = focusableElements[focusableElements.length - 1] as HTMLElement;

            if (e.shiftKey) {
                if (document.activeElement === firstElement) {
                    lastElement.focus();
                    e.preventDefault();
                }
            } else {
                if (document.activeElement === lastElement) {
                    firstElement.focus();
                    e.preventDefault();
                }
            }
        }
    };

    const activate = () => {
        if (active) {
            previousFocus = document.activeElement as HTMLElement;
            node.addEventListener('keydown', handleKeydown);
            
            // Focus first element
            const focusableElements = node.querySelectorAll(
                'a[href], button:not([disabled]), textarea:not([disabled]), input[type="text"]:not([disabled]), input[type="radio"]:not([disabled]), input[type="checkbox"]:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex="-1"])'
            );
            
            if (focusableElements.length > 0) {
                (focusableElements[0] as HTMLElement).focus();
            } else {
                node.focus();
            }
        }
    };

    const deactivate = () => {
        node.removeEventListener('keydown', handleKeydown);
        if (previousFocus && typeof previousFocus.focus === 'function') {
            previousFocus.focus();
        }
    };

    if (active) activate();

    return {
        update(newActive: boolean) {
            if (newActive !== active) {
                active = newActive;
                if (active) activate();
                else deactivate();
            }
        },
        destroy() {
            deactivate();
        }
    };
}
