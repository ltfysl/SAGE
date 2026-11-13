import { useRef } from "react";
import { motion, useScroll, useTransform, type MotionValue } from "framer-motion";
import { AlertTriangle, BarChart3, Clock, Database, Shield, Terminal } from "lucide-react";

/** A shrunken static replica of the SAGE Incident Lens dashboard. */
function MiniDashboard() {
  const cats = [
    { icon: Database, name: "DATABASE_ERROR", n: 37 },
    { icon: AlertTriangle, name: "EXCEPTION_EVENT", n: 54 },
    { icon: Clock, name: "QUEUE_FAILURE", n: 12 },
    { icon: Shield, name: "AUTH_ERROR", n: 8 },
  ];
  return (
    <div className="h-full w-full bg-dark-950 p-5 overflow-hidden">
      <div className="text-center mb-4">
        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full border border-cyan-500/20 bg-cyan-500/5 text-cyan-400 text-[10px]">
          <Shield size={10} /> Local-only • Evidence-bound
        </span>
        <div className="mt-2 text-xl font-bold bg-gradient-to-r from-cyan-400 via-blue-400 to-violet-400 bg-clip-text text-transparent">
          SAGE Incident Lens
        </div>
      </div>
      <div className="grid grid-cols-4 gap-2 mb-3">
        {[
          { label: "Severity", value: "CRITICAL", cls: "bg-rose-500/20 text-rose-400 border-rose-500/30" },
          { label: "Total Events", value: "1,204", cls: "" },
          { label: "Top Exception", value: "QueryException", cls: "" },
          { label: "Duration", value: "6m 42s", cls: "" },
        ].map((c) => (
          <div key={c.label} className={`glass-card rounded-lg p-2.5 ${c.cls}`}>
            <div className="text-[8px] text-white/40 mb-1">{c.label}</div>
            <div className="text-xs font-semibold font-mono truncate">{c.value}</div>
          </div>
        ))}
      </div>
      <div className="glass-card rounded-lg p-3 mb-3">
        <div className="text-[10px] font-semibold mb-2 flex items-center gap-1.5">
          <BarChart3 size={10} className="text-cyan-400" /> Event Categories
        </div>
        <div className="grid grid-cols-4 gap-2">
          {cats.map((c) => (
            <div key={c.name} className="bg-white/[0.03] rounded-md p-2 border border-white/5">
              <div className="flex items-center gap-1 mb-1">
                <c.icon size={9} className="text-cyan-400" />
                <span className="text-[7px] text-white/50 truncate">{c.name}</span>
              </div>
              <div className="text-sm font-bold font-mono">{c.n}</div>
            </div>
          ))}
        </div>
      </div>
      <div className="glass-card rounded-lg p-3">
        <div className="text-[10px] font-semibold mb-2 flex items-center gap-1.5">
          <Terminal size={10} className="text-cyan-400" /> Top Exceptions
        </div>
        {["Illuminate\\Database\\QueryException", "Swift_TransportException", "Symfony\\Component\\HttpKernel"].map((e, i) => (
          <div key={e} className="flex items-center gap-2 bg-white/[0.02] rounded p-1.5 mb-1 border border-white/5">
            <span className="text-[8px] text-white/30 w-3">{i + 1}</span>
            <span className="text-[8px] font-mono text-cyan-300 truncate flex-1">{e}</span>
            <span className="text-[8px] font-mono font-bold text-white/60">{[19, 11, 7][i]}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function BrowserChrome() {
  return (
    <div className="flex items-center gap-2 px-4 h-9 border-b border-white/5 bg-black/40 shrink-0">
      <span className="w-2.5 h-2.5 rounded-full bg-rose-500/70" />
      <span className="w-2.5 h-2.5 rounded-full bg-amber-500/70" />
      <span className="w-2.5 h-2.5 rounded-full bg-emerald-500/70" />
      <div className="ml-3 flex-1 h-5 rounded-md bg-white/[0.04] border border-white/5 flex items-center px-2">
        <span className="text-[9px] font-mono text-white/30">localhost:3000</span>
      </div>
    </div>
  );
}

const CHIPS = [
  { k: "15", v: "components" },
  { k: "23", v: "color tokens" },
  { k: "5", v: "motion curves" },
];

export function Showcase() {
  const ref = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll({ target: ref, offset: ["start start", "end end"] });
  const p = scrollYProgress as MotionValue<number>;

  // Phase 1 (0 → .4): mockup grows from small/tilted to full
  const scale = useTransform(p, [0, 0.4], [0.5, 1]);
  const rotateX = useTransform(p, [0, 0.4], [18, 0]);
  const y = useTransform(p, [0, 0.4], [120, 0]);
  // Phase 2 (.45 → .75): mockup slides left, chips appear
  const mx = useTransform(p, [0.45, 0.75], ["0%", "-26%"]);
  const mScale2 = useTransform(p, [0.45, 0.75], [1, 0.72]);
  const chipOp = useTransform(p, [0.5, 0.62], [0, 1]);
  const chipX = useTransform(p, [0.5, 0.75], [80, 0]);
  // Headline fades out early
  const headOp = useTransform(p, [0, 0.18], [1, 0]);
  const headY = useTransform(p, [0, 0.18], [0, -40]);
  // Outro: dims
  const outOp = useTransform(p, [0.85, 1], [1, 0.25]);

  return (
    <section ref={ref} className="relative" style={{ height: "340vh" }}>
      <div className="sticky top-0 h-screen flex flex-col items-center justify-center overflow-hidden">
        <motion.div style={{ opacity: headOp, y: headY }} className="absolute text-center z-10 px-6">
          <div className="text-xs font-mono text-cyan-400/70 tracking-[0.3em] uppercase mb-4">01 — The product</div>
          <h2 className="text-4xl md:text-6xl font-bold tracking-tight">
            Every pixel comes from <span className="gradient-text">a real app</span>
          </h2>
          <p className="mt-4 text-white/40 max-w-xl mx-auto text-sm md:text-base">
            Prism refracts the design system behind SAGE Incident Lens — the exact components, tokens and motion shipped in the repo.
          </p>
        </motion.div>

        <motion.div style={{ scale: mScale2, x: mx }} className="w-[min(880px,92vw)]">
        <motion.div
          style={{ scale, rotateX, y, opacity: outOp, transformPerspective: 1200 }}
          className="rounded-2xl glass-card glass-card-glow overflow-hidden flex flex-col h-[520px] max-h-[70vh] shadow-2xl shadow-cyan-500/10"
        >
          <BrowserChrome />
          <div className="flex-1 min-h-0">
            <MiniDashboard />
          </div>
        </motion.div>
        </motion.div>

        <motion.div style={{ opacity: chipOp, x: chipX }} className="absolute right-[6%] top-1/2 -translate-y-1/2 space-y-4 hidden md:block">
          {CHIPS.map((c, i) => (
            <motion.div
              key={c.v}
              style={{ opacity: useTransform(p, [0.5 + i * 0.06, 0.62 + i * 0.06], [0, 1]), y: useTransform(p, [0.5 + i * 0.06, 0.62 + i * 0.06], [30, 0]) }}
              className="glass-card rounded-xl px-6 py-4 text-right"
            >
              <div className="text-3xl font-bold font-mono gradient-text-cyan">{c.k}</div>
              <div className="text-[11px] text-white/40 uppercase tracking-widest">{c.v}</div>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}

const MARQUEE_ITEMS = [
  "#22d3ee cyan", "#8b5cf6 violet", "#f43f5e rose", "#10b981 emerald", "#f59e0b amber", "#3b82f6 blue",
  "glass-card", "dropzone-glow", "timeline-line", "pulse-glow", "shimmer", "slide-up",
  "Inter 300–800", "JetBrains Mono", "cat-critical", "sev-medium",
];

export function SpecMarquee() {
  const ref = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll({ target: ref, offset: ["start end", "end start"] });
  const x = useTransform(scrollYProgress, [0, 1], ["4%", "-42%"]);
  return (
    <div ref={ref} className="py-16 overflow-hidden border-y border-white/5 bg-black/20">
      <motion.div style={{ x }} className="flex whitespace-nowrap gap-12 w-max">
        {[...MARQUEE_ITEMS, ...MARQUEE_ITEMS].map((item, i) => (
          <span key={i} className="text-sm font-mono text-white/25 flex items-center gap-12">
            {item}
            <span className="w-1.5 h-1.5 rounded-full bg-cyan-500/40" />
          </span>
        ))}
      </motion.div>
    </div>
  );
}
