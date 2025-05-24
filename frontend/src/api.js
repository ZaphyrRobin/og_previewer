const API_BASE = "http://localhost:8000/api";

export async function submitURL(url) {
    const res = await fetch(`${API_BASE}/submit`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url }),
    });
    return res.json();
}

export async function getHistory(cursor = null, limit = 10) {
    const params = new URLSearchParams({ limit });
    if (cursor) {
        params.append("cursor", cursor);
    }
    const res = await fetch(`${API_BASE}/history?${params.toString()}`);
    return res.json();
}
