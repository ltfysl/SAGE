// Tokens extracted from SAGE Incident Lens:
//   apps/sage-incident-lens-web/tailwind.config.ts
//   apps/sage-incident-lens-web/src/app/globals.css

export interface ColorToken {
  name: string;
  value: string; // hex or rgba
  className?: string; // tailwind class or CSS var
  note?: string;
}

export interface ColorGroup {
  title: string;
  description: string;
  tokens: ColorToken[];
}

export const colorGroups: ColorGroup[] = [
  {
    title: "Surfaces",
    description: "Base dark palette — bg, elevated surfaces, and the light-foreground endpoint.",
    tokens: [
      { name: "dark-950", value: "#050508", className: "bg-dark-950", note: "app background" },
      { name: "dark-900", value: "#0a0a0f", className: "bg-dark-900", note: "raised surface" },
      { name: "dark-50", value: "#f8fafc", className: "text-dark-50", note: "light foreground" },
      { name: "glass-bg", value: "rgba(15,15,25,0.6)", className: "--glass-bg", note: "glass card fill" },
      { name: "glass-border", value: "rgba(255,255,255,0.06)", className: "--glass-border", note: "glass card edge" },
      { name: "glass-hover", value: "rgba(255,255,255,0.04)", className: "--glass-hover", note: "glass hover tint" },
    ],
  },
  {
    title: "Accent",
    description: "The six accent hues from tailwind.config.ts. Cyan is the primary; blue→violet→rose form the brand gradient.",
    tokens: [
      { name: "accent-cyan", value: "#22d3ee", className: "text-accent-cyan" },
      { name: "accent-blue", value: "#3b82f6", className: "text-accent-blue" },
      { name: "accent-violet", value: "#8b5cf6", className: "text-accent-violet" },
      { name: "accent-emerald", value: "#10b981", className: "text-accent-emerald" },
      { name: "accent-rose", value: "#f43f5e", className: "text-accent-rose" },
      { name: "accent-amber", value: "#f59e0b", className: "text-accent-amber" },
    ],
  },
  {
    title: "Log categories",
    description: "Semantic category colors (--cat-*) used by category badges, icons and the timeline.",
    tokens: [
      { name: "cat-critical", value: "#f43f5e", className: ".cat-critical" },
      { name: "cat-error", value: "#ef4444", className: ".cat-error" },
      { name: "cat-warning", value: "#f59e0b", className: ".cat-warning" },
      { name: "cat-info", value: "#3b82f6", className: ".cat-info" },
      { name: "cat-debug", value: "#8b5cf6", className: ".cat-debug" },
      { name: "cat-success", value: "#10b981", className: ".cat-success" },
      { name: "cat-unknown", value: "#6b7280", className: ".cat-unknown" },
    ],
  },
  {
    title: "Severity",
    description: "Foreground colors (.sev-*) for severity labels and summary values.",
    tokens: [
      { name: "sev-critical", value: "#f87171", className: ".sev-critical" },
      { name: "sev-high", value: "#fbbf24", className: ".sev-high" },
      { name: "sev-medium", value: "#60a5fa", className: ".sev-medium" },
      { name: "sev-low", value: "#34d399", className: ".sev-low" },
    ],
  },
];

export const gradients = [
  {
    name: "gradient-text",
    value: "linear-gradient(135deg, #22d3ee 0%, #8b5cf6 50%, #f43f5e 100%)",
    usage: "Brand wordmark / hero title — cyan → violet → rose at 135deg, clipped to text.",
  },
  {
    name: "gradient-text-cyan",
    value: "linear-gradient(135deg, #22d3ee, #3b82f6)",
    usage: "Secondary gradient — cyan → blue, for sub-headlines and accents.",
  },
  {
    name: "timeline-line",
    value: "linear-gradient(to bottom, rgba(34,211,238,0.6), rgba(139,92,246,0.6), rgba(244,63,94,0.3))",
    usage: "Vertical rail behind timeline entries — brand gradient fading downward.",
  },
];

export interface TypeToken {
  name: string;
  spec: string;
  classes: string;
  sample: string;
  sampleClass: string;
}

export const typeScale: TypeToken[] = [
  { name: "Display", spec: "Inter · 700 · 48px", classes: "text-5xl font-bold", sample: "SAGE Incident Lens", sampleClass: "text-4xl md:text-5xl font-bold" },
  { name: "Headline", spec: "Inter · 600 · 18px", classes: "text-lg font-semibold", sample: "Event Categories", sampleClass: "text-lg font-semibold" },
  { name: "Body", spec: "Inter · 400 · 16px", classes: "text-base", sample: "Turn messy logs into verified incident timelines.", sampleClass: "text-base text-white/70" },
  { name: "Label", spec: "Inter · 500 · 12px", classes: "text-xs font-medium", sample: "Local-only · Evidence-bound", sampleClass: "text-xs font-medium" },
  { name: "Caption", spec: "Inter · 400 · 10px", classes: "text-[10px]", sample: "2024-05-07 14:22:31", sampleClass: "text-[10px] text-white/40" },
];

