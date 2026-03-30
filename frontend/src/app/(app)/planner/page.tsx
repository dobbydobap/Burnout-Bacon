"use client";

import { useState, useMemo } from "react";
import {
  format,
  startOfWeek,
  addDays,
  addWeeks,
  subWeeks,
  isSameDay,
  parseISO,
} from "date-fns";
import { ChevronLeft, ChevronRight, Calendar } from "lucide-react";
import { useSessions } from "@/hooks/useSessions";
import styles from "./planner.module.css";

const HOURS = Array.from({ length: 16 }, (_, i) => i + 6); // 6am to 9pm

export default function PlannerPage() {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [view, setView] = useState<"day" | "week">("week");

  const weekStart = startOfWeek(currentDate, { weekStartsOn: 1 });
  const weekDays = Array.from({ length: 7 }, (_, i) => addDays(weekStart, i));

  const startDate = view === "week" ? weekStart.toISOString() : currentDate.toISOString();
  const endDate =
    view === "week"
      ? addDays(weekStart, 7).toISOString()
      : addDays(currentDate, 1).toISOString();

  const { sessions, loading } = useSessions(startDate, endDate);

  const getSessionsForSlot = (day: Date, hour: number) => {
    return sessions.filter((s) => {
      const start = s.planned_start || s.actual_start;
      if (!start) return false;
      const d = parseISO(start);
      return isSameDay(d, day) && d.getHours() === hour;
    });
  };

  const navigate = (dir: number) => {
    if (view === "week") {
      setCurrentDate(dir > 0 ? addWeeks(currentDate, 1) : subWeeks(currentDate, 1));
    } else {
      setCurrentDate(addDays(currentDate, dir));
    }
  };

  return (
    <div>
      <div className={styles.header}>
        <h1 className={styles.title}>Planner</h1>
        <div className={styles.controls}>
          <div className={styles.viewToggle}>
            <button
              className={`${styles.viewBtn} ${view === "day" ? styles.viewBtnActive : ""}`}
              onClick={() => setView("day")}
            >
              Day
            </button>
            <button
              className={`${styles.viewBtn} ${view === "week" ? styles.viewBtnActive : ""}`}
              onClick={() => setView("week")}
            >
              Week
            </button>
          </div>
          <button className={styles.navBtn} onClick={() => navigate(-1)}>
            <ChevronLeft size={16} />
          </button>
          <span className={styles.currentDate}>
            {view === "week"
              ? `${format(weekStart, "MMM d")} - ${format(addDays(weekStart, 6), "MMM d, yyyy")}`
              : format(currentDate, "EEEE, MMM d, yyyy")}
          </span>
          <button className={styles.navBtn} onClick={() => navigate(1)}>
            <ChevronRight size={16} />
          </button>
        </div>
      </div>

      <div className={styles.calendar}>
        {view === "week" ? (
          <>
            <div className={styles.dayHeaders}>
              <div className={styles.dayHeader}></div>
              {weekDays.map((day) => (
                <div key={day.toISOString()} className={styles.dayHeader}>
                  {format(day, "EEE d")}
                </div>
              ))}
            </div>
            <div>
              {HOURS.map((hour) => (
                <div key={hour} className={styles.grid}>
                  <div className={styles.timeSlot}>
                    {format(new Date().setHours(hour, 0), "h a")}
                  </div>
                  {weekDays.map((day) => {
                    const slotSessions = getSessionsForSlot(day, hour);
                    return (
                      <div key={day.toISOString()} className={styles.cell}>
                        {slotSessions.map((s) => (
                          <div key={s.id} className={styles.sessionBlock}>
                            {s.task_title || "Focus Session"}
                          </div>
                        ))}
                      </div>
                    );
                  })}
                </div>
              ))}
            </div>
          </>
        ) : (
          <div>
            {HOURS.map((hour) => (
              <div key={hour} className={styles.gridDay}>
                <div className={styles.timeSlot}>
                  {format(new Date().setHours(hour, 0), "h a")}
                </div>
                <div className={styles.cell}>
                  {getSessionsForSlot(currentDate, hour).map((s) => (
                    <div key={s.id} className={styles.sessionBlock}>
                      {s.task_title || "Focus Session"} -{" "}
                      {s.planned_duration_min || s.actual_duration_min || "?"}min
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
