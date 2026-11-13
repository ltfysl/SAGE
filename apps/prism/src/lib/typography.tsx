import { li, type LibGroup } from "./types";
import { Quote, Link2, Image as ImageIcon, Play, Search } from "lucide-react";

export const typographyGroups: LibGroup[] = [
  {
    id: "text",
    title: "Text elements",
    items: [
      li("Heading 1", `<h1 className="text-4xl font-bold tracking-tight text-ink">Incident Lens</h1>`, <h1 className="text-4xl font-bold tracking-tight text-ink">Incident Lens</h1>),
      li("Heading 2", `<h2 className="text-3xl font-bold tracking-tight text-ink">Components</h2>`, <h2 className="text-3xl font-bold tracking-tight text-ink">Components</h2>),
      li("Heading 3", `<h3 className="text-xl font-semibold text-ink">Operations</h3>`, <h3 className="text-xl font-semibold text-ink">Operations</h3>),
      li("Heading 4", `<h4 className="text-base font-semibold text-ink">Evidence</h4>`, <h4 className="text-base font-semibold text-ink">Evidence</h4>),
      li("Heading 5", `<h5 className="text-sm font-semibold uppercase tracking-wider text-ink/60">Section</h5>`, <h5 className="text-sm font-semibold uppercase tracking-wider text-ink/60">Section</h5>),
      li("Heading · gradient", `<h2 className="text-3xl font-bold gradient-text">Verified state</h2>`, <h2 className="text-3xl font-bold gradient-text">Verified state</h2>),
      li("Heading · cyan gradient", `<h2 className="text-3xl font-bold gradient-text-cyan">Codemap</h2>`, <h2 className="text-3xl font-bold gradient-text-cyan">Codemap</h2>),
      li("Lead paragraph", `<p className="text-lg text-ink/60 leading-relaxed">Compile logs into verified state transitions.</p>`, <p className="text-lg text-ink/60 leading-relaxed">Compile logs into verified state transitions.</p>),
      li("Body", `<p className="text-sm text-ink/70 leading-relaxed">SAGE parses unstructured logs into evidence-bound operations.</p>`, <p className="text-sm text-ink/70 leading-relaxed">SAGE parses unstructured logs into evidence-bound operations.</p>),
      li("Small / muted", `<p className="text-xs text-ink/40">Generated 2 minutes ago · confidence 0.94</p>`, <p className="text-xs text-ink/40">Generated 2 minutes ago · confidence 0.94</p>),
      li("Caption", `<figcaption className="text-[11px] text-ink/35 italic">Fig 1 — flow chain for /api/mail</figcaption>`, <figcaption className="text-[11px] text-ink/35 italic">Fig 1 — flow chain for /api/mail</figcaption>),
      li("Overline", `<p className="text-[10px] uppercase tracking-[0.2em] text-cyan-400 font-medium">Design system</p>`, <p className="text-[10px] uppercase tracking-[0.2em] text-cyan-400 font-medium">Design system</p>),
      li("Mono text", `<p className="font-mono text-sm text-ink/80">queue.php:114</p>`, <p className="font-mono text-sm text-ink/80">queue.php:114</p>),
      li("Mono · accent", `<p className="font-mono text-sm text-cyan-400">0.94</p>`, <p className="font-mono text-sm text-cyan-400">0.94</p>),
      li("Mark", `<p className="text-sm text-ink/70">The <mark className="bg-cyan-500/20 text-cyan-300 px-0.5 rounded">evidence</mark> links back.</p>`, <p className="text-sm text-ink/70">The <mark className="bg-cyan-500/20 text-cyan-300 px-0.5 rounded">evidence</mark> links back.</p>),
      li("Blockquote", `<blockquote className="border-l-2 border-cyan-400 pl-4 py-1 text-sm text-ink/60 italic">Every fact must carry its source span.</blockquote>`, <blockquote className="border-l-2 border-cyan-400 pl-4 py-1 text-sm text-ink/60 italic">Every fact must carry its source span.</blockquote>),
      li("Pull quote", `<div className="flex gap-3 items-start"><Quote size={18} className="text-violet-400 shrink-0 mt-1" /><p className="text-lg text-ink/70 leading-relaxed">Verified beats plausible.</p></div>`, <div className="flex gap-3 items-start"><Quote size={18} className="text-violet-400 shrink-0 mt-1" /><p className="text-lg text-ink/70 leading-relaxed">Verified beats plausible.</p></div>),
      li("Link", `<a className="text-sm text-cyan-400 hover:text-cyan-300 underline underline-offset-4 decoration-cyan-500/40 cursor-pointer">Read the spec</a>`, <a className="text-sm text-cyan-400 hover:text-cyan-300 underline underline-offset-4 decoration-cyan-500/40 cursor-pointer">Read the spec</a>),
      li("Link · icon", `<a className="inline-flex items-center gap-1 text-sm text-cyan-400 hover:text-cyan-300 cursor-pointer"><Link2 size={12} /> Docs</a>`, <a className="inline-flex items-center gap-1 text-sm text-cyan-400 hover:text-cyan-300 cursor-pointer"><Link2 size={12} /> Docs</a>),
      li("Link · subtle", `<a className="text-sm text-ink/60 hover:text-ink border-b border-dotted border-ink/30 cursor-pointer">changelog</a>`, <a className="text-sm text-ink/60 hover:text-ink border-b border-dotted border-ink/30 cursor-pointer">changelog</a>),
      li("List · unordered", `<ul className="text-sm text-ink/70 space-y-1 list-disc list-inside marker:text-cyan-400"><li>Parse logs</li><li>Compile ops</li></ul>`,
        <ul className="text-sm text-ink/70 space-y-1 list-disc list-inside marker:text-cyan-400"><li>Parse logs</li><li>Compile ops</li></ul>),
      li("List · ordered", `<ol className="text-sm text-ink/70 space-y-1 list-decimal list-inside marker:text-ink/40 marker:font-mono"><li>Ingest</li><li>Verify</li></ol>`,
        <ol className="text-sm text-ink/70 space-y-1 list-decimal list-inside marker:text-ink/40 marker:font-mono"><li>Ingest</li><li>Verify</li></ol>),
      li("List · checks", `<ul className="text-sm text-ink/70 space-y-1.5"><li className="flex gap-2"><span className="text-emerald-400">✓</span> Evidence-bound</li><li className="flex gap-2"><span className="text-emerald-400">✓</span> Deterministic</li></ul>`,
        <ul className="text-sm text-ink/70 space-y-1.5"><li className="flex gap-2"><span className="text-emerald-400">✓</span> Evidence-bound</li><li className="flex gap-2"><span className="text-emerald-400">✓</span> Deterministic</li></ul>),
      li("Definition list", `<dl className="text-sm"><dt className="text-ink font-medium">Confidence</dt><dd className="text-ink/50 text-xs mt-0.5">Heuristic reliability of a compiled op.</dd></dl>`,
        <dl className="text-sm"><dt className="text-ink font-medium">Confidence</dt><dd className="text-ink/50 text-xs mt-0.5">Heuristic reliability of a compiled op.</dd></dl>),
    ],
  },
  {
    id: "media",
    title: "Media & frames",
    items: [
      li(
        "Image frame",
        `<div className="rounded-xl overflow-hidden border border-ink/10">
  <div className="h-20 bg-gradient-to-br from-cyan-500/20 via-violet-500/20 to-rose-500/20 flex items-center justify-center"><ImageIcon size={20} className="text-ink/30" /></div>
</div>`,
        <div className="rounded-xl overflow-hidden border border-ink/10 w-full">
          <div className="h-20 bg-gradient-to-br from-cyan-500/20 via-violet-500/20 to-rose-500/20 flex items-center justify-center"><ImageIcon size={20} className="text-ink/30" /></div>
        </div>
      ),
      li(
        "Video frame",
        `<div className="relative rounded-xl overflow-hidden border border-ink/10">
  <div className="h-24 bg-gradient-to-br from-dark-900 to-dark-950 flex items-center justify-center">
    <span className="w-10 h-10 rounded-full bg-ink/10 border border-ink/20 flex items-center justify-center"><Play size={16} className="text-ink/70 ml-0.5" /></span>
  </div>
  <span className="absolute bottom-2 right-2 px-1.5 py-0.5 rounded bg-black/60 text-white text-[10px] font-mono">0:42</span>
</div>`,
        <div className="relative rounded-xl overflow-hidden border border-ink/10 w-full">
          <div className="h-24 bg-gradient-to-br from-dark-900 to-dark-950 flex items-center justify-center">
            <span className="w-10 h-10 rounded-full bg-ink/10 border border-ink/20 flex items-center justify-center"><Play size={16} className="text-ink/70 ml-0.5" /></span>
          </div>
          <span className="absolute bottom-2 right-2 px-1.5 py-0.5 rounded bg-black/60 text-white text-[10px] font-mono">0:42</span>
        </div>
      ),
      li(
        "Figure + caption",
        `<figure>
  <div className="h-16 rounded-xl bg-gradient-to-r from-violet-500/20 to-rose-500/20 border border-ink/10" />
  <figcaption className="text-[11px] text-ink/35 italic mt-1.5">Ops fan-out across domains</figcaption>
</figure>`,
        <figure className="w-full">
          <div className="h-16 rounded-xl bg-gradient-to-r from-violet-500/20 to-rose-500/20 border border-ink/10" />
          <figcaption className="text-[11px] text-ink/35 italic mt-1.5">Ops fan-out across domains</figcaption>
        </figure>
      ),
    ],
  },
  {
    id: "field-patterns",
    title: "Field patterns",
    items: [
      li(
        "Field · label + hint",
        `<div>
  <label className="block text-xs font-medium text-ink/70 mb-1.5">Webhook URL</label>
  <input placeholder="https://…" className="w-full px-3 py-2 rounded-lg bg-ink/5 border border-ink/10 text-sm outline-none focus:border-cyan-500/50" />
  <p className="mt-1 text-[11px] text-ink/35">POST events to this endpoint.</p>
</div>`,
        <div className="w-full">
          <label className="block text-xs font-medium text-ink/70 mb-1.5">Webhook URL</label>
          <input placeholder="https://…" className="w-full px-3 py-2 rounded-lg bg-ink/5 border border-ink/10 text-sm outline-none focus:border-cyan-500/50" />
          <p className="mt-1 text-[11px] text-ink/35">POST events to this endpoint.</p>
        </div>
      ),
      li(
        "Field · required",
        `<div>
  <label className="block text-xs font-medium text-ink/70 mb-1.5">API key <span className="text-rose-400">*</span></label>
  <input placeholder="sk-…" className="w-full px-3 py-2 rounded-lg bg-ink/5 border border-ink/10 text-sm outline-none focus:border-cyan-500/50 font-mono" />
</div>`,
        <div className="w-full">
          <label className="block text-xs font-medium text-ink/70 mb-1.5">API key <span className="text-rose-400">*</span></label>
          <input placeholder="sk-…" className="w-full px-3 py-2 rounded-lg bg-ink/5 border border-ink/10 text-sm outline-none focus:border-cyan-500/50 font-mono" />
        </div>
      ),
      li(
        "Search bar",
        `<div className="flex items-center gap-2 w-full">
  <div className="relative flex-1">
    <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-ink/30" />
    <input placeholder="Search ops, files, routes…" className="w-full pl-9 pr-3 py-2 rounded-lg bg-ink/5 border border-ink/10 text-sm outline-none focus:border-cyan-500/50" />
  </div>
  <button className="px-4 py-2 rounded-lg bg-cyan-500 text-dark-950 text-sm font-medium">Search</button>
</div>`,
        <div className="flex items-center gap-2 w-full">
          <div className="relative flex-1">
            <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-ink/30" />
            <input placeholder="Search ops, files, routes…" className="w-full pl-9 pr-3 py-2 rounded-lg bg-ink/5 border border-ink/10 text-sm outline-none focus:border-cyan-500/50" />
          </div>
          <button className="px-4 py-2 rounded-lg bg-cyan-500 text-dark-950 text-sm font-medium">Search</button>
        </div>
      ),
      li(
        "OTP input",
        `<div className="flex gap-1.5">{["4","8","1","","",""].map((d,i) => <span key={i} className="w-9 h-11 rounded-lg bg-ink/5 border border-ink/10 flex items-center justify-center font-mono text-lg text-ink">{d}</span>)}</div>`,
        <div className="flex gap-1.5">{["4", "8", "1", "", "", ""].map((d, i) => <span key={i} className="w-9 h-11 rounded-lg bg-ink/5 border border-ink/10 flex items-center justify-center font-mono text-lg text-ink">{d}</span>)}</div>
      ),
      li(
        "Inline edit",
        `<span className="inline-flex items-center gap-1.5 text-sm text-ink border-b border-dashed border-cyan-500/50 cursor-text">incident-042 <span className="text-[10px] text-ink/30">click to edit</span></span>`,
        <span className="inline-flex items-center gap-1.5 text-sm text-ink border-b border-dashed border-cyan-500/50 cursor-text">incident-042 <span className="text-[10px] text-ink/30">click to edit</span></span>
      ),
      li(
        "Number stepper",
        `<div className="inline-flex items-center rounded-lg border border-ink/10 overflow-hidden">
  <button className="px-2.5 py-1.5 text-ink/60 hover:bg-ink/10">−</button>
  <span className="px-3 py-1.5 font-mono text-sm text-ink border-x border-ink/10">3</span>
  <button className="px-2.5 py-1.5 text-ink/60 hover:bg-ink/10">+</button>
</div>`,
        <div className="inline-flex items-center rounded-lg border border-ink/10 overflow-hidden">
          <button className="px-2.5 py-1.5 text-ink/60 hover:bg-ink/10">−</button>
          <span className="px-3 py-1.5 font-mono text-sm text-ink border-x border-ink/10">3</span>
          <button className="px-2.5 py-1.5 text-ink/60 hover:bg-ink/10">+</button>
        </div>
      ),
      li(
        "Color input",
        `<div className="flex items-center gap-2">
  <span className="w-8 h-8 rounded-lg bg-cyan-500 border border-ink/15 cursor-pointer" />
  <input defaultValue="#22d3ee" className="w-24 px-2.5 py-1.5 rounded-lg bg-ink/5 border border-ink/10 font-mono text-xs outline-none focus:border-cyan-500/50" />
</div>`,
        <div className="flex items-center gap-2">
          <span className="w-8 h-8 rounded-lg bg-cyan-500 border border-ink/15 cursor-pointer" />
          <input defaultValue="#22d3ee" className="w-24 px-2.5 py-1.5 rounded-lg bg-ink/5 border border-ink/10 font-mono text-xs outline-none focus:border-cyan-500/50" />
        </div>
      ),
      li(
        "Copy field",
        `<div className="flex rounded-lg overflow-hidden border border-ink/10">
  <input readOnly value="pk_live_9f3…" className="flex-1 px-3 py-2 bg-ink/5 font-mono text-xs text-ink/70 outline-none" />
  <button className="px-3 bg-ink/10 text-ink/60 text-xs hover:bg-ink/15">Copy</button>
</div>`,
        <div className="flex rounded-lg overflow-hidden border border-ink/10 w-full">
          <input readOnly value="pk_live_9f3…" className="flex-1 px-3 py-2 bg-ink/5 font-mono text-xs text-ink/70 outline-none" />
          <button className="px-3 bg-ink/10 text-ink/60 text-xs hover:bg-ink/15">Copy</button>
        </div>
      ),
    ],
  },
];
