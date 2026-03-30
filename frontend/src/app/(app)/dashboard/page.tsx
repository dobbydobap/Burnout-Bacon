"use client";

import { useEffect, useState } from "react";
import {
  CheckSquare,
  Clock,
  AlertTriangle,
  TrendingUp,
  ListTodo,
  Timer,
  Target,
  Flame,
  Lightbulb,
} from "lucide-react";
import { apiFetch } from "@/lib/api";
import { Task, StudySession, AnalyticsSummary, BurnoutAssessment } from "@/lib/types";
import { useAuth } from "@/context/AuthContext";
import StatCard from "@/components/ui/StatCard";
import Card from "@/components/ui/Card";
import styles from "./dashboard.module.css";

interface Recommendation {
  id: string;
  rec_type: string;
  title: string;
  body: string;
}

export default function DashboardPage() {
  const { user } = useAuth();
  const [summary, setSummary] = useState<AnalyticsSummary | null>(null);
  const [burnout, setBurnout] = useState<BurnoutAssessment | null>(null);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [sessions, setSessions] = useState<StudySession[]>([]);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);

  useEffect(() => {
    apiFetch<AnalyticsSummary>("/api/analytics/summary").then(setSummary).catch(() => {});
    apiFetch<any>("/api/burnout/current").then(setBurnout).catch(() => {});
    apiFetch<Task[]>("/api/tasks").then(setTasks).catch(() => {});
    apiFetch<StudySession[]>("/api/sessions").then(setSessions).catch(() => {});
    apiFetch<Recommendation[]>("/api/recommendations").then(setRecommendations).catch(() => {});
  }, []);

  const riskColor =
    !burnout || burnout.risk_score < 0.3
      ? "var(--color-risk-low)"
      : burnout.risk_score < 0.6
      ? "var(--color-risk-moderate)"
      : "var(--color-risk-high)";

  return (
    <div>
      <div className={styles.header}>
        <h1 className={styles.greeting}>
          Good{" "}
          {new Date().getHours() < 12
            ? "Morning"
            : new Date().getHours() < 18
            ? "Afternoon"
            : "Evening"}
          , {user?.name?.split(" ")[0]}
        </h1>
        <p className={styles.date}>
          {new Date().toLocaleDateString("en-US", {
            weekday: "long",
            year: "numeric",
            month: "long",
            day: "numeric",
          })}
        </p>
      </div>

      <div className={styles.statsGrid}>
        <StatCard
          icon={<ListTodo size={20} />}
          iconBg="var(--color-accent-blue-light)"
          iconColor="var(--color-accent-blue)"
          label="Total Tasks"
          value={summary?.total_tasks ?? 0}
        />
        <StatCard
          icon={<CheckSquare size={20} />}
          iconBg="var(--color-accent-green-light)"
          iconColor="var(--color-accent-green)"
          label="Completed"
          value={summary?.completed_tasks ?? 0}
        />
        <StatCard
          icon={<Clock size={20} />}
          iconBg="var(--color-accent-orange-light)"
          iconColor="var(--color-accent-orange)"
          label="Pending"
          value={summary?.pending_tasks ?? 0}
        />
        <StatCard
          icon={<AlertTriangle size={20} />}
          iconBg="var(--color-accent-red-light)"
          iconColor="var(--color-accent-red)"
          label="Overdue"
          value={summary?.overdue_tasks ?? 0}
        />
        <StatCard
          icon={<Timer size={20} />}
          iconBg="var(--color-accent-gold-light)"
          iconColor="var(--color-accent-gold)"
          label="Focus Hours"
          value={`${summary?.total_focus_hours ?? 0}h`}
        />
        <StatCard
          icon={<Target size={20} />}
          iconBg="var(--color-accent-green-light)"
          iconColor="var(--color-accent-green)"
          label="Completion Rate"
          value={`${summary?.completion_rate ?? 0}%`}
        />
        <StatCard
          icon={<Flame size={20} />}
          iconBg={burnout?.risk_score && burnout.risk_score >= 0.5 ? "var(--color-accent-red-light)" : "var(--color-accent-green-light)"}
          iconColor={riskColor}
          label="Burnout Risk"
          value={burnout?.risk_level?.toUpperCase() ?? "LOW"}
        />
        <StatCard
          icon={<TrendingUp size={20} />}
          iconBg="var(--color-accent-blue-light)"
          iconColor="var(--color-accent-blue)"
          label="Day Streak"
          value={summary?.current_streak ?? 0}
        />
      </div>

      <div className={styles.cardsRow}>
        <Card>
          <h3 className={styles.cardTitle}>Recent Tasks</h3>
          {tasks.length === 0 ? (
            <p className={styles.empty}>No tasks yet. Create one from the Tasks page.</p>
          ) : (
            <div className={styles.taskList}>
              {tasks.slice(0, 5).map((task) => (
                <div key={task.id} className={styles.taskItem}>
                  <div
                    className={styles.taskDot}
                    style={{
                      background:
                        task.status === "done"
                          ? "var(--color-accent-green)"
                          : task.status === "in_progress"
                          ? "var(--color-accent-blue)"
                          : "var(--color-text-muted)",
                    }}
                  />
                  <div className={styles.taskInfo}>
                    <span className={styles.taskTitle}>{task.title}</span>
                    <span className={styles.taskMeta}>{task.category}</span>
                  </div>
                  <span
                    className={styles.taskPriority}
                    style={{
                      color:
                        task.priority === "critical"
                          ? "var(--color-accent-red)"
                          : task.priority === "high"
                          ? "var(--color-accent-orange)"
                          : "var(--color-text-muted)",
                    }}
                  >
                    {task.priority}
                  </span>
                </div>
              ))}
            </div>
          )}
        </Card>

        <Card>
          <h3 className={styles.cardTitle}>
            <Lightbulb size={18} style={{ marginRight: 8, color: "var(--color-accent-gold)" }} />
            Recommendations
          </h3>
          {recommendations.length === 0 ? (
            <p className={styles.empty}>No recommendations yet.</p>
          ) : (
            <div className={styles.taskList}>
              {recommendations.slice(0, 5).map((rec) => (
                <div key={rec.id} className={styles.taskItem}>
                  <div
                    className={styles.taskDot}
                    style={{ background: "var(--color-accent-gold)" }}
                  />
                  <div className={styles.taskInfo}>
                    <span className={styles.taskTitle}>{rec.title}</span>
                    <span className={styles.taskMeta}>{rec.body}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </Card>
      </div>
    </div>
  );
}
