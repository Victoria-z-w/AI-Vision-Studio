<template>
  <div class="history-page">
    <div class="page-header">
      <h2>Task History</h2>
      <el-button
        v-if="selectedIds.length > 0"
        type="danger"
        @click="handleBatchDelete"
      >
        Delete Selected ({{ selectedIds.length }})
      </el-button>
    </div>

    <!-- Filters -->
    <div class="filter-bar">
      <el-input
        v-model="searchQuery"
        placeholder="Search by filename..."
        clearable
        @clear="store.search('')"
        @keyup.enter="store.search(searchQuery)"
        style="width: 240px"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
      <el-select v-model="filterModel" placeholder="All Models" clearable @change="onFilterChange" style="width: 150px">
        <el-option label="YOLOv8n" value="yolo" />
        <el-option label="rembg" value="rembg" />
        <el-option label="PaddleOCR" value="ocr" />
      </el-select>
      <el-select v-model="filterStatus" placeholder="All Status" clearable @change="onFilterChange" style="width: 150px">
        <el-option label="Success" value="SUCCESS" />
        <el-option label="Failed" value="FAILED" />
        <el-option label="Processing" value="PROCESSING" />
      </el-select>
    </div>

    <!-- List -->
    <div v-if="store.items.length === 0 && !store.isLoading" class="empty">
      <el-empty description="No tasks yet. Upload your first image to get started!" />
    </div>

    <div v-else class="history-list" v-infinite-scroll="store.loadMore" :infinite-scroll-distance="100">
      <div
        v-for="item in store.items"
        :key="item.task_id"
        class="history-card"
        :class="{ selected: selectedIds.includes(item.task_id) }"
      >
        <el-checkbox
          :model-value="selectedIds.includes(item.task_id)"
          @change="(v: boolean) => toggleSelect(item.task_id, v)"
          class="card-check"
        />
        <img
          v-if="item.thumbnail_url"
          :src="item.thumbnail_url"
          class="card-thumb"
          @click="goToResult(item.task_id)"
          alt="Thumbnail"
        />
        <div class="card-body" @click="goToResult(item.task_id)">
          <div class="card-tags">
            <el-tag :type="modelTag(item.model)" size="small">{{ item.model }}</el-tag>
            <el-tag :type="statusTag(item.status)" size="small">{{ item.status }}</el-tag>
          </div>
          <div class="card-meta">
            <span v-if="item.inference_time_ms">{{ (item.inference_time_ms / 1000).toFixed(2) }}s</span>
            <span>{{ formatTime(item.created_at) }}</span>
          </div>
        </div>
        <el-button
          class="card-delete"
          type="danger"
          text
          circle
          @click.stop="handleDelete(item.task_id)"
        >
          <el-icon><Delete /></el-icon>
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { ElMessageBox } from "element-plus";
import { useHistoryStore } from "@/stores/history";

const router = useRouter();
const store = useHistoryStore();

const searchQuery = ref("");
const filterModel = ref("");
const filterStatus = ref("");
const selectedIds = ref<string[]>([]);

onMounted(() => store.load(1));

function onFilterChange() {
  store.setFilter(filterModel.value, filterStatus.value);
}

function goToResult(taskId: string) {
  router.push(`/tasks/${taskId}`);
}

function toggleSelect(id: string, val: boolean) {
  if (val) selectedIds.value.push(id);
  else selectedIds.value = selectedIds.value.filter((i) => i !== id);
}

async function handleDelete(taskId: string) {
  try {
    await ElMessageBox.confirm("Delete this task?", "Confirm", { type: "warning" });
    await store.remove(taskId);
  } catch {}
}

async function handleBatchDelete() {
  try {
    await ElMessageBox.confirm(`Delete ${selectedIds.value.length} tasks?`, "Confirm", {
      type: "warning",
    });
    await store.removeBatch(selectedIds.value);
    selectedIds.value = [];
  } catch {}
}

function formatTime(iso: string) {
  if (!iso) return "";
  return new Date(iso).toLocaleString();
}

function modelTag(model: string) {
  return model === "yolo" ? "danger" : model === "rembg" ? "success" : "";
}

function statusTag(status: string) {
  return status === "SUCCESS" ? "success" : status === "FAILED" ? "danger" : "warning";
}
</script>

<style scoped>
.history-page {
  max-width: 960px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
  font-size: 20px;
}

.filter-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.empty {
  padding: 60px 0;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.history-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: #fff;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  cursor: pointer;
  transition: box-shadow 0.2s;
}

.history-card:hover {
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.history-card.selected {
  border-color: #4ECDC4;
  background: #f0faf9;
}

.card-check {
  flex-shrink: 0;
}

.card-thumb {
  width: 80px;
  height: 60px;
  object-fit: cover;
  border-radius: 6px;
  flex-shrink: 0;
}

.card-body {
  flex: 1;
  min-width: 0;
}

.card-tags {
  display: flex;
  gap: 6px;
  margin-bottom: 6px;
}

.card-meta {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #909399;
}

.card-delete {
  flex-shrink: 0;
  opacity: 0;
  transition: opacity 0.2s;
}

.history-card:hover .card-delete {
  opacity: 1;
}
</style>
