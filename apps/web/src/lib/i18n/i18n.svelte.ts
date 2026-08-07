import { languageTag, setLanguageTag, availableLanguageTags } from '$lib/paraglide/runtime.js';

export type Locale = 'en' | 'fr';

class ParaglideI18nState {
	locale = $state<Locale>('en');

	constructor() {
		if (typeof window !== 'undefined') {
			const saved = localStorage.getItem('PARAGLIDE_LOCALE') as Locale | null;
			const initialTag = (saved === 'en' || saved === 'fr') 
				? saved 
				: ((languageTag() || 'en') as Locale);
			
			this.locale = initialTag;
			setLanguageTag(initialTag);
		}
	}

	setLocale(loc: Locale) {
		setLanguageTag(loc);
		this.locale = loc;
		if (typeof window !== 'undefined') {
			localStorage.setItem('PARAGLIDE_LOCALE', loc);
			// Set cookie as well for server/SSR strategies
			document.cookie = `PARAGLIDE_LOCALE=${loc}; path=/; max-age=31536000`;
		}
	}

	toggleLocale() {
		this.setLocale(this.locale === 'en' ? 'fr' : 'en');
	}

	// Reactive translation function that explicitly accesses `this.locale`
	// so Svelte 5 fine-grained reactivity tracks language state changes!
	t(msgFn: (params?: any, options?: { languageTag?: Locale }) => string, params?: any): string {
		const currentTag = this.locale;
		return msgFn(params, { languageTag: currentTag });
	}

	// Generates a prompt language instruction suffix based on the active locale
	getLanguageInstruction(): string {
		const tag = this.locale || 'en';
		return tag === 'fr'
			? '\n\n(Please answer in French / Veuillez répondre en français)'
			: '\n\n(Please answer in English)';
	}
}

export const i18n = new ParaglideI18nState();
export const t = (msgFn: (params?: any, options?: { languageTag?: Locale }) => string, params?: any) => i18n.t(msgFn, params);
export const getPromptLanguageInstruction = () => i18n.getLanguageInstruction();
