import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { defineConfig } from 'vitepress';
import { apiLinkTransformer } from './plugins/apiLinkTransformer';
import { syncPlugin } from './plugins/syncPlugin';

const dirname = path.dirname(fileURLToPath(import.meta.url));
const sidebar = JSON.parse(fs.readFileSync(path.resolve(dirname, 'sidebar.json'), 'utf8'));

const base = '/python-lib-xulbux/';
const siteUrl = 'https://xulbux.github.io/python-lib-xulbux/';
const siteTitle = 'XulbuX Python Library';
const siteDescription = 'A modern, high-performance Python library to simplify common tasks.';

function loadShikiTheme(fileName: string, fallback: string) {
  const themePath = path.resolve(dirname, 'themes', fileName);
  return fs.existsSync(themePath) ? JSON.parse(fs.readFileSync(themePath, 'utf8')) : fallback;
}

// https://vitepress.dev/reference/site-config
export default defineConfig({
  base,
  cleanUrls: true,
  description: siteDescription,
  head: [
    ['link', { href: `${base}icon.png`, rel: 'icon' }],
    ['meta', { content: '#ffffff', media: '(prefers-color-scheme: light)', name: 'theme-color' }],
    ['meta', { content: '#141414', media: '(prefers-color-scheme: dark)', name: 'theme-color' }],
    ['meta', { content: 'website', property: 'og:type' }],
    ['meta', { content: siteTitle, property: 'og:site_name' }],
    ['meta', { content: `${siteUrl}icon.png`, property: 'og:image' }],
    ['meta', { content: 'summary', name: 'twitter:card' }],
  ],
  markdown: {
    codeTransformers: [apiLinkTransformer(dirname, base)],
    math: true,
    theme: {
      dark: loadShikiTheme('isolux-pro-dark.json', 'github-dark'),
      light: loadShikiTheme('isolux-pro-light.json', 'github-light'),
    },
  },
  sitemap: { hostname: siteUrl },
  themeConfig: {
    // https://vitepress.dev/reference/default-theme-config
    footer: {
      copyright:
        '✨ From <a href="https://xulbux.com" target="_blank" rel="noopener"><b>XulbuX</b></a> ✨',
      message:
        'Released under the <a href="https://github.com/xulbux/python-lib-xulbux/blob/main/LICENSE" target="_blank" rel="noopener">MIT License</a>&numsp;·&numsp;Syntax highlighted with <a href="https://github.com/xulbux/vscode-theme-isolux" target="_blank" rel="noopener">Isolux</a>',
    },
    logo: '/icon.png',
    nav: [
      { link: '/', text: 'Home' },
      { link: sidebar[0]?.items[0]?.link || '/', text: 'Docs' },
      { link: '/changelog', text: 'Changelog' },
    ],
    outline: [2, 4],
    search: { provider: 'local' },
    sidebar,
    siteTitle: 'XulbuX',
    socialLinks: [{ icon: 'github', link: 'https://github.com/xulbux/python-lib-xulbux' }],
  },
  title: siteTitle,
  transformHead({ description, pageData, title }) {
    const cleanPath = pageData.relativePath.replace(/(?:(?<sep>^|\/)index)?\.md$/, '$<sep>');
    const canonicalUrl = `${siteUrl}${cleanPath}`;
    const pageTitle = title || siteTitle;
    const pageDescription = description || siteDescription;

    return [
      ['link', { href: canonicalUrl, rel: 'canonical' }],
      ['meta', { content: pageTitle, property: 'og:title' }],
      ['meta', { content: pageDescription, property: 'og:description' }],
      ['meta', { content: canonicalUrl, property: 'og:url' }],
    ];
  },
  vite: { plugins: [syncPlugin(dirname)] },
  vue: { template: { compilerOptions: { whitespace: 'preserve' } } },
});
