import React, { useState } from "react";
import { chat } from "./api.js";

export default function Chat({ suggestions }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);

  async function ask(q) {
    const question = (q ?? input).trim();
    if (!question || busy) return;
    setInput("");
    setMessages((m) => [...m, { role: "user", text: question }]);
    setBusy(true);
    try {
      const res = await chat(question);
      setMessages((m) => [...m, { role: "assistant", text: res.answer, used: res.used }]);
    } catch (e) {
      setMessages((m) => [...m, { role: "assistant", text: "Sorry — " + e.message }]);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="chat">
      <div className="chat-log">
        {messages.length === 0 && (
          <div className="chat-empty">
            <p>Ask your data anything.</p>
            {suggestions?.length > 0 && (
              <div className="chips">
                {suggestions.slice(0, 4).map((s, i) => (
                  <button key={i} className="chip" onClick={() => ask(s)}>{s}</button>
                ))}
              </div>
            )}
          </div>
        )}
        {messages.map((m, i) => (
          <div key={i} className={`bubble ${m.role}`}>
            <div>{m.text}</div>
            {m.used && (m.used.entities?.length > 0 || m.used.sources?.length > 0) && (
              <div className="cite">
                {m.used.entities?.length > 0 && <span>entities: {m.used.entities.slice(0, 5).join(", ")}</span>}
                {m.used.sources?.length > 0 && <span> · sources: {m.used.sources.join(", ")}</span>}
              </div>
            )}
          </div>
        ))}
        {busy && <div className="bubble assistant">…</div>}
      </div>
      <div className="chat-input">
        <input
          value={input}
          placeholder="Ask a question…"
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && ask()}
        />
        <button onClick={() => ask()} disabled={busy}>Ask</button>
      </div>
    </div>
  );
}
