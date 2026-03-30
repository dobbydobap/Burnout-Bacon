"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  CheckSquare,
  Calendar,
  Timer,
  BarChart3,
  Bell,
  FileText,
  Flame,
  LogOut,
} from "lucide-react";
import { useAuth } from "@/context/AuthContext";
import styles from "./Sidebar.module.css";

const iconMap: Record<string, React.ElementType> = {
  LayoutDashboard,
  CheckSquare,
  Calendar,
  Timer,
  BarChart3,
  Bell,
  FileText,
};

const NAV_ITEMS = [
  { label: "Dashboard", href: "/dashboard", icon: "LayoutDashboard" },
  { label: "Tasks", href: "/tasks", icon: "CheckSquare" },
  { label: "Planner", href: "/planner", icon: "Calendar" },
  { label: "Focus", href: "/focus", icon: "Timer" },
  { label: "Analytics", href: "/analytics", icon: "BarChart3" },
  { label: "Alerts", href: "/alerts", icon: "Bell" },
  { label: "Reports", href: "/reports", icon: "FileText" },
];

export default function Sidebar() {
  const pathname = usePathname();
  const { user, logout } = useAuth();

  return (
    <aside className={styles.sidebar}>
      <div className={styles.logo}>
        <div className={styles.logoIcon}>
          <Flame size={20} />
        </div>
        <span className={styles.logoText}>Burnout Beacon</span>
      </div>

      <nav className={styles.nav}>
        {NAV_ITEMS.map((item) => {
          const Icon = iconMap[item.icon];
          const isActive = pathname === item.href || pathname.startsWith(item.href + "/");
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`${styles.navItem} ${isActive ? styles.navItemActive : ""}`}
            >
              <Icon size={18} />
              {item.label}
            </Link>
          );
        })}
      </nav>

      {user && (
        <div className={styles.userSection}>
          <div className={styles.avatar}>
            {user.name.charAt(0).toUpperCase()}
          </div>
          <div style={{ flex: 1, minWidth: 0 }}>
            <div className={styles.userName}>{user.name}</div>
            <div className={styles.userEmail}>{user.email}</div>
          </div>
          <button className={styles.logoutBtn} onClick={logout} title="Logout">
            <LogOut size={16} />
          </button>
        </div>
      )}
    </aside>
  );
}
