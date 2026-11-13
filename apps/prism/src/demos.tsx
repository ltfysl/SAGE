import { useRef, useState } from "react";
import { motion } from "framer-motion";
import {
  AlertTriangle, CheckCircle, Database, Download, Shield, Upload,
} from "lucide-react";

export function GlassCardPreview() {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
      <div className="glass-card rounded-2xl p-6">
        <div className="text-sm font-medium mb-1">glass-card</div>
        <p className="text-xs text-white/40">Blur + 6% white border. Hover lifts the edge.</p>
      </div>
      <div className="glass-card glass-card-glow rounded-2xl p-6">
        <div className="text-sm font-medium mb-1">glass-card-glow</div>
        <p className="text-xs text-white/40">Adds the cyan/blue ambient glow.</p>
      </div>
    </div>
  );
}

export function PillBadgePreview() {
  return (
    <div className="flex flex-wrap gap-3 items-center">
      <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-cyan-500/20 bg-cyan-500/5 text-cyan-400 text-sm">
        <Shield size={14} /> Local-only • Evidence-bound • No cloud upload
      </div>
      <span className="badge badge-success">ANALYZED</span>
      <span className="badge cat-warning">WARNING</span>
    </div>
  );
}

export function ButtonsPreview() {
  return (
    <div className="flex flex-wrap items-center gap-3">
      <button className="px-4 py-2.5 rounded-xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 text-sm hover:bg-cyan-500/20 transition-colors flex items-center gap-2">
        <Download size={14} /> Export Markdown
      </button>
      <button className="px-3 py-1.5 rounded-lg bg-white/[0.04] border border-white/10 text-xs text-white/60 hover:border-cyan-500/30 hover:text-cyan-300 transition-colors">
        top exception
      </button>
      <button className="text-sm text-white/40 hover:text-cyan-400 transition-colors">
        or analyze the <span className="underline">sample log</span>
      </button>
    </div>
  );
}

export function DropzonePreview() {
  const [over, setOver] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const fileRef = useRef<HTMLInputElement>(null);
  return (
    <div className="space-y-3">
      <div
        onDragOver={(e) => { e.preventDefault(); setOver(true); }}
        onDragLeave={() => setOver(false)}
        onDrop={(e) => {
          e.preventDefault();
          setOver(false);
          const f = e.dataTransfer.files?.[0];
          if (f) setFile(f);
        }}
        onClick={() => fileRef.current?.click()}
        className={`glass-card border-2 border-dashed rounded-2xl p-8 text-center cursor-pointer transition-all duration-300 ${
          over ? "border-cyan-400 bg-cyan-500/10 scale-[1.02]" : "border-white/10 hover:border-cyan-500/30 hover:bg-white/[0.02]"
        }`}
      >
        <input
          ref={fileRef}
          type="file"
          accept=".log,.txt"
          className="hidden"
          onChange={(e) => {
            const f = e.target.files?.[0];
            if (f) setFile(f);
          }}
        />
        <motion.div animate={over ? { scale: 1.1 } : { scale: 1 }}>
          <Upload size={36} className="mx-auto mb-3 text-cyan-400" />
        </motion.div>
        <p className="text-base font-medium mb-1">Drop a Laravel log file here</p>
        <p className="text-xs text-white/40">or click to browse • .log / .txt • Max 50MB</p>
        {file && <p className="mt-3 text-xs text-cyan-400">{file.name} ({(file.size / 1024).toFixed(0)} KB)</p>}
      </div>
      <p className="text-[11px] text-white/25 text-center">Interactive — drag anything over it or click to browse.</p>
    </div>
  );
}

export function LoadingStepsPreview() {
  const steps = ["Parsing log blocks…", "Compiling evidence-bound events…", "Building incident timeline…", "Generating checklist…"];
  return (
    <div className="flex items-start gap-8">
      <motion.div
        animate={{ rotate: 360 }}
        transition={{ repeat: Infinity, duration: 1.5, ease: "linear" }}
        className="w-10 h-10 shrink-0 border-2 border-cyan-500/30 border-t-cyan-400 rounded-full"
      />
      <div className="space-y-2.5">
        {steps.map((s, i) => (
          <div key={s} className="flex items-center gap-3 text-sm">
            {i < 2 ? (
              <CheckCircle size={16} className="text-emerald-400" />
            ) : i === 2 ? (
              <div className="w-4 h-4 rounded-full border-2 border-cyan-400 border-t-transparent animate-spin" />
            ) : (
              <div className="w-4 h-4 rounded-full border border-white/10" />
            )}
            <span className={i <= 2 ? "text-white/70" : "text-white/20"}>{s}</span>
          </div>
        ))}
      </div>
      <div className="flex items-center gap-1.5 ml-auto pt-1">
        {[0, 1, 2].map((i) => (
          <span key={i} className="pulse-dot w-2 h-2 rounded-full bg-cyan-400 inline-block" />
        ))}
      </div>
    </div>
  );
}

