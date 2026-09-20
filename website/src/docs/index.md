---
layout: false
---

<div style="padding: 2rem; text-align: center; font-family: sans-serif;">
  Redirecting to the <a :href="redirectLink">documentation</a>...
</div>

<script setup>
import { useData, useRouter, withBase } from 'vitepress';
import { onMounted } from 'vue';

const { theme } = useData();
const router = useRouter();

// Get the first link from the sidebar dynamically:
const firstLink = theme.value.sidebar?.[0]?.items?.[0]?.link || '/';
const redirectLink = withBase(firstLink);

onMounted(() => {
  // Client-side redirect:
  if (typeof window !== 'undefined') {
    router.go(redirectLink);
  }
})
</script>
