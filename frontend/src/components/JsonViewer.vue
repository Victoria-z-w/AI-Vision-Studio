<template>
  <div class="json-viewer">
    <div class="json-header">
      <span class="json-title">Structured Result (JSON)</span>
      <el-button size="small" text @click="copy">
        <el-icon><CopyDocument /></el-icon>
        {{ copied ? "Copied!" : "Copy" }}
      </el-button>
    </div>
    <pre class="json-content"><code>{{ formatted }}</code></pre>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";

const props = defineProps<{ data: unknown }>();
const copied = ref(false);

const formatted = computed(() => JSON.stringify(props.data, null, 2));

async function copy() {
  await navigator.clipboard.writeText(formatted.value);
  copied.value = true;
  setTimeout(() => (copied.value = false), 2000);
}
</script>

<style scoped>
.json-viewer {
  background: #1e1e2e;
  border-radius: 8px;
  overflow: hidden;
}

.json-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 16px;
  background: #2a2a3e;
  border-bottom: 1px solid #3a3a4e;
}

.json-title {
  color: #cdd6f4;
  font-size: 13px;
  font-weight: 500;
}

.json-content {
  padding: 16px;
  margin: 0;
  color: #a6e3a1;
  font-size: 13px;
  line-height: 1.6;
  overflow-x: auto;
  white-space: pre-wrap;
  word-break: break-all;
}
</style>