export const monoScale: TypeToken[] = [
  { name: "Mono stat", spec: "JetBrains Mono · 600 · 24px", classes: "text-2xl font-bold font-mono", sample: "1,204", sampleClass: "text-2xl font-bold font-mono" },
  { name: "Mono body", spec: "JetBrains Mono · 400 · 13px", classes: "font-mono text-[13px]", sample: 'Illuminate\\Database\\QueryException', sampleClass: "font-mono text-[13px] text-cyan-300" },
  { name: "Code block", spec: "JetBrains Mono · 400 · 12.8px", classes: ".code-block", sample: '[2024-05-07 14:22:31] production.ERROR: SQLSTATE[42S02]', sampleClass: "font-mono text-xs text-white/60" },
];

export interface MotionToken {
  name: string;
  css: string;
  usage: string;
}

export const motionTokens: MotionToken[] = [
  {
    name: "pulse-glow",
    css: `animation: pulseGlow 2s ease-in-out infinite;
@keyframes pulseGlow {
  0%, 100% { box-shadow: 0 0 20px rgba(34,211,238,0.3); }
  50%      { box-shadow: 0 0 40px rgba(34,211,238,0.6); }
}`,
    usage: "Ambient cyan glow on primary elements — e.g. an active analysis card.",
  },
  {
    name: "slide-up",
    css: `animation: slideUp 0.5s ease-out;
@keyframes slideUp {
  from { opacity: 0; transform: translateY(20px); }
  to   { opacity: 1; transform: translateY(0); }
}`,
    usage: "Entrance for cards, banners and dashboard sections.",
  },
  {
    name: "fade-in",
    css: `animation: fadeIn 0.5s ease-out forwards;
@keyframes fadeIn {
  from { opacity: 0; }
  to   { opacity: 1; }
}`,
    usage: "Soft mount for overlays and answer panels.",
  },
  {
    name: "shimmer",
    css: `background: linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.05) 50%, transparent 100%);
background-size: 200% 100%;
animation: shimmer 2s infinite;
@keyframes shimmer {
  0%   { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}`,
    usage: "Skeleton loading on rows and cards while analysis runs.",
  },
  {
    name: "pulse-dot",
    css: `animation: pulse-dot 1.4s ease-in-out infinite;
@keyframes pulse-dot {
  0%, 100% { opacity: 0.3; transform: scale(0.8); }
  50%      { opacity: 1;   transform: scale(1.2); }
}
.pulse-dot:nth-child(2) { animation-delay: 0.2s; }
.pulse-dot:nth-child(3) { animation-delay: 0.4s; }`,
    usage: "Three-dot typing/processing indicator, staggered by nth-child delay.",
  },
];

// ── Component snippets (adapted from page.tsx) ──

export interface Snippet {
  id: string;
  title: string;
  description: string;
  code: string;
}

