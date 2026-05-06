"use client";

import { useState, useCallback, useRef } from "react";
import { motion } from "framer-motion";
import {
  Upload, FileText, Shield, Activity, AlertTriangle,
  Database, Mail, Clock, Search, Download, ChevronRight,
  CheckCircle, XCircle, ArrowRight, Zap, BarChart3,
  Terminal, AlertCircle, Server, Wifi, HardDrive
} from "lucide-react";

// ── Types ──
interface AnalysisResult {
  summary: {
    first_error: string; last_error: string; duration: string;
    total_events: number; top_exception: string; top_category: string;
    most_affected_component: string; severity: string;
  };
  categories: Array<{
    category: string; count: number; first_seen: string; last_seen: string;
    evidence: Array<{ message: string; span: string }>;
  }>;
  top_exceptions: Array<{
    exception: string; count: number; first_seen: string; last_seen: string;
    category: string; evidence: string[];
  }>;
  timeline: Array<{
    timestamp: string; category: string; message: string;
    evidence: { span: string };
  }>;
  evidence_highlights: Array<{
    category: string; timestamp: string; message: string; file: string; line: number;
  }>;
  likely_impact: Array<{ area: string; detail: string }>;
  checklist: string[];
  meta: { parsed_blocks: number; compiled_operations: number; source_file: string };
}

// ── Severity colors ──
const severityStyles: Record<string, string> = {
  critical: "bg-rose-500/20 text-rose-400 border-rose-500/30",
  high: "bg-amber-500/20 text-amber-400 border-amber-500/30",
  medium: "bg-cyan-500/20 text-cyan-400 border-cyan-500/30",
  low: "bg-emerald-500/20 text-emerald-400 border-emerald-500/30",
};

const categoryIcons: Record<string, any> = {
  DATABASE_ERROR: Database, MAIL_FAILURE: Mail, QUEUE_FAILURE: Clock,
  FAILED_JOB: AlertCircle, HTTP_ERROR: Server, AUTH_ERROR: Shield,
  RECOVERY_EVENT: CheckCircle, EXCEPTION_EVENT: AlertTriangle,
  WARNING_EVENT: Activity, ERROR_EVENT: XCircle,
};