export function StatCardPreview() {
  const cards = [
    { label: "Severity", value: "CRITICAL", icon: AlertTriangle, cls: "bg-rose-500/20 text-rose-400 border-rose-500/30" },
    { label: "Total Events", value: "1,204", icon: AlertTriangle, cls: "" },
    { label: "Top Exception", value: "QueryException", icon: AlertTriangle, cls: "" },
    { label: "Duration", value: "6m 42s", icon: AlertTriangle, cls: "" },
  ];
  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      {cards.map((c) => (
        <div key={c.label} className={`glass-card rounded-xl p-5 ${c.cls}`}>
          <div className="flex items-center gap-2 text-white/40 text-xs mb-2">
            <c.icon size={14} /> {c.label}
          </div>
          <div className="text-lg font-semibold font-mono">{c.value}</div>
        </div>
      ))}
    </div>
  );
}

export function CategoryTilePreview() {
  return (
    <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
      {[
        { name: "DATABASE_ERROR", n: 37, t: "14:22:31" },
        { name: "EXCEPTION_EVENT", n: 54, t: "14:22:09" },
        { name: "QUEUE_FAILURE", n: 12, t: "14:25:40" },
      ].map((c) => (
        <div key={c.name} className="bg-white/[0.03] rounded-xl p-4 border border-white/5 hover:border-cyan-500/20 transition-colors">
          <div className="flex items-center gap-2 mb-2">
            <Database size={14} className="text-cyan-400" />
            <span className="text-xs text-white/50">{c.name}</span>
          </div>
          <div className="text-2xl font-bold font-mono">{c.n}</div>
          <div className="text-[10px] text-white/30 mt-1">{c.t}</div>
        </div>
      ))}
    </div>
  );
}

export function BadgesPreview() {
  const sev = [
    { n: "critical", c: "bg-rose-500/20 text-rose-400 border-rose-500/30" },
    { n: "high", c: "bg-amber-500/20 text-amber-400 border-amber-500/30" },
    { n: "medium", c: "bg-cyan-500/20 text-cyan-400 border-cyan-500/30" },
    { n: "low", c: "bg-emerald-500/20 text-emerald-400 border-emerald-500/30" },
  ];
  const cats = ["critical", "error", "warning", "info", "debug", "success", "unknown"];
  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-2">
        {sev.map((s) => (
          <span key={s.n} className={`px-3 py-1 rounded-full border text-xs font-medium uppercase tracking-wide ${s.c}`}>
            {s.n}
          </span>
        ))}
      </div>
      <div className="flex flex-wrap gap-2">
        {cats.map((c) => (
          <span key={c} className={`badge cat-${c}`}>{c}</span>
        ))}
      </div>
    </div>
  );
}

export function TimelinePreview() {
  const events = [
    { t: "14:22:31", c: "EXCEPTION_EVENT", m: "QueryException: Base table or view not found" },
    { t: "14:23:02", c: "DATABASE_ERROR", m: "SQLSTATE[42S02] connection retry failed" },
    { t: "14:25:40", c: "QUEUE_FAILURE", m: "Job SendReportEmail exceeded max attempts" },
    { t: "14:28:11", c: "RECOVERY_EVENT", m: "Queue worker restarted, draining backlog" },
  ];
  return (
    <div className="relative pl-6 border-l border-white/10 space-y-4">
      {events.map((e) => (
        <div key={e.t} className="relative">
          <div className="absolute -left-[25px] w-2 h-2 rounded-full bg-cyan-500 mt-1.5" />
          <div className="text-[10px] text-white/30 font-mono">{e.t}</div>
          <div className="flex items-center gap-2">
            <span className="text-xs text-white/60">{e.c}</span>
          </div>
          <div className="text-xs text-white/40 mt-1">{e.m}</div>
        </div>
      ))}
    </div>
  );
}

