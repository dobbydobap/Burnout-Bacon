"use client";

import {
  createContext,
  useContext,
  useState,
  useRef,
  useCallback,
  useEffect,
  ReactNode,
} from "react";

interface TimerState {
  isRunning: boolean;
  elapsedSeconds: number;
  activeSessionId: string | null;
  activeTaskId: string | null;
  activeTaskTitle: string | null;
}

interface TimerContextType extends TimerState {
  startTimer: (sessionId: string, taskId?: string, taskTitle?: string) => void;
  stopTimer: () => void;
  resetTimer: () => void;
}

const TimerContext = createContext<TimerContextType | null>(null);

export function TimerProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<TimerState>({
    isRunning: false,
    elapsedSeconds: 0,
    activeSessionId: null,
    activeTaskId: null,
    activeTaskTitle: null,
  });
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (state.isRunning) {
      intervalRef.current = setInterval(() => {
        setState((prev) => ({ ...prev, elapsedSeconds: prev.elapsedSeconds + 1 }));
      }, 1000);
    } else if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [state.isRunning]);

  const startTimer = useCallback(
    (sessionId: string, taskId?: string, taskTitle?: string) => {
      setState({
        isRunning: true,
        elapsedSeconds: 0,
        activeSessionId: sessionId,
        activeTaskId: taskId ?? null,
        activeTaskTitle: taskTitle ?? null,
      });
    },
    []
  );

  const stopTimer = useCallback(() => {
    setState((prev) => ({ ...prev, isRunning: false }));
  }, []);

  const resetTimer = useCallback(() => {
    setState({
      isRunning: false,
      elapsedSeconds: 0,
      activeSessionId: null,
      activeTaskId: null,
      activeTaskTitle: null,
    });
  }, []);

  return (
    <TimerContext.Provider value={{ ...state, startTimer, stopTimer, resetTimer }}>
      {children}
    </TimerContext.Provider>
  );
}

export function useTimer() {
  const ctx = useContext(TimerContext);
  if (!ctx) throw new Error("useTimer must be used within TimerProvider");
  return ctx;
}