// ── Loading steps ──
const LOADING_STEPS = [
  "Parsing log blocks…",
  "Compiling evidence-bound events…",
  "Building incident timeline…",
  "Detecting affected components…",
  "Generating investigation checklist…",
];

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [uploadId, setUploadId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [loadingStep, setLoadingStep] = useState(0);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [askAnswer, setAskAnswer] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [dragOver, setDragOver] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);

  // ── Upload ──
  const handleFile = useCallback(async (f: File) => {
    setFile(f); setError(null); setResult(null); setAskAnswer(null);
    setLoading(true); setLoadingStep(0);
    const interval = setInterval(() => setLoadingStep(s => Math.min(s + 1, LOADING_STEPS.length - 1)), 800);
    try {
      const form = new FormData(); form.append("file", f);
      const res = await fetch("/api/analyze", { method: "POST", body: form });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Analysis failed");
      setResult(data); setUploadId(data.uploadId || null);
    } catch (e: any) { setError(e.message); }
    finally { clearInterval(interval); setLoading(false); }
  }, []);

  const handleSample = useCallback(async () => {
    setLoading(true); setLoadingStep(0); setError(null);
    const interval = setInterval(() => setLoadingStep(s => Math.min(s + 1, LOADING_STEPS.length - 1)), 800);
    try {
      const res = await fetch("/api/sample");
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Sample analysis failed");
      setResult(data);
    } catch (e: any) { setError(e.message); }
    finally { clearInterval(interval); setLoading(false); }
  }, []);

  // ── Ask ──
  const handleAsk = useCallback(async (question: string) => {
    setAskAnswer(null);
    try {
      const res = await fetch("/api/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ uploadId, question }),
      });
      const data = await res.json();
      setAskAnswer(data.answer || "No answer");
    } catch { setAskAnswer("Failed to get answer"); }
  }, [uploadId]);

  // ── Export ──
  const handleExport = useCallback(() => {
    if (!result) return;
    const md = `# SAGE Incident Lens Report\n\n## Summary\n- First error: ${result.summary.first_error}\n- Last error: ${result.summary.last_error}\n- Total events: ${result.summary.total_events}\n- Top exception: ${result.summary.top_exception}\n- Severity: ${result.summary.severity}\n\n## Event Categories\n${result.categories.map(c => `- ${c.category}: ${c.count}`).join("\n")}\n\n## Top Exceptions\n${result.top_exceptions.map(e => `- ${e.exception}: ${e.count}`).join("\n")}`;
    const blob = new Blob([md], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a"); a.href = url; a.download = "incident-report.md"; a.click();
    URL.revokeObjectURL(url);
  }, [result]);

  const questions = ["top exception", "mail failures", "queue failures", "database errors", "timeline", "impact", "checklist"];

  return (
    <div className="min-h-screen bg-dark-950 text-white font-sans selection:bg-cyan-500/30">
      {/* Animated Background */}
      <div className="fixed inset-0 -z-10">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-cyan-900/20 via-dark-950 to-dark-950" />
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-violet-600/10 rounded-full blur-3xl animate-pulse" />
        <div className="absolute bottom-1/3 right-1/4 w-64 h-64 bg-cyan-500/10 rounded-full blur-3xl animate-pulse delay-1000" />
      </div>

      <main className="max-w-6xl mx-auto px-6 py-12">
        {/* Hero */}
        <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} className="text-center mb-12">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-cyan-500/20 bg-cyan-500/5 text-cyan-400 text-sm mb-6">
            <Shield size={14} /> Local-only • Evidence-bound • No cloud upload
          </div>
          <h1 className="text-5xl font-bold mb-4">
            <span className="bg-gradient-to-r from-cyan-400 via-blue-400 to-violet-400 bg-clip-text text-transparent">
              SAGE Incident Lens
            </span>
          </h1>
          <p className="text-lg text-white/50 max-w-2xl mx-auto">
            Local-first Laravel log incident analysis. Turn messy logs into verified incident timelines with evidence-backed insights.
          </p>
        </motion.div>

          {!result && !loading && (
            <motion.div key="upload" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="max-w-2xl mx-auto space-y-6">
              {/* Dropzone */}
              <div
                onDragOver={e => { e.preventDefault(); setDragOver(true); }}
                onDragLeave={() => setDragOver(false)}
                onDrop={e => { e.preventDefault(); setDragOver(false); const f = e.dataTransfer.files[0]; if (f) handleFile(f); }}
                className={`glass-card border-2 border-dashed rounded-2xl p-12 text-center cursor-pointer transition-all duration-300 ${dragOver ? "border-cyan-400 bg-cyan-500/10 scale-[1.02]" : "border-white/10 hover:border-cyan-500/30 hover:bg-white/[0.02]"}`}
                onClick={() => fileRef.current?.click()}
              >
                <input ref={fileRef} type="file" accept=".log,.txt" className="hidden" onChange={e => { const f = e.target.files?.[0]; if (f) handleFile(f); }} />
                <motion.div animate={dragOver ? { scale: 1.1 } : { scale: 1 }}>
                  <Upload size={48} className="mx-auto mb-4 text-cyan-400" />
                </motion.div>
                <p className="text-lg font-medium mb-2">Drop a Laravel log file here</p>
                <p className="text-sm text-white/40">or click to browse • .log / .txt • Max 50MB</p>
                {file && <p className="mt-4 text-sm text-cyan-400">{file.name} ({(file.size / 1024).toFixed(0)} KB)</p>}
              </div>
              {/* Sample button */}
              <div className="text-center">
                <button onClick={handleSample} className="text-sm text-white/40 hover:text-cyan-400 transition-colors">
                  or analyze the <span className="underline">sample log</span>
                </button>
              </div>
            </motion.div>
          )}

          {/* Loading */}
          {loading && (
            <motion.div key="loading" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="max-w-md mx-auto">
              <div className="glass-card rounded-2xl p-8">
                <motion.div animate={{ rotate: 360 }} transition={{ repeat: Infinity, duration: 1.5, ease: "linear" }} className="w-12 h-12 mx-auto mb-6 border-2 border-cyan-500/30 border-t-cyan-400 rounded-full" />
                <div className="space-y-3">
                  {LOADING_STEPS.map((step, i) => (
                    <motion.div key={step} initial={{ opacity: 0, x: -10 }} animate={{ opacity: i <= loadingStep ? 1 : 0.3, x: 0 }} className="flex items-center gap-3 text-sm">
                      {i < loadingStep ? <CheckCircle size={16} className="text-emerald-400" /> : i === loadingStep ? <div className="w-4 h-4 rounded-full border-2 border-cyan-400 border-t-transparent animate-spin" /> : <div className="w-4 h-4 rounded-full border border-white/10" />}
                      <span className={i <= loadingStep ? "text-white/70" : "text-white/20"}>{step}</span>
                    </motion.div>
                  ))}
                </div>
              </div>
            </motion.div>
          )}

          {/* Error */}
          {error && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="glass-card border-rose-500/30 rounded-xl p-6 max-w-lg mx-auto">
              <div className="flex items-center gap-3 text-rose-400"><AlertTriangle size={20} /><span className="font-medium">Analysis Error</span></div>
              <p className="mt-2 text-sm text-rose-300/70">{error}</p>
            </motion.div>
          )}

          {/* Dashboard */}
          {result && (
            <motion.div key="dashboard" initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-8">
              {/* Summary Cards */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {[
                  { label: "Severity", value: result.summary.severity.toUpperCase(), icon: AlertTriangle, className: severityStyles[result.summary.severity] || severityStyles.medium },
                  { label: "Total Events", value: result.summary.total_events, icon: BarChart3 },
                  { label: "Top Exception", value: result.summary.top_exception?.split("\\").pop() || "N/A", icon: Terminal },
                  { label: "Duration", value: result.summary.duration, icon: Clock },
                ].map((card, i) => (
                  <motion.div key={card.label} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.1 }} className={`glass-card rounded-xl p-5 ${card.className || ""}`}>
                    <div className="flex items-center gap-2 text-white/40 text-xs mb-2"><card.icon size={14} />{card.label}</div>
                    <div className="text-lg font-semibold font-mono">{card.value}</div>
                  </motion.div>
                ))}
              </div>

              {/* Event Categories */}
              <div className="glass-card rounded-2xl p-6">
                <h2 className="text-lg font-semibold mb-4 flex items-center gap-2"><BarChart3 size={18} className="text-cyan-400" />Event Categories</h2>
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
                  {result.categories.map((cat, i) => {
                    const Icon = categoryIcons[cat.category] || Activity;
                    return (
                      <motion.div key={cat.category} initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: i * 0.05 }} className="bg-white/[0.03] rounded-xl p-4 border border-white/5 hover:border-cyan-500/20 transition-colors">
                        <div className="flex items-center gap-2 mb-2"><Icon size={14} className="text-cyan-400" /><span className="text-xs text-white/50">{cat.category}</span></div>
                        <div className="text-2xl font-bold font-mono">{cat.count}</div>
                        <div className="text-[10px] text-white/30 mt-1">{cat.first_seen?.split(" ")[1] || ""}</div>
                      </motion.div>
                    );
                  })}
                </div>
              </div>

              {/* Top Exceptions */}
              <div className="glass-card rounded-2xl p-6">
                <h2 className="text-lg font-semibold mb-4 flex items-center gap-2"><Terminal size={18} className="text-cyan-400" />Top Exceptions</h2>
                <div className="space-y-3">
                  {result.top_exceptions.slice(0, 8).map((exc, i) => (
                    <div key={exc.exception} className="flex items-center gap-4 bg-white/[0.02] rounded-lg p-3 border border-white/5">
                      <span className="text-xs text-white/30 w-6">{i + 1}</span>
                      <div className="flex-1 min-w-0">
                        <div className="text-sm font-mono text-cyan-300 truncate">{exc.exception}</div>
                        <div className="text-[10px] text-white/30">{exc.first_seen}</div>
                      </div>
                      <span className="text-sm font-mono font-bold text-white/60">{exc.count}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Evidence Highlights */}
              <div className="glass-card rounded-2xl p-6">
                <h2 className="text-lg font-semibold mb-4 flex items-center gap-2"><Search size={18} className="text-cyan-400" />Evidence Highlights</h2>
                <div className="space-y-3">
                  {result.evidence_highlights.slice(0, 6).map((h, i) => (
                    <div key={i} className="bg-black/30 rounded-lg p-4 border border-white/5 font-mono text-xs">
                      <div className="flex items-center gap-2 mb-2">
                        <span className="px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-400 text-[10px]">{h.category}</span>
                        <span className="text-white/30">{h.timestamp}</span>
                      </div>
                      <p className="text-white/60 truncate">{h.message}</p>
                      {h.file && <p className="text-white/20 mt-1 text-[10px]">{h.file}:{h.line}</p>}
                    </div>
                  ))}
                </div>
              </div>

              {/* Timeline */}
              <div className="glass-card rounded-2xl p-6">
                <h2 className="text-lg font-semibold mb-4 flex items-center gap-2"><Clock size={18} className="text-cyan-400" />Timeline</h2>
                <div className="relative pl-6 border-l border-white/10 space-y-4">
                  {result.timeline.slice(0, 12).map((e, i) => {
                    const Icon = categoryIcons[e.category] || Activity;
                    return (
                      <motion.div key={i} initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.05 }} className="relative">
                        <div className="absolute -left-[25px] w-2 h-2 rounded-full bg-cyan-500 mt-1.5" />
                        <div className="text-[10px] text-white/30 font-mono">{e.timestamp}</div>
                        <div className="flex items-center gap-2"><Icon size={12} className="text-cyan-400" /><span className="text-xs text-white/60">{e.category}</span></div>
                        <div className="text-xs text-white/40 mt-1 line-clamp-2">{e.message}</div>
                      </motion.div>
                    );
                  })}
                </div>
              </div>

              {/* Likely Impact */}
              {result.likely_impact.length > 0 && (
                <div className="glass-card rounded-2xl p-6">
                  <h2 className="text-lg font-semibold mb-4 flex items-center gap-2"><Zap size={18} className="text-amber-400" />Likely Impact</h2>
                  <div className="grid gap-3">
                    {result.likely_impact.map((imp, i) => (
                      <div key={i} className="bg-amber-500/5 border border-amber-500/10 rounded-lg p-4">
                        <div className="font-medium text-amber-300 text-sm">{imp.area}</div>
                        <div className="text-xs text-white/40 mt-1">{imp.detail}</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Checklist */}
              {result.checklist.length > 0 && (
                <div className="glass-card rounded-2xl p-6">
                  <h2 className="text-lg font-semibold mb-4 flex items-center gap-2"><CheckCircle size={18} className="text-emerald-400" />Investigation Checklist</h2>
                  <div className="space-y-2">
                    {result.checklist.map((item, i) => (
                      <div key={i} className="flex items-start gap-3 text-sm text-white/60">
                        <input type="checkbox" className="mt-0.5 accent-cyan-500" />
                        <span>{item}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Ask SAGE + Export */}
              <div className="flex flex-wrap gap-4 items-start">
                <div className="glass-card rounded-2xl p-6 flex-1 min-w-[300px]">
                  <h2 className="text-lg font-semibold mb-4 flex items-center gap-2"><Search size={18} className="text-violet-400" />Ask SAGE</h2>
                  <div className="flex flex-wrap gap-2">
                    {questions.map(q => (
                      <button key={q} onClick={() => handleAsk(q)} className="px-3 py-1.5 rounded-lg bg-white/[0.04] border border-white/10 text-xs text-white/60 hover:border-cyan-500/30 hover:text-cyan-300 transition-colors">
                        {q}
                      </button>
                    ))}
                  </div>
                  {askAnswer && (
                    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="mt-4 bg-black/30 rounded-lg p-4 border border-cyan-500/10">
                      <pre className="text-xs text-white/70 whitespace-pre-wrap font-sans">{askAnswer}</pre>
                    </motion.div>
                  )}
                </div>

                <button onClick={handleExport} className="px-4 py-2.5 rounded-xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 text-sm hover:bg-cyan-500/20 transition-colors flex items-center gap-2">
                  <Download size={14} />Export Markdown
                </button>
              </div>
            </motion.div>
          )}

        {/* Footer */}
        <div className="mt-16 pt-8 border-t border-white/5 text-center text-xs text-white/20">
          <p>All analysis runs locally. Your logs are processed on this machine and are not uploaded to external services.</p>
        </div>
      </main>
    </div>
  );
}
