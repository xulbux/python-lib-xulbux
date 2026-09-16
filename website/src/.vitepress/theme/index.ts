import type { Theme } from 'vitepress';
import DefaultTheme from 'vitepress/theme';
import { setupCodeCopyBehavior } from '../plugins/codeCopyBehavior';
import { setupCodeScrollButtons } from '../plugins/codeScrollButtons';
import { setupSmoothScroll } from '../plugins/smoothScroll';
import AttachedCode from './components/AttachedCode.vue';
import Release from './components/Release.vue';
import TerminalOutput from './components/TerminalOutput.vue';
// @ts-ignore-next-line
import './style.css';

export default {
  enhanceApp({ app }) {
    app.component('AttachedCode', AttachedCode);
    app.component('Release', Release);
    app.component('TerminalOutput', TerminalOutput);
  },
  extends: DefaultTheme,
  setup() {
    setupSmoothScroll();
    setupCodeScrollButtons();
    setupCodeCopyBehavior();
  },
} satisfies Theme;
