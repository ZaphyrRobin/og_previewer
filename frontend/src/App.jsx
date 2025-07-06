// src/App.jsx
import { useEffect, useState } from "react";
import { submitURL, getHistory } from "./api";
import "./App.css";

function App() {
  const [url, setUrl] = useState("");
  const [history, setHistory] = useState([]);
  const [nextCursor, setNextCursor] = useState(null);
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async (cursor = null) => {
    setLoading(true);
    const data = await getHistory(cursor);

    // Maker sure no duplicates
    setHistory((prev) => {
      const existingIds = new Set(prev.map(item => item.id));
      const filteredNew = data.results.filter(item => !existingIds.has(item.id));
      return [...prev, ...filteredNew];
    });

    // Update the next cusor
    setNextCursor(data.next_cursor);
    setLoading(false);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!url.trim()) {
      return;
    }

    setSubmitting(true);

    try {
      const entry = await submitURL(url.trim());
      // Remove any existing entry with the same id as the new one
      setHistory((prev) => {
        const filtered = prev.filter(item => item.id !== entry.id);
        return [entry, ...filtered];
      });
    } catch (err) {
      console.error("Submission error:", err);
      alert("Failed to submit URL.");
    }
    setSubmitting(false);
    setUrl("");
  };

  return (
    <div className="container">
      <h1 className="title">OG Previewer</h1>
      <form onSubmit={handleSubmit} className="form">
        <input
          type="url"
          className="input"
          placeholder="Enter URL"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          required
        />
        <button className="button" type="submit" disabled={submitting}>
          {submitting ? "Submitting..." : "Submit"}
        </button>
      </form>

      <h2 className="subtitle">History</h2>
      <div className="history">
        {history.map((entry) => (
          <div key={entry.id} className="entry">
            <p>
              <strong>URL:</strong>{" "}
              <a href={entry.url} target="_blank" rel="noopener noreferrer" className="url-link">
                {entry.url}
              </a>
            </p>
            {entry.image_url && (
              <img src={entry.image_url} alt="Preview" className="preview-image" />
            )}
          </div>
        ))}
      </div>

      {nextCursor && (
        <div className="load-more-container">
          <button className="load-more-button" onClick={() => fetchHistory(nextCursor)} disabled={loading}>
            {loading ? "Loading..." : "Load More"}
          </button>
        </div>
      )}
    </div>
  );
}

export default App;
