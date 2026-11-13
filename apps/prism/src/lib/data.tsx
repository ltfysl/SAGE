import { useState } from "react";
import { li, type LibGroup } from "./types";
import {
  ChevronDown, ChevronRight, Check, GitCommit, FileCode,
  Terminal, CircleDot, Clock,
} from "lucide-react";

function Avatar({ initials, tone, size = "w-9 h-9 text-xs" }: { initials: string; tone: string; size?: string }) {
  return (
    <span className={`${size} rounded-full ${tone} flex items-center justify-center font-semibold shrink-0`}>{initials}</span>
  );
}

const avatarTones = [
  "bg-cyan-500/20 text-cyan-300 border border-cyan-500/30",
  "bg-violet-500/20 text-violet-300 border border-violet-500/30",
  "bg-emerald-500/20 text-emerald-300 border border-emerald-500/30",
  "bg-rose-500/20 text-rose-300 border border-rose-500/30",
  "bg-amber-500/20 text-amber-300 border border-amber-500/30",
];

function AccordionItem({ q, a, defaultOpen = false }: { q: string; a: string; defaultOpen?: boolean }) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <div className="border border-ink/10 rounded-xl overflow-hidden">
      <button onClick={() => setOpen(!open)} className="w-full flex items-center justify-between px-3.5 py-2.5 text-sm text-ink/80 hover:bg-ink/5 transition-colors">
        {q}
        <ChevronDown size={14} className={`text-ink/40 transition-transform ${open ? "rotate-180" : ""}`} />
      </button>
      {open && <div className="px-3.5 pb-3 text-xs text-ink/50 leading-relaxed">{a}</div>}
    </div>
  );
}

const stats: [string, string, string][] = [
  ["errors today", "47", "+12%"],
  ["mttr", "23m", "-18%"],
  ["ops verified", "1,204", "+5%"],
];

const statTones = ["text-cyan-400", "text-emerald-400", "text-violet-400"];

