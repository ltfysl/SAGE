import { useState } from "react";
import { li, type LibGroup } from "./types";
import { Search, Mail, Lock, Eye, EyeOff, ChevronDown, Check, Minus, Calendar, Globe, FileText, AlertCircle, Star, Heart } from "lucide-react";

const inputCls =
  "w-full px-3 py-2 rounded-lg bg-ink/5 border border-ink/10 text-sm text-ink placeholder:text-ink/30 outline-none focus:border-cyan-500/50 focus:bg-ink/[0.07] transition-all";

function Switch({ on: initial = true, tone = "bg-cyan-500" }: { on?: boolean; tone?: string }) {
  const [on, setOn] = useState(initial);
  return (
    <button
      onClick={() => setOn(!on)}
      className={`w-10 h-[22px] rounded-full relative transition-colors ${on ? tone : "bg-ink/15"}`}
    >
      <span
        className="absolute top-[3px] w-4 h-4 rounded-full bg-white transition-all"
        style={{ left: on ? 22 : 3 }}
      />
    </button>
  );
}

function Check2({ tone = "accent-cyan border-cyan-500 bg-cyan-500", initial = true }: { tone?: string; initial?: boolean }) {
  const [on, setOn] = useState(initial);
  return (
    <button
      onClick={() => setOn(!on)}
      className={`w-[18px] h-[18px] rounded-[5px] border flex items-center justify-center transition-all ${on ? `${tone} border-transparent` : "border-ink/25 bg-ink/5"}`}
    >
      {on && <Check size={12} className="text-dark-950" strokeWidth={3} />}
    </button>
  );
}

function Radio2({ initial = false }: { initial?: boolean }) {
  const [on, setOn] = useState(initial);
  return (
    <button
      onClick={() => setOn(!on)}
      className={`w-[18px] h-[18px] rounded-full border flex items-center justify-center transition-all ${on ? "border-cyan-500" : "border-ink/25"}`}
    >
      {on && <span className="w-2 h-2 rounded-full bg-cyan-400" />}
    </button>
  );
}

function Slider({ initial = 60 }: { initial?: number }) {
  const [v, setV] = useState(initial);
  return (
    <input
      type="range"
      min={0}
      max={100}
      value={v}
      onChange={(e) => setV(Number(e.target.value))}
      className="w-full accent-cyan-400 h-1.5 bg-ink/10 rounded-full appearance-none cursor-pointer"
    />
  );
}

