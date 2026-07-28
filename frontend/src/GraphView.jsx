import React, { useEffect, useRef, useState } from "react";

// Tiny dependency-free force-directed layout rendered as SVG.
const PALETTE = [
  "#60a5fa", "#f472b6", "#34d399", "#fbbf24", "#a78bfa",
  "#fb7185", "#22d3ee", "#facc15", "#4ade80", "#c084fc",
];

export default function GraphView({ data }) {
  const svgRef = useRef(null);
  const [tick, setTick] = useState(0);
  const state = useRef({ nodes: [], edges: [], colors: {} });

  useEffect(() => {
    const W = 720, H = 460;
    const types = [...new Set((data.nodes || []).map((n) => n.type))];
    const colors = {};
    types.forEach((t, i) => (colors[t] = PALETTE[i % PALETTE.length]));
    const nodes = (data.nodes || []).map((n, i) => ({
      ...n,
      x: W / 2 + Math.cos(i) * 120 + (Math.random() - 0.5) * 40,
      y: H / 2 + Math.sin(i) * 120 + (Math.random() - 0.5) * 40,
      vx: 0, vy: 0,
    }));
    const byId = Object.fromEntries(nodes.map((n) => [n.id, n]));
    const edges = (data.edges || [])
      .filter((e) => byId[e.source] && byId[e.target])
      .map((e) => ({ ...e, s: byId[e.source], t: byId[e.target] }));
    state.current = { nodes, edges, colors, W, H };

    let frame;
    let iter = 0;
    const step = () => {
      const { nodes, edges, W, H } = state.current;
      // Repulsion
      for (let i = 0; i < nodes.length; i++) {
        for (let j = i + 1; j < nodes.length; j++) {
          const a = nodes[i], b = nodes[j];
          let dx = a.x - b.x, dy = a.y - b.y;
          let d2 = dx * dx + dy * dy || 1;
          const f = 1400 / d2;
          const d = Math.sqrt(d2);
          a.vx += (dx / d) * f; a.vy += (dy / d) * f;
          b.vx -= (dx / d) * f; b.vy -= (dy / d) * f;
        }
      }
      // Springs
      for (const e of edges) {
        let dx = e.t.x - e.s.x, dy = e.t.y - e.s.y;
        const d = Math.sqrt(dx * dx + dy * dy) || 1;
        const f = (d - 90) * 0.02;
        e.s.vx += (dx / d) * f; e.s.vy += (dy / d) * f;
        e.t.vx -= (dx / d) * f; e.t.vy -= (dy / d) * f;
      }
      // Integrate + gravity to center
      for (const n of nodes) {
        n.vx += (W / 2 - n.x) * 0.002;
        n.vy += (H / 2 - n.y) * 0.002;
        n.x += Math.max(-8, Math.min(8, n.vx));
        n.y += Math.max(-8, Math.min(8, n.vy));
        n.vx *= 0.85; n.vy *= 0.85;
        n.x = Math.max(20, Math.min(W - 20, n.x));
        n.y = Math.max(20, Math.min(H - 20, n.y));
      }
      setTick((t) => t + 1);
      if (iter++ < 240) frame = requestAnimationFrame(step);
    };
    frame = requestAnimationFrame(step);
    return () => cancelAnimationFrame(frame);
  }, [data]);

  const { nodes, edges, colors, W = 720, H = 460 } = state.current;
  if (!nodes.length) return <div className="empty">No relationships to display yet.</div>;

  return (
    <div>
      <svg ref={svgRef} viewBox={`0 0 ${W} ${H}`} className="graph-svg">
        {edges.map((e, i) => (
          <line key={i} x1={e.s.x} y1={e.s.y} x2={e.t.x} y2={e.t.y}
            stroke="#334155" strokeWidth="1" />
        ))}
        {nodes.map((n) => (
          <g key={n.id}>
            <circle cx={n.x} cy={n.y} r="7" fill={colors[n.type] || "#94a3b8"} />
            <text x={n.x + 10} y={n.y + 4} fontSize="10" fill="#cbd5e1">
              {(n.label || "").slice(0, 22)}
            </text>
          </g>
        ))}
      </svg>
      <div className="legend">
        {Object.entries(colors).map(([t, c]) => (
          <span key={t} className="legend-item">
            <span className="dot" style={{ background: c }} /> {t}
          </span>
        ))}
      </div>
    </div>
  );
}
