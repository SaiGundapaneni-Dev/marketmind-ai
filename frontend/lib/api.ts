import {
  getToken,
  removeToken,
} from "./auth";

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL ??
  "http://127.0.0.1:8000";

export async function apiFetch(
  endpoint: string,
  options: RequestInit = {}
) {
  const token = getToken();

  const headers = new Headers(
    options.headers
  );

  if (
    options.body &&
    !headers.has("Content-Type")
  ) {
    headers.set(
      "Content-Type",
      "application/json"
    );
  }

  if (token) {
    headers.set(
      "Authorization",
      `Bearer ${token}`
    );
  }

  const response = await fetch(
    `${API_BASE}${endpoint}`,
    {
      ...options,
      headers,
    }
  );

  if (
    response.status === 401 ||
    response.status === 403
  ) {
    removeToken();

    if (typeof window !== "undefined") {
      window.localStorage.removeItem(
        "vestora_user"
      );

      window.location.href = "/login";
    }
  }

  return response;
}