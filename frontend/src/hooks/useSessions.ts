"use client";

import { useState, useEffect, useCallback } from "react";
import { apiFetch } from "@/lib/api";
import { StudySession } from "@/lib/types";

export function useSessions(startDate?: string, endDate?: string) {
  const [sessions, setSessions] = useState<StudySession[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchSessions = useCallback(async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (startDate) params.set("start_date", startDate);
      if (endDate) params.set("end_date", endDate);
      const qs = params.toString();
      const data = await apiFetch<StudySession[]>(
        `/api/sessions${qs ? `?${qs}` : ""}`
      );
      setSessions(data);
    } catch {
      // handled by apiFetch
    } finally {
      setLoading(false);
    }
  }, [startDate, endDate]);

  useEffect(() => {
    fetchSessions();
  }, [fetchSessions]);

  const startSession = async (taskId?: string, sessionType?: string) => {
    const session = await apiFetch<StudySession>("/api/sessions/start", {
      method: "POST",
      body: JSON.stringify({
        task_id: taskId || null,
        session_type: sessionType || "deep_work",
      }),
    });
    setSessions((prev) => [session, ...prev]);
    return session;
  };

  const stopSession = async (
    sessionId: string,
    wasCompleted: boolean,
    focusRating?: number,
    notes?: string
  ) => {
    const session = await apiFetch<StudySession>(
      `/api/sessions/${sessionId}/stop`,
      {
        method: "POST",
        body: JSON.stringify({
          was_completed: wasCompleted,
          focus_rating: focusRating,
          notes: notes || null,
        }),
      }
    );
    setSessions((prev) => prev.map((s) => (s.id === sessionId ? session : s)));
    return session;
  };

  return { sessions, loading, fetchSessions, startSession, stopSession };
}
