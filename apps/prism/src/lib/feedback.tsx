import { li, type LibGroup } from "./types";
import {
  Info, CheckCircle2, AlertTriangle, XCircle, X, Loader2,
  Bell, Inbox, WifiOff, FileQuestion, RotateCcw,
} from "lucide-react";

const alerts: [string, string, string, string, typeof Info][] = [
  ["info", "border-cyan-500/30 bg-cyan-500/10 text-cyan-300", "border-l-cyan-400", "Info", Info],
  ["success", "border-emerald-500/30 bg-emerald-500/10 text-emerald-300", "border-l-emerald-400", "CheckCircle2", CheckCircle2],
  ["warning", "border-amber-500/30 bg-amber-500/10 text-amber-300", "border-l-amber-400", "AlertTriangle", AlertTriangle],
  ["error", "border-rose-500/30 bg-rose-500/10 text-rose-300", "border-l-rose-400", "XCircle", XCircle],
];

const progressColors: [string, string][] = [
  ["cyan", "bg-cyan-400"], ["violet", "bg-violet-400"], ["emerald", "bg-emerald-400"],
  ["rose", "bg-rose-400"], ["amber", "bg-amber-400"], ["gradient", "bg-gradient-to-r from-cyan-400 to-violet-400"],
];

export const feedbackGroups: LibGroup[] = [
  {
    id: "alerts",
    title: "Alerts & banners",
    items: [
      ...alerts.map(([n, cls, , iconName, I]) =>
        li(
          `Alert · ${n}`,
          `<div className="flex items-start gap-2.5 p-3 rounded-xl border ${cls}">
  <${iconName} size={15} className="mt-0.5 shrink-0" />
  <p className="text-xs leading-relaxed">Something happened — here's what to know.</p>
</div>`,
          <div className={`flex items-start gap-2.5 p-3 rounded-xl border ${cls}`}>
            <I size={15} className="mt-0.5 shrink-0" />
            <p className="text-xs leading-relaxed">Something happened — here's what to know.</p>
          </div>
        )
      ),
      li(
        "Alert · edge accent",
        `<div className="p-3 rounded-r-xl border-y border-r border-l-2 border-ink/10 ${alerts[3][2]} bg-ink/[0.03]">
  <p className="text-xs text-ink/70">Queue depth exceeded threshold for <b>emails</b>.</p>
</div>`,
        <div className={`p-3 rounded-r-xl border-y border-r border-l-2 border-ink/10 ${alerts[3][2]} bg-ink/[0.03]`}>
          <p className="text-xs text-ink/70">Queue depth exceeded threshold for <b>emails</b>.</p>
        </div>
      ),
      li(
        "Alert · dismissible",
        `<div className="flex items-center gap-2.5 p-3 rounded-xl border border-cyan-500/30 bg-cyan-500/10 text-cyan-300">
  <Info size={15} className="shrink-0" />
  <p className="text-xs flex-1">Analysis complete — 3 criticals found.</p>
  <X size={13} className="cursor-pointer opacity-60 hover:opacity-100" />
</div>`,
        <div className="flex items-center gap-2.5 p-3 rounded-xl border border-cyan-500/30 bg-cyan-500/10 text-cyan-300">
          <Info size={15} className="shrink-0" />
          <p className="text-xs flex-1">Analysis complete — 3 criticals found.</p>
          <X size={13} className="cursor-pointer opacity-60 hover:opacity-100" />
        </div>
      ),
      li(
        "Banner · announcement",
        `<div className="flex items-center justify-center gap-2 px-4 py-2 rounded-xl bg-gradient-to-r from-cyan-500/15 to-violet-500/15 border border-cyan-500/20 text-xs">
  <Bell size={12} className="text-cyan-400" />
  <span className="text-ink/80">Prism v2 is live — <span className="text-cyan-300 underline underline-offset-2 cursor-pointer">see changelog</span></span>
</div>`,
        <div className="flex items-center justify-center gap-2 px-4 py-2 rounded-xl bg-gradient-to-r from-cyan-500/15 to-violet-500/15 border border-cyan-500/20 text-xs">
          <Bell size={12} className="text-cyan-400" />
          <span className="text-ink/80">Prism v2 is live — <span className="text-cyan-300 underline underline-offset-2 cursor-pointer">see changelog</span></span>
        </div>
      ),
      li(
        "Error banner",
        `<div className="p-4 rounded-xl border border-rose-500/30 bg-rose-500/10 flex items-center gap-3">
  <AlertTriangle size={18} className="text-rose-400" />
  <div><p className="text-sm font-medium text-rose-300">Analysis failed</p>
  <p className="text-xs text-rose-300/60 mt-0.5">laravel.log: unexpected end of stream at line 10,482</p></div>
</div>`,
        <div className="p-4 rounded-xl border border-rose-500/30 bg-rose-500/10 flex items-center gap-3">
          <AlertTriangle size={18} className="text-rose-400" />
          <div><p className="text-sm font-medium text-rose-300">Analysis failed</p>
            <p className="text-xs text-rose-300/60 mt-0.5">laravel.log: unexpected end of stream at line 10,482</p></div>
        </div>
      ),
      li(
        "Alert · with action",
        `<div className="flex items-center gap-2.5 p-3 rounded-xl border border-amber-500/30 bg-amber-500/10">
  <AlertTriangle size={15} className="text-amber-300 shrink-0" />
  <p className="text-xs text-amber-200 flex-1">Snapshot is 4 days old.</p>
  <button className="text-[11px] font-medium text-amber-300 border border-amber-500/40 rounded-md px-2 py-1 hover:bg-amber-500/20">Refresh</button>
</div>`,
        <div className="flex items-center gap-2.5 p-3 rounded-xl border border-amber-500/30 bg-amber-500/10">
          <AlertTriangle size={15} className="text-amber-300 shrink-0" />
          <p className="text-xs text-amber-200 flex-1">Snapshot is 4 days old.</p>
          <button className="text-[11px] font-medium text-amber-300 border border-amber-500/40 rounded-md px-2 py-1 hover:bg-amber-500/20">Refresh</button>
        </div>
      ),
    ],
  },
  {
    id: "progress",
    title: "Progress & meters",
    items: [
      ...progressColors.map(([n, cls]) =>
        li(
          `Progress bar · ${n}`,
          `<div className="h-1.5 rounded-full bg-ink/10 overflow-hidden"><div className="h-full w-2/3 rounded-full ${cls}" /></div>`,
          <div className="h-1.5 rounded-full bg-ink/10 overflow-hidden"><div className={`h-full w-2/3 rounded-full ${cls}`} /></div>
        )
      ),
      li(
        "Progress · labelled",
        `<div>
  <div className="flex justify-between text-xs mb-1.5"><span className="text-ink/60">Compiling ops…</span><span className="font-mono text-cyan-400">67%</span></div>
  <div className="h-1.5 rounded-full bg-ink/10 overflow-hidden"><div className="h-full w-2/3 rounded-full bg-cyan-400" /></div>
</div>`,
        <div>
          <div className="flex justify-between text-xs mb-1.5"><span className="text-ink/60">Compiling ops…</span><span className="font-mono text-cyan-400">67%</span></div>
          <div className="h-1.5 rounded-full bg-ink/10 overflow-hidden"><div className="h-full w-2/3 rounded-full bg-cyan-400" /></div>
        </div>
      ),
      li(
        "Progress · segmented",
        `<div className="flex h-1.5 rounded-full overflow-hidden gap-px">
  <div className="w-1/2 bg-emerald-400" /><div className="w-1/4 bg-amber-400" /><div className="w-1/6 bg-rose-400" /><div className="flex-1 bg-ink/10" />
</div>`,
        <div className="flex h-1.5 rounded-full overflow-hidden gap-px">
          <div className="w-1/2 bg-emerald-400" /><div className="w-1/4 bg-amber-400" /><div className="w-1/6 bg-rose-400" /><div className="flex-1 bg-ink/10" />
        </div>
      ),
      li(
        "Progress · striped",
        `<div className="h-2 rounded-full bg-ink/10 overflow-hidden"><div className="h-full w-3/4 rounded-full bg-[repeating-linear-gradient(45deg,#22d3ee_0_8px,rgba(34,211,238,0.4)_8px_16px)]" /></div>`,
        <div className="h-2 rounded-full bg-ink/10 overflow-hidden"><div className="h-full w-3/4 rounded-full bg-[repeating-linear-gradient(45deg,#22d3ee_0_8px,rgba(34,211,238,0.4)_8px_16px)]" /></div>
      ),
      li(
        "Meter · capacity",
        `<div>
  <div className="flex justify-between text-[11px] mb-1"><span className="text-ink/50">Storage</span><span className="text-ink/70">38 / 50 GB</span></div>
  <div className="h-2 rounded-full bg-ink/10 overflow-hidden"><div className="h-full w-3/4 rounded-full bg-gradient-to-r from-cyan-400 to-violet-400" /></div>
</div>`,
        <div>
          <div className="flex justify-between text-[11px] mb-1"><span className="text-ink/50">Storage</span><span className="text-ink/70">38 / 50 GB</span></div>
          <div className="h-2 rounded-full bg-ink/10 overflow-hidden"><div className="h-full w-3/4 rounded-full bg-gradient-to-r from-cyan-400 to-violet-400" /></div>
        </div>
      ),
      li(
        "Ring progress",
        `<svg viewBox="0 0 36 36" className="w-14 h-14 -rotate-90">
  <circle cx="18" cy="18" r="15.5" fill="none" stroke="rgb(var(--ink) / 0.1)" strokeWidth="3" />
  <circle cx="18" cy="18" r="15.5" fill="none" stroke="#22d3ee" strokeWidth="3" strokeDasharray="97.4" strokeDashoffset="32" strokeLinecap="round" />
</svg>`,
        <svg viewBox="0 0 36 36" className="w-14 h-14 -rotate-90">
          <circle cx="18" cy="18" r="15.5" fill="none" stroke="rgb(var(--ink) / 0.1)" strokeWidth="3" />
          <circle cx="18" cy="18" r="15.5" fill="none" stroke="#22d3ee" strokeWidth="3" strokeDasharray="97.4" strokeDashoffset="32" strokeLinecap="round" />
        </svg>
      ),
      li(
        "Steps progress",
        `<div className="flex items-center gap-1.5">
  <div className="h-1 flex-1 rounded-full bg-cyan-400" /><div className="h-1 flex-1 rounded-full bg-cyan-400" />
  <div className="h-1 flex-1 rounded-full bg-cyan-400/40" /><div className="h-1 flex-1 rounded-full bg-ink/10" />
</div>`,
        <div className="flex items-center gap-1.5">
          <div className="h-1 flex-1 rounded-full bg-cyan-400" /><div className="h-1 flex-1 rounded-full bg-cyan-400" />
          <div className="h-1 flex-1 rounded-full bg-cyan-400/40" /><div className="h-1 flex-1 rounded-full bg-ink/10" />
        </div>
      ),
    ],
  },
  {
    id: "loaders",
    title: "Loaders & skeletons",
    items: [
      li("Spinner", `<Loader2 size={20} className="animate-spin text-cyan-400" />`, <Loader2 size={20} className="animate-spin text-cyan-400" />),
      li("Spinner · large", `<Loader2 size={32} className="animate-spin text-violet-400" />`, <Loader2 size={32} className="animate-spin text-violet-400" />),
      li(
        "Spinner · ring",
        `<span className="w-6 h-6 rounded-full border-2 border-ink/15 border-t-cyan-400 animate-spin inline-block" />`,
        <span className="w-6 h-6 rounded-full border-2 border-ink/15 border-t-cyan-400 animate-spin inline-block" />
      ),
      li(
        "Pulse dots",
        `<span className="inline-flex gap-1">{[0,1,2].map(i => <span key={i} className="w-1.5 h-1.5 rounded-full bg-cyan-400 pulse-dot" />)}</span>`,
        <span className="inline-flex gap-1">{[0, 1, 2].map((i) => <span key={i} className="w-1.5 h-1.5 rounded-full bg-cyan-400 pulse-dot" />)}</span>
      ),
      li(
        "Dots · bouncing",
        `<span className="inline-flex gap-1">{[0,1,2].map(i => <span key={i} className="w-1.5 h-1.5 rounded-full bg-violet-400 animate-bounce" style={{ animationDelay: \`\${i * 0.15}s\` }} />)}</span>`,
        <span className="inline-flex gap-1">{[0, 1, 2].map((i) => <span key={i} className="w-1.5 h-1.5 rounded-full bg-violet-400 animate-bounce" style={{ animationDelay: `${i * 0.15}s` }} />)}</span>
      ),
      li(
        "Bars loader",
        `<span className="inline-flex items-end gap-0.5 h-4">{[0,1,2,3].map(i => <span key={i} className="w-1 bg-cyan-400 animate-pulse" style={{ height: \`\${[40,100,70,90][i]}%\`, animationDelay: \`\${i * 0.12}s\` }} />)}</span>`,
        <span className="inline-flex items-end gap-0.5 h-4">{[0, 1, 2, 3].map((i) => <span key={i} className="w-1 bg-cyan-400 animate-pulse" style={{ height: `${[40, 100, 70, 90][i]}%`, animationDelay: `${i * 0.12}s` }} />)}</span>
      ),
      li("Skeleton · line", `<div className="h-3 rounded bg-ink/10 relative overflow-hidden"><div className="absolute inset-0 animate-shimmer" /></div>`, <div className="h-3 rounded bg-ink/10 relative overflow-hidden"><div className="absolute inset-0 animate-shimmer" /></div>),
      li("Skeleton · avatar+lines",
        `<div className="flex gap-3 items-center">
  <div className="w-10 h-10 rounded-full bg-ink/10 relative overflow-hidden"><div className="absolute inset-0 animate-shimmer" /></div>
  <div className="flex-1 space-y-2">
    <div className="h-2.5 w-2/3 rounded bg-ink/10 relative overflow-hidden"><div className="absolute inset-0 animate-shimmer" /></div>
    <div className="h-2.5 w-1/2 rounded bg-ink/10 relative overflow-hidden"><div className="absolute inset-0 animate-shimmer" /></div>
  </div>
</div>`,
        <div className="flex gap-3 items-center">
          <div className="w-10 h-10 rounded-full bg-ink/10 relative overflow-hidden"><div className="absolute inset-0 animate-shimmer" /></div>
          <div className="flex-1 space-y-2">
            <div className="h-2.5 w-2/3 rounded bg-ink/10 relative overflow-hidden"><div className="absolute inset-0 animate-shimmer" /></div>
            <div className="h-2.5 w-1/2 rounded bg-ink/10 relative overflow-hidden"><div className="absolute inset-0 animate-shimmer" /></div>
          </div>
        </div>
      ),
      li("Skeleton · card",
        `<div className="glass-card p-4 space-y-3">
  <div className="h-24 rounded-lg bg-ink/5 relative overflow-hidden"><div className="absolute inset-0 animate-shimmer" /></div>
  <div className="h-3 w-3/4 rounded bg-ink/10 relative overflow-hidden"><div className="absolute inset-0 animate-shimmer" /></div>
</div>`,
        <div className="glass-card p-4 space-y-3">
          <div className="h-24 rounded-lg bg-ink/5 relative overflow-hidden"><div className="absolute inset-0 animate-shimmer" /></div>
          <div className="h-3 w-3/4 rounded bg-ink/10 relative overflow-hidden"><div className="absolute inset-0 animate-shimmer" /></div>
        </div>
      ),
      li(
        "Loading · text",
        `<span className="text-xs text-ink/50 flex items-center gap-2"><Loader2 size={12} className="animate-spin" /> Compiling operations…</span>`,
        <span className="text-xs text-ink/50 flex items-center gap-2"><Loader2 size={12} className="animate-spin" /> Compiling operations…</span>
      ),
    ],
  },
  {
    id: "empty-states",
    title: "Empty & error states",
    items: [
      li(
        "Empty · inbox",
        `<div className="text-center py-8">
  <Inbox size={28} className="mx-auto text-ink/20 mb-3" />
  <p className="text-sm text-ink/60">No incidents yet</p>
  <p className="text-xs text-ink/35 mt-1">Ingest a log to see analysis here.</p>
</div>`,
        <div className="text-center py-8">
          <Inbox size={28} className="mx-auto text-ink/20 mb-3" />
          <p className="text-sm text-ink/60">No incidents yet</p>
          <p className="text-xs text-ink/35 mt-1">Ingest a log to see analysis here.</p>
        </div>
      ),
      li(
        "Empty · search",
        `<div className="text-center py-8">
  <FileQuestion size={28} className="mx-auto text-ink/20 mb-3" />
  <p className="text-sm text-ink/60">No matches for "timeout"</p>
  <p className="text-xs text-ink/35 mt-1">Try fewer keywords or a different category.</p>
</div>`,
        <div className="text-center py-8">
          <FileQuestion size={28} className="mx-auto text-ink/20 mb-3" />
          <p className="text-sm text-ink/60">No matches for "timeout"</p>
          <p className="text-xs text-ink/35 mt-1">Try fewer keywords or a different category.</p>
        </div>
      ),
      li(
        "Error · offline",
        `<div className="text-center py-8">
  <WifiOff size={28} className="mx-auto text-amber-400/50 mb-3" />
  <p className="text-sm text-ink/60">Connection lost</p>
  <button className="mt-3 inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-ink/10 text-xs text-ink/70 hover:bg-ink/15"><RotateCcw size={11} /> Retry</button>
</div>`,
        <div className="text-center py-8">
          <WifiOff size={28} className="mx-auto text-amber-400/50 mb-3" />
          <p className="text-sm text-ink/60">Connection lost</p>
          <button className="mt-3 inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-ink/10 text-xs text-ink/70 hover:bg-ink/15"><RotateCcw size={11} /> Retry</button>
        </div>
      ),
      li(
        "Error · 404",
        `<div className="text-center py-6">
  <p className="font-mono text-4xl gradient-text font-bold">404</p>
  <p className="text-xs text-ink/40 mt-2">This page went missing — probably a null pointer.</p>
</div>`,
        <div className="text-center py-6">
          <p className="font-mono text-4xl gradient-text font-bold">404</p>
          <p className="text-xs text-ink/40 mt-2">This page went missing — probably a null pointer.</p>
        </div>
      ),
    ],
  },
];
