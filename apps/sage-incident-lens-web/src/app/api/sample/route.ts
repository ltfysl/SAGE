import { NextResponse } from "next/server";
import { execFileSync } from "child_process";

export const runtime = "nodejs";

const REPO_ROOT = "/Users/latifyesil/Projekte/SAGE";
const SAMPLE_FILE = "data/samples/laravel_realistic_mixed_incident.log";
const PYTHON_BIN = "/Library/Frameworks/Python.framework/Versions/3.11/bin/python3";

export async function GET() {
  try {
    const stdout = execFileSync(
      PYTHON_BIN,
      ["-m", "sage.cli", "logs-analyze", "--file", SAMPLE_FILE, "--format", "json"],
      {
        cwd: REPO_ROOT,
        env: { ...process.env, PYTHONPATH: "src" },
        maxBuffer: 10 * 1024 * 1024,
        timeout: 60_000,
        encoding: "utf-8",
      }
    ).trim();

    if (!stdout) {
      return NextResponse.json({ error: "No output from sample analysis" }, { status: 500 });
    }

    const parsed = JSON.parse(stdout);

    return NextResponse.json({
      uploadId: "sample",
      fileName: SAMPLE_FILE.split("/").pop(),
      ...parsed,
    });
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : String(err);
    console.error("Sample error:", message);
    return NextResponse.json({ error: message }, { status: 500 });
  }
}
