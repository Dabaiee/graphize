import React, { useEffect, useState } from "react";
import { getConfig, saveConfig, testConfig } from "./api.js";

const PROVIDERS = [
  { id: "anthropic", label: "Anthropic (Claude)", note: "Best quality. Needs an Anthropic API key." },
  { id: "openai", label: "OpenAI (GPT)", note: "Needs an OpenAI API key." },
  { id: "ollama", label: "Ollama — local & free", note: "Runs an open model on your machine. Free & offline; lower quality than Claude/GPT." },
];

export default function Settings({ onClose, onSaved }) {
  const [cfg, setCfg] = useState(null);
  const [keys, setKeys] = useState({ anthropic_api_key: "", openai_api_key: "" });
  const [test, setTest] = useState(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => { getConfig().then(setCfg); }, []);
  if (!cfg) return null;

  const set = (k, v) => setCfg({ ...cfg, [k]: v });

  function patch() {
    const p = {
      provider: cfg.provider,
      anthropic_model: cfg.anthropic_model, openai_model: cfg.openai_model,
      openai_base_url: cfg.openai_base_url, ollama_base_url: cfg.ollama_base_url,
      ollama_model: cfg.ollama_model,
    };
    if (keys.anthropic_api_key) p.anthropic_api_key = keys.anthropic_api_key;
    if (keys.openai_api_key) p.openai_api_key = keys.openai_api_key;
    return p;
  }

  async function save(close) {
    setBusy(true);
    const updated = await saveConfig(patch());
    setCfg(updated);
    setKeys({ anthropic_api_key: "", openai_api_key: "" });
    setBusy(false);
    onSaved?.(updated);
    if (close) onClose();
  }

  async function runTest() {
    setBusy(true); setTest(null);
    await saveConfig(patch());              // persist before testing
    setKeys({ anthropic_api_key: "", openai_api_key: "" });
    setTest(await testConfig());
    onSaved?.(await getConfig());
    setBusy(false);
  }

  const p = cfg.provider;
  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-head">
          <h2>Model settings</h2>
          <button className="x" onClick={onClose} aria-label="Close">✕</button>
        </div>

        <label className="fld">Provider
          <select value={p} onChange={(e) => set("provider", e.target.value)}>
            {PROVIDERS.map((x) => <option key={x.id} value={x.id}>{x.label}</option>)}
          </select>
        </label>
        <p className="note">{PROVIDERS.find((x) => x.id === p)?.note}</p>

        {p === "anthropic" && (<>
          <label className="fld">API key
            <input type="password"
              placeholder={cfg.keys_set.anthropic ? "•••••• saved — leave blank to keep" : "sk-ant-..."}
              value={keys.anthropic_api_key}
              onChange={(e) => setKeys({ ...keys, anthropic_api_key: e.target.value })} />
          </label>
          <label className="fld">Model
            <input value={cfg.anthropic_model} onChange={(e) => set("anthropic_model", e.target.value)} />
          </label>
        </>)}

        {p === "openai" && (<>
          <label className="fld">API key
            <input type="password"
              placeholder={cfg.keys_set.openai ? "•••••• saved — leave blank to keep" : "sk-..."}
              value={keys.openai_api_key}
              onChange={(e) => setKeys({ ...keys, openai_api_key: e.target.value })} />
          </label>
          <label className="fld">Model
            <input value={cfg.openai_model} onChange={(e) => set("openai_model", e.target.value)} />
          </label>
          <label className="fld">Base URL <span className="opt">(optional)</span>
            <input placeholder="https://api.openai.com/v1" value={cfg.openai_base_url}
              onChange={(e) => set("openai_base_url", e.target.value)} />
          </label>
        </>)}

        {p === "ollama" && (<>
          <label className="fld">Base URL
            <input value={cfg.ollama_base_url} onChange={(e) => set("ollama_base_url", e.target.value)} />
          </label>
          <label className="fld">Model
            <input placeholder="llama3.1" value={cfg.ollama_model}
              onChange={(e) => set("ollama_model", e.target.value)} />
          </label>
          <p className="note">
            Install <a href="https://ollama.com" target="_blank" rel="noreferrer">Ollama</a>, then
            <code> ollama pull {cfg.ollama_model || "llama3.1"}</code>. If this app runs in Docker,
            use <code>http://host.docker.internal:11434</code> as the base URL.
          </p>
        </>)}

        {test && (
          <div className={`test ${test.ok ? "ok" : "err"}`}>
            {test.ok ? `✓ Connected — ${test.model}` : `✕ ${test.error}`}
          </div>
        )}

        <div className="modal-foot">
          <button className="btn-ghost2" onClick={runTest} disabled={busy}>
            {busy ? "…" : "Test connection"}
          </button>
          <button className="btn-save" onClick={() => save(true)} disabled={busy}>Save</button>
        </div>
      </div>
    </div>
  );
}
