const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export class ApiError extends Error {
  status: number;
  data: any;

  constructor(status: number, data: any) {
    super(data?.detail || "API Error");
    this.status = status;
    this.data = data;
  }
}

export async function apiFetch<T>(
  path: string,
  options?: RequestInit
): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
    ...options,
  });

  if (res.status === 401) {
    // Try refresh
    const refreshRes = await fetch(`${API_BASE}/api/auth/refresh`, {
      method: "POST",
      credentials: "include",
    });

    if (refreshRes.ok) {
      // Retry original request
      const retryRes = await fetch(`${API_BASE}${path}`, {
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
          ...options?.headers,
        },
        ...options,
      });
      if (!retryRes.ok) {
        if (retryRes.status === 401) {
          window.location.href = "/login";
          throw new ApiError(401, { detail: "Session expired" });
        }
        throw new ApiError(retryRes.status, await retryRes.json());
      }
      if (retryRes.status === 204) return undefined as T;
      return retryRes.json();
    }

    window.location.href = "/login";
    throw new ApiError(401, { detail: "Session expired" });
  }

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({ detail: "Unknown error" }));
    throw new ApiError(res.status, errorData);
  }

  if (res.status === 204) return undefined as T;
  return res.json();
}
