import { li, type LibGroup } from "./types";
import {
  Plus, Trash2, Download, ArrowRight, Loader2, Heart, Share2,
  Settings, Search, Bell, ChevronDown, Copy, Check, Zap, Star,
  MoreHorizontal, RefreshCw, Upload, X,
} from "lucide-react";

const base = "inline-flex items-center justify-center gap-2 font-medium rounded-lg transition-all duration-200";

const variants: [string, string][] = [
  ["Primary", "bg-cyan-500 text-dark-950 hover:bg-cyan-400"],
  ["Secondary", "bg-ink/10 text-ink hover:bg-ink/15"],
  ["Outline", "border border-ink/15 text-ink/80 hover:border-ink/30 hover:bg-ink/5"],
  ["Ghost", "text-ink/70 hover:bg-ink/10 hover:text-ink"],
  ["Danger", "bg-rose-500 text-white hover:bg-rose-400"],
  ["Danger outline", "border border-rose-500/40 text-rose-400 hover:bg-rose-500/10"],
  ["Success", "bg-emerald-500 text-dark-950 hover:bg-emerald-400"],
  ["Violet", "bg-violet-500 text-white hover:bg-violet-400"],
  ["Amber", "bg-amber-500 text-dark-950 hover:bg-amber-400"],
  ["Gradient", "bg-gradient-to-r from-cyan-500 to-violet-500 text-white hover:opacity-90"],
  ["Link", "text-cyan-400 hover:underline underline-offset-4"],
];

const sizes: [string, string][] = [
  ["sm", "px-2.5 py-1 text-xs"],
  ["md", "px-4 py-2 text-sm"],
  ["lg", "px-6 py-3 text-base"],
];

const buttonItems = variants.flatMap(([v, vc]) =>
  sizes.map(([s, sc]) =>
    li(
      `${v} button · ${s}`,
      `<button className="${base} ${vc} ${sc}">Button</button>`,
      <button className={`${base} ${vc} ${sc}`}>Button</button>
    )
  )
);

const buttonStates = variants.slice(0, 5).flatMap(([v, vc]) => [
  li(
    `${v} button · disabled`,
    `<button disabled className="${base} ${vc} px-4 py-2 text-sm opacity-50 cursor-not-allowed">Button</button>`,
    <button disabled className={`${base} ${vc} px-4 py-2 text-sm opacity-50 cursor-not-allowed`}>Button</button>
  ),
  li(
    `${v} button · loading`,
    `<button className="${base} ${vc} px-4 py-2 text-sm"><Loader2 className="animate-spin" size={14} /> Loading</button>`,
    <button className={`${base} ${vc} px-4 py-2 text-sm`}><Loader2 className="animate-spin" size={14} /> Loading</button>
  ),
]);

const iconBtns: [string, typeof Settings][] = [
  ["Settings", Settings], ["Search", Search], ["Bell", Bell], ["Close", X],
  ["Refresh", RefreshCw], ["Upload", Upload], ["Download", Download], ["More", MoreHorizontal],
];
const iconButtonItems = iconBtns.map(([n, I]) =>
  li(
    `Icon button · ${n.toLowerCase()}`,
    `<button className="p-2 rounded-lg text-ink/60 hover:text-ink hover:bg-ink/10 transition-colors"><${n} size={16} /></button>`,
    <button className="p-2 rounded-lg text-ink/60 hover:text-ink hover:bg-ink/10 transition-colors"><I size={16} /></button>
  )
);

