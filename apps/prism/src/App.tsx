import { useState, type ReactNode } from "react";
import { motion } from "framer-motion";
import { ChevronDown, GitBranch, Moon, Sun, Search } from "lucide-react";
import { Showcase, SpecMarquee } from "./showcase";
import { CopyButton, DemoCard, LibCard, SectionHead, Swatch } from "./ui";
import { library, libraryCount } from "./lib";
import { colorGroups, gradients, typeScale, monoScale, motionTokens, snippets } from "./data";
import {
  AskPreview, BadgesPreview, ButtonsPreview, CategoryTilePreview, ChecklistPreview,
  DropzonePreview, EvidencePreview, GlassCardPreview, ImpactPreview, LoadingStepsPreview,
  OrbsPreview, PillBadgePreview, StatCardPreview, TimelinePreview, ErrorBannerPreview,
} from "./demos";

const previews: Record<string, ReactNode> = {
  "glass-card": <GlassCardPreview />,
  "pill-badge": <PillBadgePreview />,
  buttons: <ButtonsPreview />,
  dropzone: <DropzonePreview />,
  "loading-steps": <LoadingStepsPreview />,
  "stat-card": <StatCardPreview />,
  "category-tile": <CategoryTilePreview />,
  "severity-badge": <BadgesPreview />,
  timeline: <TimelinePreview />,
  "evidence-card": <EvidencePreview />,
  "impact-card": <ImpactPreview />,
  "error-banner": <ErrorBannerPreview />,
  checklist: <ChecklistPreview />,
  "ask-panel": <AskPreview />,
  orbs: <OrbsPreview />,
};

const WIDE = new Set(["glass-card", "loading-steps", "stat-card", "timeline", "severity-badge"]);

function ThemeToggle() {
  const [light, setLight] = useState(() => document.documentElement.classList.contains("light"));
  return (
    <button
      onClick={() => {
        const next = !light;
        setLight(next);
        document.documentElement.classList.toggle("light", next);
      }}
      title="Toggle light / dark"
      className="p-1.5 rounded-full text-ink/40 hover:text-cyan-300 hover:bg-ink/5 transition-colors"
    >
      {light ? <Moon size={13} /> : <Sun size={13} />}
    </button>
  );
}

function Nav() {
  const links = [
    ["Colors", "#colors"],
    ["Type", "#type"],
    ["Components", "#components"],
    ["Library", "#library"],
    ["Motion", "#motion"],
  ] as const;
  return (
    <header className="fixed top-0 inset-x-0 z-50">
      <div className="max-w-6xl mx-auto px-6 pt-4">
        <div className="glass-card rounded-full px-5 py-2.5 flex items-center gap-6">
          <a href="#top" className="font-bold tracking-tight text-sm">
            <span className="gradient-text">Prism</span>
          </a>
          <nav className="hidden sm:flex items-center gap-5 text-xs text-ink/50">
            {links.map(([label, href]) => (
              <a key={href} href={href} className="hover:text-cyan-300 transition-colors">{label}</a>
            ))}
          </nav>
          <div className="ml-auto flex items-center gap-3">
            <ThemeToggle />
            <a
              href="https://github.com/ltfysl/SAGE"
              className="inline-flex items-center gap-1.5 text-[11px] font-mono text-ink/30 hover:text-cyan-300 transition-colors"
            >
              <GitBranch size={11} /> ltfysl/SAGE
            </a>
          </div>
        </div>
      </div>
    </header>
  );
}

function Hero() {
  return (
    <section id="top" className="relative min-h-screen flex items-center justify-center overflow-hidden">
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-cyan-900/20 via-bgc to-bgc" />
      <div className="orb orb-cyan -top-20 -left-20 animate-pulse" />
      <div className="orb orb-violet top-1/3 -right-24 animate-pulse" />
      <div className="relative text-center px-6">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.7 }}>
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-cyan-500/20 bg-cyan-500/5 text-cyan-400 text-sm mb-8">
            Extracted live from the SAGE design system
          </div>
        </motion.div>
        <motion.h1
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.1 }}
          className="text-6xl md:text-8xl font-bold tracking-tight"
        >
          <span className="gradient-text">Prism</span>
        </motion.h1>
        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.25 }}
          className="mt-6 text-lg md:text-xl text-ink/50 max-w-2xl mx-auto"
        >
          One design system, refracted into {libraryCount}+ components, every token and motion curve — in light and dark, straight from{" "}
          <span className="font-mono text-ink/70">apps/sage-incident-lens-web</span>.
        </motion.p>
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.9 }}
          className="mt-14 flex flex-col items-center gap-2 text-ink/25"
        >
          <span className="text-[10px] font-mono uppercase tracking-[0.3em]">Scroll</span>
          <motion.div animate={{ y: [0, 8, 0] }} transition={{ repeat: Infinity, duration: 1.6 }}>
            <ChevronDown size={18} />
          </motion.div>
        </motion.div>
      </div>
    </section>
  );
}