export function EvidencePreview() {
  return (
    <div className="space-y-3">
      <div className="bg-black/30 rounded-lg p-4 border border-white/5 font-mono text-xs">
        <div className="flex items-center gap-2 mb-2">
          <span className="px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-400 text-[10px]">EXCEPTION_EVENT</span>
          <span className="text-white/30">14:22:31</span>
        </div>
        <p className="text-white/60 truncate">Illuminate\Database\QueryException: SQLSTATE[42S02]: Base table or view not found</p>
        <p className="text-white/20 mt-1 text-[10px]">storage/logs/laravel.log:4182</p>
      </div>
      <div className="code-block">[2024-05-07 14:22:31] production.ERROR: SQLSTATE[42S02] {"{900+ lines}"}</div>
    </div>
  );
}

export function ImpactPreview() {
  return (
    <div className="space-y-3">
      <div className="bg-amber-500/5 border border-amber-500/10 rounded-lg p-4">
        <div className="font-medium text-amber-300 text-sm">Reporting pipeline</div>
        <div className="text-xs text-white/40 mt-1">Nightly report job failed — customers on weekly plans got no summary email.</div>
      </div>
    </div>
  );
}

export function ErrorBannerPreview() {
  return (
    <div className="glass-card border-rose-500/30 rounded-xl p-6">
      <div className="flex items-center gap-3 text-rose-400">
        <AlertTriangle size={20} />
        <span className="font-medium">Analysis Error</span>
      </div>
      <p className="mt-2 text-sm text-rose-300/70">Log file exceeds the 50MB parse limit.</p>
    </div>
  );
}

export function ChecklistPreview() {
  const items = ["Confirm QueryException source migration", "Check queue worker restart policy", "Verify mail driver fallback"];
  return (
    <div className="space-y-2">
      {items.map((i) => (
        <label key={i} className="flex items-start gap-3 text-sm text-white/60 cursor-pointer">
          <input type="checkbox" className="mt-0.5 accent-cyan-500" />
          <span>{i}</span>
        </label>
      ))}
    </div>
  );
}

export function AskPreview() {
  const [answer, setAnswer] = useState<string | null>(null);
  const qs = ["top exception", "mail failures", "timeline", "impact", "checklist"];
  const answers: Record<string, string> = {
    "top exception": "Illuminate\\Database\\QueryException — 19 occurrences, first seen 14:22:31.",
    "mail failures": "Swift_TransportException (11): SMTP auth refused after cert rotation.",
    timeline: "Error burst 14:22→14:28; recovery begins when the worker restarts at 14:28:11.",
    impact: "Reporting pipeline degraded; weekly summary emails were not delivered.",
    checklist: "3 open items — migration source, worker restart policy, mail driver fallback.",
  };
  return (
    <div>
      <div className="flex flex-wrap gap-2">
        {qs.map((q) => (
          <button
            key={q}
            onClick={() => setAnswer(answers[q])}
            className="px-3 py-1.5 rounded-lg bg-white/[0.04] border border-white/10 text-xs text-white/60 hover:border-cyan-500/30 hover:text-cyan-300 transition-colors"
          >
            {q}
          </button>
        ))}
      </div>
      {answer && (
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="mt-4 bg-black/30 rounded-lg p-4 border border-cyan-500/10">
          <pre className="text-xs text-white/70 whitespace-pre-wrap font-sans">{answer}</pre>
        </motion.div>
      )}
    </div>
  );
}

export function OrbsPreview() {
  return (
    <div className="relative h-40 rounded-xl overflow-hidden border border-white/5 bg-dark-950">
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-cyan-900/20 via-dark-950 to-dark-950" />
      <div className="absolute -top-6 left-8 w-40 h-40 bg-violet-600/20 rounded-full blur-3xl animate-pulse" />
      <div className="absolute -bottom-8 right-8 w-32 h-32 bg-cyan-500/20 rounded-full blur-3xl animate-pulse delay-1000" />
      <div className="absolute inset-0 flex items-center justify-center">
        <span className="text-2xl font-bold gradient-text">Ambient depth</span>
      </div>
    </div>
  );
}
