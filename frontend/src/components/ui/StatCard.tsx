import styles from "./StatCard.module.css";

interface StatCardProps {
  icon: React.ReactNode;
  iconBg: string;
  iconColor: string;
  label: string;
  value: string | number;
  trend?: string;
  trendUp?: boolean;
}

export default function StatCard({
  icon,
  iconBg,
  iconColor,
  label,
  value,
  trend,
  trendUp,
}: StatCardProps) {
  return (
    <div className={styles.statCard}>
      <div
        className={styles.iconWrapper}
        style={{ background: iconBg, color: iconColor }}
      >
        {icon}
      </div>
      <div className={styles.content}>
        <div className={styles.label}>{label}</div>
        <div className={styles.value}>{value}</div>
        {trend && (
          <div
            className={`${styles.trend} ${
              trendUp ? styles.trendUp : styles.trendDown
            }`}
          >
            {trend}
          </div>
        )}
      </div>
    </div>
  );
}