export const dataGroups: LibGroup[] = [
  {
    id: "avatars",
    title: "Avatars",
    items: [
      ...avatarTones.map((t, i) =>
        li(
          `Avatar · ${["cyan", "violet", "emerald", "rose", "amber"][i]}`,
          `<span className="w-9 h-9 rounded-full ${t} flex items-center justify-center text-xs font-semibold">${["LT", "SK", "JD", "AR", "MK"][i]}</span>`,
          <Avatar initials={["LT", "SK", "JD", "AR", "MK"][i]} tone={t} />
        )
      ),
      li("Avatar · small", `<span className="w-6 h-6 rounded-full bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 flex items-center justify-center text-[9px] font-semibold">LT</span>`,
        <Avatar initials="LT" tone={avatarTones[0]} size="w-6 h-6 text-[9px]" />),
      li("Avatar · large", `<span className="w-14 h-14 rounded-full bg-violet-500/20 text-violet-300 border border-violet-500/30 flex items-center justify-center text-lg font-semibold">SK</span>`,
        <Avatar initials="SK" tone={avatarTones[1]} size="w-14 h-14 text-lg" />),
      li(
        "Avatar · status online",
        `<span className="relative inline-block">
  <span className="w-9 h-9 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 flex items-center justify-center text-xs font-semibold">JD</span>
  <span className="absolute -bottom-0.5 -right-0.5 w-3 h-3 rounded-full bg-emerald-400 border-2 border-bgc" />
</span>`,
        <span className="relative inline-block">
          <Avatar initials="JD" tone={avatarTones[2]} />
          <span className="absolute -bottom-0.5 -right-0.5 w-3 h-3 rounded-full bg-emerald-400 border-2 border-bgc" />
        </span>
      ),
      li(
        "Avatar · status away",
        `<span className="relative inline-block">
  <span className="w-9 h-9 rounded-full bg-amber-500/20 text-amber-300 border border-amber-500/30 flex items-center justify-center text-xs font-semibold">MK</span>
  <span className="absolute -bottom-0.5 -right-0.5 w-3 h-3 rounded-full bg-amber-400 border-2 border-bgc" />
</span>`,
        <span className="relative inline-block">
          <Avatar initials="MK" tone={avatarTones[4]} />
          <span className="absolute -bottom-0.5 -right-0.5 w-3 h-3 rounded-full bg-amber-400 border-2 border-bgc" />
        </span>
      ),
      li(
        "Avatar · group",
        `<div className="flex -space-x-2">
  {["LT","SK","JD"].map((n,i) => <span key={n} className="w-8 h-8 rounded-full border-2 border-bgc flex items-center justify-center text-[10px] font-semibold" style={{ background: ["#0e7490","#6d28d9","#047857"][i], color: "#fff" }}>{n}</span>)}
  <span className="w-8 h-8 rounded-full border-2 border-bgc bg-ink/10 text-ink/50 flex items-center justify-center text-[10px]">+4</span>
</div>`,
        <div className="flex -space-x-2">
          {["LT", "SK", "JD"].map((n, i) => (
            <span key={n} className="w-8 h-8 rounded-full border-2 border-bgc flex items-center justify-center text-[10px] font-semibold" style={{ background: ["#0e7490", "#6d28d9", "#047857"][i], color: "#fff" }}>{n}</span>
          ))}
          <span className="w-8 h-8 rounded-full border-2 border-bgc bg-ink/10 text-ink/50 flex items-center justify-center text-[10px]">+4</span>
        </div>
      ),
      li(
        "Avatar · image",
        `<span className="w-9 h-9 rounded-full bg-gradient-to-br from-cyan-400 to-violet-500 flex items-center justify-center text-xs font-bold text-white">LY</span>`,
        <span className="w-9 h-9 rounded-full bg-gradient-to-br from-cyan-400 to-violet-500 flex items-center justify-center text-xs font-bold text-white">LY</span>
      ),
    ],
  },
  {
    id: "stats",
    title: "Stats & KPIs",
    items: [
      ...stats.map(([label, value, delta], i) =>
        li(
          `Stat card · ${label}`,
          `<div className="glass-card p-4">
  <p className="text-[11px] uppercase tracking-wider text-ink/40">${label}</p>
  <p className="text-2xl font-bold ${statTones[i]} mt-1 font-mono">${value}</p>
  <p className="text-[11px] text-ink/40 mt-0.5">${delta} vs last week</p>
</div>`,
          <div className="glass-card p-4 w-40">
            <p className="text-[11px] uppercase tracking-wider text-ink/40">{label}</p>
            <p className={`text-2xl font-bold ${statTones[i]} mt-1 font-mono`}>{value}</p>
            <p className="text-[11px] text-ink/40 mt-0.5">{delta} vs last week</p>
          </div>
        )
      ),
      li(
        "Stat · inline",
        `<span className="inline-flex items-baseline gap-1.5"><span className="font-mono text-lg font-bold text-cyan-400">98.2%</span><span className="text-[10px] text-ink/40">confidence</span></span>`,
        <span className="inline-flex items-baseline gap-1.5"><span className="font-mono text-lg font-bold text-cyan-400">98.2%</span><span className="text-[10px] text-ink/40">confidence</span></span>
      ),
      li(
        "Stat · delta up",
        `<span className="inline-flex items-center gap-1 text-emerald-400 text-xs font-mono"><ChevronDown size={12} className="rotate-180" /> +18.4%</span>`,
        <span className="inline-flex items-center gap-1 text-emerald-400 text-xs font-mono"><ChevronDown size={12} className="rotate-180" /> +18.4%</span>
      ),
      li(
        "Stat · delta down",
        `<span className="inline-flex items-center gap-1 text-rose-400 text-xs font-mono"><ChevronDown size={12} /> -3.2%</span>`,
        <span className="inline-flex items-center gap-1 text-rose-400 text-xs font-mono"><ChevronDown size={12} /> -3.2%</span>
      ),
      li(
        "KPI tile",
        `<div className="glass-card p-3 flex items-center gap-3">
  <div className="w-9 h-9 rounded-lg bg-cyan-500/10 border border-cyan-500/25 flex items-center justify-center text-cyan-400"><CircleDot size={15} /></div>
  <div><p className="font-mono font-bold text-ink">312</p><p className="text-[10px] text-ink/40">ops compiled</p></div>
</div>`,
        <div className="glass-card p-3 flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-cyan-500/10 border border-cyan-500/25 flex items-center justify-center text-cyan-400"><CircleDot size={15} /></div>
          <div><p className="font-mono font-bold text-ink">312</p><p className="text-[10px] text-ink/40">ops compiled</p></div>
        </div>
      ),
    ],
  },
  {
    id: "tables",
    title: "Tables",
    items: [
      li(
        "Table · default",
        `<table className="w-full text-xs">
  <thead><tr className="text-left text-ink/40 border-b border-ink/10">
    <th className="pb-2 font-medium">File</th><th className="pb-2 font-medium">Ops</th><th className="pb-2 font-medium">Confidence</th>
  </tr></thead>
  <tbody className="divide-y divide-ink/5">
    <tr><td className="py-2 font-mono">web.php</td><td className="py-2">12</td><td className="py-2 text-emerald-400">0.94</td></tr>
    <tr><td className="py-2 font-mono">Kernel.php</td><td className="py-2">8</td><td className="py-2 text-amber-400">0.71</td></tr>
  </tbody>
</table>`,
        <table className="w-full text-xs">
          <thead><tr className="text-left text-ink/40 border-b border-ink/10">
            <th className="pb-2 font-medium">File</th><th className="pb-2 font-medium">Ops</th><th className="pb-2 font-medium">Confidence</th>
          </tr></thead>
          <tbody className="divide-y divide-ink/5">
            <tr><td className="py-2 font-mono">web.php</td><td className="py-2">12</td><td className="py-2 text-emerald-400">0.94</td></tr>
            <tr><td className="py-2 font-mono">Kernel.php</td><td className="py-2">8</td><td className="py-2 text-amber-400">0.71</td></tr>
          </tbody>
        </table>
      ),
      li(
        "Table · striped",
        `<table className="w-full text-xs">
  <thead><tr className="text-left text-ink/40 bg-ink/5"><th className="px-2 py-1.5 font-medium rounded-l">Route</th><th className="px-2 py-1.5 font-medium">Status</th><th className="px-2 py-1.5 font-medium rounded-r">p95</th></tr></thead>
  <tbody>
    <tr className="bg-ink/[0.02]"><td className="px-2 py-1.5 font-mono">/api/jobs</td><td className="px-2 py-1.5"><span className="badge badge-success !py-0.5 !px-2 !text-[10px]">200</span></td><td className="px-2 py-1.5 font-mono">84ms</td></tr>
    <tr><td className="px-2 py-1.5 font-mono">/api/mail</td><td className="px-2 py-1.5"><span className="badge cat-error !py-0.5 !px-2 !text-[10px]">500</span></td><td className="px-2 py-1.5 font-mono">2.3s</td></tr>
    <tr className="bg-ink/[0.02]"><td className="px-2 py-1.5 font-mono">/api/auth</td><td className="px-2 py-1.5"><span className="badge badge-success !py-0.5 !px-2 !text-[10px]">200</span></td><td className="px-2 py-1.5 font-mono">41ms</td></tr>
  </tbody>
</table>`,
        <table className="w-full text-xs">
          <thead><tr className="text-left text-ink/40 bg-ink/5"><th className="px-2 py-1.5 font-medium rounded-l">Route</th><th className="px-2 py-1.5 font-medium">Status</th><th className="px-2 py-1.5 font-medium rounded-r">p95</th></tr></thead>
          <tbody>
            <tr className="bg-ink/[0.02]"><td className="px-2 py-1.5 font-mono">/api/jobs</td><td className="px-2 py-1.5"><span className="badge badge-success !py-0.5 !px-2 !text-[10px]">200</span></td><td className="px-2 py-1.5 font-mono">84ms</td></tr>
            <tr><td className="px-2 py-1.5 font-mono">/api/mail</td><td className="px-2 py-1.5"><span className="badge cat-error !py-0.5 !px-2 !text-[10px]">500</span></td><td className="px-2 py-1.5 font-mono">2.3s</td></tr>
            <tr className="bg-ink/[0.02]"><td className="px-2 py-1.5 font-mono">/api/auth</td><td className="px-2 py-1.5"><span className="badge badge-success !py-0.5 !px-2 !text-[10px]">200</span></td><td className="px-2 py-1.5 font-mono">41ms</td></tr>
          </tbody>
        </table>
      ),
      li(
        "Table · hoverable",
        `<table className="w-full text-xs">
  <tbody className="divide-y divide-ink/5">
    <tr className="hover:bg-ink/5 transition-colors"><td className="py-2">UnhandledJobException</td><td className="py-2 text-right text-rose-400 font-mono">x23</td></tr>
    <tr className="hover:bg-ink/5 transition-colors"><td className="py-2">QueryTimeout</td><td className="py-2 text-right text-amber-400 font-mono">x9</td></tr>
  </tbody>
</table>`,
        <table className="w-full text-xs">
          <tbody className="divide-y divide-ink/5">
            <tr className="hover:bg-ink/5 transition-colors"><td className="py-2">UnhandledJobException</td><td className="py-2 text-right text-rose-400 font-mono">x23</td></tr>
            <tr className="hover:bg-ink/5 transition-colors"><td className="py-2">QueryTimeout</td><td className="py-2 text-right text-amber-400 font-mono">x9</td></tr>
          </tbody>
        </table>
      ),
      li(
        "Key-value list",
        `<dl className="text-xs space-y-1.5">
  <div className="flex justify-between"><dt className="text-ink/40">log file</dt><dd className="font-mono text-ink/80">laravel.log</dd></div>
  <div className="flex justify-between"><dt className="text-ink/40">lines</dt><dd className="font-mono text-ink/80">12,847</dd></div>
  <div className="flex justify-between"><dt className="text-ink/40">span</dt><dd className="font-mono text-ink/80">06:00–23:59</dd></div>
</dl>`,
        <dl className="text-xs space-y-1.5">
          <div className="flex justify-between"><dt className="text-ink/40">log file</dt><dd className="font-mono text-ink/80">laravel.log</dd></div>
          <div className="flex justify-between"><dt className="text-ink/40">lines</dt><dd className="font-mono text-ink/80">12,847</dd></div>
          <div className="flex justify-between"><dt className="text-ink/40">span</dt><dd className="font-mono text-ink/80">06:00–23:59</dd></div>
        </dl>
      ),
    ],
  },
  {
    id: "lists",
    title: "Lists & rows",
    items: [
      li(
        "List · icon rows",
        `<div className="space-y-1 text-sm">
  <div className="flex items-center gap-2.5 px-2.5 py-2 rounded-lg hover:bg-ink/5 cursor-pointer"><FileCode size={14} className="text-cyan-400" /> web.php <span className="ml-auto text-[10px] text-ink/30 font-mono">12 ops</span></div>
  <div className="flex items-center gap-2.5 px-2.5 py-2 rounded-lg hover:bg-ink/5 cursor-pointer"><FileCode size={14} className="text-violet-400" /> Kernel.php <span className="ml-auto text-[10px] text-ink/30 font-mono">8 ops</span></div>
</div>`,
        <div className="space-y-1 text-sm">
          <div className="flex items-center gap-2.5 px-2.5 py-2 rounded-lg hover:bg-ink/5 cursor-pointer"><FileCode size={14} className="text-cyan-400" /> web.php <span className="ml-auto text-[10px] text-ink/30 font-mono">12 ops</span></div>
          <div className="flex items-center gap-2.5 px-2.5 py-2 rounded-lg hover:bg-ink/5 cursor-pointer"><FileCode size={14} className="text-violet-400" /> Kernel.php <span className="ml-auto text-[10px] text-ink/30 font-mono">8 ops</span></div>
        </div>
      ),
      li(
        "Log row",
        `<div className="flex items-center gap-2.5 px-2.5 py-1.5 rounded-lg font-mono text-xs hover:bg-ink/5">
  <span className="text-ink/30">09:14:22</span>
  <span className="px-1.5 py-0.5 rounded bg-rose-500/15 text-rose-400 text-[10px] font-sans font-semibold">ERROR</span>
  <span className="text-ink/70 truncate">PaymentGateway timeout after 30s</span>
</div>`,
        <div className="flex items-center gap-2.5 px-2.5 py-1.5 rounded-lg font-mono text-xs hover:bg-ink/5">
          <span className="text-ink/30">09:14:22</span>
          <span className="px-1.5 py-0.5 rounded bg-rose-500/15 text-rose-400 text-[10px] font-sans font-semibold">ERROR</span>
          <span className="text-ink/70 truncate">PaymentGateway timeout after 30s</span>
        </div>
      ),
      li(
        "Log row · debug",
        `<div className="flex items-center gap-2.5 px-2.5 py-1.5 rounded-lg font-mono text-xs">
  <span className="text-ink/30">09:14:25</span>
  <span className="px-1.5 py-0.5 rounded bg-violet-500/15 text-violet-400 text-[10px] font-sans font-semibold">DEBUG</span>
  <span className="text-ink/50 truncate">Cache warmed for 1,204 keys</span>
</div>`,
        <div className="flex items-center gap-2.5 px-2.5 py-1.5 rounded-lg font-mono text-xs">
          <span className="text-ink/30">09:14:25</span>
          <span className="px-1.5 py-0.5 rounded bg-violet-500/15 text-violet-400 text-[10px] font-sans font-semibold">DEBUG</span>
          <span className="text-ink/50 truncate">Cache warmed for 1,204 keys</span>
        </div>
      ),
      li(
        "Checklist row",
        `<div className="flex items-center gap-2.5 text-sm">
  <span className="w-[18px] h-[18px] rounded-full bg-emerald-500/15 border border-emerald-500/40 flex items-center justify-center"><Check size={10} className="text-emerald-400" strokeWidth={3} /></span>
  <span className="text-ink/70">Evidence bound to web.php:42</span>
</div>`,
        <div className="flex items-center gap-2.5 text-sm">
          <span className="w-[18px] h-[18px] rounded-full bg-emerald-500/15 border border-emerald-500/40 flex items-center justify-center"><Check size={10} className="text-emerald-400" strokeWidth={3} /></span>
          <span className="text-ink/70">Evidence bound to web.php:42</span>
        </div>
      ),
      li(
        "Checklist · pending",
        `<div className="flex items-center gap-2.5 text-sm">
  <span className="w-[18px] h-[18px] rounded-full border border-ink/20" />
  <span className="text-ink/40">Verify spec coverage ≥ 90%</span>
</div>`,
        <div className="flex items-center gap-2.5 text-sm">
          <span className="w-[18px] h-[18px] rounded-full border border-ink/20" />
          <span className="text-ink/40">Verify spec coverage ≥ 90%</span>
        </div>
      ),
      li(
        "Notification row",
        `<div className="flex gap-3 p-3 rounded-xl glass-card">
  <span className="w-8 h-8 rounded-lg bg-cyan-500/10 border border-cyan-500/25 flex items-center justify-center text-cyan-400 shrink-0"><GitCommit size={14} /></span>
  <div className="min-w-0"><p className="text-xs font-medium text-ink">Codemap rebuilt</p><p className="text-[11px] text-ink/40 truncate">1,847 symbols · 4.2s · just now</p></div>
</div>`,
        <div className="flex gap-3 p-3 rounded-xl glass-card">
          <span className="w-8 h-8 rounded-lg bg-cyan-500/10 border border-cyan-500/25 flex items-center justify-center text-cyan-400 shrink-0"><GitCommit size={14} /></span>
          <div className="min-w-0"><p className="text-xs font-medium text-ink">Codemap rebuilt</p><p className="text-[11px] text-ink/40 truncate">1,847 symbols · 4.2s · just now</p></div>
        </div>
      ),
      li(
        "File row",
        `<div className="flex items-center gap-2.5 px-3 py-2 rounded-lg border border-ink/10 bg-ink/[0.03]">
  <FileCode size={14} className="text-cyan-400" />
  <span className="text-xs font-mono text-ink/80 flex-1">laravel-2026-11-13.log</span>
  <span className="text-[10px] text-ink/30">4.1 MB</span>
</div>`,
        <div className="flex items-center gap-2.5 px-3 py-2 rounded-lg border border-ink/10 bg-ink/[0.03]">
          <FileCode size={14} className="text-cyan-400" />
          <span className="text-xs font-mono text-ink/80 flex-1">laravel-2026-11-13.log</span>
          <span className="text-[10px] text-ink/30">4.1 MB</span>
        </div>
      ),
      li(
        "Comment row",
        `<div className="flex gap-2.5">
  <span className="w-7 h-7 rounded-full bg-violet-500/20 text-violet-300 border border-violet-500/30 flex items-center justify-center text-[9px] font-semibold shrink-0">SK</span>
  <div><p className="text-xs text-ink/70"><b className="text-ink">sara</b> · 2m ago</p>
  <p className="text-xs text-ink/50 mt-0.5">The queue driver was set to sync in production.</p></div>
</div>`,
        <div className="flex gap-2.5">
          <span className="w-7 h-7 rounded-full bg-violet-500/20 text-violet-300 border border-violet-500/30 flex items-center justify-center text-[9px] font-semibold shrink-0">SK</span>
          <div><p className="text-xs text-ink/70"><b className="text-ink">sara</b> · 2m ago</p>
            <p className="text-xs text-ink/50 mt-0.5">The queue driver was set to sync in production.</p></div>
        </div>
      ),
      li(
        "Tree item",
        `<div className="font-mono text-xs space-y-1">
  <div className="flex items-center gap-1.5 text-ink/70"><ChevronDown size={12} className="text-ink/40" /><span>app/</span></div>
  <div className="flex items-center gap-1.5 text-ink/50 pl-4"><ChevronRight size={12} className="text-ink/30" /><span>Http/</span></div>
  <div className="flex items-center gap-1.5 text-ink/50 pl-4"><FileCode size={12} className="text-cyan-400" /><span>Kernel.php</span></div>
</div>`,
        <div className="font-mono text-xs space-y-1">
          <div className="flex items-center gap-1.5 text-ink/70"><ChevronDown size={12} className="text-ink/40" /><span>app/</span></div>
          <div className="flex items-center gap-1.5 text-ink/50 pl-4"><ChevronRight size={12} className="text-ink/30" /><span>Http/</span></div>
          <div className="flex items-center gap-1.5 text-ink/50 pl-4"><FileCode size={12} className="text-cyan-400" /><span>Kernel.php</span></div>
        </div>
      ),
    ],
  },
  {
    id: "timeline-accordion",
    title: "Timeline & accordion",
    items: [
      li(
        "Timeline · steps",
        `<div className="relative pl-8 space-y-4">
  <div className="timeline-line" />
  <div className="relative"><span className="timeline-dot border-cyan-400 bg-cyan-500/20 -left-[26px] top-0.5" /><p className="text-xs font-medium text-ink">Ingest started</p><p className="text-[10px] text-ink/35">09:14:01</p></div>
  <div className="relative"><span className="timeline-dot border-violet-400 bg-violet-500/20 -left-[26px] top-0.5" /><p className="text-xs font-medium text-ink">Ops compiled</p><p className="text-[10px] text-ink/35">09:14:09</p></div>
</div>`,
        <div className="relative pl-8 space-y-4">
          <div className="timeline-line" />
          <div className="relative"><span className="timeline-dot border-cyan-400 bg-cyan-500/20 -left-[26px] top-0.5" /><p className="text-xs font-medium text-ink">Ingest started</p><p className="text-[10px] text-ink/35">09:14:01</p></div>
          <div className="relative"><span className="timeline-dot border-violet-400 bg-violet-500/20 -left-[26px] top-0.5" /><p className="text-xs font-medium text-ink">Ops compiled</p><p className="text-[10px] text-ink/35">09:14:09</p></div>
        </div>
      ),
      li(
        "Timeline · horizontal",
        `<div className="flex items-center gap-0">
  <span className="w-2.5 h-2.5 rounded-full bg-cyan-400" /><div className="h-px w-10 bg-cyan-400" />
  <span className="w-2.5 h-2.5 rounded-full bg-violet-400" /><div className="h-px w-10 bg-ink/15" />
  <span className="w-2.5 h-2.5 rounded-full border border-ink/20" />
</div>`,
        <div className="flex items-center gap-0">
          <span className="w-2.5 h-2.5 rounded-full bg-cyan-400" /><div className="h-px w-10 bg-cyan-400" />
          <span className="w-2.5 h-2.5 rounded-full bg-violet-400" /><div className="h-px w-10 bg-ink/15" />
          <span className="w-2.5 h-2.5 rounded-full border border-ink/20" />
        </div>
      ),
      li(
        "Activity feed",
        `<div className="space-y-2.5 text-xs">
  <div className="flex gap-2"><Clock size={12} className="text-cyan-400 mt-0.5 shrink-0" /><span className="text-ink/60">Snapshot restored · <span className="text-ink/30">12m ago</span></span></div>
  <div className="flex gap-2"><GitCommit size={12} className="text-violet-400 mt-0.5 shrink-0" /><span className="text-ink/60">PR #14 merged · <span className="text-ink/30">1h ago</span></span></div>
</div>`,
        <div className="space-y-2.5 text-xs">
          <div className="flex gap-2"><Clock size={12} className="text-cyan-400 mt-0.5 shrink-0" /><span className="text-ink/60">Snapshot restored · <span className="text-ink/30">12m ago</span></span></div>
          <div className="flex gap-2"><GitCommit size={12} className="text-violet-400 mt-0.5 shrink-0" /><span className="text-ink/60">PR #14 merged · <span className="text-ink/30">1h ago</span></span></div>
        </div>
      ),
      li("Accordion · closed", `<Accordion q="What is an Operation?" a="…" />`, <AccordionItem q="What is an Operation?" a="A verified state transition produced by the compiler." />),
      li("Accordion · open", `<Accordion q="How does verification work?" a="…" defaultOpen />`, <AccordionItem q="How does verification work?" a="Each op is checked against its evidence span before apply." defaultOpen />),
      li(
        "Accordion · stacked",
        `<div className="space-y-2"><Accordion /><Accordion /></div>`,
        <div className="space-y-2">
          <AccordionItem q="Where does evidence come from?" a="Parsed file:line spans linked to each op." />
          <AccordionItem q="Can I export a codemap?" a="Yes — sage codemap --json > map.json" />
        </div>
      ),
    ],
  },
  {
    id: "code",
    title: "Code & terminal",
    items: [
      li(
        "Code block",
        `<pre className="code-block"><code>sage ingest laravel.log \\
  --tail 500 --verify</code></pre>`,
        <pre className="code-block"><code>sage ingest laravel.log{"\n"}  --tail 500 --verify</code></pre>
      ),
      li(
        "Inline code",
        `<p className="text-xs text-ink/60">Run <code className="px-1.5 py-0.5 rounded bg-ink/10 text-cyan-300 font-mono text-[11px]">sage verify</code> after ingest.</p>`,
        <p className="text-xs text-ink/60">Run <code className="px-1.5 py-0.5 rounded bg-ink/10 text-cyan-300 font-mono text-[11px]">sage verify</code> after ingest.</p>
      ),
      li(
        "Terminal",
        `<div className="rounded-xl overflow-hidden border border-ink/10">
  <div className="flex gap-1.5 px-3 py-2 bg-ink/5 border-b border-ink/10">
    <span className="w-2.5 h-2.5 rounded-full bg-rose-500/70" /><span className="w-2.5 h-2.5 rounded-full bg-amber-500/70" /><span className="w-2.5 h-2.5 rounded-full bg-emerald-500/70" />
  </div>
  <div className="p-3 font-mono text-xs space-y-1 bg-ink/[0.03]">
    <p><span className="text-cyan-400">$</span> <span className="text-ink/80">sage compile</span></p>
    <p className="text-emerald-400">✓ 312 ops verified in 1.8s</p>
  </div>
</div>`,
        <div className="rounded-xl overflow-hidden border border-ink/10">
          <div className="flex gap-1.5 px-3 py-2 bg-ink/5 border-b border-ink/10">
            <span className="w-2.5 h-2.5 rounded-full bg-rose-500/70" /><span className="w-2.5 h-2.5 rounded-full bg-amber-500/70" /><span className="w-2.5 h-2.5 rounded-full bg-emerald-500/70" />
          </div>
          <div className="p-3 font-mono text-xs space-y-1 bg-ink/[0.03]">
            <p><span className="text-cyan-400">$</span> <span className="text-ink/80">sage compile</span></p>
            <p className="text-emerald-400">✓ 312 ops verified in 1.8s</p>
          </div>
        </div>
      ),
      li(
        "Diff line",
        `<div className="font-mono text-xs rounded-lg overflow-hidden border border-ink/10">
  <p className="px-3 py-1 bg-emerald-500/10 text-emerald-300">+ return redirect()-&gt;route('home');</p>
  <p className="px-3 py-1 bg-rose-500/10 text-rose-300">- die('disabled');</p>
</div>`,
        <div className="font-mono text-xs rounded-lg overflow-hidden border border-ink/10">
          <p className="px-3 py-1 bg-emerald-500/10 text-emerald-300">+ return redirect()-&gt;route('home');</p>
          <p className="px-3 py-1 bg-rose-500/10 text-rose-300">- die('disabled');</p>
        </div>
      ),
      li(
        "kbd",
        `<span className="text-xs text-ink/60">Press <kbd className="px-1.5 py-0.5 rounded bg-ink/10 border border-ink/15 border-b-2 font-mono text-[10px]">⌘K</kbd> to search</span>`,
        <span className="text-xs text-ink/60">Press <kbd className="px-1.5 py-0.5 rounded bg-ink/10 border border-ink/15 border-b-2 font-mono text-[10px]">⌘K</kbd> to search</span>
      ),
      li(
        "Prompt chip",
        `<span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-ink/5 border border-ink/10 font-mono text-[11px] text-ink/60"><Terminal size={11} className="text-cyan-400" />sage --help</span>`,
        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-ink/5 border border-ink/10 font-mono text-[11px] text-ink/60"><Terminal size={11} className="text-cyan-400" />sage --help</span>
      ),
      li(
        "JSON token",
        `<code className="font-mono text-xs"><span className="text-violet-400">"op"</span><span className="text-ink/40">:</span> <span className="text-cyan-300">"route.register"</span></code>`,
        <code className="font-mono text-xs"><span className="text-violet-400">"op"</span><span className="text-ink/40">:</span> <span className="text-cyan-300">"route.register"</span></code>
      ),
    ],
  },
];
