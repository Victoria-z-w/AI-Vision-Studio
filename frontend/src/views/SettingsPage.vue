<template>
  <div class="settings-page">
    <h2>System Settings</h2>

    <el-card class="section-card">
      <template #header><h4>Model Status</h4></template>
      <el-table :data="models" style="width: 100%">
        <el-table-column prop="name" label="Model" width="140" />
        <el-table-column prop="loaded" label="Loaded" width="120">
          <template #default="{ row }">
            <el-tag :type="row.loaded ? 'success' : 'info'" size="small">
              {{ row.loaded ? "Loaded" : "Not loaded" }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="device" label="Device" width="120">
          <template #default="{ row }">
            {{ row.device || "-" }}
          </template>
        </el-table-column>
        <el-table-column label="Actions">
          <template #default="{ row }">
            <el-button
              v-if="row.loaded"
              size="small"
              type="danger"
              plain
              @click="unloadModel(row.name)"
            >
              Unload
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-card class="section-card">
      <template #header><h4>System Information</h4></template>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="API Version">0.1.0</el-descriptions-item>
        <el-descriptions-item label="Device Available">{{ deviceAvailable.join(", ") }}</el-descriptions-item>
        <el-descriptions-item label="Database">SQLite</el-descriptions-item>
        <el-descriptions-item label="Max File Size">20 MB</el-descriptions-item>
        <el-descriptions-item label="Max Image Dimension">4096 px</el-descriptions-item>
      </el-descriptions>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import axios from "axios";
import type { ModelStatus } from "@/types";

const models = ref<ModelStatus[]>([]);
const deviceAvailable = ref<string[]>(["cpu"]);

onMounted(async () => {
  try {
    const { data } = await axios.get("/api/v1/admin/models/status");
    models.value = data.models || [];
    deviceAvailable.value = data.device_available || ["cpu"];
  } catch {
    models.value = [];
  }
});

async function unloadModel(name: string) {
  try {
    await axios.post("/api/v1/admin/models/unload", null, { params: { model: name } });
    const { data } = await axios.get("/api/v1/admin/models/status");
    models.value = data.models || [];
  } catch {}
}
</script>

<style scoped>
.settings-page {
  max-width: 800px;
  margin: 0 auto;
}

.settings-page h2 {
  margin: 0 0 20px;
  font-size: 20px;
}

.section-card {
  margin-bottom: 20px;
}

.section-card h4 {
  margin: 0;
}
</style>
