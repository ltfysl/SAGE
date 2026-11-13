import { useState, type ReactNode } from "react";
import { motion } from "framer-motion";
import { Check, Copy } from "lucide-react";

export function CopyButton({ text, label = "Copy" }: { text: string; label?: string }) {
  const [copied, setCopied] = useState(false);
  return (
    <button
      onClick={async (e) => {
        e.stopPropagation();
        try {
          await navigator.clipboard.writeText(text);
        } catch {
          const ta = document.createElement("textarea");
          ta.value = text;
          document.body.appendChild(ta);
          ta.select();
          document.execCommand("copy");
          document.body.removeChild(ta);
        }
        setCopied(true);
        setTimeout(() => setCopied(false), 1600);
      }}
      className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-white/[0.04] border border-white/10 text-[11px] text-white/50 hover:border-cyan-500/30 hover:text-cyan-300 transition-colors"
    >
      {copied ? <Check size={12} className="text-emerald-400" /> : <Copy size={12} />}
      {copied ? "Copied" : label}
    </button>
  );
}

export function SectionHead({
  index,
  title,
  children,
}: {
  index: string;
  title: string;
  children?: ReactNode;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 24 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-80px" }}
      transition={{ duration: 0.6 }}
      className="mb-10"
    >
      <div className="text-xs font-mono text-cyan-400/70 mb-3 tracking-widest uppercase">{index}</div>
      <h2 className="text-3xl md:text-4xl font-bold tracking-tight">{title}</h2>
      {children && <p className="mt-3 text-white/40 max-w-2xl">{children}</p>}
    </motion.div>
  );
}

export function DemoCard({
  title,
  description,
  preview,
  code,
  wide,
}: {
  title: string;
  description?: string;
  preview: ReactNode;
  code: string;
  wide?: boolean;
}) {
  const [showCode, setShowCode] = useState(false);
  return (
    <motion.div
      initial={{ opacity: 0, y: 24 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-60px" }}
      transition={{ duration: 0.5 }}
      className={`glass-card rounded-2xl overflow-hidden ${wide ? "md:col-span-2" : ""}`}
    >
      <div className="flex items-center justify-between px-5 py-3 border-b border-white/5">
        <div>
          <div className="text-sm font-semibold">{title}</div>
          {description && <div className="text-[11px] text-white/35 mt-0.5">{description}</div>}
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowCode((s) => !s)}
            className={`px-2.5 py-1 rounded-md text-[11px] border transition-colors ${
              showCode
                ? "bg-cyan-500/10 border-cyan-500/30 text-cyan-300"
                : "bg-white/[0.04] border-white/10 text-white/50 hover:text-cyan-300"
            }`}
          >
            {showCode ? "Preview" : "Code"}
          </button>
          <CopyButton text={code} />
        </div>
      </div>
      {showCode ? (
        <pre className="code-block m-0 rounded-none border-0 text-[11px] leading-relaxed max-h-80 overflow-auto">
          <code>{code}</code>
        </pre>
      ) : (
        <div className="p-6">{preview}</div>
      )}
    </motion.div>
  );
}

export function Swatch({ name, value, className, note }: { name: string; value: string; className?: string; note?: string }) {
  const [copied, setCopied] = useState(false);
  const copy = async () => {
    try {
      await navigator.clipboard.writeText(value);
      setCopied(true);
      setTimeout(() => setCopied(false), 1400);
    } catch {
      /* clipboard unavailable */
    }
  };
  return (
    <button
      onClick={copy}
      className="group text-left glass-card rounded-xl overflow-hidden hover:scale-[1.02] transition-transform"
      title="Click to copy"
    >
      <div className="h-16 w-full relative" style={{ background: value }}>
        <span
          className={`absolute inset-0 flex items-center justify-center text-[10px] font-mono transition-opacity ${
            copied ? "opacity-100" : "opacity-0 group-hover:opacity-70"
          }`}
          style={{ color: value.startsWith("rgba") || value === "#f8fafc" ? "#0a0a0f" : "#fff", mixBlendMode: "difference" }}
        >
          {copied ? "copied!" : "copy"}
        </span>
      </div>
      <div className="px-3 py-2.5">
        <div className="text-xs font-medium text-white/80">{name}</div>
        <div className="text-[10px] font-mono text-white/35 mt-0.5">{value}</div>
        {className && <div className="text-[10px] font-mono text-cyan-400/50 mt-0.5">{className}</div>}
        {note && <div className="text-[10px] text-white/30 mt-1">{note}</div>}
      </div>
    </button>
  );
}
