import { languageTag, setLanguageTag } from './runtime-helper';

export type Locale = 'en' | 'fr';

class ParaglideI18nState {
	locale = $state<Locale>('en');

	constructor() {
		if (typeof window !== 'undefined') {
			try {
				const saved = localStorage.getItem('PARAGLIDE_LOCALE') as Locale | null;
				const initialTag = (saved === 'en' || saved === 'fr') 
					? saved 
					: ((typeof languageTag === 'function' ? languageTag() : 'en') as Locale);
				
				this.locale = initialTag;
				if (typeof setLanguageTag === 'function') {
					setLanguageTag(initialTag);
				}
			} catch (e) {
				console.warn('[i18n] Failed to initialize locale from storage:', e);
			}
		}
	}

	setLocale(loc: Locale) {
		try {
			if (typeof setLanguageTag === 'function') {
				setLanguageTag(loc);
			}
			this.locale = loc;
			if (typeof window !== 'undefined') {
				localStorage.setItem('PARAGLIDE_LOCALE', loc);
				document.cookie = `PARAGLIDE_LOCALE=${loc}; path=/; max-age=31536000`;
			}
		} catch (e) {
			console.error('[i18n] Failed to set locale:', e);
		}
	}

	toggleLocale() {
		this.setLocale(this.locale === 'en' ? 'fr' : 'en');
	}

	// Reactive translation function with defensive error guards
	t(msgFn: any, params?: any): string {
		const currentTag = this.locale;
		if (typeof msgFn !== 'function') {
			if (typeof msgFn === 'string') return msgFn;
			return '';
		}
		try {
			return msgFn(params, { languageTag: currentTag }) || '';
		} catch (err) {
			console.error('[i18n] Error rendering translation:', err);
			return '';
		}
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
export const t = (msgFn: any, params?: any) => i18n.t(msgFn, params);
export const getPromptLanguageInstruction = () => i18n.getLanguageInstruction();
