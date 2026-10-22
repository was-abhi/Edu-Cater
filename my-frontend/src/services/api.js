const API_BASE_URL = "http://127.0.0.1:8000/api/v1";

async function postRequest(endpoint, payload) {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(
      typeof data.detail === "string"
        ? data.detail
        : "Unable to retrieve data."
    );
  }

  return data;
}

export function fetchCutoffs(payload) {
  return postRequest("/cutoffs", payload);
}

export function fetchRecommendations(payload) {
  return postRequest("/recommendations", payload);
}