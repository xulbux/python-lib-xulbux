<template>
  <section class="release-card" :class="[levelClass, statusClass]">
    <!-- Hidden anchor targets for backward compatibility and secondary hashes -->
    <span v-for="alias in anchorAliases" :key="alias" :id="alias" class="release-anchor-alias" />

    <div class="release-header">
      <div class="release-meta">
        <h3 :id="anchorId" class="release-heading">
          <a
            :href="`#${anchorId}`"
            class="header-anchor"
            :aria-label="`Permalink to ${displayVersion}`">
            &#x200B;
          </a>
          <span class="release-version">{{ displayVersion }}</span>
        </h3>

        <span v-if="isMajor" class="release-badge badge-major ignore-header">Major Release</span>
        <span v-if="status === 'broken'" class="release-badge badge-broken ignore-header">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round">
            <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3" />
            <path d="M12 9v4" />
            <path d="M12 17h.01" />
          </svg>
          Broken Release
        </span>
        <span v-else-if="status === 'hotfix'" class="release-badge badge-hotfix ignore-header">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round">
            <path d="M12 20v-8" />
            <path d="M12.656 7H14a4 4 0 0 1 4 4v1.344" />
            <path d="M14.12 3.88 16 2" />
            <path d="M17.123 17.123A6 6 0 0 1 6 14v-3a4 4 0 0 1 1.72-3.287" />
            <path d="m2 2 20 20" />
            <path d="M21 5a4 4 0 0 1-3.55 3.97" />
            <path d="M22 13h-3.344" />
            <path d="M3 21a4 4 0 0 1 3.81-4" />
            <path d="M3 5a4 4 0 0 0 3.55 3.97" />
            <path d="M6 13H2" />
            <path d="m8 2 1.88 1.88" />
            <path d="M9.712 4.06A3 3 0 0 1 15 6v1.13" />
          </svg>
          Hotfix
        </span>
      </div>

      <span class="release-date ignore-header" :class="{ 'is-unreleased': isUnreleased }">
        {{ displayDate }}
      </span>
    </div>

    <div class="release-content">
      <slot />
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted } from 'vue';

const {
  version,
  date,
  status = undefined,
} = defineProps<{ version: string; date: string; status?: 'broken' | 'hotfix' }>();

const cleanVersion = computed(() => version.trim());
const isRangeVersion = computed(() => cleanVersion.value.includes('-'));

const rangeParts = computed(() => {
  if (!isRangeVersion.value) {
    return [];
  }
  return cleanVersion.value.split('-').map((part) => part.trim().replace(/^v/, ''));
});

const displayVersion = computed(() => {
  if (isRangeVersion.value && rangeParts.value.length >= 2) {
    return `v${rangeParts.value[0]} – v${rangeParts.value[1]}`;
  }
  const ver = cleanVersion.value.replace(/^v/, '');
  return `v${ver}`;
});

const anchorId = computed(() => {
  if (isRangeVersion.value && rangeParts.value.length >= 2) {
    const first = rangeParts.value[0].replace(/\./g, '-');
    const last = rangeParts.value[1].replace(/\./g, '-');
    return `v${first}-${last}`;
  }
  return `v${cleanVersion.value.replace(/^v/, '').replace(/\./g, '-')}`;
});

const anchorAliases = computed(() => {
  const aliases: string[] = [];
  if (isRangeVersion.value && rangeParts.value.length >= 2) {
    const first = rangeParts.value[0].replace(/\./g, '-');
    aliases.push(`v${first}`);
  } else {
    const ver = cleanVersion.value.replace(/^v/, '');
    const parts = ver.split('.');
    if (parts.length >= 2 && parts[1] === '0' && (parts.length === 2 || parts[2] === '0')) {
      aliases.push(`v${parts[0]}`);
      aliases.push(`v${parts[0]}-0`);
      if (parts.length >= 3) {
        aliases.push(`v${parts[0]}-0-0`);
      }
    }
  }
  return aliases.filter((aliasItem) => aliasItem !== anchorId.value);
});

const isMajor = computed(() => {
  if (isRangeVersion.value) {
    return false;
  }
  const ver = cleanVersion.value.replace(/^v/, '');
  const parts = ver.split('.');
  return parts.length >= 2 && parts[1] === '0' && (parts.length === 2 || parts[2] === '0');
});

const isMinor = computed(() => {
  if (isRangeVersion.value || isMajor.value) {
    return false;
  }
  const ver = cleanVersion.value.replace(/^v/, '');
  const parts = ver.split('.');
  return parts.length >= 3 && parts[2] === '0';
});

const levelClass = computed(() => {
  if (isMajor.value) {
    return 'level-major';
  }
  if (isMinor.value) {
    return 'level-minor';
  }
  return 'level-patch';
});

const statusClass = computed(() => {
  if (status === 'broken') {
    return 'is-broken';
  }
  if (status === 'hotfix') {
    return 'is-hotfix';
  }
  return '';
});

const isUnreleased = computed(() => date.trim() === '');

const displayDate = computed(() => {
  if (isUnreleased.value) {
    return 'Unreleased';
  }
  return date?.trim() ?? '';
});

let observer: MutationObserver | undefined = undefined;

onMounted(() => {
  if (status) {
    function syncStatusClass() {
      for (const link of document.querySelectorAll(`a.outline-link[href="#${anchorId.value}"]`)) {
        if (!link.classList.contains(`status-${status}`)) {
          link.classList.add(`status-${status}`);
        }
      }
    }

    // Sync immediately and after brief delays to ensure VitePress has rendered the outline:
    syncStatusClass();
    setTimeout(syncStatusClass, 100);
    setTimeout(syncStatusClass, 500);
    setTimeout(syncStatusClass, 1000);

    // Watch for dynamically rendered DOM elements (like the mobile outline dropdown):
    observer = new MutationObserver((mutations) => {
      let hasNewNodes = false;
      for (const mut of mutations) {
        if (mut.addedNodes.length > 0) {
          hasNewNodes = true;
          break;
        }
      }
      if (hasNewNodes) {
        syncStatusClass();
      }
    });
    observer.observe(document.body, { childList: true, subtree: true });
  }
});

onUnmounted(() => {
  if (observer) {
    observer.disconnect();
  }
});
</script>
