import { languageTag, setLanguageTag, availableLanguageTags } from './runtime-helper';
import * as m from '$lib/paraglide/messages.js';

export { i18n, t, getPromptLanguageInstruction } from './i18n.svelte';
export { languageTag, setLanguageTag, availableLanguageTags, m };
export type { Locale } from './i18n.svelte';