export const formsGroups: LibGroup[] = [
  {
    id: "inputs",
    title: "Text inputs",
    items: [
      li(
        "Input · default",
        `<input placeholder="Search incidents…" className="${inputCls}" />`,
        <input placeholder="Search incidents…" className={inputCls} />
      ),
      li(
        "Input · with icon",
        `<div className="relative">
  <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-ink/30" />
  <input placeholder="Search…" className="${inputCls} pl-9" />
</div>`,
        <div className="relative">
          <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-ink/30" />
          <input placeholder="Search…" className={`${inputCls} pl-9`} />
        </div>
      ),
      li(
        "Input · labelled",
        `<label className="block text-xs text-ink/50 mb-1.5">Email</label>
<div className="relative">
  <Mail size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-ink/30" />
  <input placeholder="you@team.dev" className="${inputCls} pl-9" />
</div>`,
        <div>
          <label className="block text-xs text-ink/50 mb-1.5">Email</label>
          <div className="relative">
            <Mail size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-ink/30" />
            <input placeholder="you@team.dev" className={`${inputCls} pl-9`} />
          </div>
        </div>
      ),
      li(
        "Input · password",
        `<div className="relative">
  <Lock size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-ink/30" />
  <input type="password" defaultValue="hunter22" className="${inputCls} pl-9 pr-9" />
  <Eye size={14} className="absolute right-3 top-1/2 -translate-y-1/2 text-ink/30 cursor-pointer" />
</div>`,
        <PasswordDemo />
      ),
      li(
        "Input · error",
        `<input defaultValue="not-an-email" className="${inputCls} !border-rose-500/60 focus:!border-rose-500" />
<p className="mt-1.5 text-[11px] text-rose-400 flex items-center gap-1"><AlertCircle size={11} /> Enter a valid email</p>`,
        <div>
          <input defaultValue="not-an-email" className={`${inputCls} !border-rose-500/60 focus:!border-rose-500`} />
          <p className="mt-1.5 text-[11px] text-rose-400 flex items-center gap-1"><AlertCircle size={11} /> Enter a valid email</p>
        </div>
      ),
      li(
        "Input · disabled",
        `<input disabled placeholder="Locked" className="${inputCls} opacity-40 cursor-not-allowed" />`,
        <input disabled placeholder="Locked" className={`${inputCls} opacity-40 cursor-not-allowed`} />
      ),
      li(
        "Input · mono",
        `<input defaultValue="sage ingest laravel.log --tail 500" className="${inputCls} font-mono text-xs" />`,
        <input defaultValue="sage ingest laravel.log --tail 500" className={`${inputCls} font-mono text-xs`} />
      ),
      li(
        "Input · prefix",
        `<div className="flex rounded-lg overflow-hidden border border-ink/10 bg-ink/5">
  <span className="px-3 py-2 text-xs text-ink/40 bg-ink/5 border-r border-ink/10 flex items-center">https://</span>
  <input placeholder="logs.example.dev" className="flex-1 px-3 py-2 bg-transparent text-sm text-ink outline-none" />
</div>`,
        <div className="flex rounded-lg overflow-hidden border border-ink/10 bg-ink/5">
          <span className="px-3 py-2 text-xs text-ink/40 bg-ink/5 border-r border-ink/10 flex items-center">https://</span>
          <input placeholder="logs.example.dev" className="flex-1 px-3 py-2 bg-transparent text-sm text-ink outline-none" />
        </div>
      ),
      li(
        "Input · small",
        `<input placeholder="sm" className="${inputCls} !py-1 !text-xs w-28" />`,
        <input placeholder="sm" className={`${inputCls} !py-1 !text-xs w-28`} />
      ),
      li(
        "Input · large",
        `<input placeholder="Search everything…" className="${inputCls} !py-3 !text-base !rounded-xl" />`,
        <input placeholder="Search everything…" className={`${inputCls} !py-3 !text-base !rounded-xl`} />
      ),
    ],
  },
  {
    id: "textarea-select",
    title: "Textarea & select",
    items: [
      li(
        "Textarea",
        `<textarea rows={3} placeholder="Describe the incident…" className="${inputCls} resize-none" />`,
        <textarea rows={3} placeholder="Describe the incident…" className={`${inputCls} resize-none`} />
      ),
      li(
        "Textarea · mono",
        `<textarea rows={3} defaultValue="2024-11-13 09:14:22 production.ERROR: PaymentGateway timeout" className="${inputCls} font-mono text-xs resize-none" />`,
        <textarea rows={3} defaultValue="2024-11-13 09:14:22 production.ERROR: PaymentGateway timeout" className={`${inputCls} font-mono text-xs resize-none`} />
      ),
      li(
        "Textarea · count",
        `<div>
  <textarea rows={2} defaultValue="Queue backlog…" maxLength={80} className="${inputCls} resize-none" />
  <p className="mt-1 text-right text-[10px] text-ink/30">14 / 80</p>
</div>`,
        <div>
          <textarea rows={2} defaultValue="Queue backlog…" maxLength={80} className={`${inputCls} resize-none`} />
          <p className="mt-1 text-right text-[10px] text-ink/30">14 / 80</p>
        </div>
      ),
      li(
        "Select",
        `<div className="relative">
  <select className="${inputCls} appearance-none pr-9">
    <option>Production</option><option>Staging</option>
  </select>
  <ChevronDown size={14} className="absolute right-3 top-1/2 -translate-y-1/2 text-ink/30 pointer-events-none" />
</div>`,
        <div className="relative">
          <select className={`${inputCls} appearance-none pr-9`}>
            <option>Production</option><option>Staging</option>
          </select>
          <ChevronDown size={14} className="absolute right-3 top-1/2 -translate-y-1/2 text-ink/30 pointer-events-none" />
        </div>
      ),
      li(
        "Select · with icon",
        `<div className="relative">
  <Globe size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-ink/30" />
  <select className="${inputCls} appearance-none pl-9 pr-9"><option>eu-west-1</option><option>us-east-1</option></select>
  <ChevronDown size={14} className="absolute right-3 top-1/2 -translate-y-1/2 text-ink/30 pointer-events-none" />
</div>`,
        <div className="relative">
          <Globe size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-ink/30" />
          <select className={`${inputCls} appearance-none pl-9 pr-9`}><option>eu-west-1</option><option>us-east-1</option></select>
          <ChevronDown size={14} className="absolute right-3 top-1/2 -translate-y-1/2 text-ink/30 pointer-events-none" />
        </div>
      ),
      li(
        "Date input",
        `<div className="relative">
  <Calendar size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-ink/30" />
  <input type="date" defaultValue="2026-11-13" className="${inputCls} pl-9" />
</div>`,
        <div className="relative">
          <Calendar size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-ink/30" />
          <input type="date" defaultValue="2026-11-13" className={`${inputCls} pl-9`} />
        </div>
      ),
      li(
        "Dropdown menu (static)",
        `<div className="w-44 rounded-xl glass-card p-1.5 text-sm">
  <button className="w-full text-left px-2.5 py-1.5 rounded-lg hover:bg-ink/10 flex items-center gap-2"><FileText size={13} /> Export logs</button>
  <button className="w-full text-left px-2.5 py-1.5 rounded-lg hover:bg-ink/10 flex items-center gap-2"><Search size={13} /> Re-analyze</button>
  <div className="my-1 border-t border-ink/10" />
  <button className="w-full text-left px-2.5 py-1.5 rounded-lg text-rose-400 hover:bg-rose-500/10">Delete</button>
</div>`,
        <div className="w-44 rounded-xl glass-card p-1.5 text-sm">
          <button className="w-full text-left px-2.5 py-1.5 rounded-lg hover:bg-ink/10 flex items-center gap-2"><FileText size={13} /> Export logs</button>
          <button className="w-full text-left px-2.5 py-1.5 rounded-lg hover:bg-ink/10 flex items-center gap-2"><Search size={13} /> Re-analyze</button>
          <div className="my-1 border-t border-ink/10" />
          <button className="w-full text-left px-2.5 py-1.5 rounded-lg text-rose-400 hover:bg-rose-500/10">Delete</button>
        </div>
      ),
    ],
  },
  {
    id: "toggles",
    title: "Checkbox, radio & switch",
    items: [
      li("Checkbox · on", `<button className="w-[18px] h-[18px] rounded-[5px] bg-cyan-500 flex items-center justify-center"><Check size={12} className="text-dark-950" strokeWidth={3} /></button>`, <Check2 />),
      li("Checkbox · off", `<button className="w-[18px] h-[18px] rounded-[5px] border border-ink/25 bg-ink/5" />`, <Check2 initial={false} />),
      li("Checkbox · violet", `<button className="w-[18px] h-[18px] rounded-[5px] bg-violet-500 flex items-center justify-center"><Check size={12} className="text-white" strokeWidth={3} /></button>`, <Check2 tone="bg-violet-500" />),
      li("Checkbox · emerald", `<button className="w-[18px] h-[18px] rounded-[5px] bg-emerald-500 flex items-center justify-center"><Check size={12} className="text-dark-950" strokeWidth={3} /></button>`, <Check2 tone="bg-emerald-500" />),
      li("Checkbox · indeterminate", `<button className="w-[18px] h-[18px] rounded-[5px] bg-cyan-500 flex items-center justify-center"><Minus size={12} className="text-dark-950" strokeWidth={3} /></button>`,
        <button className="w-[18px] h-[18px] rounded-[5px] bg-cyan-500 flex items-center justify-center"><Minus size={12} className="text-dark-950" strokeWidth={3} /></button>),
      li(
        "Checkbox · labelled",
        `<label className="flex items-center gap-2 text-sm text-ink/70 cursor-pointer">
  <span className="w-[18px] h-[18px] rounded-[5px] bg-cyan-500 flex items-center justify-center"><Check size={12} className="text-dark-950" strokeWidth={3} /></span>
  Include stack traces
</label>`,
        <label className="flex items-center gap-2 text-sm text-ink/70 cursor-pointer">
          <Check2 /> Include stack traces
        </label>
      ),
      li("Radio · on", `<button className="w-[18px] h-[18px] rounded-full border border-cyan-500 flex items-center justify-center"><span className="w-2 h-2 rounded-full bg-cyan-400" /></button>`, <Radio2 initial />),
      li("Radio · off", `<button className="w-[18px] h-[18px] rounded-full border border-ink/25" />`, <Radio2 />),
      li(
        "Radio · group",
        `<div className="space-y-2 text-sm text-ink/70">
  <label className="flex items-center gap-2"><span className="w-[18px] h-[18px] rounded-full border border-cyan-500 flex items-center justify-center"><span className="w-2 h-2 rounded-full bg-cyan-400" /></span> All severities</label>
  <label className="flex items-center gap-2"><span className="w-[18px] h-[18px] rounded-full border border-ink/25" /> Errors only</label>
</div>`,
        <div className="space-y-2 text-sm text-ink/70">
          <label className="flex items-center gap-2"><Radio2 initial /> All severities</label>
          <label className="flex items-center gap-2"><Radio2 /> Errors only</label>
        </div>
      ),
      li("Switch · on", `<button className="w-10 h-[22px] rounded-full bg-cyan-500 relative"><span className="absolute top-[3px] left-[22px] w-4 h-4 rounded-full bg-white" /></button>`, <Switch />),
      li("Switch · off", `<button className="w-10 h-[22px] rounded-full bg-ink/15 relative"><span className="absolute top-[3px] left-[3px] w-4 h-4 rounded-full bg-white" /></button>`, <Switch on={false} />),
      li("Switch · violet", `<button className="w-10 h-[22px] rounded-full bg-violet-500 relative"><span className="absolute top-[3px] left-[22px] w-4 h-4 rounded-full bg-white" /></button>`, <Switch tone="bg-violet-500" />),
      li("Switch · emerald", `<button className="w-10 h-[22px] rounded-full bg-emerald-500 relative"><span className="absolute top-[3px] left-[22px] w-4 h-4 rounded-full bg-white" /></button>`, <Switch tone="bg-emerald-500" />),
      li(
        "Switch · labelled",
        `<div className="flex items-center justify-between w-52">
  <span className="text-sm text-ink/70">Auto-analyze on ingest</span>
  <button className="w-10 h-[22px] rounded-full bg-cyan-500 relative"><span className="absolute top-[3px] left-[22px] w-4 h-4 rounded-full bg-white" /></button>
</div>`,
        <div className="flex items-center justify-between w-52">
          <span className="text-sm text-ink/70">Auto-analyze on ingest</span>
          <Switch />
        </div>
      ),
      li(
        "Settings row",
        `<div className="flex items-start justify-between w-60">
  <div><p className="text-sm text-ink">Evidence links</p><p className="text-xs text-ink/40">Attach file:line spans to ops</p></div>
  <button className="w-10 h-[22px] rounded-full bg-cyan-500 relative shrink-0"><span className="absolute top-[3px] left-[22px] w-4 h-4 rounded-full bg-white" /></button>
</div>`,
        <div className="flex items-start justify-between w-60">
          <div><p className="text-sm text-ink">Evidence links</p><p className="text-xs text-ink/40">Attach file:line spans to ops</p></div>
          <Switch />
        </div>
      ),
    ],
  },
  {
    id: "sliders-rating",
    title: "Sliders & rating",
    items: [
      li("Slider", `<input type="range" className="w-full accent-cyan-400 h-1.5 bg-ink/10 rounded-full appearance-none cursor-pointer" />`, <Slider />),
      li("Slider · low", `<input type="range" value={20} className="w-full accent-cyan-400 h-1.5 bg-ink/10 rounded-full appearance-none" />`, <Slider initial={20} />),
      li("Slider · high", `<input type="range" value={90} className="w-full accent-violet-400 h-1.5 bg-ink/10 rounded-full appearance-none" />`, <Slider initial={90} />),
      li(
        "Slider · labelled",
        `<div className="w-full">
  <div className="flex justify-between text-xs text-ink/50 mb-2"><span>Confidence threshold</span><span className="font-mono text-cyan-400">0.72</span></div>
  <input type="range" className="w-full accent-cyan-400 h-1.5 bg-ink/10 rounded-full appearance-none" />
</div>`,
        <div className="w-full">
          <div className="flex justify-between text-xs text-ink/50 mb-2"><span>Confidence threshold</span><span className="font-mono text-cyan-400">0.72</span></div>
          <Slider initial={72} />
        </div>
      ),
      li(
        "Rating · stars",
        `<div className="flex gap-0.5 text-amber-400">{[0,1,2,3].map(i => <Star key={i} size={16} fill="currentColor" />)}<Star size={16} className="text-ink/20" /></div>`,
        <div className="flex gap-0.5 text-amber-400">{[0, 1, 2, 3].map((i) => <Star key={i} size={16} fill="currentColor" />)}<Star size={16} className="text-ink/20" /></div>
      ),
      li(
        "Rating · hearts",
        `<div className="flex gap-0.5 text-rose-400">{[0,1,2].map(i => <Heart key={i} size={16} fill="currentColor" />)}<Heart size={16} /><Heart size={16} /></div>`,
        <div className="flex gap-0.5 text-rose-400">{[0, 1, 2].map((i) => <Heart key={i} size={16} fill="currentColor" />)}<Heart size={16} /><Heart size={16} /></div>
      ),
    ],
  },
];

function PasswordDemo() {
  const [show, setShow] = useState(false);
  return (
    <div className="relative">
      <Lock size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-ink/30" />
      <input
        type={show ? "text" : "password"}
        defaultValue="hunter22"
        className={`${inputCls} pl-9 pr-9`}
      />
      <button onClick={() => setShow(!show)} className="absolute right-3 top-1/2 -translate-y-1/2 text-ink/30 hover:text-ink/60">
        {show ? <EyeOff size={14} /> : <Eye size={14} />}
      </button>
    </div>
  );
}
