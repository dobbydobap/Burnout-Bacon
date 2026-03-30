"use client";

import { useEffect, useState } from "react";
import { AlertTriangle, AlertCircle, Info, X, Bell } from "lucide-react";
import { apiFetch } from "@/lib/api";
import { Alert } from "@/lib/types";
import { formatTimeAgo } from "@/lib/utils";
import styles from "./alerts.module.css";

export default function AlertsPage() {
  const [alerts, setAlerts] = useState<Alert[]>([]);

  useEffect(() => {
    apiFetch<Alert[]>("/api/alerts")
      .then(setAlerts)
      .catch(() => {});
  }, []);

  const markRead = async (id: string) => {
    await apiFetch(`/api/alerts/${id}/read`, { method: "PATCH" });
    setAlerts((prev) => prev.map((a) => (a.id === id ? { ...a, is_read: true } : a)));
  };

  const dismiss = async (id: string) => {
    await apiFetch(`/api/alerts/${id}/dismiss`, { method: "PATCH" });
    setAlerts((prev) => prev.filter((a) => a.id !== id));
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case "critical":
        return <AlertTriangle size={18} color="var(--color-accent-red)" />;
      case "warning":
        return <AlertCircle size={18} color="var(--color-accent-orange)" />;
      default:
        return <Info size={18} color="var(--color-accent-blue)" />;
    }
  };

  const getSeverityClass = (severity: string) => {
    switch (severity) {
      case "critical":
        return styles.alertCritical;
      case "warning":
        return styles.alertWarning;
      default:
        return styles.alertInfo;
    }
  };

  return (
    <div>
      <h1 className={styles.title}>Alerts</h1>

      {alerts.length === 0 ? (
        <div className={styles.empty}>
          <Bell size={48} style={{ marginBottom: "var(--space-4)", color: "var(--color-bg-secondary)" }} />
          <p>No alerts. You&apos;re on track!</p>
        </div>
      ) : (
        <div className={styles.alertsList}>
          {alerts.map((alert) => (
            <div
              key={alert.id}
              className={`${styles.alertCard} ${getSeverityClass(alert.severity)}`}
              style={{ opacity: alert.is_read ? 0.7 : 1 }}
              onClick={() => !alert.is_read && markRead(alert.id)}
            >
              <div className={styles.alertIcon}>
                {getSeverityIcon(alert.severity)}
              </div>
              <div className={styles.alertContent}>
                <div className={styles.alertTitle}>{alert.title}</div>
                <div className={styles.alertMessage}>{alert.message}</div>
                <div className={styles.alertTime}>{formatTimeAgo(alert.created_at)}</div>
              </div>
              <div className={styles.alertActions}>
                <button
                  className={styles.dismissBtn}
                  onClick={(e) => {
                    e.stopPropagation();
                    dismiss(alert.id);
                  }}
                >
                  <X size={16} />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
