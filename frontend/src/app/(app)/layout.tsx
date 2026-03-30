"use client";

import { AuthProvider } from "@/context/AuthContext";
import { TimerProvider } from "@/context/TimerContext";
import AppShell from "@/components/layout/AppShell";

export default function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <AuthProvider>
      <TimerProvider>
        <AppShell>{children}</AppShell>
      </TimerProvider>
    </AuthProvider>
  );
}
