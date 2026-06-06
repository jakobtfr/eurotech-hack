// Thin fetch helper for the (future) Python backend at apps/api.
// No calls are wired up yet — this only centralizes the base URL + error handling.

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export async function apiFetch<T>(
  path: string,
  init?: RequestInit,
): Promise<T> {
  const url = path.startsWith("http")
    ? path
    : `${API_BASE_URL}${path.startsWith("/") ? path : `/${path}`}`;

  const res = await fetch(url, {
    headers: { "Content-Type": "application/json", ...init?.headers },
    ...init,
  });

  if (!res.ok) {
    throw new Error(`API ${res.status} ${res.statusText} for ${url}`);
  }

  return res.json() as Promise<T>;
}
