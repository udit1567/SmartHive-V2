const BASE_URL = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:5000";

export class ApiError extends Error {
  constructor(status, payload) {
    const message =
      payload?.message || payload?.error || `Request failed (${status})`;
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.payload = payload;
  }
}

async function parseBody(response) {
  const contentType = response.headers.get("content-type") || "";
  if (contentType.includes("application/json")) {
    return response.json();
  }
  return response.text();
}

export async function request(path, options = {}) {
  const { method = "GET", token, deviceToken, json, form } = options;
  const headers = {};

  if (json) {
    headers["Content-Type"] = "application/json";
  }
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }
  if (deviceToken) {
    headers.Authorization = deviceToken;
  }

  const response = await fetch(`${BASE_URL}${path}`, {
    method,
    headers,
    body: form ?? (json ? JSON.stringify(json) : undefined),
  });

  const payload = await parseBody(response);
  if (!response.ok) {
    throw new ApiError(response.status, payload);
  }
  return payload;
}

export { BASE_URL };
