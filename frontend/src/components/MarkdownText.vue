<script setup>
import DOMPurify from "dompurify";
import { marked } from "marked";
import { computed } from "vue";

marked.setOptions({ breaks: true, gfm: true });

const props = defineProps({
  text: { type: String, default: "" },
});

const html = computed(() => DOMPurify.sanitize(marked.parse(props.text || "")));
</script>

<template>
  <div class="markdown" v-html="html"></div>
</template>

<style scoped>
.markdown :deep(p) {
  margin: 0 0 0.5rem;
}

.markdown :deep(p:last-child) {
  margin-bottom: 0;
}

.markdown :deep(ul),
.markdown :deep(ol) {
  margin: 0.2rem 0 0.5rem 1.2rem;
}

.markdown :deep(li) {
  margin: 0.15rem 0;
}

.markdown :deep(pre) {
  background: rgba(0, 0, 0, 0.08);
  border-radius: 8px;
  padding: 0.65rem 0.75rem;
  overflow-x: auto;
  font-size: 0.82rem;
  margin: 0.4rem 0;
}

.markdown :deep(code) {
  background: rgba(0, 0, 0, 0.08);
  border-radius: 4px;
  padding: 0.1rem 0.3rem;
  font-size: 0.88em;
}

.markdown :deep(pre code) {
  background: none;
  padding: 0;
}

.markdown :deep(a) {
  color: inherit;
  text-decoration: underline;
}

.markdown :deep(strong) {
  font-weight: 800;
}

.markdown :deep(h1),
.markdown :deep(h2),
.markdown :deep(h3) {
  font-size: 1em;
  font-weight: 800;
  margin: 0.4rem 0 0.3rem;
}

.markdown :deep(blockquote) {
  border-left: 3px solid rgba(0, 0, 0, 0.15);
  margin: 0.4rem 0;
  padding-left: 0.6rem;
  opacity: 0.9;
}
</style>
