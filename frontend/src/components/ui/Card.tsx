import styles from "./Card.module.css";

interface CardProps {
  dark?: boolean;
  noPadding?: boolean;
  className?: string;
  children: React.ReactNode;
  style?: React.CSSProperties;
}

export default function Card({
  dark = false,
  noPadding = false,
  className,
  children,
  style,
}: CardProps) {
  return (
    <div
      className={`${styles.card} ${dark ? styles.cardDark : ""} ${
        noPadding ? styles.noPadding : ""
      } ${className || ""}`}
      style={style}
    >
      {children}
    </div>
  );
}
