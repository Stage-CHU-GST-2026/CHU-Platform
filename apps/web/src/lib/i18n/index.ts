import { languageTag, setLanguageTag, availableLanguageTags } from '$lib/paraglide/runtime.js';
import * as m from '$lib/paraglide/messages.js';

export { i18n, t, getPromptLanguageInstruction } from './i18n.svelte';
export { m, languageTag, setLanguageTag, availableLanguageTags };
export type { Locale } from './i18n.svelte';
