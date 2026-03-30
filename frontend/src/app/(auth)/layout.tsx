"use client";

import { AuthProvider } from "@/context/AuthContext";
import styles from "./auth.module.css";

export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <AuthProvider>
      <div className={styles.wrapper}>
        <div className={styles.container}>{children}</div>
      </div>
    </AuthProvider>
  );
}