export const actionsGroups: LibGroup[] = [
  {
    id: "buttons",
    title: "Buttons",
    items: [
      ...buttonItems,
      ...buttonStates,
      li(
        "Button · icon left",
        `<button className="${base} bg-cyan-500 text-dark-950 hover:bg-cyan-400 px-4 py-2 text-sm"><Plus size={14} /> New incident</button>`,
        <button className={`${base} bg-cyan-500 text-dark-950 hover:bg-cyan-400 px-4 py-2 text-sm`}><Plus size={14} /> New incident</button>
      ),
      li(
        "Button · icon right",
        `<button className="${base} bg-ink/10 text-ink hover:bg-ink/15 px-4 py-2 text-sm">Continue <ArrowRight size={14} /></button>`,
        <button className={`${base} bg-ink/10 text-ink hover:bg-ink/15 px-4 py-2 text-sm`}>Continue <ArrowRight size={14} /></button>
      ),
      li(
        "Button · pill",
        `<button className="${base} rounded-full bg-violet-500 text-white hover:bg-violet-400 px-5 py-2 text-sm">Deploy</button>`,
        <button className={`${base} rounded-full bg-violet-500 text-white hover:bg-violet-400 px-5 py-2 text-sm`}>Deploy</button>
      ),
      li(
        "Button · block",
        `<button className="${base} w-full bg-cyan-500 text-dark-950 hover:bg-cyan-400 px-4 py-2 text-sm">Full width</button>`,
        <button className={`${base} w-full bg-cyan-500 text-dark-950 hover:bg-cyan-400 px-4 py-2 text-sm`}>Full width</button>
      ),
      li(
        "Button · glow",
        `<button className="${base} bg-cyan-500 text-dark-950 px-4 py-2 text-sm glow-cyan">Analyze</button>`,
        <button className={`${base} bg-cyan-500 text-dark-950 px-4 py-2 text-sm glow-cyan`}>Analyze</button>
      ),
    ],
  },
  {
    id: "icon-buttons",
    title: "Icon buttons",
    items: [
      ...iconButtonItems,
      li(
        "Icon button · accent",
        `<button className="p-2 rounded-lg bg-cyan-500/10 border border-cyan-500/30 text-cyan-400"><Heart size={16} /></button>`,
        <button className="p-2 rounded-lg bg-cyan-500/10 border border-cyan-500/30 text-cyan-400"><Heart size={16} /></button>
      ),
      li(
        "Icon button · solid",
        `<button className="p-2 rounded-lg bg-cyan-500 text-dark-950"><Share2 size={16} /></button>`,
        <button className="p-2 rounded-lg bg-cyan-500 text-dark-950"><Share2 size={16} /></button>
      ),
    ],
  },
  {
    id: "button-groups",
    title: "Button groups & segmented",
    items: [
      li(
        "Button group",
        `<div className="inline-flex rounded-lg border border-ink/10 overflow-hidden divide-x divide-ink/10">
  <button className="px-3 py-1.5 text-xs bg-ink/5 text-ink/70 hover:bg-ink/10">Left</button>
  <button className="px-3 py-1.5 text-xs bg-cyan-500/15 text-cyan-300">Center</button>
  <button className="px-3 py-1.5 text-xs bg-ink/5 text-ink/70 hover:bg-ink/10">Right</button>
</div>`,
        <div className="inline-flex rounded-lg border border-ink/10 overflow-hidden divide-x divide-ink/10">
          <button className="px-3 py-1.5 text-xs bg-ink/5 text-ink/70 hover:bg-ink/10">Left</button>
          <button className="px-3 py-1.5 text-xs bg-cyan-500/15 text-cyan-300">Center</button>
          <button className="px-3 py-1.5 text-xs bg-ink/5 text-ink/70 hover:bg-ink/10">Right</button>
        </div>
      ),
      li(
        "Segmented control",
        `<div className="inline-flex p-1 rounded-xl bg-ink/5 border border-ink/10">
  <button className="px-3 py-1.5 text-xs rounded-lg text-ink/60">Day</button>
  <button className="px-3 py-1.5 text-xs rounded-lg bg-cyan-500/15 text-cyan-300 border border-cyan-500/30">Week</button>
  <button className="px-3 py-1.5 text-xs rounded-lg text-ink/60">Month</button>
</div>`,
        <div className="inline-flex p-1 rounded-xl bg-ink/5 border border-ink/10">
          <button className="px-3 py-1.5 text-xs rounded-lg text-ink/60">Day</button>
          <button className="px-3 py-1.5 text-xs rounded-lg bg-cyan-500/15 text-cyan-300 border border-cyan-500/30">Week</button>
          <button className="px-3 py-1.5 text-xs rounded-lg text-ink/60">Month</button>
        </div>
      ),
      li(
        "Toolbar",
        `<div className="inline-flex items-center gap-1 p-1 rounded-xl glass-card">
  <button className="p-1.5 rounded-md text-ink/60 hover:text-ink hover:bg-ink/10"><Copy size={14} /></button>
  <button className="p-1.5 rounded-md text-ink/60 hover:text-ink hover:bg-ink/10"><Download size={14} /></button>
  <div className="w-px h-4 bg-ink/10 mx-1" />
  <button className="p-1.5 rounded-md text-rose-400 hover:bg-rose-500/10"><Trash2 size={14} /></button>
</div>`,
        <div className="inline-flex items-center gap-1 p-1 rounded-xl glass-card">
          <button className="p-1.5 rounded-md text-ink/60 hover:text-ink hover:bg-ink/10"><Copy size={14} /></button>
          <button className="p-1.5 rounded-md text-ink/60 hover:text-ink hover:bg-ink/10"><Download size={14} /></button>
          <div className="w-px h-4 bg-ink/10 mx-1" />
          <button className="p-1.5 rounded-md text-rose-400 hover:bg-rose-500/10"><Trash2 size={14} /></button>
        </div>
      ),
      li(
        "Split button",
        `<div className="inline-flex rounded-lg overflow-hidden">
  <button className="px-3 py-2 text-sm bg-cyan-500 text-dark-950 hover:bg-cyan-400">Merge</button>
  <button className="px-2 py-2 bg-cyan-600 text-dark-950 border-l border-dark-950/20"><ChevronDown size={14} /></button>
</div>`,
        <div className="inline-flex rounded-lg overflow-hidden">
          <button className="px-3 py-2 text-sm bg-cyan-500 text-dark-950 hover:bg-cyan-400">Merge</button>
          <button className="px-2 py-2 bg-cyan-600 text-dark-950 border-l border-dark-950/20"><ChevronDown size={14} /></button>
        </div>
      ),
      li(
        "FAB",
        `<button className="w-11 h-11 rounded-full bg-gradient-to-br from-cyan-500 to-violet-500 text-white flex items-center justify-center shadow-lg shadow-cyan-500/25"><Plus size={18} /></button>`,
        <button className="w-11 h-11 rounded-full bg-gradient-to-br from-cyan-500 to-violet-500 text-white flex items-center justify-center shadow-lg shadow-cyan-500/25"><Plus size={18} /></button>
      ),
      li(
        "Copy chip",
        `<button className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-ink/5 border border-ink/10 text-[11px] text-ink/50 hover:border-cyan-500/30 hover:text-cyan-300 transition-colors"><Copy size={12} /> Copy</button>`,
        <button className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-ink/5 border border-ink/10 text-[11px] text-ink/50 hover:border-cyan-500/30 hover:text-cyan-300 transition-colors"><Copy size={12} /> Copy</button>
      ),
      li(
        "Action row",
        `<div className="flex gap-2">
  <button className="${base} bg-cyan-500 text-dark-950 px-4 py-2 text-sm">Save</button>
  <button className="${base} text-ink/70 hover:bg-ink/10 px-4 py-2 text-sm">Cancel</button>
</div>`,
        <div className="flex gap-2">
          <button className={`${base} bg-cyan-500 text-dark-950 px-4 py-2 text-sm`}>Save</button>
          <button className={`${base} text-ink/70 hover:bg-ink/10 px-4 py-2 text-sm`}>Cancel</button>
        </div>
      ),
      li(
        "Destructive confirm",
        `<div className="flex gap-2">
  <button className="${base} bg-rose-500 text-white px-4 py-2 text-sm"><Trash2 size={14} /> Delete</button>
  <button className="${base} text-ink/70 hover:bg-ink/10 px-4 py-2 text-sm">Keep</button>
</div>`,
        <div className="flex gap-2">
          <button className={`${base} bg-rose-500 text-white px-4 py-2 text-sm`}><Trash2 size={14} /> Delete</button>
          <button className={`${base} text-ink/70 hover:bg-ink/10 px-4 py-2 text-sm`}>Keep</button>
        </div>
      ),
    ],
  },
  {
    id: "badges",
    title: "Badges & tags",
    items: [
      ...(["critical", "error", "warning", "info", "debug", "success", "unknown"] as const).map((c) =>
        li(
          `Category badge · ${c}`,
          `<span className="badge cat-${c}">${c.toUpperCase()}</span>`,
          <span className={`badge cat-${c}`}>{c.toUpperCase()}</span>
        )
      ),
      li("Badge · success", `<span className="badge badge-success">OK</span>`, <span className="badge badge-success">OK</span>),
      li(
        "Status badge · live",
        `<span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs"><span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" /> Live</span>`,
        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs"><span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" /> Live</span>
      ),
      li(
        "Status badge · deploying",
        `<span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 text-xs"><Loader2 size={10} className="animate-spin" /> Deploying</span>`,
        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 text-xs"><Loader2 size={10} className="animate-spin" /> Deploying</span>
      ),
      li(
        "Status badge · degraded",
        `<span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-400 text-xs"><span className="w-1.5 h-1.5 rounded-full bg-amber-400" /> Degraded</span>`,
        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-400 text-xs"><span className="w-1.5 h-1.5 rounded-full bg-amber-400" /> Degraded</span>
      ),
      li(
        "Badge · count",
        `<span className="inline-flex items-center justify-center min-w-[20px] h-5 px-1.5 rounded-full bg-rose-500 text-white text-[10px] font-bold">9</span>`,
        <span className="inline-flex items-center justify-center min-w-[20px] h-5 px-1.5 rounded-full bg-rose-500 text-white text-[10px] font-bold">9</span>
      ),
      li(
        "Badge · outline",
        `<span className="px-2.5 py-1 rounded-full border border-ink/20 text-ink/60 text-xs">beta</span>`,
        <span className="px-2.5 py-1 rounded-full border border-ink/20 text-ink/60 text-xs">beta</span>
      ),
      li(
        "Badge · gradient",
        `<span className="px-2.5 py-1 rounded-full bg-gradient-to-r from-cyan-500/20 to-violet-500/20 border border-cyan-500/30 text-cyan-300 text-xs font-medium">PRO</span>`,
        <span className="px-2.5 py-1 rounded-full bg-gradient-to-r from-cyan-500/20 to-violet-500/20 border border-cyan-500/30 text-cyan-300 text-xs font-medium">PRO</span>
      ),
      ...([
        ["cyan", "bg-cyan-500/10 text-cyan-400 border-cyan-500/20"],
        ["violet", "bg-violet-500/10 text-violet-400 border-violet-500/20"],
        ["emerald", "bg-emerald-500/10 text-emerald-400 border-emerald-500/20"],
        ["rose", "bg-rose-500/10 text-rose-400 border-rose-500/20"],
        ["amber", "bg-amber-500/10 text-amber-400 border-amber-500/20"],
        ["blue", "bg-blue-500/10 text-blue-400 border-blue-500/20"],
      ] as [string, string][]).map(([c, cls]) =>
        li(
          `Tag · ${c}`,
          `<span className="px-2 py-0.5 rounded ${cls} text-[11px] font-medium border">#${c}</span>`,
          <span className={`px-2 py-0.5 rounded ${cls} text-[11px] font-medium border`}>#{c}</span>
        )
      ),
      li(
        "Removable chip",
        `<span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-ink/10 text-ink/70 text-xs">laravel <X size={11} className="cursor-pointer hover:text-rose-400" /></span>`,
        <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-ink/10 text-ink/70 text-xs">laravel <X size={11} className="cursor-pointer hover:text-rose-400" /></span>
      ),
      li(
        "Chip · selected",
        `<span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-cyan-500/15 border border-cyan-500/40 text-cyan-300 text-xs"><Check size={11} /> auth</span>`,
        <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-cyan-500/15 border border-cyan-500/40 text-cyan-300 text-xs"><Check size={11} /> auth</span>
      ),
      li(
        "Severity chip · critical",
        `<span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-[11px] font-semibold sev-critical bg-rose-500/10"><Zap size={11} /> P0</span>`,
        <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-[11px] font-semibold sev-critical bg-rose-500/10"><Zap size={11} /> P0</span>
      ),
      li(
        "Rating star",
        `<span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-amber-500/10 text-amber-400 text-xs"><Star size={11} fill="currentColor" /> 4.9</span>`,
        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-amber-500/10 text-amber-400 text-xs"><Star size={11} fill="currentColor" /> 4.9</span>
      ),
    ],
  },
];
