import { li, type LibGroup } from "./types";
import {
  AlertTriangle, CheckCircle2, X, Zap, Shield, CreditCard,
  Upload, Bell, Info, GitBranch, ExternalLink, Crown,
} from "lucide-react";

const cardVariants: [string, string][] = [
  ["glass", "glass-card"],
  ["glow", "glass-card glass-card-glow"],
  ["bordered", "rounded-2xl border border-ink/10 bg-ink/[0.03]"],
  ["elevated", "rounded-2xl bg-ink/5 border border-ink/10 shadow-xl shadow-black/20"],
  ["flat", "rounded-2xl bg-ink/[0.04]"],
  ["gradient border", "rounded-2xl border border-transparent bg-clip-padding [border-image:linear-gradient(135deg,rgba(34,211,238,0.4),rgba(139,92,246,0.4))_1] bg-ink/[0.03]"],
];

const modalTones: [string, string, string][] = [
  ["cyan", "bg-cyan-500/10 border-cyan-500/30 text-cyan-400", "bg-cyan-500 text-dark-950 hover:bg-cyan-400"],
  ["rose", "bg-rose-500/10 border-rose-500/30 text-rose-400", "bg-rose-500 text-white hover:bg-rose-400"],
  ["violet", "bg-violet-500/10 border-violet-500/30 text-violet-400", "bg-violet-500 text-white hover:bg-violet-400"],
];

