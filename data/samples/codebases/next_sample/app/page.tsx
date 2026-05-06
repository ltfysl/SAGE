export default function Home() {
  async function analyze(file: File) {
    const form = new FormData(); form.append("file", file);
    const res = await fetch("/api/analyze", { method: "POST", body: form });
    return res.json();
  }
  return <div>SAGE Incident Lens</div>;
}
