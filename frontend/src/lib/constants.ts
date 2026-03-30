export const PRIORITIES = ["low", "medium", "high", "critical"] as const;
export const STATUSES = ["todo", "in_progress", "done", "cancelled"] as const;
export const SESSION_TYPES = ["deep_work", "light_review", "break"] as const;

export const PRIORITY_COLORS: Record<string, string> = {
  low: "var(--color-accent-blue)",
  medium: "var(--color-accent-gold)",
  high: "var(--color-accent-orange)",
  critical: "var(--color-accent-red)",
};

export const STATUS_COLORS: Record<string, string> = {
  todo: "var(--color-text-muted)",
  in_progress: "var(--color-accent-blue)",
  done: "var(--color-accent-green)",
  cancelled: "var(--color-text-muted)",
};

export const CATEGORIES = [
  "Math",
  "Physics",
  "Chemistry",
  "Biology",
  "Computer Science",
  "English",
  "History",
  "Work",
  "Personal",
  "Other",
] as const;

export const NAV_ITEMS = [
  { label: "Dashboard", href: "/dashboard", icon: "LayoutDashboard" },
  { label: "Tasks", href: "/tasks", icon: "CheckSquare" },
  { label: "Planner", href: "/planner", icon: "Calendar" },
  { label: "Focus", href: "/focus", icon: "Timer" },
  { label: "Analytics", href: "/analytics", icon: "BarChart3" },
  { label: "Alerts", href: "/alerts", icon: "Bell" },
  { label: "Reports", href: "/reports", icon: "FileText" },
] as const;
