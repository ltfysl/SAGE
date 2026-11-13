import { li, type LibGroup } from "./types";

export const miscGroups: LibGroup[] = [
  {
    id: "chat",
    title: "Chat & messages",
    items: [
      li(
        "Message · incoming",
        `<div className="max-w-[75%] px-3.5 py-2.5 rounded-2xl rounded-bl-sm bg-ink/10 text-sm text-ink/80">Why did MailJob time out?</div>`,
        <div className="max-w-[75%] px-3.5 py-2.5 rounded-2xl rounded-bl-sm bg-ink/10 text-sm text-ink/80">Why did MailJob time out?</div>
      ),
      li(
        "Message · outgoing",
        `<div className="ml-auto max-w-[75%] px-3.5 py-2.5 rounded-2xl rounded-br-sm bg-cyan-500/15 border border-cyan-500/25 text-sm text-ink/80">QUEUE_DRIVER was set to sync.</div>`,
        <div className="ml-auto max-w-[75%] px-3.5 py-2.5 rounded-2xl rounded-br-sm bg-cyan-500/15 border border-cyan-500/25 text-sm text-ink/80">QUEUE_DRIVER was set to sync.</div>
      ),
      li(
        "Message · typing",
        `<div className="inline-flex gap-1 px-3.5 py-3 rounded-2xl rounded-bl-sm bg-ink/10">{[0,1,2].map(i => <span key={i} className="w-1.5 h-1.5 rounded-full bg-ink/40 pulse-dot" />)}</div>`,
        <div className="inline-flex gap-1 px-3.5 py-3 rounded-2xl rounded-bl-sm bg-ink/10">{[0, 1, 2].map((i) => <span key={i} className="w-1.5 h-1.5 rounded-full bg-ink/40 pulse-dot" />)}</div>
      ),
      li(
        "Composer",
        `<div className="flex items-center gap-2 px-3.5 py-2.5 rounded-2xl glass-card">
  <input placeholder="Ask about this incident…" className="flex-1 bg-transparent text-sm text-ink outline-none placeholder:text-ink/30" />
  <button className="text-cyan-400 text-xs font-medium">Send</button>
</div>`,
        <div className="flex items-center gap-2 px-3.5 py-2.5 rounded-2xl glass-card w-full">
          <input placeholder="Ask about this incident…" className="flex-1 bg-transparent text-sm text-ink outline-none placeholder:text-ink/30" />
          <button className="text-cyan-400 text-xs font-medium">Send</button>
        </div>
      ),
    ],
  },
  {
    id: "chrome",
    title: "Page chrome",
    items: [
      li(
        "Section header",
        `<div className="mb-6">
  <p className="text-xs font-mono text-cyan-400/70 tracking-widest uppercase mb-2">02 — Color</p>
  <h2 className="text-2xl font-bold tracking-tight text-ink">Color tokens</h2>
  <p className="text-sm text-ink/40 mt-1">Every swatch copies on click.</p>
</div>`,
        <div className="w-full">
          <p className="text-xs font-mono text-cyan-400/70 tracking-widest uppercase mb-2">02 — Color</p>
          <h2 className="text-2xl font-bold tracking-tight text-ink">Color tokens</h2>
          <p className="text-sm text-ink/40 mt-1">Every swatch copies on click.</p>
        </div>
      ),
      li(
        "Footer bar",
        `<div className="flex items-center justify-between px-4 py-3 rounded-xl border-t border-ink/10 text-[11px] text-ink/40">
  <span className="gradient-text font-bold">Prism</span>
  <span className="font-mono">© 2026 SAGE</span>
</div>`,
        <div className="flex items-center justify-between px-4 py-3 rounded-xl border border-ink/10 text-[11px] text-ink/40 w-full">
          <span className="gradient-text font-bold">Prism</span>
          <span className="font-mono">© 2026 SAGE</span>
        </div>
      ),
      li(
        "Carousel dots",
        `<div className="flex gap-1.5">
  <span className="w-6 h-1.5 rounded-full bg-cyan-400" />
  <span className="w-1.5 h-1.5 rounded-full bg-ink/15" />
  <span className="w-1.5 h-1.5 rounded-full bg-ink/15" />
</div>`,
        <div className="flex gap-1.5">
          <span className="w-6 h-1.5 rounded-full bg-cyan-400" />
          <span className="w-1.5 h-1.5 rounded-full bg-ink/15" />
          <span className="w-1.5 h-1.5 rounded-full bg-ink/15" />
        </div>
      ),
      li(
        "Timestamp",
        `<span className="text-[11px] text-ink/30 font-mono">updated 2m ago</span>`,
        <span className="text-[11px] text-ink/30 font-mono">updated 2m ago</span>
      ),
      li(
        "Version pill",
        `<span className="px-2 py-0.5 rounded-full border border-ink/15 font-mono text-[10px] text-ink/50">v2.4.1</span>`,
        <span className="px-2 py-0.5 rounded-full border border-ink/15 font-mono text-[10px] text-ink/50">v2.4.1</span>
      ),
      li(
        "Keyboard hint bar",
        `<div className="flex items-center gap-3 text-[11px] text-ink/40">
  <span className="flex items-center gap-1"><kbd className="px-1.5 py-0.5 rounded bg-ink/10 border border-ink/15 font-mono text-[10px]">↑↓</kbd> navigate</span>
  <span className="flex items-center gap-1"><kbd className="px-1.5 py-0.5 rounded bg-ink/10 border border-ink/15 font-mono text-[10px]">⏎</kbd> select</span>
  <span className="flex items-center gap-1"><kbd className="px-1.5 py-0.5 rounded bg-ink/10 border border-ink/15 font-mono text-[10px]">esc</kbd> close</span>
</div>`,
        <div className="flex items-center gap-3 text-[11px] text-ink/40">
          <span className="flex items-center gap-1"><kbd className="px-1.5 py-0.5 rounded bg-ink/10 border border-ink/15 font-mono text-[10px]">↑↓</kbd> navigate</span>
          <span className="flex items-center gap-1"><kbd className="px-1.5 py-0.5 rounded bg-ink/10 border border-ink/15 font-mono text-[10px]">⏎</kbd> select</span>
          <span className="flex items-center gap-1"><kbd className="px-1.5 py-0.5 rounded bg-ink/10 border border-ink/15 font-mono text-[10px]">esc</kbd> close</span>
        </div>
      ),
      li(
        "Status line",
        `<div className="flex items-center gap-2 text-[11px] font-mono text-ink/40">
  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" /> all systems nominal · 99.98% uptime
</div>`,
        <div className="flex items-center gap-2 text-[11px] font-mono text-ink/40">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" /> all systems nominal · 99.98% uptime
        </div>
      ),
      li(
        "Gauge tile",
        `<div className="glass-card p-4 text-center">
  <p className="font-mono text-2xl font-bold text-emerald-400">0.94</p>
  <p className="text-[10px] uppercase tracking-wider text-ink/40 mt-1">mean confidence</p>
</div>`,
        <div className="glass-card p-4 text-center w-full">
          <p className="font-mono text-2xl font-bold text-emerald-400">0.94</p>
          <p className="text-[10px] uppercase tracking-wider text-ink/40 mt-1">mean confidence</p>
        </div>
      ),
    ],
  },
];
