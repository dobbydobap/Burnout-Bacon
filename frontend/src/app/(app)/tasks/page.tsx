"use client";

import { useState } from "react";
import { Plus, Edit2, Trash2, Check, CheckSquare, Clock, Calendar } from "lucide-react";
import { useTasks } from "@/hooks/useTasks";
import { Task, TaskCreate } from "@/lib/types";
import { CATEGORIES, PRIORITIES } from "@/lib/constants";
import { formatDate, minutesToHours, capitalize } from "@/lib/utils";
import Button from "@/components/ui/Button";
import Badge from "@/components/ui/Badge";
import Modal from "@/components/ui/Modal";
import Input, { Select, Textarea } from "@/components/ui/Input";
import styles from "./tasks.module.css";

const STATUS_FILTERS = [
  { value: "", label: "All" },
  { value: "todo", label: "To Do" },
  { value: "in_progress", label: "In Progress" },
  { value: "done", label: "Done" },
];

export default function TasksPage() {
  const { tasks, loading, createTask, updateTask, deleteTask } = useTasks();
  const [statusFilter, setStatusFilter] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [editingTask, setEditingTask] = useState<Task | null>(null);

  // Form state
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [category, setCategory] = useState("Other");
  const [priority, setPriority] = useState("medium");
  const [deadline, setDeadline] = useState("");
  const [estimatedMinutes, setEstimatedMinutes] = useState("");

  const filteredTasks = statusFilter
    ? tasks.filter((t) => t.status === statusFilter)
    : tasks;

  const resetForm = () => {
    setTitle("");
    setDescription("");
    setCategory("Other");
    setPriority("medium");
    setDeadline("");
    setEstimatedMinutes("");
    setEditingTask(null);
  };

  const openCreate = () => {
    resetForm();
    setShowForm(true);
  };

  const openEdit = (task: Task) => {
    setTitle(task.title);
    setDescription(task.description || "");
    setCategory(task.category);
    setPriority(task.priority);
    setDeadline(task.deadline ? task.deadline.slice(0, 16) : "");
    setEstimatedMinutes(task.estimated_minutes?.toString() || "");
    setEditingTask(task);
    setShowForm(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const data: any = {
      title,
      description: description || undefined,
      category,
      priority,
      deadline: deadline ? new Date(deadline).toISOString() : undefined,
      estimated_minutes: estimatedMinutes ? parseInt(estimatedMinutes) : undefined,
    };

    if (editingTask) {
      await updateTask(editingTask.id, data);
    } else {
      await createTask(data);
    }
    setShowForm(false);
    resetForm();
  };

  const toggleComplete = async (task: Task) => {
    const newStatus = task.status === "done" ? "todo" : "done";
    await updateTask(task.id, { status: newStatus });
  };

  const priorityBadge = (p: string) => {
    const colors: Record<string, { bg: string; color: string }> = {
      low: { bg: "var(--color-accent-blue-light)", color: "var(--color-accent-blue)" },
      medium: { bg: "var(--color-accent-gold-light)", color: "#8B7000" },
      high: { bg: "var(--color-accent-orange-light)", color: "var(--color-accent-orange)" },
      critical: { bg: "var(--color-accent-red-light)", color: "var(--color-accent-red)" },
    };
    const c = colors[p] || colors.medium;
    return <Badge bg={c.bg} color={c.color}>{capitalize(p)}</Badge>;
  };

  return (
    <div>
      <div className={styles.header}>
        <h1 className={styles.title}>Tasks</h1>
        <Button onClick={openCreate}>
          <Plus size={16} /> New Task
        </Button>
      </div>

      <div className={styles.filters}>
        {STATUS_FILTERS.map((f) => (
          <button
            key={f.value}
            className={`${styles.filterBtn} ${
              statusFilter === f.value ? styles.filterBtnActive : ""
            }`}
            onClick={() => setStatusFilter(f.value)}
          >
            {f.label}
          </button>
        ))}
      </div>

      {loading ? (
        <p className={styles.empty}>Loading tasks...</p>
      ) : filteredTasks.length === 0 ? (
        <div className={styles.empty}>
          <CheckSquare size={48} className={styles.emptyIcon} />
          <p>No tasks found. Create your first task!</p>
        </div>
      ) : (
        <div className={styles.taskGrid}>
          {filteredTasks.map((task) => (
            <div key={task.id} className={styles.taskRow}>
              <div
                className={`${styles.taskCheck} ${
                  task.status === "done" ? styles.taskCheckDone : ""
                }`}
                onClick={() => toggleComplete(task)}
              >
                {task.status === "done" && <Check size={14} />}
              </div>
              <div className={styles.taskContent}>
                <span
                  className={`${styles.taskName} ${
                    task.status === "done" ? styles.taskNameDone : ""
                  }`}
                >
                  {task.title}
                </span>
                <div className={styles.taskDetails}>
                  <span>{task.category}</span>
                  {task.estimated_minutes && (
                    <>
                      <Clock size={12} />
                      <span>{minutesToHours(task.estimated_minutes)}</span>
                    </>
                  )}
                  {task.deadline && (
                    <>
                      <Calendar size={12} />
                      <span>{formatDate(task.deadline)}</span>
                    </>
                  )}
                </div>
              </div>
              {priorityBadge(task.priority)}
              <div className={styles.taskActions}>
                <button
                  className={styles.actionBtn}
                  onClick={() => openEdit(task)}
                  title="Edit"
                >
                  <Edit2 size={16} />
                </button>
                <button
                  className={`${styles.actionBtn} ${styles.deleteBtn}`}
                  onClick={() => deleteTask(task.id)}
                  title="Delete"
                >
                  <Trash2 size={16} />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {showForm && (
        <Modal
          title={editingTask ? "Edit Task" : "New Task"}
          onClose={() => {
            setShowForm(false);
            resetForm();
          }}
        >
          <form onSubmit={handleSubmit}>
            <div className={styles.formGrid}>
              <div className={styles.formFull}>
                <Input
                  label="Title"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="Task title"
                  required
                />
              </div>
              <div className={styles.formFull}>
                <Textarea
                  label="Description"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Optional description"
                />
              </div>
              <Select
                label="Category"
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                options={CATEGORIES.map((c) => ({ value: c, label: c }))}
              />
              <Select
                label="Priority"
                value={priority}
                onChange={(e) => setPriority(e.target.value)}
                options={PRIORITIES.map((p) => ({ value: p, label: capitalize(p) }))}
              />
              <Input
                label="Deadline"
                type="datetime-local"
                value={deadline}
                onChange={(e) => setDeadline(e.target.value)}
              />
              <Input
                label="Estimated (minutes)"
                type="number"
                value={estimatedMinutes}
                onChange={(e) => setEstimatedMinutes(e.target.value)}
                placeholder="e.g. 120"
                min="1"
              />
            </div>
            <div className={styles.formActions}>
              <Button
                variant="secondary"
                type="button"
                onClick={() => {
                  setShowForm(false);
                  resetForm();
                }}
              >
                Cancel
              </Button>
              <Button type="submit">
                {editingTask ? "Update Task" : "Create Task"}
              </Button>
            </div>
          </form>
        </Modal>
      )}
    </div>
  );
}