export const snippets: Snippet[] = [
  {
    id: "glass-card",
    title: "Glass card",
    description: "The surface every panel is built on. Add .glass-card-glow for an ambient accent.",
    code: `<!-- index.css -->
.glass-card {
  background: var(--glass-bg);              /* rgba(15,15,25,0.6) */
  backdrop-filter: blur(20px);
  border: 1px solid var(--glass-border);    /* rgba(255,255,255,0.06) */
  border-radius: 16px;
  transition: all 0.3s ease;
}
.glass-card:hover {
  border-color: rgba(255,255,255,0.12);
  background: rgba(20,20,35,0.65);
}
.glass-card-glow {
  box-shadow: 0 0 30px rgba(34,211,238,0.08),
              0 0 60px rgba(59,130,246,0.04);
}

<!-- usage -->
<div class="glass-card glass-card-glow rounded-2xl p-6">…</div>`,
  },
  {
    id: "pill-badge",
    title: "Status pill",
    description: "Hero eyebrow — a bordered pill with icon, used for trust signals.",
    code: `<div className="inline-flex items-center gap-2 px-4 py-1.5
  rounded-full border border-cyan-500/20 bg-cyan-500/5
  text-cyan-400 text-sm">
  <Shield size={14} /> Local-only • Evidence-bound • No cloud upload
</div>`,
  },
  {
    id: "buttons",
    title: "Buttons",
    description: "Accent action, ghost chip and inline text link — the only three button shapes used.",
    code: `{/* Accent action */}
<button className="px-4 py-2.5 rounded-xl bg-cyan-500/10
  border border-cyan-500/20 text-cyan-400 text-sm
  hover:bg-cyan-500/20 transition-colors
  flex items-center gap-2">
  <Download size={14} /> Export Markdown
</button>

{/* Ghost chip (Ask SAGE) */}
<button className="px-3 py-1.5 rounded-lg bg-white/[0.04]
  border border-white/10 text-xs text-white/60
  hover:border-cyan-500/30 hover:text-cyan-300 transition-colors">
  top exception
</button>

{/* Inline link */}
<button className="text-sm text-white/40 hover:text-cyan-400 transition-colors">
  or analyze the <span className="underline">sample log</span>
</button>`,
  },
  {
    id: "dropzone",
    title: "Dropzone",
    description: "Dashed glass panel that scales and tints on drag-over.",
    code: `<div
  onDragOver={e => { e.preventDefault(); setDragOver(true); }}
  onDragLeave={() => setDragOver(false)}
  onDrop={onDrop}
  onClick={() => fileRef.current?.click()}
  className={\`glass-card border-2 border-dashed rounded-2xl p-12
    text-center cursor-pointer transition-all duration-300
    \${dragOver
      ? "border-cyan-400 bg-cyan-500/10 scale-[1.02]"
      : "border-white/10 hover:border-cyan-500/30 hover:bg-white/[0.02]"}\`}>
  <Upload size={48} className="mx-auto mb-4 text-cyan-400" />
  <p className="text-lg font-medium mb-2">Drop a Laravel log file here</p>
  <p className="text-sm text-white/40">or click to browse • .log / .txt</p>
</div>`,
  },
  {
    id: "loading-steps",
    title: "Loading steps",
    description: "Spinner ring plus a stepped checklist that ticks through pipeline phases.",
    code: `<motion.div
  animate={{ rotate: 360 }}
  transition={{ repeat: Infinity, duration: 1.5, ease: "linear" }}
  className="w-12 h-12 border-2 border-cyan-500/30
    border-t-cyan-400 rounded-full" />

{LOADING_STEPS.map((step, i) => (
  <div className="flex items-center gap-3 text-sm">
    {i < loadingStep
      ? <CheckCircle size={16} className="text-emerald-400" />
      : i === loadingStep
        ? <div className="w-4 h-4 rounded-full border-2
            border-cyan-400 border-t-transparent animate-spin" />
        : <div className="w-4 h-4 rounded-full border border-white/10" />}
    <span className={i <= loadingStep ? "text-white/70" : "text-white/20"}>
      {step}
    </span>
  </div>
))}`,
  },
  {
    id: "stat-card",
    title: "Stat card",
    description: "Summary metric tile — icon + label over a mono value; severity variant picks up sev colors.",
    code: `<div className="glass-card rounded-xl p-5">
  <div className="flex items-center gap-2 text-white/40 text-xs mb-2">
    <BarChart3 size={14} /> Total Events
  </div>
  <div className="text-lg font-semibold font-mono">1,204</div>
</div>

{/* severity variant */}
<div className="glass-card rounded-xl p-5
  bg-rose-500/20 text-rose-400 border-rose-500/30">
  <div className="flex items-center gap-2 text-xs mb-2">
    <AlertTriangle size={14} /> Severity
  </div>
  <div className="text-lg font-semibold font-mono">CRITICAL</div>
</div>`,
  },
  {
    id: "category-tile",
    title: "Category tile",
    description: "Compact icon + count tile from the Event Categories grid.",
    code: `<div className="bg-white/[0.03] rounded-xl p-4 border border-white/5
  hover:border-cyan-500/20 transition-colors">
  <div className="flex items-center gap-2 mb-2">
    <Database size={14} className="text-cyan-400" />
    <span className="text-xs text-white/50">DATABASE_ERROR</span>
  </div>
  <div className="text-2xl font-bold font-mono">37</div>
  <div className="text-[10px] text-white/30 mt-1">14:22:31</div>
</div>`,
  },
  {
    id: "severity-badge",
    title: "Severity & category badges",
    description: "severityStyles map from page.tsx and the .cat-* badge classes from globals.css.",
    code: `const severityStyles = {
  critical: "bg-rose-500/20 text-rose-400 border-rose-500/30",
  high:     "bg-amber-500/20 text-amber-400 border-amber-500/30",
  medium:   "bg-cyan-500/20 text-cyan-400 border-cyan-500/30",
  low:      "bg-emerald-500/20 text-emerald-400 border-emerald-500/30",
};

/* category badge (globals.css) */
.cat-critical {
  background: rgba(244,63,94,0.15);
  color: #f87171;
  border: 1px solid rgba(244,63,94,0.3);
}

<span className="badge cat-critical">CRITICAL</span>`,
  },
  {
    id: "timeline",
    title: "Timeline",
    description: "Gradient rail with dots — each entry fades in from the left with a stagger.",
    code: `<div className="relative pl-6 border-l border-white/10 space-y-4">
  {timeline.map((e, i) => (
    <motion.div
      initial={{ opacity: 0, x: -10 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: i * 0.05 }}
      className="relative">
      <div className="absolute -left-[25px] w-2 h-2
        rounded-full bg-cyan-500 mt-1.5" />
      <div className="text-[10px] text-white/30 font-mono">{e.timestamp}</div>
      <div className="text-xs text-white/40 line-clamp-2">{e.message}</div>
    </motion.div>
  ))}
</div>`,
  },
  {
    id: "evidence-card",
    title: "Evidence highlight",
    description: "Mono evidence card — category chip, timestamp, truncated message, file:line source.",
    code: `<div className="bg-black/30 rounded-lg p-4 border border-white/5
  font-mono text-xs">
  <div className="flex items-center gap-2 mb-2">
    <span className="px-2 py-0.5 rounded bg-cyan-500/10
      text-cyan-400 text-[10px]">EXCEPTION_EVENT</span>
    <span className="text-white/30">14:22:31</span>
  </div>
  <p className="text-white/60 truncate">{message}</p>
  <p className="text-white/20 mt-1 text-[10px]">{file}:{line}</p>
</div>`,
  },
  {
    id: "impact-card",
    title: "Impact alert",
    description: "Amber-tinted alert row used for likely-impact findings.",
    code: `<div className="bg-amber-500/5 border border-amber-500/10
  rounded-lg p-4">
  <div className="font-medium text-amber-300 text-sm">{imp.area}</div>
  <div className="text-xs text-white/40 mt-1">{imp.detail}</div>
</div>`,
  },
  {
    id: "error-banner",
    title: "Error banner",
    description: "Rose-bordered glass banner surfaced when analysis fails.",
    code: `<div className="glass-card border-rose-500/30 rounded-xl p-6">
  <div className="flex items-center gap-3 text-rose-400">
    <AlertTriangle size={20} />
    <span className="font-medium">Analysis Error</span>
  </div>
  <p className="mt-2 text-sm text-rose-300/70">{error}</p>
</div>`,
  },
  {
    id: "checklist",
    title: "Investigation checklist",
    description: "Cyan-accented checkboxes over muted text.",
    code: `{checklist.map((item) => (
  <div className="flex items-start gap-3 text-sm text-white/60">
    <input type="checkbox" className="mt-0.5 accent-cyan-500" />
    <span>{item}</span>
  </div>
))}`,
  },
  {
    id: "ask-panel",
    title: "Ask chips + answer",
    description: "Suggested-question chips that slide an answer panel in on selection.",
    code: `<div className="flex flex-wrap gap-2">
  {questions.map(q => (
    <button key={q} onClick={() => handleAsk(q)}
      className="px-3 py-1.5 rounded-lg bg-white/[0.04]
        border border-white/10 text-xs text-white/60
        hover:border-cyan-500/30 hover:text-cyan-300
        transition-colors">
      {q}
    </button>
  ))}
</div>
{askAnswer && (
  <motion.div
    initial={{ opacity: 0, y: 10 }}
    animate={{ opacity: 1, y: 0 }}
    className="mt-4 bg-black/30 rounded-lg p-4
      border border-cyan-500/10">
    <pre className="text-xs text-white/70
      whitespace-pre-wrap font-sans">{askAnswer}</pre>
  </motion.div>
)}`,
  },
  {
    id: "orbs",
    title: "Background orbs",
    description: "Blurred accent orbs + grid mask that give the app its depth.",
    code: `<div className="fixed inset-0 -z-10">
  <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,
    _var(--tw-gradient-stops))]
    from-cyan-900/20 via-dark-950 to-dark-950" />
  <div className="absolute top-1/4 left-1/4 w-96 h-96
    bg-violet-600/10 rounded-full blur-3xl animate-pulse" />
  <div className="absolute bottom-1/3 right-1/4 w-64 h-64
    bg-cyan-500/10 rounded-full blur-3xl animate-pulse delay-1000" />
</div>`,
  },
];
