"use client";

import { useEffect, useState } from "react";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
} from "recharts";
import { apiFetch } from "@/lib/api";
import { BurnoutAssessment, HeatmapEntry } from "@/lib/types";
import Card from "@/components/ui/Card";
import Button from "@/components/ui/Button";
import styles from "./analytics.module.css";

const COLORS = ["#F5C518", "#42A5F5", "#4CAF50", "#FF9800", "#E53935", "#9C27B0", "#00BCD4"];

interface CategoryStat {
  category: string;
  total_tasks: number;
  completed_tasks: number;
  total_focus_minutes: number;
  completion_rate: number;
}

interface FocusPatterns {
  hourly: { hour: number; minutes: number }[];
  daily: { day: string; minutes: number }[];
}

export default function AnalyticsPage() {
  const [heatmap, setHeatmap] = useState<HeatmapEntry[]>([]);
  const [burnout, setBurnout] = useState<BurnoutAssessment | null>(null);
  const [categories, setCategories] = useState<CategoryStat[]>([]);
  const [patterns, setPatterns] = useState<FocusPatterns | null>(null);
  const [assessing, setAssessing] = useState(false);

  useEffect(() => {
    apiFetch<HeatmapEntry[]>(`/api/analytics/heatmap?year=${new Date().getFullYear()}`).then(setHeatmap).catch(() => {});
    apiFetch<any>("/api/burnout/current").then(setBurnout).catch(() => {});
    apiFetch<CategoryStat[]>("/api/analytics/categories").then(setCategories).catch(() => {});
    apiFetch<FocusPatterns>("/api/analytics/focus-patterns").then(setPatterns).catch(() => {});
  }, []);

  const triggerAssessment = async () => {
    setAssessing(true);
    try {
      const result = await apiFetch<BurnoutAssessment>("/api/burnout/assess", { method: "POST" });
      setBurnout(result);
    } catch {}
    setAssessing(false);
  };

  const maxFocus = Math.max(...heatmap.map((d) => d.value), 1);
  const getHeatmapColor = (value: number) => {
    if (value === 0) return "var(--color-bg-secondary)";
    const intensity = value / maxFocus;
    if (intensity < 0.25) return "#FFF3C4";
    if (intensity < 0.5) return "#F5C518";
    if (intensity < 0.75) return "#E0B400";
    return "#B8860B";
  };

  const burnoutScore = burnout?.risk_score ?? 0;
  const riskLevel = burnout?.risk_level ?? "low";
  const riskColor =
    burnoutScore < 0.3 ? "var(--color-risk-low)"
    : burnoutScore < 0.6 ? "var(--color-risk-moderate)"
    : "var(--color-risk-high)";

  const pieData = categories.map((c) => ({ name: c.category, value: c.total_tasks }));

  // Focus by hour chart data
  const hourlyData = patterns?.hourly.filter((h) => h.minutes > 0) || [];

  return (
    <div>
      <h1 className={styles.title}>Analytics</h1>

      <div className={styles.grid}>
        <Card>
          <h3 className={styles.cardTitle}>Burnout Risk</h3>
          <div className={styles.gaugeWrapper}>
            <svg width="180" height="100" viewBox="0 0 180 100">
              <path
                d="M 10 90 A 80 80 0 0 1 170 90"
                fill="none"
                stroke="var(--color-bg-secondary)"
                strokeWidth="14"
                strokeLinecap="round"
              />
              <path
                d="M 10 90 A 80 80 0 0 1 170 90"
                fill="none"
                stroke={riskColor}
                strokeWidth="14"
                strokeLinecap="round"
                strokeDasharray={`${burnoutScore * 251} 251`}
              />
            </svg>
            <div className={styles.gaugeValue} style={{ color: riskColor }}>
              {Math.round(burnoutScore * 100)}%
            </div>
            <div className={styles.gaugeLabel}>{riskLevel.charAt(0).toUpperCase() + riskLevel.slice(1)} Risk</div>
            <Button size="sm" variant="secondary" onClick={triggerAssessment} disabled={assessing} style={{ marginTop: 12 }}>
              {assessing ? "Assessing..." : "Run Assessment"}
            </Button>
          </div>
          {burnout?.recommendation && (
            <p style={{ fontSize: "var(--font-size-sm)", color: "var(--color-text-secondary)", marginTop: "var(--space-4)", textAlign: "center" }}>
              {burnout.recommendation}
            </p>
          )}
        </Card>

        <Card>
          <h3 className={styles.cardTitle}>Tasks by Category</h3>
          {pieData.length === 0 ? (
            <p className={styles.empty}>No tasks yet.</p>
          ) : (
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={90}
                  paddingAngle={3}
                  dataKey="value"
                  label={({ name, value }) => `${name}: ${value}`}
                >
                  {pieData.map((_, i) => (
                    <Cell key={i} fill={COLORS[i % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          )}
        </Card>

        <Card className={styles.fullWidth}>
          <h3 className={styles.cardTitle}>Productivity Heatmap</h3>
          <div className={styles.heatmapGrid}>
            {heatmap.map((d) => (
              <div
                key={d.date}
                className={styles.heatmapCell}
                style={{ background: getHeatmapColor(d.value) }}
                title={`${d.date}: ${d.value}min`}
              />
            ))}
          </div>
        </Card>

        <Card>
          <h3 className={styles.cardTitle}>Focus by Hour</h3>
          {hourlyData.length === 0 ? (
            <p className={styles.empty}>No session data yet.</p>
          ) : (
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={patterns?.hourly}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--color-bg-secondary)" />
                <XAxis dataKey="hour" tick={{ fontSize: 10 }} />
                <YAxis tick={{ fontSize: 10 }} />
                <Tooltip />
                <Bar dataKey="minutes" fill="#F5C518" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </Card>

        <Card>
          <h3 className={styles.cardTitle}>Focus by Day</h3>
          {!patterns?.daily.some((d) => d.minutes > 0) ? (
            <p className={styles.empty}>No session data yet.</p>
          ) : (
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={patterns?.daily}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--color-bg-secondary)" />
                <XAxis dataKey="day" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 10 }} />
                <Tooltip />
                <Bar dataKey="minutes" fill="#42A5F5" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </Card>

        <Card className={styles.fullWidth}>
          <h3 className={styles.cardTitle}>Category Performance</h3>
          {categories.length === 0 ? (
            <p className={styles.empty}>No tasks yet.</p>
          ) : (
            <div style={{ overflowX: "auto" }}>
              <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "var(--font-size-sm)" }}>
                <thead>
                  <tr style={{ borderBottom: "1px solid var(--color-bg-secondary)", textAlign: "left" }}>
                    <th style={{ padding: "var(--space-3)" }}>Category</th>
                    <th style={{ padding: "var(--space-3)" }}>Tasks</th>
                    <th style={{ padding: "var(--space-3)" }}>Completed</th>
                    <th style={{ padding: "var(--space-3)" }}>Focus Time</th>
                    <th style={{ padding: "var(--space-3)" }}>Rate</th>
                  </tr>
                </thead>
                <tbody>
                  {categories.map((c) => (
                    <tr key={c.category} style={{ borderBottom: "1px solid var(--color-bg-secondary)" }}>
                      <td style={{ padding: "var(--space-3)", fontWeight: 600 }}>{c.category}</td>
                      <td style={{ padding: "var(--space-3)" }}>{c.total_tasks}</td>
                      <td style={{ padding: "var(--space-3)" }}>{c.completed_tasks}</td>
                      <td style={{ padding: "var(--space-3)" }}>{(c.total_focus_minutes / 60).toFixed(1)}h</td>
                      <td style={{ padding: "var(--space-3)", color: c.completion_rate >= 50 ? "var(--color-accent-green)" : "var(--color-accent-orange)" }}>
                        {c.completion_rate}%
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Card>
      </div>
    </div>
  );
}
