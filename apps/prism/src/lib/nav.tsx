import { useState } from "react";
import { li, type LibGroup } from "./types";
import {
  Home, ChevronRight, ChevronLeft, ChevronsLeft, ChevronsRight, ChevronDown,
  LayoutDashboard, FileCode, Settings, Activity, Layers, Compass,
  Search, Bell, Menu, Dot,
} from "lucide-react";

function Tabs({ variant }: { variant: "underline" | "pill" | "boxed" }) {
  const [t, setT] = useState(1);
  const tabs = ["Overview", "Ops", "Evidence"];
  if (variant === "underline")
    return (
      <div className="flex gap-4 border-b border-ink/10">
        {tabs.map((x, i) => (
          <button key={x} onClick={() => setT(i)} className={`pb-2 text-sm border-b-2 -mb-px transition-colors ${t === i ? "border-cyan-400 text-ink" : "border-transparent text-ink/50 hover:text-ink/80"}`}>{x}</button>
        ))}
      </div>
    );
  if (variant === "pill")
    return (
      <div className="flex gap-1 p-1 rounded-xl bg-ink/5 border border-ink/10 w-fit">
        {tabs.map((x, i) => (
          <button key={x} onClick={() => setT(i)} className={`px-3 py-1.5 rounded-lg text-xs transition-colors ${t === i ? "bg-cyan-500/15 text-cyan-300 border border-cyan-500/30" : "text-ink/50 hover:text-ink/80"}`}>{x}</button>
        ))}
      </div>
    );
  return (
    <div className="flex gap-1">
      {tabs.map((x, i) => (
        <button key={x} onClick={() => setT(i)} className={`px-3 py-1.5 rounded-t-lg border text-xs transition-colors ${t === i ? "border-ink/15 border-b-transparent bg-ink/5 text-ink -mb-px" : "border-transparent text-ink/50"}`}>{x}</button>
      ))}
    </div>
  );
}

