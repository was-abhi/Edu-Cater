
import { useState } from "react";

function App() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function testBackend() {
    setLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/api/v1/test"
      );

      if (!response.ok) {
        throw new Error(`HTTP error: ${response.status}`);
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message || "Failed to connect to backend");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main style={{ padding: "2rem", fontFamily: "sans-serif" }}>
      <h1>Edu-Cater</h1>
      <p>Frontend-to-backend connection test</p>

      <button onClick={testBackend} disabled={loading}>
        {loading ? "Testing..." : "Test Backend"}
      </button>

      {result && (
        <pre>{JSON.stringify(result, null, 2)}</pre>
      )}

      {error && <p style={{ color: "red" }}>{error}</p>}
    </main>
  );
}

export default App;
