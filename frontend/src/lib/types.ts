export interface User {
  id: string;
  name: string;
  email: string;
}

export interface Task {
  id: string;
  user_id: string;
  title: string;
  description: string | null;
  category: string;
  priority: "low" | "medium" | "high" | "critical";
  status: "todo" | "in_progress" | "done" | "cancelled";
  deadline: string | null;
  estimated_minutes: number | null;
  actual_minutes: number;
  created_at: string;
  updated_at: string | null;
  completed_at: string | null;
}

export interface TaskCreate {
  title: string;
  description?: string;
  category: string;
  priority?: string;
  deadline?: string;
  estimated_minutes?: number;
}

export interface TaskUpdate {
  title?: string;
  description?: string;
  category?: string;
  priority?: string;
  status?: string;
  deadline?: string;
  estimated_minutes?: number;
}

export interface StudySession {
  id: string;
  user_id: string;
  task_id: string | null;
  planned_start: string | null;
  planned_end: string | null;
  actual_start: string | null;
  actual_end: string | null;
  planned_duration_min: number | null;
  actual_duration_min: number | null;
  session_type: string;
  focus_rating: number | null;
  notes: string | null;
  was_completed: boolean;
  created_at: string;
  task_title: string | null;
}

export interface Alert {
  id: string;
  user_id: string;
  alert_type: string;
  severity: string;
  title: string;
  message: string;
  is_read: boolean;
  is_dismissed: boolean;
  related_task_id: string | null;
  created_at: string;
}

export interface AnalyticsSummary {
  total_tasks: number;
  completed_tasks: number;
  pending_tasks: number;
  overdue_tasks: number;
  total_focus_hours: number;
  avg_session_duration: number;
  completion_rate: number;
  current_streak: number;
}

export interface HeatmapEntry {
  date: string;
  value: number;
}

export interface BurnoutAssessment {
  id: string;
  risk_score: number;
  risk_level: string;
  factors_json: string | null;
  recommendation: string | null;
  assessed_at: string;
}
