<template>
  <div class="home-page">
    <div class="hero">
      <h1>AI Vision Studio</h1>
      <p>Upload an image and run computer vision inference with state-of-the-art models</p>
      <el-button type="primary" size="large" @click="$router.push('/upload')" round>
        Get Started
        <el-icon class="ml-2"><ArrowRight /></el-icon>
      </el-button>
    </div>

    <el-row :gutter="24" class="feature-cards">
      <el-col :span="8" v-for="card in cards" :key="card.title">
        <el-card shadow="hover" class="feature-card" @click="$router.push(card.route)">
          <el-icon :size="36" :color="card.color">
            <component :is="card.icon" />
          </el-icon>
          <h3>{{ card.title }}</h3>
          <p>{{ card.desc }}</p>
        </el-card>
      </el-col>
    </el-row>

    <div v-if="recentItems.length > 0" class="recent-tasks">
      <h3>Recent Tasks</h3>
      <el-row :gutter="16">
        <el-col :span="6" v-for="item in recentItems" :key="item.task_id">
          <el-card
            shadow="hover"
            class="recent-card"
            @click="$router.push(`/tasks/${item.task_id}`)"
          >
            <img v-if="item.thumbnail_url" :src="item.thumbnail_url" alt="Thumbnail" />
            <div class="recent-info">
              <el-tag :type="tagType(item.model)" size="small">{{ item.model }}</el-tag>
              <el-tag :type="statusTag(item.status)" size="small" class="ml-2">{{ item.status }}</el-tag>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useHistoryStore } from "@/stores/history";
import type { TaskHistoryItem } from "@/types";

const historyStore = useHistoryStore();
const recentItems = ref<TaskHistoryItem[]>([]);

const cards = [
  { title: "Object Detection", desc: "Detect 80 object classes with YOLOv8n", icon: "Aim", color: "#FF6B6B", route: "/upload" },
  { title: "Background Removal", desc: "Remove image backgrounds with rembg", icon: "PictureFilled", color: "#4ECDC4", route: "/upload" },
  { title: "Text Recognition", desc: "Extract text regions with PaddleOCR", icon: "Document", color: "#45B7D1", route: "/upload" },
];

onMounted(async () => {
  await historyStore.load(1);
  recentItems.value = historyStore.items.slice(0, 4);
});

function tagType(model: string) {
  return model === "yolo" ? "danger" : model === "rembg" ? "success" : "primary";
}

function statusTag(status: string) {
  return status === "SUCCESS" ? "success" : status === "FAILED" ? "danger" : "warning";
}
</script>

<style scoped>
.home-page {
  max-width: 960px;
  margin: 0 auto;
}

.hero {
  text-align: center;
  padding: 48px 0 32px;
}

.hero h1 {
  font-size: 32px;
  color: #303133;
  margin: 0;
}

.hero p {
  font-size: 15px;
  color: #909399;
  margin: 12px 0 24px;
}

.ml-2 {
  margin-left: 6px;
}

.feature-cards {
  margin-bottom: 40px;
}

.feature-card {
  cursor: pointer;
  text-align: center;
  padding: 24px 16px;
  border-radius: 12px;
  transition: transform 0.2s;
}

.feature-card:hover {
  transform: translateY(-4px);
}

.feature-card h3 {
  margin: 12px 0 8px;
  font-size: 17px;
}

.feature-card p {
  font-size: 13px;
  color: #909399;
  margin: 0;
}

.recent-tasks {
  margin-top: 32px;
}

.recent-tasks h3 {
  font-size: 18px;
  margin: 0 0 16px;
}

.recent-card {
  cursor: pointer;
  border-radius: 10px;
}

.recent-card img {
  width: 100%;
  height: 120px;
  object-fit: cover;
  border-radius: 6px;
  margin-bottom: 8px;
}

.recent-info {
  display: flex;
  gap: 6px;
}
</style>
