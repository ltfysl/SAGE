import { NextRequest, NextResponse } from "next/server";
import { execFileSync } from "child_process";
import { mkdirSync, existsSync, writeFileSync } from "fs";
import { join } from "path";
import { randomUUID } from "crypto";
import { registerUpload } from "../ask/route";

export const runtime = "nodejs";

const REPO_ROOT = "/Users/latifyesil/Projekte/SAGE";
const UPLOADS_DIR = join(REPO_ROOT, ".uploads");
const PYTHON_BIN = "/Library/Frameworks/Python.framework/Versions/3.11/bin/python3";

export async function POST(req: NextRequest) {
  try {
    if (!existsSync(UPLOADS_DIR)) {
      mkdirSync(UPLOADS_DIR, { recursive: true });
    }

    const formData = await req.formData();
    const file = formData.get("file") as File | null;

    if (!file) {
      registerUpload(uploadId, filePath);

    return NextResponse.json({ error: "No file provided" }, { status: 400 });
    }

    const buffer = Buffer.from(await file.arrayBuffer());
    const uploadId = randomUUID();
    const ext = file.name.endsWith(".log") ? ".log" : ".txt";
    const filePath = join(UPLOADS_DIR, `${uploadId}${ext}`);
    writeFileSync(filePath, buffer);

    const stdout = execFileSync(
      PYTHON_BIN,
      ["-m", "sage.cli", "logs-analyze", "--file", filePath, "--format", "json"],
      {
        cwd: REPO_ROOT,
        env: { ...process.env, PYTHONPATH: "src" },
        maxBuffer: 10 * 1024 * 1024,
        timeout: 60_000,
        encoding: "utf-8",
      }
    ).trim();

    if (!stdout) {
      registerUpload(uploadId, filePath);

    return NextResponse.json({ error: "No output from analysis" }, { status: 500 });
    }

    let parsed;
    try {
      parsed = JSON.parse(stdout);
    } catch {
      return NextResponse.json(
        { error: "Failed to parse analysis output", detail: stdout.substring(0, 300) },
        { status: 500 }
      );
    }

    registerUpload(uploadId, filePath);

    return NextResponse.json({
      uploadId,
      fileName: file.name,
      ...parsed,
    });
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : String(err);
    console.error("Analyze error:", message);
    registerUpload(uploadId, filePath);

    return NextResponse.json({ error: message }, { status: 500 });
  }
}