function Colors() {
  return (
    <section id="colors" className="max-w-6xl mx-auto px-6 py-28">
      <SectionHead index="02 — Color" title="Color tokens">
        Every swatch copies its value on click. Surfaces and glass tokens come from <span className="font-mono">globals.css</span>; accents from <span className="font-mono">tailwind.config.ts</span>.
      </SectionHead>
      <div className="space-y-14">
        {colorGroups.map((g) => (
          <div key={g.title}>
            <div className="mb-4">
              <h3 className="text-sm font-semibold text-ink/80">{g.title}</h3>
              <p className="text-xs text-ink/35 mt-1">{g.description}</p>
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
              {g.tokens.map((t) => (
                <Swatch key={t.name} name={t.name} value={t.value} className={t.className} note={t.note} />
              ))}
            </div>
          </div>
        ))}
      </div>

      <div className="mt-16">
        <h3 className="text-sm font-semibold text-ink/80 mb-4">Gradients</h3>
        <div className="grid md:grid-cols-3 gap-4">
          {gradients.map((g) => (
            <div key={g.name} className="glass-card rounded-xl p-5">
              <div className="h-10 rounded-lg mb-3 border border-ink/5" style={{ background: g.value }} />
              <div className="flex items-center justify-between gap-2">
                <span className="text-xs font-mono text-cyan-300">.{g.name}</span>
                <CopyButton text={g.value} />
              </div>
              <p className="text-[11px] text-ink/35 mt-2">{g.usage}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function TypeSection() {
  return (
    <section id="type" className="max-w-6xl mx-auto px-6 py-28">
      <SectionHead index="03 — Typography" title="Type tokens">
        Two families: <span className="font-semibold text-ink/70">Inter</span> for UI and{" "}
        <span className="font-semibold text-ink/70">JetBrains Mono</span> for stats, exceptions and code.
      </SectionHead>
      <div className="grid md:grid-cols-2 gap-4">
        {[
          { title: "Inter — interface", rows: typeScale },
          { title: "JetBrains Mono — data", rows: monoScale },
        ].map((col) => (
          <div key={col.title} className="glass-card rounded-2xl p-6">
            <div className="text-xs font-mono text-ink/40 mb-5">{col.title}</div>
            <div className="space-y-5">
              {col.rows.map((t) => (
                <div key={t.name} className="flex items-baseline justify-between gap-4 border-b border-ink/5 pb-4 last:border-0 last:pb-0">
                  <div className="min-w-0">
                    <div className={t.sampleClass + " truncate"}>{t.sample}</div>
                    <div className="text-[10px] font-mono text-ink/30 mt-1">{t.spec}</div>
                  </div>
                  <CopyButton text={t.classes} label={t.classes} />
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}

function Components() {
  return (
    <section id="components" className="max-w-6xl mx-auto px-6 py-28">
      <SectionHead index="04 — Components" title="Components">
        Live previews of the components that make up SAGE Incident Lens. Toggle <span className="font-mono">Code</span> to read the real snippet, or copy it straight out.
      </SectionHead>
      <div className="grid md:grid-cols-2 gap-4">
        {snippets.map((s) => (
          <DemoCard
            key={s.id}
            title={s.title}
            description={s.description}
            code={s.code}
            preview={previews[s.id]}
            wide={WIDE.has(s.id)}
          />
        ))}
      </div>
    </section>
  );
}

function LibrarySection() {
  const [query, setQuery] = useState("");
  const [active, setActive] = useState<string | null>(null);
  const q = query.trim().toLowerCase();
  const groups = library
    .filter((g) => !active || g.id === active)
    .map((g) => ({
      ...g,
      items: q ? g.items.filter((i) => i.name.toLowerCase().includes(q)) : g.items,
    }))
    .filter((g) => g.items.length > 0);
  return (
    <section id="library" className="max-w-6xl mx-auto px-6 py-28">
      <SectionHead index="05 — Library" title={`${libraryCount} components`}>
        The full matrix — every variant, size and state, rendered in both themes. Toggle <span className="font-mono">{"</>"}</span> for the snippet, copy it straight out.
      </SectionHead>
      <div className="sticky top-20 z-30 glass-card rounded-2xl px-4 py-3 mb-10 flex flex-wrap items-center gap-2">
        <div className="relative">
          <Search size={13} className="absolute left-2.5 top-1/2 -translate-y-1/2 text-ink/30" />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Filter components…"
            className="w-44 pl-8 pr-3 py-1.5 rounded-lg bg-ink/5 border border-ink/10 text-xs text-ink placeholder:text-ink/30 outline-none focus:border-cyan-500/50"
          />
        </div>
        <button
          onClick={() => setActive(null)}
          className={`px-2.5 py-1.5 rounded-lg text-[11px] transition-colors ${!active ? "bg-cyan-500/15 text-cyan-300 border border-cyan-500/30" : "text-ink/50 hover:text-ink/80"}`}
        >
          All
        </button>
        {library.map((g) => (
          <button
            key={g.id}
            onClick={() => setActive(active === g.id ? null : g.id)}
            className={`px-2.5 py-1.5 rounded-lg text-[11px] transition-colors ${active === g.id ? "bg-cyan-500/15 text-cyan-300 border border-cyan-500/30" : "text-ink/50 hover:text-ink/80"}`}
          >
            {g.title}
          </button>
        ))}
      </div>
      <div className="space-y-14">
        {groups.map((g) => (
          <div key={g.id}>
            <div className="flex items-baseline gap-3 mb-4">
              <h3 className="text-sm font-semibold text-ink/80">{g.title}</h3>
              <span className="text-[10px] font-mono text-ink/30">{g.items.length}</span>
            </div>
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
              {g.items.map((item) => (
                <LibCard key={item.name} name={item.name} code={item.code}>
                  {item.el}
                </LibCard>
              ))}
            </div>
          </div>
        ))}
        {groups.length === 0 && (
          <p className="text-sm text-ink/40 text-center py-16">No components match “{query}”.</p>
        )}
      </div>
    </section>
  );
}

function MotionSection() {
  const demoFor: Record<string, ReactNode> = {
    "pulse-glow": <div className="w-16 h-16 rounded-2xl bg-cyan-500/20 animate-pulse-glow" />,
    "slide-up": <div className="glass-card rounded-xl px-6 py-3 text-sm animate-slide-up">Slides up on mount</div>,
    "fade-in": <div className="glass-card rounded-xl px-6 py-3 text-sm animate-fade-in">Fades in</div>,
    shimmer: <div className="w-40 h-10 rounded-lg animate-shimmer border border-ink/5" />,
    "pulse-dot": (
      <div className="flex items-center gap-1.5">
        {[0, 1, 2].map((i) => (
          <span key={i} className="pulse-dot w-2.5 h-2.5 rounded-full bg-cyan-400 inline-block" />
        ))}
      </div>
    ),
  };
  return (
    <section id="motion" className="max-w-6xl mx-auto px-6 py-28">
      <SectionHead index="06 — Motion" title="Motion & effects">
        The five animation tokens in <span className="font-mono">tailwind.config.ts</span> and <span className="font-mono">globals.css</span>, running live.
      </SectionHead>
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
        {motionTokens.map((m) => (
          <motion.div
            key={m.name}
            initial={{ opacity: 0, y: 24 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-60px" }}
            className="glass-card rounded-2xl p-5"
          >
            <div className="flex items-center justify-between mb-4">
              <span className="text-xs font-mono text-cyan-300">.{m.name}</span>
              <CopyButton text={m.css} />
            </div>
            <div className="h-24 rounded-lg bg-black/30 border border-ink/5 flex items-center justify-center mb-3 overflow-hidden">
              {demoFor[m.name]}
            </div>
            <p className="text-[11px] text-ink/35">{m.usage}</p>
          </motion.div>
        ))}
      </div>
    </section>
  );
}

function Footer() {
  return (
    <footer className="border-t border-ink/5">
      <div className="max-w-6xl mx-auto px-6 py-12 flex flex-col md:flex-row items-center justify-between gap-4 text-xs text-ink/25">
        <div>
          <span className="gradient-text font-bold">Prism</span> — a gallery of the SAGE design system.
        </div>
        <div className="font-mono">
          source: <a href="https://github.com/ltfysl/SAGE/tree/main/apps/sage-incident-lens-web" className="hover:text-cyan-300 transition-colors">ltfysl/SAGE · apps/sage-incident-lens-web</a>
        </div>
        <a
          href="https://app.devin.ai/sessions/2e5d70db6daa4c88a3ad474fbc320297"
          className="hover:text-cyan-300 transition-colors"
        >
          Request changes
        </a>
      </div>
    </footer>
  );
}

export default function App() {
  return (
    <div className="min-h-screen bg-bgc text-ink font-sans">
      <Nav />
      <Hero />
      <Showcase />
      <SpecMarquee />
      <Colors />
      <TypeSection />
      <Components />
      <LibrarySection />
      <MotionSection />
      <Footer />
    </div>
  );
}
