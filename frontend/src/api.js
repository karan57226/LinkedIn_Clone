const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "";

async function request(path) {
  const response = await fetch(`${API_BASE_URL}${path}`);

  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }

  return response.json();
}

async function post(path, body) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(body)
  });

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

export function createProfile(profile) {
  return post("/api/profiles", profile);
}

export function createPost(postBody) {
  return post("/api/posts", postBody);
}

export function createJob(job) {
  return post("/api/jobs", job);
}
