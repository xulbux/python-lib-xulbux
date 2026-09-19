import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { defineConfig } from 'vitepress';
import { apiLinkTransformer } from './plugins/apiLinkTransformer';
import { syncPlugin } from './plugins/syncPlugin';

const dirname = path.dirname(fileURLToPath(import.meta.url));
const sidebar = JSON.parse(fs.readFileSync(path.resolve(dirname, 'sidebar.json'), 'utf8'));

const base = '/python-lib-xulbux/';

// https://vitepress.dev/reference/site-config
export default defineConfig({
  base,
  cleanUrls: true,
  description: 'A modern, high-performance Python library to simplify common tasks.',
  head: [['link', { href: `${base}logo.svg`, rel: 'icon' }]],
  markdown: {
    codeTransformers: [apiLinkTransformer(dirname, base)],
    math: true,
    theme: { dark: 'github-dark', light: 'github-light' },
  },
  sitemap: { hostname: 'https://xulbux.github.io/python-lib-xulbux/' },
  themeConfig: {
    // https://vitepress.dev/reference/default-theme-config
    footer: {
      copyright:
        '✨ From <a href="https://xulbux.com" target="_blank" rel="noopener"><b>XulbuX</b></a> ✨',
      message: 'Released under the MIT License.',
    },
    logo: '/logo.svg',
    nav: [
      { link: '/', text: 'Home' },
      { link: sidebar[0]?.items[0]?.link || '/', text: 'Docs' },
      { link: '/changelog', text: 'Changelog' },
    ],
    outline: [2, 4],
    search: { provider: 'local' },
    sidebar,
    socialLinks: [{ icon: 'github', link: 'https://github.com/xulbux/python-lib-xulbux' }],
  },
  title: 'XulbuX',
  vite: { plugins: [syncPlugin(dirname)] },
  vue: { template: { compilerOptions: { whitespace: 'preserve' } } },
});
