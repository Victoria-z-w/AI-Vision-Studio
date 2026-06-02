import { createRouter, createWebHistory } from "vue-router";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: "/",
      name: "home",
      component: () => import("@/views/HomePage.vue"),
    },
    {
      path: "/upload",
      name: "upload",
      component: () => import("@/views/UploadPage.vue"),
    },
    {
      path: "/tasks/:taskId",
      name: "result",
      component: () => import("@/views/ResultPage.vue"),
    },
    {
      path: "/history",
      name: "history",
      component: () => import("@/views/HistoryPage.vue"),
    },
    {
      path: "/settings",
      name: "settings",
      component: () => import("@/views/SettingsPage.vue"),
    },
  ],
});

export default router;
