<template>
  <el-container class="app-layout">
    <el-aside width="220px" class="app-sidebar">
      <div class="logo" @click="$router.push('/')">
        <span class="logo-text">AI Vision Studio</span>
      </div>
      <el-menu
        :default-active="activeRoute"
        router
        background-color="#1a1a2e"
        text-color="#b0b0c0"
        active-text-color="#4ECDC4"
      >
        <el-menu-item index="/">
          <el-icon><HomeFilled /></el-icon>
          <span>Home</span>
        </el-menu-item>
        <el-menu-item index="/upload">
          <el-icon><Upload /></el-icon>
          <span>Upload</span>
        </el-menu-item>
        <el-menu-item index="/history">
          <el-icon><Clock /></el-icon>
          <span>History</span>
        </el-menu-item>
        <el-menu-item index="/settings">
          <el-icon><Setting /></el-icon>
          <span>Settings</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="app-header">
        <span class="header-title">{{ pageTitle }}</span>
      </el-header>
      <el-main class="app-main">
        <slot />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useRoute } from "vue-router";

const route = useRoute();

const activeRoute = computed(() => {
  const path = route.path;
  if (path.startsWith("/tasks")) return "/history";
  return path;
});

const pageTitle = computed(() => {
  const titles: Record<string, string> = {
    "/": "Dashboard",
    "/upload": "Upload & Inference",
    "/history": "Task History",
    "/settings": "System Settings",
  };
  if (route.path.startsWith("/tasks/")) return "Inference Result";
  return titles[route.path] || "AI Vision Studio";
});
</script>

<style scoped>
.app-layout {
  height: 100vh;
}

.app-sidebar {
  background: #1a1a2e;
  overflow: hidden;
}

.logo {
  padding: 20px 16px;
  cursor: pointer;
  text-align: center;
}

.logo-text {
  color: #4ECDC4;
  font-size: 18px;
  font-weight: 700;
  letter-spacing: 1px;
}

.app-header {
  background: #ffffff;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  align-items: center;
  padding: 0 24px;
  height: 56px;
}

.header-title {
  font-size: 16px;
  font-weight: 500;
  color: #303133;
}

.app-main {
  background: #f5f7fa;
  padding: 24px;
  overflow-y: auto;
}
</style>
