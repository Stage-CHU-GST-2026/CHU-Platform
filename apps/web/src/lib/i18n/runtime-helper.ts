import * as pRuntime from '$lib/paraglide/runtime.js';

export function languageTag(): 'en' | 'fr' {
	if (typeof (pRuntime as any).languageTag === 'function') {
		return (pRuntime as any).languageTag();
	}
	return 'en';
}

export function setLanguageTag(tag: any): void {
	if (typeof (pRuntime as any).setLanguageTag === 'function') {
		(pRuntime as any).setLanguageTag(tag);
	}
}

export const availableLanguageTags: readonly ['en', 'fr'] = (pRuntime as any).availableLanguageTags || ['en', 'fr'];