export const surfaceGroups: LibGroup[] = [
  {
    id: "cards",
    title: "Cards",
    items: [
      ...cardVariants.map(([n, cls]) =>
        li(
          `Card · ${n}`,
          `<div className="${cls} p-4">
  <p className="text-sm font-medium text-ink">Card title</p>
  <p className="text-xs text-ink/50 mt-1">Supporting copy goes here.</p>
</div>`,
          <div className={`${cls} p-4 w-full`}>
            <p className="text-sm font-medium text-ink">Card title</p>
            <p className="text-xs text-ink/50 mt-1">Supporting copy goes here.</p>
          </div>
        )
      ),
      li(
        "Card · with header",
        `<div className="glass-card overflow-hidden">
  <div className="px-4 py-2.5 border-b border-ink/10 flex items-center gap-2"><Zap size={13} className="text-cyan-400" /><span className="text-xs font-medium">Operations</span></div>
  <div className="p-4 text-xs text-ink/50">312 ops compiled from 3 files.</div>
</div>`,
        <div className="glass-card overflow-hidden w-full">
          <div className="px-4 py-2.5 border-b border-ink/10 flex items-center gap-2"><Zap size={13} className="text-cyan-400" /><span className="text-xs font-medium">Operations</span></div>
          <div className="p-4 text-xs text-ink/50">312 ops compiled from 3 files.</div>
        </div>
      ),
      li(
        "Card · with footer action",
        `<div className="glass-card overflow-hidden">
  <div className="p-4 text-xs text-ink/50">Ready to verify 312 operations?</div>
  <div className="px-4 py-2.5 border-t border-ink/10 flex justify-end gap-2">
    <button className="text-xs text-ink/50 px-2.5 py-1">Later</button>
    <button className="text-xs px-3 py-1.5 rounded-lg bg-cyan-500 text-dark-950 font-medium">Verify</button>
  </div>
</div>`,
        <div className="glass-card overflow-hidden w-full">
          <div className="p-4 text-xs text-ink/50">Ready to verify 312 operations?</div>
          <div className="px-4 py-2.5 border-t border-ink/10 flex justify-end gap-2">
            <button className="text-xs text-ink/50 px-2.5 py-1">Later</button>
            <button className="text-xs px-3 py-1.5 rounded-lg bg-cyan-500 text-dark-950 font-medium">Verify</button>
          </div>
        </div>
      ),
      li(
        "Card · media",
        `<div className="glass-card overflow-hidden">
  <div className="h-20 bg-gradient-to-br from-cyan-500/30 to-violet-500/30" />
  <div className="p-4"><p className="text-sm font-medium text-ink">Release notes</p><p className="text-xs text-ink/50 mt-1">v2.4 — SpecSync coverage checks</p></div>
</div>`,
        <div className="glass-card overflow-hidden w-full">
          <div className="h-20 bg-gradient-to-br from-cyan-500/30 to-violet-500/30" />
          <div className="p-4"><p className="text-sm font-medium text-ink">Release notes</p><p className="text-xs text-ink/50 mt-1">v2.4 — SpecSync coverage checks</p></div>
        </div>
      ),
      li(
        "Card · profile",
        `<div className="glass-card p-4 flex items-center gap-3">
  <span className="w-11 h-11 rounded-full bg-gradient-to-br from-cyan-400 to-violet-500 flex items-center justify-center font-bold text-white">LY</span>
  <div><p className="text-sm font-medium text-ink">Latif Y.</p><p className="text-xs text-ink/40">@ltfysl · owner</p></div>
</div>`,
        <div className="glass-card p-4 flex items-center gap-3 w-full">
          <span className="w-11 h-11 rounded-full bg-gradient-to-br from-cyan-400 to-violet-500 flex items-center justify-center font-bold text-white">LY</span>
          <div><p className="text-sm font-medium text-ink">Latif Y.</p><p className="text-xs text-ink/40">@ltfysl · owner</p></div>
        </div>
      ),
      li(
        "Card · hover lift",
        `<div className="glass-card p-4 hover:-translate-y-0.5 hover:border-cyan-500/30 transition-all duration-300 cursor-pointer">
  <p className="text-sm font-medium text-ink flex items-center justify-between">Codemap <ExternalLink size={12} className="text-ink/30" /></p>
  <p className="text-xs text-ink/50 mt-1">1,847 symbols indexed</p>
</div>`,
        <div className="glass-card p-4 hover:-translate-y-0.5 hover:border-cyan-500/30 transition-all duration-300 cursor-pointer w-full">
          <p className="text-sm font-medium text-ink flex items-center justify-between">Codemap <ExternalLink size={12} className="text-ink/30" /></p>
          <p className="text-xs text-ink/50 mt-1">1,847 symbols indexed</p>
        </div>
      ),
      li(
        "Pricing card",
        `<div className="glass-card p-5 border-t-2 border-t-cyan-400">
  <p className="text-xs uppercase tracking-wider text-cyan-400 flex items-center gap-1"><Crown size={12} /> Pro</p>
  <p className="text-3xl font-bold font-mono mt-2 text-ink">$12<span className="text-sm text-ink/40">/mo</span></p>
  <ul className="mt-3 space-y-1.5 text-xs text-ink/60">
    <li className="flex gap-1.5"><CheckCircle2 size={12} className="text-emerald-400 mt-0.5" /> Unlimited ingests</li>
    <li className="flex gap-1.5"><CheckCircle2 size={12} className="text-emerald-400 mt-0.5" /> Codemap exports</li>
  </ul>
</div>`,
        <div className="glass-card p-5 border-t-2 border-t-cyan-400 w-full">
          <p className="text-xs uppercase tracking-wider text-cyan-400 flex items-center gap-1"><Crown size={12} /> Pro</p>
          <p className="text-3xl font-bold font-mono mt-2 text-ink">$12<span className="text-sm text-ink/40">/mo</span></p>
          <ul className="mt-3 space-y-1.5 text-xs text-ink/60">
            <li className="flex gap-1.5"><CheckCircle2 size={12} className="text-emerald-400 mt-0.5" /> Unlimited ingests</li>
            <li className="flex gap-1.5"><CheckCircle2 size={12} className="text-emerald-400 mt-0.5" /> Codemap exports</li>
          </ul>
        </div>
      ),
      li(
        "Evidence card",
        `<div className="glass-card p-4 border-l-2 border-l-violet-400">
  <p className="text-[10px] uppercase tracking-wider text-ink/40">evidence</p>
  <p className="font-mono text-xs text-violet-300 mt-1">app/Http/Kernel.php:42</p>
  <p className="text-xs text-ink/50 mt-1.5">middleware → web,auth,verified</p>
</div>`,
        <div className="glass-card p-4 border-l-2 border-l-violet-400 w-full">
          <p className="text-[10px] uppercase tracking-wider text-ink/40">evidence</p>
          <p className="font-mono text-xs text-violet-300 mt-1">app/Http/Kernel.php:42</p>
          <p className="text-xs text-ink/50 mt-1.5">middleware → web,auth,verified</p>
        </div>
      ),
      li(
        "Category tile",
        `<div className="glass-card p-4 text-center hover:border-cyan-500/30 transition-colors cursor-pointer">
  <GitBranch size={20} className="mx-auto text-cyan-400 mb-2" />
  <p className="text-sm font-medium text-ink">Flow chains</p>
  <p className="text-[10px] text-ink/40 mt-0.5">23 reconstructed</p>
</div>`,
        <div className="glass-card p-4 text-center hover:border-cyan-500/30 transition-colors cursor-pointer w-full">
          <GitBranch size={20} className="mx-auto text-cyan-400 mb-2" />
          <p className="text-sm font-medium text-ink">Flow chains</p>
          <p className="text-[10px] text-ink/40 mt-0.5">23 reconstructed</p>
        </div>
      ),
    ],
  },
  {
    id: "overlays",
    title: "Modals, drawers & popovers",
    items: [
      ...modalTones.map(([n, iconCls, btnCls]) =>
        li(
          `Modal · ${n}`,
          `<div className="glass-card p-5 max-w-xs">
  <div className="w-9 h-9 rounded-full border flex items-center justify-center mb-3 ${iconCls}"><AlertTriangle size={16} /></div>
  <p className="text-sm font-medium text-ink">Delete incident?</p>
  <p className="text-xs text-ink/50 mt-1">This removes the compiled ops and evidence. Can't be undone.</p>
  <div className="mt-4 flex gap-2 justify-end">
    <button className="px-3 py-1.5 rounded-lg text-xs text-ink/60 hover:bg-ink/10">Cancel</button>
    <button className="px-3 py-1.5 rounded-lg text-xs font-medium ${btnCls}">Delete</button>
  </div>
</div>`,
          <div className="glass-card p-5 max-w-xs w-full">
            <div className={`w-9 h-9 rounded-full border flex items-center justify-center mb-3 ${iconCls}`}><AlertTriangle size={16} /></div>
            <p className="text-sm font-medium text-ink">Delete incident?</p>
            <p className="text-xs text-ink/50 mt-1">This removes the compiled ops and evidence. Can't be undone.</p>
            <div className="mt-4 flex gap-2 justify-end">
              <button className="px-3 py-1.5 rounded-lg text-xs text-ink/60 hover:bg-ink/10">Cancel</button>
              <button className={`px-3 py-1.5 rounded-lg text-xs font-medium ${btnCls}`}>Delete</button>
            </div>
          </div>
        )
      ),
      li(
        "Modal · confirm",
        `<div className="glass-card p-5 max-w-xs">
  <p className="text-sm font-medium text-ink">Re-run analysis?</p>
  <p className="text-xs text-ink/50 mt-1">Uses the latest parser against the same log.</p>
  <div className="mt-4 flex gap-2 justify-end">
    <button className="px-3 py-1.5 rounded-lg text-xs text-ink/60 hover:bg-ink/10">Cancel</button>
    <button className="px-3 py-1.5 rounded-lg text-xs font-medium bg-cyan-500 text-dark-950">Run</button>
  </div>
</div>`,
        <div className="glass-card p-5 max-w-xs w-full">
          <p className="text-sm font-medium text-ink">Re-run analysis?</p>
          <p className="text-xs text-ink/50 mt-1">Uses the latest parser against the same log.</p>
          <div className="mt-4 flex gap-2 justify-end">
            <button className="px-3 py-1.5 rounded-lg text-xs text-ink/60 hover:bg-ink/10">Cancel</button>
            <button className="px-3 py-1.5 rounded-lg text-xs font-medium bg-cyan-500 text-dark-950">Run</button>
          </div>
        </div>
      ),
      li(
        "Drawer (static)",
        `<div className="w-56 glass-card p-4 h-full border-l-2 border-l-cyan-500/40">
  <div className="flex items-center justify-between mb-3"><p className="text-sm font-medium text-ink">Op detail</p><X size={14} className="text-ink/40" /></div>
  <p className="font-mono text-[11px] text-violet-300">route.register</p>
  <p className="text-xs text-ink/50 mt-1">Target: /api/jobs</p>
</div>`,
        <div className="w-56 glass-card p-4 border-l-2 border-l-cyan-500/40">
          <div className="flex items-center justify-between mb-3"><p className="text-sm font-medium text-ink">Op detail</p><X size={14} className="text-ink/40" /></div>
          <p className="font-mono text-[11px] text-violet-300">route.register</p>
          <p className="text-xs text-ink/50 mt-1">Target: /api/jobs</p>
        </div>
      ),
      li(
        "Tooltip (static)",
        `<div className="relative">
  <span className="text-sm text-ink/60 underline decoration-dotted underline-offset-4">confidence</span>
  <div className="absolute -top-9 left-1/2 -translate-x-1/2 px-2.5 py-1.5 rounded-lg bg-ink text-bgc text-[11px] whitespace-nowrap shadow-lg">Heuristic reliability 0–1</div>
</div>`,
        <div className="relative pt-10">
          <span className="text-sm text-ink/60 underline decoration-dotted underline-offset-4">confidence</span>
          <div className="absolute top-0 left-1/2 -translate-x-1/2 px-2.5 py-1.5 rounded-lg bg-ink text-bgc text-[11px] whitespace-nowrap shadow-lg">Heuristic reliability 0–1</div>
        </div>
      ),
      li(
        "Popover (static)",
        `<div className="w-52 glass-card p-3 shadow-xl">
  <p className="text-xs font-medium text-ink">Filter ops</p>
  <p className="text-[11px] text-ink/40 mt-0.5">Pick a domain to narrow the index.</p>
  <div className="mt-2 flex flex-wrap gap-1">
    <span className="px-2 py-0.5 rounded bg-cyan-500/15 text-cyan-300 text-[10px]">logs</span>
    <span className="px-2 py-0.5 rounded bg-ink/10 text-ink/50 text-[10px]">codemap</span>
  </div>
</div>`,
        <div className="w-52 glass-card p-3 shadow-xl">
          <p className="text-xs font-medium text-ink">Filter ops</p>
          <p className="text-[11px] text-ink/40 mt-0.5">Pick a domain to narrow the index.</p>
          <div className="mt-2 flex flex-wrap gap-1">
            <span className="px-2 py-0.5 rounded bg-cyan-500/15 text-cyan-300 text-[10px]">logs</span>
            <span className="px-2 py-0.5 rounded bg-ink/10 text-ink/50 text-[10px]">codemap</span>
          </div>
        </div>
      ),
    ],
  },
  {
    id: "toasts",
    title: "Toasts & notifications",
    items: [
      li(
        "Toast · success",
        `<div className="flex items-center gap-2.5 px-3.5 py-2.5 rounded-xl glass-card border-l-2 border-l-emerald-400">
  <CheckCircle2 size={15} className="text-emerald-400" />
  <p className="text-xs text-ink/80">312 ops verified</p>
  <X size={12} className="ml-2 text-ink/30" />
</div>`,
        <div className="flex items-center gap-2.5 px-3.5 py-2.5 rounded-xl glass-card border-l-2 border-l-emerald-400">
          <CheckCircle2 size={15} className="text-emerald-400" />
          <p className="text-xs text-ink/80">312 ops verified</p>
          <X size={12} className="ml-2 text-ink/30" />
        </div>
      ),
      li(
        "Toast · error",
        `<div className="flex items-center gap-2.5 px-3.5 py-2.5 rounded-xl glass-card border-l-2 border-l-rose-400">
  <X size={15} className="text-rose-400" />
  <p className="text-xs text-ink/80">Ingest failed — retrying</p>
</div>`,
        <div className="flex items-center gap-2.5 px-3.5 py-2.5 rounded-xl glass-card border-l-2 border-l-rose-400">
          <X size={15} className="text-rose-400" />
          <p className="text-xs text-ink/80">Ingest failed — retrying</p>
        </div>
      ),
      li(
        "Toast · info",
        `<div className="flex items-center gap-2.5 px-3.5 py-2.5 rounded-xl glass-card border-l-2 border-l-cyan-400">
  <Info size={15} className="text-cyan-400" />
  <p className="text-xs text-ink/80">Snapshot updated</p>
</div>`,
        <div className="flex items-center gap-2.5 px-3.5 py-2.5 rounded-xl glass-card border-l-2 border-l-cyan-400">
          <Info size={15} className="text-cyan-400" />
          <p className="text-xs text-ink/80">Snapshot updated</p>
        </div>
      ),
      li(
        "Toast · with action",
        `<div className="flex items-center gap-2.5 px-3.5 py-2.5 rounded-xl glass-card border-l-2 border-l-violet-400">
  <Bell size={15} className="text-violet-400" />
  <p className="text-xs text-ink/80">3 new criticals</p>
  <button className="text-[11px] font-medium text-violet-300 underline underline-offset-2">View</button>
</div>`,
        <div className="flex items-center gap-2.5 px-3.5 py-2.5 rounded-xl glass-card border-l-2 border-l-violet-400">
          <Bell size={15} className="text-violet-400" />
          <p className="text-xs text-ink/80">3 new criticals</p>
          <button className="text-[11px] font-medium text-violet-300 underline underline-offset-2">View</button>
        </div>
      ),
      li(
        "Notification · rich",
        `<div className="w-64 glass-card p-3.5">
  <div className="flex items-center gap-2"><Bell size={13} className="text-cyan-400" /><p className="text-xs font-medium text-ink">Incident triaged</p><span className="ml-auto text-[10px] text-ink/30">now</span></div>
  <p className="text-[11px] text-ink/50 mt-1.5">MailJob timeout mapped to queue.php:114 — confidence 0.91</p>
</div>`,
        <div className="w-64 glass-card p-3.5">
          <div className="flex items-center gap-2"><Bell size={13} className="text-cyan-400" /><p className="text-xs font-medium text-ink">Incident triaged</p><span className="ml-auto text-[10px] text-ink/30">now</span></div>
          <p className="text-[11px] text-ink/50 mt-1.5">MailJob timeout mapped to queue.php:114 — confidence 0.91</p>
        </div>
      ),
    ],
  },
  {
    id: "special",
    title: "Dropzones & misc",
    items: [
      li(
        "Dropzone · idle",
        `<div className="border-2 border-dashed border-ink/10 rounded-2xl p-6 text-center glass-card">
  <Upload size={24} className="mx-auto text-cyan-400 mb-2" />
  <p className="text-sm font-medium text-ink">Drop a log file</p>
  <p className="text-xs text-ink/40 mt-0.5">.log / .txt · max 50MB</p>
</div>`,
        <div className="border-2 border-dashed border-ink/10 rounded-2xl p-6 text-center glass-card w-full">
          <Upload size={24} className="mx-auto text-cyan-400 mb-2" />
          <p className="text-sm font-medium text-ink">Drop a log file</p>
          <p className="text-xs text-ink/40 mt-0.5">.log / .txt · max 50MB</p>
        </div>
      ),
      li(
        "Dropzone · active",
        `<div className="border-2 border-dashed border-cyan-400 bg-cyan-500/10 rounded-2xl p-6 text-center scale-[1.02] transition-all">
  <Upload size={24} className="mx-auto text-cyan-300 mb-2" />
  <p className="text-sm font-medium text-ink">Release to ingest</p>
</div>`,
        <div className="border-2 border-dashed border-cyan-400 bg-cyan-500/10 rounded-2xl p-6 text-center scale-[1.02] transition-all w-full">
          <Upload size={24} className="mx-auto text-cyan-300 mb-2" />
          <p className="text-sm font-medium text-ink">Release to ingest</p>
        </div>
      ),
      li(
        "Divider",
        `<div className="flex items-center gap-3 text-[10px] uppercase tracking-widest text-ink/30">
  <div className="h-px flex-1 bg-ink/10" /> or <div className="h-px flex-1 bg-ink/10" />
</div>`,
        <div className="flex items-center gap-3 text-[10px] uppercase tracking-widest text-ink/30 w-full">
          <div className="h-px flex-1 bg-ink/10" /> or <div className="h-px flex-1 bg-ink/10" />
        </div>
      ),
      li(
        "Divider · gradient",
        `<div className="h-px bg-gradient-to-r from-transparent via-cyan-500/40 to-transparent" />`,
        <div className="h-px bg-gradient-to-r from-transparent via-cyan-500/40 to-transparent w-full" />
      ),
      li(
        "Shield callout",
        `<div className="flex items-center gap-3 p-3.5 rounded-xl bg-gradient-to-r from-emerald-500/10 to-cyan-500/10 border border-emerald-500/20">
  <Shield size={18} className="text-emerald-400" />
  <div><p className="text-xs font-medium text-ink">Evidence-bound</p><p className="text-[11px] text-ink/50">Every op links to a verified span.</p></div>
</div>`,
        <div className="flex items-center gap-3 p-3.5 rounded-xl bg-gradient-to-r from-emerald-500/10 to-cyan-500/10 border border-emerald-500/20 w-full">
          <Shield size={18} className="text-emerald-400" />
          <div><p className="text-xs font-medium text-ink">Evidence-bound</p><p className="text-[11px] text-ink/50">Every op links to a verified span.</p></div>
        </div>
      ),
      li(
        "Credit card row",
        `<div className="flex items-center gap-3 px-3.5 py-2.5 rounded-xl border border-ink/10 bg-ink/[0.03]">
  <CreditCard size={16} className="text-ink/50" />
  <span className="text-xs font-mono text-ink/70">•••• 4242</span>
  <span className="ml-auto text-[10px] text-ink/30">exp 12/28</span>
</div>`,
        <div className="flex items-center gap-3 px-3.5 py-2.5 rounded-xl border border-ink/10 bg-ink/[0.03] w-full">
          <CreditCard size={16} className="text-ink/50" />
          <span className="text-xs font-mono text-ink/70">•••• 4242</span>
          <span className="ml-auto text-[10px] text-ink/30">exp 12/28</span>
        </div>
      ),
    ],
  },
];
