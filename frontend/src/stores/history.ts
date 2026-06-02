import { defineStore } from "pinia";
import { ref } from "vue";
import type { TaskHistoryItem, TaskHistoryResponse } from "@/types";
import { getTaskHistory, deleteTask, deleteTasksBatch } from "@/api/tasks";

export const useHistoryStore = defineStore("history", () => {
  const items = ref<TaskHistoryItem[]>([]);
  const isLoading = ref(false);
  const pagination = ref({ page: 1, size: 20, total: 0, has_next: false });
  const filterModel = ref<string>("");
  const filterStatus = ref<string>("");
  const searchQuery = ref("");

  async function load(page = 1) {
    isLoading.value = true;
    try {
      const res = await getTaskHistory({
        model: filterModel.value || undefined,
        status: filterStatus.value || undefined,
        q: searchQuery.value || undefined,
        page,
        size: 20,
      });
      if (page === 1) {
        items.value = res.items;
      } else {
        items.value.push(...res.items);
      }
      pagination.value = res.pagination;
    } finally {
      isLoading.value = false;
    }
  }

  async function loadMore() {
    if (pagination.value.has_next) {
      await load(pagination.value.page + 1);
    }
  }

  async function remove(taskId: string) {
    await deleteTask(taskId);
    items.value = items.value.filter((i) => i.task_id !== taskId);
  }

  async function removeBatch(taskIds: string[]) {
    await deleteTasksBatch(taskIds);
    items.value = items.value.filter((i) => !taskIds.includes(i.task_id));
  }

  function setFilter(model: string, status: string) {
    filterModel.value = model;
    filterStatus.value = status;
    load(1);
  }

  function search(q: string) {
    searchQuery.value = q;
    load(1);
  }

  return {
    items,
    isLoading,
    pagination,
    filterModel,
    filterStatus,
    searchQuery,
    load,
    loadMore,
    remove,
    removeBatch,
    setFilter,
    search,
  };
});
