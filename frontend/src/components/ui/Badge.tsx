import styles from "./Badge.module.css";

interface BadgeProps {
  children: React.ReactNode;
  bg: string;
  color: string;
}

export default function Badge({ children, bg, color }: BadgeProps) {
  return (
    <span className={styles.badge} style={{ background: bg, color }}>
      {children}
    </span>
  );
}
