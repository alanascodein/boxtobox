"use client";

import { useRef, useState } from "react";
import { api } from "@/lib/api";

type Msg = { role: "user" | "ai"; text: string; provider?: string };

const SUGGESTIONS = [
  "Who is buying chilli near me?",
  "What price should I ask for tomato?",
  "How much did I earn this month?",
  "What's the demand outlook for beans?",
  "What do I have left to sell?",
];

export default function CopilotDrawer() {
  const [open, setOpen] = useState(false);
  const [msgs, setMsgs] = useState<Msg[]>([
    { role: "ai", text: "Hi! I'm your FarmMesh copilot 🌱 Ask me about buyers, prices, demand outlook, your listings or earnings — I always answer from live marketplace data, never guesswork." },
  ]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const endRef = useRef<HTMLDivElement>(null);

  async function ask(q: string) {
    const question = q.trim();
    if (!question || busy) return;
    setMsgs((m) => [...m, { role: "user", text: question }]);
    setInput("");
    setBusy(true);
    try {
      const res = await api<{ reply: string; provider: string }>("/api/vendor/copilot", {
        method: "POST",
        body: JSON.stringify({ question }),
      });
      setMsgs((m) => [...m, { role: "ai", text: res.reply, provider: res.provider }]);
    } catch (err) {
      setMsgs((m) => [...m, { role: "ai", text: err instanceof Error ? err.message : "Something went wrong." }]);
    } finally {
      setBusy(false);
      setTimeout(() => endRef.current?.scrollIntoView({ behavior: "smooth" }), 50);
    }
  }

  return (
    <>
      {/* Launcher */}
      <button
        onClick={() => setOpen(!open)}
        className="fixed bottom-6 right-6 z-50 grid h-14 w-14 place-items-center rounded-full bg-stone-900 text-2xl text-white shadow-lift transition hover:scale-105"
        aria-label="AI Copilot"
      >
        {open ? "✕" : "🤖"}
      </button>

      {open && (
        <div className="fixed bottom-24 right-6 z-50 flex h-[520px] w-[380px] max-w-[calc(100vw-3rem)] flex-col overflow-hidden rounded-3xl border border-stone-200 bg-white shadow-lift">
          <div className="bg-stone-900 px-5 py-4 text-white">
            <div className="font-display font-bold">FarmMesh Copilot</div>
            <div className="text-xs text-stone-300">Grounded in your live marketplace data</div>
          </div>

          <div className="flex-1 space-y-3 overflow-y-auto p-4">
            {msgs.map((m, i) => (
              <div key={i} className={`max-w-[85%] whitespace-pre-line rounded-2xl px-4 py-2.5 text-sm leading-relaxed ${
                m.role === "user" ? "ml-auto bg-brand-600 text-white" : "bg-stone-100 text-stone-800"
              }`}>
                {m.text}
                {m.provider && m.provider !== "engine" && (
                  <div className="mt-1 text-[10px] text-stone-400">via {m.provider}</div>
                )}
              </div>
            ))}
            {busy && <div className="w-20 rounded-2xl bg-stone-100 px-4 py-3"><span className="animate-pulse-soft">Thinking…</span></div>}
            <div ref={endRef} />
          </div>

          <div className="border-t border-stone-100 p-3">
            <div className="mb-2 flex flex-wrap gap-1.5">
              {SUGGESTIONS.slice(0, 3).map((s) => (
                <button key={s} onClick={() => ask(s)} className="rounded-full bg-stone-100 px-2.5 py-1 text-[11px] text-stone-600 transition hover:bg-brand-50 hover:text-brand-700">
                  {s}
                </button>
              ))}
            </div>
            <form onSubmit={(e) => { e.preventDefault(); ask(input); }} className="flex gap-2">
              <input className="input !py-2 text-sm" placeholder="Ask anything…" value={input} onChange={(e) => setInput(e.target.value)} disabled={busy} />
              <button type="submit" className="btn-primary !px-3.5 !py-2" disabled={busy || !input.trim()}>↑</button>
            </form>
          </div>
        </div>
      )}
    </>
  );
}
