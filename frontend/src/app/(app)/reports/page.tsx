"use client";

import { useEffect, useState } from "react";
import { format, startOfWeek } from "date-fns";
import { apiFetch } from "@/lib/api";
import styles from "./reports.module.css";

interface DailyReport {
  date: string;
  total_sessions_planned: number;
  sessions_completed: number;
  sessions_missed: number;
  total_focus_hours: number;
  tasks_nearing_deadline: number;
  burnout_risk_level: string;
}

interface WeeklyReport {
  week_start: string;
  week_end: string;
  productivity_score: number;
  total_focus_hours: number;
  tasks_completed: number;
  completion_rate: number;
  most_productive_day: string;
  burnout_trend: string;
  recommendations: string[];
}

export default function ReportsPage() {
  const [daily, setDaily] = useState<DailyReport | null>(null);
  const [weekly, setWeekly] = useState<WeeklyReport | null>(null);

  useEffect(() => {
    apiFetch<DailyReport>("/api/reports/daily").then(setDaily).catch(() => {});
    apiFetch<WeeklyReport>("/api/reports/weekly").then(setWeekly).catch(() => {});
  }, []);

  const riskColor = (level: string) => {
    if (level === "critical") return "var(--color-accent-red)";
    if (level === "high") return "var(--color-accent-orange)";
    if (level === "moderate") return "var(--color-accent-orange)";
    return "var(--color-accent-green)";
  };

  return (
    <div>
      <h1 className={styles.title}>Reports</h1>

      <div className={styles.grid}>
        <div className={styles.reportCard}>
          <h2 className={styles.reportTitle}>Daily Report</h2>
          <p className={styles.reportDate}>
            {daily ? format(new Date(daily.date), "EEEE, MMMM d, yyyy") : "Loading..."}
          </p>
          {daily && (
            <div>
              <div className={styles.metricRow}>
                <span className={styles.metricLabel}>Sessions Planned</span>
                <span className={styles.metricValue}>{daily.total_sessions_planned}</span>
              </div>
              <div className={styles.metricRow}>
                <span className={styles.metricLabel}>Completed</span>
                <span className={styles.metricValue}>{daily.sessions_completed}</span>
              </div>
              <div className={styles.metricRow}>
                <span className={styles.metricLabel}>Missed</span>
                <span className={styles.metricValue}>{daily.sessions_missed}</span>
              </div>
              <div className={styles.metricRow}>
                <span className={styles.metricLabel}>Focus Time</span>
                <span className={styles.metricValue}>{daily.total_focus_hours}h</span>
              </div>
              <div className={styles.metricRow}>
                <span className={styles.metricLabel}>Tasks Near Deadline</span>
                <span className={styles.metricValue}>{daily.tasks_nearing_deadline}</span>
              </div>
              <div className={styles.metricRow}>
                <span className={styles.metricLabel}>Burnout Risk</span>
                <span className={styles.metricValue} style={{ color: riskColor(daily.burnout_risk_level) }}>
                  {daily.burnout_risk_level.charAt(0).toUpperCase() + daily.burnout_risk_level.slice(1)}
                </span>
              </div>
            </div>
          )}
        </div>

        <div className={styles.reportCard}>
          <h2 className={styles.reportTitle}>Weekly Report</h2>
          <p className={styles.reportDate}>
            {weekly ? `${weekly.week_start} — ${weekly.week_end}` : "Loading..."}
          </p>
          {weekly && (
            <div>
              <div className={styles.metricRow}>
                <span className={styles.metricLabel}>Focus Hours</span>
                <span className={styles.metricValue}>{weekly.total_focus_hours}h</span>
              </div>
              <div className={styles.metricRow}>
                <span className={styles.metricLabel}>Tasks Completed</span>
                <span className={styles.metricValue}>{weekly.tasks_completed}</span>
              </div>
              <div className={styles.metricRow}>
                <span className={styles.metricLabel}>Completion Rate</span>
                <span className={styles.metricValue}>{weekly.completion_rate}%</span>
              </div>
              <div className={styles.metricRow}>
                <span className={styles.metricLabel}>Most Productive Day</span>
                <span className={styles.metricValue}>{weekly.most_productive_day}</span>
              </div>
              <div className={styles.metricRow}>
                <span className={styles.metricLabel}>Burnout Trend</span>
                <span className={styles.metricValue} style={{
                  color: weekly.burnout_trend === "increasing" ? "var(--color-accent-red)" : "var(--color-accent-green)"
                }}>
                  {weekly.burnout_trend.charAt(0).toUpperCase() + weekly.burnout_trend.slice(1)}
                </span>
              </div>
              {weekly.recommendations.length > 0 && (
                <div style={{ marginTop: "var(--space-4)", padding: "var(--space-3)", background: "var(--color-accent-gold-light)", borderRadius: "var(--radius-md)" }}>
                  <strong style={{ fontSize: "var(--font-size-xs)", color: "var(--color-accent-gold)" }}>RECOMMENDATIONS</strong>
                  {weekly.recommendations.map((r, i) => (
                    <p key={i} style={{ fontSize: "var(--font-size-sm)", color: "var(--color-text-secondary)", marginTop: "var(--space-2)" }}>
                      {r}
                    </p>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
