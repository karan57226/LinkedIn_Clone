const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

async function request(path) {
  const response = await fetch(`${API_BASE_URL}${path}`);

  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }

  return response.json();
}

export function getFeed() {
  return request("/api/feed");
}

export function getProfiles() {
  return request("/api/profiles");
}

export function getJobs() {
  return request("/api/jobs");
}
