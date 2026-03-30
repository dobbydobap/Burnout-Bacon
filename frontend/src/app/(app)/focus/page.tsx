"use client";

import { useState, useEffect } from "react";
import { Play, Square, Star } from "lucide-react";
import { useTimer } from "@/context/TimerContext";
import { useSessions } from "@/hooks/useSessions";
import { useTasks } from "@/hooks/useTasks";
import { minutesToHours, formatTimeAgo } from "@/lib/utils";
import { Select } from "@/components/ui/Input";
import Button from "@/components/ui/Button";
import styles from "./focus.module.css";

function formatTimer(seconds: number): string {
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = seconds % 60;
  return `${h.toString().padStart(2, "0")}:${m.toString().padStart(2, "0")}:${s
    .toString()
    .padStart(2, "0")}`;
}

export default function FocusPage() {
  const timer = useTimer();
  const { tasks } = useTasks();
  const { sessions, startSession, stopSession, fetchSessions } = useSessions();
  const [selectedTaskId, setSelectedTaskId] = useState<string>("");
  const [showSummary, setShowSummary] = useState(false);
  const [focusRating, setFocusRating] = useState(0);
  const [completedDuration, setCompletedDuration] = useState(0);

  const activeTasks = tasks.filter((t) => t.status !== "done" && t.status !== "cancelled");

  const handleStart = async () => {
    const taskId = selectedTaskId || undefined;
    const task = tasks.find((t) => t.id === taskId);
    const session = await startSession(taskId);
    timer.startTimer(session.id, taskId, task?.title);
  };

  const handleStop = async () => {
    if (!timer.activeSessionId) return;
    timer.stopTimer();
    setCompletedDuration(timer.elapsedSeconds);
    setShowSummary(true);
  };

  const handleSaveSummary = async () => {
    if (!timer.activeSessionId) return;
    await stopSession(timer.activeSessionId, true, focusRating || undefined);
    timer.resetTimer();
    setShowSummary(false);
    setFocusRating(0);
    fetchSessions();
  };

  const handleDiscardSummary = async () => {
    if (!timer.activeSessionId) return;
    await stopSession(timer.activeSessionId, false);
    timer.resetTimer();
    setShowSummary(false);
    setFocusRating(0);
    fetchSessions();
  };

  if (showSummary) {
    return (
      <div className={styles.page}>
        <h1 className={styles.title}>Focus</h1>
        <div className={styles.summaryCard}>
          <h2 className={styles.summaryTitle}>Session Complete</h2>
          <div className={styles.summaryTime}>
            {formatTimer(completedDuration)}
          </div>
          {timer.activeTaskTitle && (
            <p className={styles.activeTask}>{timer.activeTaskTitle}</p>
          )}
          <p style={{ color: "var(--color-text-secondary)", marginBottom: "var(--space-4)" }}>
            How focused were you?
          </p>
          <div className={styles.ratingStars}>
            {[1, 2, 3, 4, 5].map((n) => (
              <button
                key={n}
                className={`${styles.star} ${n <= focusRating ? styles.starActive : ""}`}
                onClick={() => setFocusRating(n)}
              >
                <Star size={28} fill={n <= focusRating ? "currentColor" : "none"} />
              </button>
            ))}
          </div>
          <div style={{ display: "flex", gap: "var(--space-3)", justifyContent: "center", marginTop: "var(--space-8)" }}>
            <Button variant="secondary" onClick={handleDiscardSummary}>
              Discard
            </Button>
            <Button onClick={handleSaveSummary}>Save Session</Button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.page}>
      <h1 className={styles.title}>Focus</h1>

      <div className={styles.timerCard}>
        {!timer.isRunning && (
          <div className={styles.taskSelect}>
            <span className={styles.taskSelectLabel}>Select a task (optional)</span>
            <Select
              options={[
                { value: "", label: "Free session" },
                ...activeTasks.map((t) => ({ value: t.id, label: t.title })),
              ]}
              value={selectedTaskId}
              onChange={(e) => setSelectedTaskId(e.target.value)}
            />
          </div>
        )}

        {timer.isRunning && timer.activeTaskTitle && (
          <div className={styles.activeTask}>{timer.activeTaskTitle}</div>
        )}

        <div className={styles.timerDisplay}>{formatTimer(timer.elapsedSeconds)}</div>
        <div className={styles.timerLabel}>
          {timer.isRunning ? "Session in progress" : "Ready to focus"}
        </div>

        <div className={styles.timerControls}>
          {timer.isRunning ? (
            <button className={`${styles.startBtn} ${styles.stopBtn}`} onClick={handleStop}>
              <Square size={24} />
            </button>
          ) : (
            <button className={styles.startBtn} onClick={handleStart}>
              <Play size={24} />
            </button>
          )}
        </div>
      </div>

      <div className={styles.sessionsList}>
        <h2 className={styles.sectionTitle}>Recent Sessions</h2>
        {sessions.length === 0 ? (
          <p style={{ color: "var(--color-text-muted)", textAlign: "center", padding: "var(--space-8) 0" }}>
            No sessions yet. Start your first focus session!
          </p>
        ) : (
          sessions.slice(0, 10).map((s) => (
            <div key={s.id} className={styles.sessionItem}>
              <div
                className={styles.sessionDot}
                style={{
                  background: s.was_completed
                    ? "var(--color-accent-green)"
                    : s.actual_end
                    ? "var(--color-accent-orange)"
                    : "var(--color-accent-blue)",
                }}
              />
              <div className={styles.sessionInfo}>
                <div className={styles.sessionTitle}>
                  {s.task_title || "Free Session"}
                </div>
                <div className={styles.sessionMeta}>
                  {s.created_at && formatTimeAgo(s.created_at)}
                  {s.focus_rating && ` · ${s.focus_rating}/5 focus`}
                </div>
              </div>
              <div className={styles.sessionDuration}>
                {s.actual_duration_min ? minutesToHours(s.actual_duration_min) : "—"}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
