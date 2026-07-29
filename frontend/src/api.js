// Backend runs on port 8180 of the same host the UI is served from.
const HOST = window.location.hostname;
export const API = `http://${HOST}:8180`;
export const WS = `ws://${HOST}:8180`;

export async function uploadFiles(files) {
  const form = new FormData();
  for (const f of files) form.append("files", f);
  const res = await fetch(`${API}/api/upload`, { method: "POST", body: form });
  if (!res.ok) throw new Error("Upload failed");
  return res.json();
}

export async function loadSample() {
  const res = await fetch(`${API}/api/sample`, { method: "POST" });
  if (!res.ok) throw new Error("Sample load failed");
  return res.json();
}

export async function pasteText(text, sessionId) {
  const res = await fetch(`${API}/api/paste`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text, session_id: sessionId }),
  });
  if (!res.ok) throw new Error("Paste failed");
  return res.json();
}

// Runs a build, calling onEvent for each progress message. Resolves when done.
export function runBuild(sessionId, answers, onEvent) {
  return new Promise((resolve, reject) => {
    const ws = new WebSocket(`${WS}/api/build/${sessionId}`);
    ws.onopen = () => ws.send(JSON.stringify(answers));
    ws.onmessage = (e) => {
      const event = JSON.parse(e.data);
      onEvent(event);
      if (event.stage === "complete") resolve(event.data.result);
      if (event.stage === "error") reject(new Error(event.message));
    };
    ws.onerror = () => reject(new Error("Connection error"));
    ws.onclose = () => resolve(null);
  });
}

export async function getConfig() {
  const res = await fetch(`${API}/api/config`);
  if (!res.ok) throw new Error("Failed to load config");
  return res.json();
}

export async function saveConfig(patch) {
  const res = await fetch(`${API}/api/config`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(patch),
  });
  if (!res.ok) throw new Error("Failed to save config");
  return res.json();
}

export async function testConfig() {
  const res = await fetch(`${API}/api/config/test`, { method: "POST" });
  return res.json();
}

export async function chat(question) {
  const res = await fetch(`${API}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });
  if (!res.ok) throw new Error("Chat failed");
  return res.json();
}
