import { mdsvex } from 'mdsvex';
import adapter from '@sveltejs/adapter-node';
import { sveltekit } from '@sveltejs/kit/vite';
import tailwindcss from '@tailwindcss/vite';
import { defineConfig } from 'vite';
import { paraglide } from '@inlang/paraglide-sveltekit/vite';

export default defineConfig({
	server: {
		proxy: {
			'/api': {
				target: 'http://localhost:10000',
				changeOrigin: true,
				proxyTimeout: 0,
				timeout: 0,
			},
		},
	},
	ssr: {
		noExternal: ['paneforge', 'svelte-toolbelt']
	},
	plugins: [
		paraglide({
			project: './project.inlang',
			outdir: './src/lib/paraglide'
		}),
		tailwindcss(),
		sveltekit({
			adapter: adapter(),
			preprocess: [mdsvex({ extensions: ['.svx', '.md'] })],
			extensions: ['.svelte', '.svx', '.md']
		})
	]
});
