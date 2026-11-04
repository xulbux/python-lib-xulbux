import { onMounted, onUnmounted } from 'vue';

interface BlockMeasurement {
  canScrollLeft: boolean;
  canScrollRight: boolean;
  container: HTMLElement;
  isScrollable: boolean;
  leftBtn: HTMLButtonElement | null;
  pre: HTMLElement;
  rightBtn: HTMLButtonElement | null;
}

function updateButtons() {
  const blocks = document.querySelectorAll<HTMLElement>('div[class*="language-"] > pre');
  const measurements: BlockMeasurement[] = [];

  // Pass 1: Read layout metrics without mutating the DOM to prevent forced synchronous reflows:
  for (const pre of blocks) {
    const { parentElement: container } = pre;
    if (container) {
      const { clientWidth, scrollLeft, scrollWidth } = pre;
      measurements.push({
        canScrollLeft: scrollLeft > 0,
        canScrollRight: scrollLeft < scrollWidth - clientWidth - 1,
        container,
        isScrollable: scrollWidth > clientWidth + 1,
        leftBtn: container.querySelector<HTMLButtonElement>('.scroll-btn-left'),
        pre,
        rightBtn: container.querySelector<HTMLButtonElement>('.scroll-btn-right'),
      });
    }
  }

  // Ensure all links (`<a href>`) have `tabindex="0"` for WebKit/Safari Tab navigation (matching `svg-api`),
  // and strip redundant `tabindex="0"` from non-collapsible sidebar section headers and duplicate `.caret` buttons:
  for (const link of document.querySelectorAll<HTMLAnchorElement>('a[href]:not([tabindex])')) {
    link.setAttribute('tabindex', '0');
  }
  for (const el of document.querySelectorAll<HTMLElement>(
    '.VPSidebarItem:not(.collapsible) > .item[tabindex], .VPSidebarItem.collapsible:not(.is-link) > .item > .caret[tabindex]'
  )) {
    el.removeAttribute('tabindex');
    el.removeAttribute('role');
  }

  // Pass 2: Apply all DOM mutations:
  for (const item of measurements) {
    let { leftBtn, rightBtn } = item;
    if (!item.isScrollable) {
      if (leftBtn) {
        leftBtn.classList.remove('visible');
        leftBtn.disabled = true;
      }
      if (rightBtn) {
        rightBtn.classList.remove('visible');
        rightBtn.disabled = true;
      }
    } else {
      if (!leftBtn) {
        leftBtn = document.createElement('button');
        leftBtn.type = 'button';
        leftBtn.className = 'scroll-btn-left scroll-btn';
        leftBtn.setAttribute('aria-label', 'Scroll left');
        leftBtn.innerHTML =
          '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m15 18-6-6 6-6"/></svg>';
        item.container.appendChild(leftBtn);

        const targetPre = item.pre;
        leftBtn.addEventListener('click', () =>
          targetPre.scrollBy({ behavior: 'smooth', left: -250 })
        );
      }

      if (!rightBtn) {
        rightBtn = document.createElement('button');
        rightBtn.type = 'button';
        rightBtn.className = 'scroll-btn-right scroll-btn';
        rightBtn.setAttribute('aria-label', 'Scroll right');
        rightBtn.innerHTML =
          '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m9 18 6-6-6-6"/></svg>';
        item.container.appendChild(rightBtn);

        const targetPre = item.pre;
        rightBtn.addEventListener('click', () =>
          targetPre.scrollBy({ behavior: 'smooth', left: 250 })
        );
      }

      leftBtn.classList.add('visible');
      rightBtn.classList.add('visible');

      leftBtn.disabled = !item.canScrollLeft;
      rightBtn.disabled = !item.canScrollRight;
      leftBtn.classList.toggle('disabled', !item.canScrollLeft);
      rightBtn.classList.toggle('disabled', !item.canScrollRight);
    }
  }
}

function handleScroll(event: Event) {
  const target = event.target as HTMLElement;
  if (
    target &&
    target.tagName === 'PRE' &&
    target.parentElement?.matches('div[class*="language-"]')
  ) {
    const { parentElement: container } = target;
    const leftBtn = container.querySelector<HTMLButtonElement>('.scroll-btn-left');
    const rightBtn = container.querySelector<HTMLButtonElement>('.scroll-btn-right');

    const { clientWidth, scrollLeft, scrollWidth } = target;
    const canScrollLeft = scrollLeft > 0;
    const canScrollRight = scrollLeft < scrollWidth - clientWidth - 1;

    if (leftBtn) {
      leftBtn.disabled = !canScrollLeft;
      leftBtn.classList.toggle('disabled', !canScrollLeft);
    }
    if (rightBtn) {
      rightBtn.disabled = !canScrollRight;
      rightBtn.classList.toggle('disabled', !canScrollRight);
    }
  }
}

function hasNonButtonAddedNodes(mutations: MutationRecord[]): boolean {
  for (const mutation of mutations) {
    for (const node of mutation.addedNodes) {
      if (!(node instanceof HTMLElement) || !node.classList.contains('scroll-btn')) {
        return true;
      }
    }
  }
  return false;
}

export function setupCodeScrollButtons() {
  if (typeof globalThis.window === 'undefined') {
    return;
  }

  let observer: MutationObserver | undefined = undefined;
  let pendingTimer: ReturnType<typeof setTimeout> | undefined = undefined;

  function scheduleUpdate(delayMs: number) {
    if (pendingTimer !== undefined) {
      clearTimeout(pendingTimer);
    }
    pendingTimer = setTimeout(() => {
      pendingTimer = undefined;
      updateButtons();
    }, delayMs);
  }

  onMounted(() => {
    scheduleUpdate(100);
    globalThis.window.addEventListener('resize', updateButtons);

    // Use capture phase to catch non-bubbling scroll events on `<pre>` elements:
    document.addEventListener('scroll', handleScroll, true);

    observer = new MutationObserver((mutations) => {
      if (hasNonButtonAddedNodes(mutations)) {
        scheduleUpdate(50);
      }
    });

    observer.observe(document.body, { childList: true, subtree: true });
  });

  onUnmounted(() => {
    if (pendingTimer !== undefined) {
      clearTimeout(pendingTimer);
    }
    globalThis.window.removeEventListener('resize', updateButtons);
    document.removeEventListener('scroll', handleScroll, true);
    if (observer) {
      observer.disconnect();
    }
  });
}
