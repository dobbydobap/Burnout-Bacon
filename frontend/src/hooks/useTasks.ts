"use client";

import { useState, useEffect, useCallback } from "react";
import { apiFetch } from "@/lib/api";
import { Task, TaskCreate, TaskUpdate } from "@/lib/types";

export function useTasks() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchTasks = useCallback(async (filters?: Record<string, string>) => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (filters) {
        Object.entries(filters).forEach(([k, v]) => {
          if (v) params.set(k, v);
        });
      }
      const qs = params.toString();
      const data = await apiFetch<Task[]>(`/api/tasks${qs ? `?${qs}` : ""}`);
      setTasks(data);
    } catch {
      // handled by apiFetch
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchTasks();
  }, [fetchTasks]);

  const createTask = async (data: TaskCreate) => {
    const task = await apiFetch<Task>("/api/tasks", {
      method: "POST",
      body: JSON.stringify(data),
    });
    setTasks((prev) => [task, ...prev]);
    return task;
  };

  const updateTask = async (id: string, data: TaskUpdate) => {
    const task = await apiFetch<Task>(`/api/tasks/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    });
    setTasks((prev) => prev.map((t) => (t.id === id ? task : t)));
    return task;
  };

  const deleteTask = async (id: string) => {
    await apiFetch(`/api/tasks/${id}`, { method: "DELETE" });
    setTasks((prev) => prev.filter((t) => t.id !== id));
  };

  return { tasks, loading, fetchTasks, createTask, updateTask, deleteTask };
}
