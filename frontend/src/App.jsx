import React, { useRef, useState } from "react";
import { uploadFiles, loadSample, pasteText, runBuild } from "./api.js";
import GraphView from "./GraphView.jsx";
import Chat from "./Chat.jsx";

const STAGE_LABEL = {
  intent: "Understanding intent",
  files: "Selecting files",
  schema: "Designing schema",
  construct: "Building graph",
  resolve: "Resolving entities",
  load: "Storing in Neo4j",
  critic: "Checking quality",
  complete: "Done",
  error: "Error",
};

export default function App() {
  const [sources, setSources] = useState([]);
  const [sessionId, setSessionId] = useState(null);
  const [answers, setAnswers] = useState({ about: "", questions: "", track: "" });
  const [pasted, setPasted] = useState("");
  const [phase, setPhase] = useState("idle"); // idle | building | ready
  const [events, setEvents] = useState([]);
  const [result, setResult] = useState(null);
  const fileRef = useRef(null);

  async function onUpload(e) {
    const files = e.target.files;
    if (!files?.length) return;
    const res = await uploadFiles(files);
    setSessionId(res.session_id);
    setSources(res.sources);
  }

  async function onSample() {
    const res = await loadSample();
    setSessionId(res.session_id);
    setSources(res.sources);
    setAnswers({
      about: "Coffee gear products, their suppliers, and customer reviews",
      questions: "Which products work well together and who supplies them?",
      track: "products, suppliers, how products relate to each other",
    });
  }

  async function onBuild() {
    let sid = sessionId;
    // If the user pasted text, submit it as an (unstructured) source first.
    if (pasted.trim()) {
      const res = await pasteText(pasted, sid);
      sid = res.session_id;
      setSessionId(sid);
      setSources(res.sources);
    }
    if (!sid) return;
    setPhase("building");
    setEvents([]);
    setResult(null);
    try {
      const r = await runBuild(sid, answers, (ev) =>
        setEvents((prev) => [...prev, ev])
      );
      if (r) {
        setResult(r);
        setPhase("ready");
      }
    } catch (err) {
      setEvents((prev) => [...prev, { stage: "error", status: "error", message: err.message }]);
    }
  }

  return (
    <div className="app">
      <header>
        <h1>⚡ Graphize</h1>
        <p>Paste your data, say what matters, click once — get a knowledge graph you can talk to.</p>
      </header>

      {phase !== "ready" && (
        <section className="card builder">
          <div className="step">
            <label>1 · Your data</label>
            <div className="drop" onClick={() => fileRef.current?.click()}>
              <input ref={fileRef} type="file" multiple hidden onChange={onUpload}
                accept=".csv,.json,.pdf,.txt,.md,.docx" />
              <span>Click to add files — CSV · JSON · PDF · TXT · DOCX</span>
            </div>
            <div className="or">or <button className="link" onClick={onSample}>load the sample dataset</button></div>
            <div className="paste">
              <label>Or paste text directly</label>
              <textarea
                rows={5}
                placeholder="Paste any text here — notes, an article, a transcript… and we'll build a graph from it."
                value={pasted}
                onChange={(e) => setPasted(e.target.value)}
              />
            </div>
            {sources.length > 0 && (
              <ul className="sources">
                {sources.map((s) => (
                  <li key={s.name}>
                    <b>{s.name}</b> — {s.kind === "structured"
                      ? `${s.rows} rows, ${s.columns.length} columns`
                      : `${s.chunks} text chunks`}
                  </li>
                ))}
              </ul>
            )}
          </div>

          <div className="step">
            <label>2 · What matters (plain English — optional)</label>
            <input placeholder="What is this data about?"
              value={answers.about}
              onChange={(e) => setAnswers({ ...answers, about: e.target.value })} />
            <input placeholder="What do you want to ask it?"
              value={answers.questions}
              onChange={(e) => setAnswers({ ...answers, questions: e.target.value })} />
            <input placeholder="Anything specific to track? (leave blank to auto-detect)"
              value={answers.track}
              onChange={(e) => setAnswers({ ...answers, track: e.target.value })} />
          </div>

          <button
            className="build"
            disabled={(!sessionId && !pasted.trim()) || phase === "building"}
            onClick={onBuild}
          >
            {phase === "building" ? "Building…" : "⚡ Build my graph"}
          </button>
        </section>
      )}

      {events.length > 0 && (
        <section className="card progress">
          <h2>Progress</h2>
          {events.map((ev, i) => (
            <div key={i} className={`event ${ev.status}`}>
              <span className="stage">{STAGE_LABEL[ev.stage] || ev.stage}</span>
              <span className="msg">{ev.message}</span>
            </div>
          ))}
        </section>
      )}

      {phase === "ready" && result && (
        <>
          <section className="card summary">
            <h2>{result.objective}</h2>
            <div className="stats">
              <div><b>{result.stats.nodes}</b><span>entities</span></div>
              <div><b>{result.stats.relationships}</b><span>relationships</span></div>
              <div><b>{result.stats.chunks}</b><span>text chunks</span></div>
              <div><b>{result.stats.labels.length}</b><span>types</span></div>
            </div>
            <div className="chips">
              {result.stats.labels.map((l) => <span key={l} className="chip static">{l}</span>)}
            </div>
            {result.review?.suggestions?.length > 0 && (
              <details className="review">
                <summary>Quality check: {result.review.verdict}</summary>
                {result.review.issues?.length > 0 && (
                  <><b>Issues</b><ul>{result.review.issues.map((x, i) => <li key={i}>{x}</li>)}</ul></>
                )}
                {result.review.suggestions?.length > 0 && (
                  <><b>Suggestions</b><ul>{result.review.suggestions.map((x, i) => <li key={i}>{x}</li>)}</ul></>
                )}
              </details>
            )}
            <button className="link" onClick={() => { setPhase("idle"); setEvents([]); }}>
              ← build another
            </button>
          </section>

          <div className="two-col">
            <section className="card">
              <h2>Your knowledge graph</h2>
              <GraphView data={result.graph} />
            </section>
            <section className="card">
              <h2>Ask your data</h2>
              <Chat suggestions={result.review?.example_questions} />
            </section>
          </div>
        </>
      )}
    </div>
  );
}