export const navGroups: LibGroup[] = [
  {
    id: "tabs",
    title: "Tabs",
    items: [
      li("Tabs · underline", `<Tabs variant="underline" />`, <Tabs variant="underline" />),
      li("Tabs · pill", `<Tabs variant="pill" />`, <Tabs variant="pill" />),
      li("Tabs · boxed", `<Tabs variant="boxed" />`, <Tabs variant="boxed" />),
      li(
        "Tab · with badge",
        `<button className="flex items-center gap-1.5 px-3 py-1.5 text-sm text-cyan-300 border-b-2 border-cyan-400">Ops <span className="px-1.5 rounded-full bg-cyan-500/15 text-[10px]">312</span></button>`,
        <button className="flex items-center gap-1.5 px-3 py-1.5 text-sm text-cyan-300 border-b-2 border-cyan-400">Ops <span className="px-1.5 rounded-full bg-cyan-500/15 text-[10px]">312</span></button>
      ),
      li(
        "Vertical tabs",
        `<div className="flex flex-col gap-0.5 w-36 text-sm">
  <button className="text-left px-3 py-2 rounded-lg bg-cyan-500/10 border-l-2 border-cyan-400 text-cyan-300">General</button>
  <button className="text-left px-3 py-2 rounded-lg text-ink/50 hover:bg-ink/5">Domains</button>
  <button className="text-left px-3 py-2 rounded-lg text-ink/50 hover:bg-ink/5">Models</button>
</div>`,
        <div className="flex flex-col gap-0.5 w-36 text-sm">
          <button className="text-left px-3 py-2 rounded-lg bg-cyan-500/10 border-l-2 border-cyan-400 text-cyan-300">General</button>
          <button className="text-left px-3 py-2 rounded-lg text-ink/50 hover:bg-ink/5">Domains</button>
          <button className="text-left px-3 py-2 rounded-lg text-ink/50 hover:bg-ink/5">Models</button>
        </div>
      ),
    ],
  },
  {
    id: "breadcrumbs",
    title: "Breadcrumbs & pagination",
    items: [
      li(
        "Breadcrumb",
        `<nav className="flex items-center gap-1.5 text-xs text-ink/50">
  <Home size={12} /> <ChevronRight size={11} className="text-ink/25" />
  <span className="hover:text-ink cursor-pointer">domains</span> <ChevronRight size={11} className="text-ink/25" />
  <span className="text-ink">logs</span>
</nav>`,
        <nav className="flex items-center gap-1.5 text-xs text-ink/50">
          <Home size={12} /> <ChevronRight size={11} className="text-ink/25" />
          <span className="hover:text-ink cursor-pointer">domains</span> <ChevronRight size={11} className="text-ink/25" />
          <span className="text-ink">logs</span>
        </nav>
      ),
      li(
        "Breadcrumb · mono",
        `<nav className="flex items-center gap-1 font-mono text-xs text-ink/40">
  <span>app</span>/<span>Http</span>/<span>Controllers</span>/<span className="text-cyan-400">MailController.php</span>
</nav>`,
        <nav className="flex items-center gap-1 font-mono text-xs text-ink/40">
          <span>app</span>/<span>Http</span>/<span>Controllers</span>/<span className="text-cyan-400">MailController.php</span>
        </nav>
      ),
      li(
        "Pagination",
        `<div className="flex items-center gap-1">
  <button className="p-1.5 rounded-md text-ink/50 hover:bg-ink/10"><ChevronLeft size={14} /></button>
  <button className="w-7 h-7 rounded-md text-xs bg-cyan-500/15 text-cyan-300 border border-cyan-500/30">1</button>
  <button className="w-7 h-7 rounded-md text-xs text-ink/50 hover:bg-ink/10">2</button>
  <button className="w-7 h-7 rounded-md text-xs text-ink/50 hover:bg-ink/10">3</button>
  <button className="p-1.5 rounded-md text-ink/50 hover:bg-ink/10"><ChevronRight size={14} /></button>
</div>`,
        <div className="flex items-center gap-1">
          <button className="p-1.5 rounded-md text-ink/50 hover:bg-ink/10"><ChevronLeft size={14} /></button>
          <button className="w-7 h-7 rounded-md text-xs bg-cyan-500/15 text-cyan-300 border border-cyan-500/30">1</button>
          <button className="w-7 h-7 rounded-md text-xs text-ink/50 hover:bg-ink/10">2</button>
          <button className="w-7 h-7 rounded-md text-xs text-ink/50 hover:bg-ink/10">3</button>
          <button className="p-1.5 rounded-md text-ink/50 hover:bg-ink/10"><ChevronRight size={14} /></button>
        </div>
      ),
      li(
        "Pagination · first/last",
        `<div className="flex items-center gap-1">
  <button className="p-1.5 rounded-md text-ink/50 hover:bg-ink/10"><ChevronsLeft size={14} /></button>
  <button className="p-1.5 rounded-md text-ink/50 hover:bg-ink/10"><ChevronLeft size={14} /></button>
  <span className="px-2 text-xs text-ink/50 font-mono">12 / 98</span>
  <button className="p-1.5 rounded-md text-ink/50 hover:bg-ink/10"><ChevronRight size={14} /></button>
  <button className="p-1.5 rounded-md text-ink/50 hover:bg-ink/10"><ChevronsRight size={14} /></button>
</div>`,
        <div className="flex items-center gap-1">
          <button className="p-1.5 rounded-md text-ink/50 hover:bg-ink/10"><ChevronsLeft size={14} /></button>
          <button className="p-1.5 rounded-md text-ink/50 hover:bg-ink/10"><ChevronLeft size={14} /></button>
          <span className="px-2 text-xs text-ink/50 font-mono">12 / 98</span>
          <button className="p-1.5 rounded-md text-ink/50 hover:bg-ink/10"><ChevronRight size={14} /></button>
          <button className="p-1.5 rounded-md text-ink/50 hover:bg-ink/10"><ChevronsRight size={14} /></button>
        </div>
      ),
      li(
        "Stepper",
        `<div className="flex items-center gap-2 text-xs">
  <span className="w-6 h-6 rounded-full bg-cyan-500 text-dark-950 flex items-center justify-center font-bold">1</span>
  <div className="w-8 h-px bg-cyan-400" />
  <span className="w-6 h-6 rounded-full bg-cyan-500/15 border border-cyan-500/40 text-cyan-300 flex items-center justify-center">2</span>
  <div className="w-8 h-px bg-ink/15" />
  <span className="w-6 h-6 rounded-full border border-ink/20 text-ink/40 flex items-center justify-center">3</span>
</div>`,
        <div className="flex items-center gap-2 text-xs">
          <span className="w-6 h-6 rounded-full bg-cyan-500 text-dark-950 flex items-center justify-center font-bold">1</span>
          <div className="w-8 h-px bg-cyan-400" />
          <span className="w-6 h-6 rounded-full bg-cyan-500/15 border border-cyan-500/40 text-cyan-300 flex items-center justify-center">2</span>
          <div className="w-8 h-px bg-ink/15" />
          <span className="w-6 h-6 rounded-full border border-ink/20 text-ink/40 flex items-center justify-center">3</span>
        </div>
      ),
      li(
        "Stepper · labelled",
        `<div className="flex items-center gap-3 text-xs">
  <div className="flex items-center gap-1.5"><span className="w-5 h-5 rounded-full bg-emerald-500/15 border border-emerald-500/40 text-emerald-400 flex items-center justify-center text-[10px]">✓</span><span className="text-ink/60">Ingest</span></div>
  <div className="w-6 h-px bg-ink/15" />
  <div className="flex items-center gap-1.5"><span className="w-5 h-5 rounded-full bg-cyan-500 text-dark-950 flex items-center justify-center text-[10px] font-bold">2</span><span className="text-ink">Compile</span></div>
  <div className="w-6 h-px bg-ink/15" />
  <div className="flex items-center gap-1.5"><span className="w-5 h-5 rounded-full border border-ink/20 text-ink/40 flex items-center justify-center text-[10px]">3</span><span className="text-ink/40">Verify</span></div>
</div>`,
        <div className="flex items-center gap-3 text-xs">
          <div className="flex items-center gap-1.5"><span className="w-5 h-5 rounded-full bg-emerald-500/15 border border-emerald-500/40 text-emerald-400 flex items-center justify-center text-[10px]">✓</span><span className="text-ink/60">Ingest</span></div>
          <div className="w-6 h-px bg-ink/15" />
          <div className="flex items-center gap-1.5"><span className="w-5 h-5 rounded-full bg-cyan-500 text-dark-950 flex items-center justify-center text-[10px] font-bold">2</span><span className="text-ink">Compile</span></div>
          <div className="w-6 h-px bg-ink/15" />
          <div className="flex items-center gap-1.5"><span className="w-5 h-5 rounded-full border border-ink/20 text-ink/40 flex items-center justify-center text-[10px]">3</span><span className="text-ink/40">Verify</span></div>
        </div>
      ),
    ],
  },
  {
    id: "menus",
    title: "Menus & nav items",
    items: [
      li(
        "Nav item · active",
        `<button className="w-full flex items-center gap-2.5 px-3 py-2 rounded-lg bg-cyan-500/10 border border-cyan-500/25 text-cyan-300 text-sm"><LayoutDashboard size={15} /> Dashboard</button>`,
        <button className="w-full flex items-center gap-2.5 px-3 py-2 rounded-lg bg-cyan-500/10 border border-cyan-500/25 text-cyan-300 text-sm"><LayoutDashboard size={15} /> Dashboard</button>
      ),
      li(
        "Nav item · idle",
        `<button className="w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-ink/60 text-sm hover:bg-ink/5 hover:text-ink transition-colors"><FileCode size={15} /> Codemap</button>`,
        <button className="w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-ink/60 text-sm hover:bg-ink/5 hover:text-ink transition-colors"><FileCode size={15} /> Codemap</button>
      ),
      li(
        "Nav item · with badge",
        `<button className="w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-ink/60 text-sm hover:bg-ink/5"><Activity size={15} /> Incidents <span className="ml-auto px-1.5 py-0.5 rounded-full bg-rose-500/15 text-rose-400 text-[10px] font-semibold">3</span></button>`,
        <button className="w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-ink/60 text-sm hover:bg-ink/5"><Activity size={15} /> Incidents <span className="ml-auto px-1.5 py-0.5 rounded-full bg-rose-500/15 text-rose-400 text-[10px] font-semibold">3</span></button>
      ),
      li(
        "Nav item · nested",
        `<div className="text-sm">
  <button className="w-full flex items-center gap-2 px-3 py-2 rounded-lg text-ink/60 hover:bg-ink/5"><Layers size={15} /> Domains <ChevronDown size={12} className="ml-auto text-ink/30" /></button>
  <button className="w-full flex items-center gap-2 pl-9 pr-3 py-1.5 rounded-lg text-cyan-300 text-xs bg-cyan-500/5"><Dot size={12} /> logs</button>
  <button className="w-full flex items-center gap-2 pl-9 pr-3 py-1.5 rounded-lg text-ink/50 text-xs"><Dot size={12} className="text-ink/25" /> specsync</button>
</div>`,
        <div className="text-sm">
          <button className="w-full flex items-center gap-2 px-3 py-2 rounded-lg text-ink/60 hover:bg-ink/5"><Layers size={15} /> Domains <ChevronDown size={12} className="ml-auto text-ink/30" /></button>
          <button className="w-full flex items-center gap-2 pl-9 pr-3 py-1.5 rounded-lg text-cyan-300 text-xs bg-cyan-500/5"><Dot size={12} /> logs</button>
          <button className="w-full flex items-center gap-2 pl-9 pr-3 py-1.5 rounded-lg text-ink/50 text-xs"><Dot size={12} className="text-ink/25" /> specsync</button>
        </div>
      ),
      li(
        "Sidebar section",
        `<div className="w-44">
  <p className="px-3 text-[10px] uppercase tracking-wider text-ink/30 mb-1">Workspace</p>
  <button className="w-full flex items-center gap-2.5 px-3 py-2 rounded-lg bg-cyan-500/10 text-cyan-300 text-sm"><Compass size={14} /> Explore</button>
  <button className="w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-ink/60 text-sm hover:bg-ink/5"><Settings size={14} /> Settings</button>
</div>`,
        <div className="w-44">
          <p className="px-3 text-[10px] uppercase tracking-wider text-ink/30 mb-1">Workspace</p>
          <button className="w-full flex items-center gap-2.5 px-3 py-2 rounded-lg bg-cyan-500/10 text-cyan-300 text-sm"><Compass size={14} /> Explore</button>
          <button className="w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-ink/60 text-sm hover:bg-ink/5"><Settings size={14} /> Settings</button>
        </div>
      ),
      li(
        "Navbar",
        `<div className="w-full flex items-center gap-4 px-4 py-2.5 rounded-xl glass-card text-sm">
  <span className="font-bold gradient-text">Prism</span>
  <span className="text-ink/50 hidden sm:inline">Docs</span>
  <span className="text-ink/50 hidden sm:inline">API</span>
  <div className="ml-auto flex items-center gap-2">
    <Search size={14} className="text-ink/40" /><Bell size={14} className="text-ink/40" /><Menu size={14} className="text-ink/40 sm:hidden" />
  </div>
</div>`,
        <div className="w-full flex items-center gap-4 px-4 py-2.5 rounded-xl glass-card text-sm">
          <span className="font-bold gradient-text">Prism</span>
          <span className="text-ink/50 hidden sm:inline">Docs</span>
          <span className="text-ink/50 hidden sm:inline">API</span>
          <div className="ml-auto flex items-center gap-2">
            <Search size={14} className="text-ink/40" /><Bell size={14} className="text-ink/40" /><Menu size={14} className="text-ink/40 sm:hidden" />
          </div>
        </div>
      ),
      li(
        "Context menu",
        `<div className="w-40 rounded-xl glass-card p-1 text-xs">
  <button className="w-full text-left px-2.5 py-1.5 rounded-lg hover:bg-ink/10 flex justify-between"><span>Rename</span><kbd className="text-ink/30 font-mono">F2</kbd></button>
  <button className="w-full text-left px-2.5 py-1.5 rounded-lg hover:bg-ink/10 flex justify-between"><span>Duplicate</span><kbd className="text-ink/30 font-mono">⌘D</kbd></button>
  <div className="my-1 border-t border-ink/10" />
  <button className="w-full text-left px-2.5 py-1.5 rounded-lg text-rose-400 hover:bg-rose-500/10">Delete</button>
</div>`,
        <div className="w-40 rounded-xl glass-card p-1 text-xs">
          <button className="w-full text-left px-2.5 py-1.5 rounded-lg hover:bg-ink/10 flex justify-between"><span>Rename</span><kbd className="text-ink/30 font-mono">F2</kbd></button>
          <button className="w-full text-left px-2.5 py-1.5 rounded-lg hover:bg-ink/10 flex justify-between"><span>Duplicate</span><kbd className="text-ink/30 font-mono">⌘D</kbd></button>
          <div className="my-1 border-t border-ink/10" />
          <button className="w-full text-left px-2.5 py-1.5 rounded-lg text-rose-400 hover:bg-rose-500/10">Delete</button>
        </div>
      ),
      li(
        "Command palette row",
        `<div className="w-56 flex items-center gap-2.5 px-3 py-2 rounded-lg bg-cyan-500/10 border border-cyan-500/20 text-sm">
  <Search size={13} className="text-cyan-400" />
  <span className="text-ink">sage ingest</span>
  <kbd className="ml-auto text-[10px] font-mono text-ink/30">⏎</kbd>
</div>`,
        <div className="w-56 flex items-center gap-2.5 px-3 py-2 rounded-lg bg-cyan-500/10 border border-cyan-500/20 text-sm">
          <Search size={13} className="text-cyan-400" />
          <span className="text-ink">sage ingest</span>
          <kbd className="ml-auto text-[10px] font-mono text-ink/30">⏎</kbd>
        </div>
      ),
    ],
  },
];
