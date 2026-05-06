import { NextRequest, NextResponse } from "next/server";
import { execFileSync } from "child_process";
import { existsSync } from "fs";
import { join } from "path";

export const runtime = "nodejs";

const REPO_ROOT = "/Users/latifyesil/Projekte/SAGE";
const UPLOADS_DIR = join(REPO_ROOT, ".uploads");
const PYTHON_BIN = "/Library/Frameworks/Python.framework/Versions/3.11/bin/python3";

// Simple in-memory map of uploadId -> file path
const uploadMap = new Map<string, string>();

export function registerUpload(uploadId: string, filePath: string) {
  uploadMap.set(uploadId, filePath);
}

export async function POST(req: NextRequest) {
  try {
    const { uploadId, question } = (await req.json()) as {
      uploadId?: string;
      question?: string;
    };

    if (!uploadId || !question) {
      return NextResponse.json(
        { error: "uploadId and question are required" },
        { status: 400 }
      );
    }

    let filePath: string | undefined = uploadMap.get(uploadId);

    if (!filePath && existsSync(UPLOADS_DIR)) {
      const fs = await import("fs");
      const files = fs.readdirSync(UPLOADS_DIR);
      const match = files.find((f) => f.startsWith(uploadId));
      if (match) {
        filePath = join(UPLOADS_DIR, match);
      }
    }

    if (!filePath || !existsSync(filePath)) {
      return NextResponse.json(
        { error: "Upload not found. Please re-upload the log file." },
        { status: 404 }
      );
    }

    const stdout = execFileSync(
      PYTHON_BIN,
      ["-m", "sage.cli", "logs-ask", "--file", filePath, "--question", question],
      {
        cwd: REPO_ROOT,
        env: { ...process.env, PYTHONPATH: "src" },
        maxBuffer: 10 * 1024 * 1024,
        timeout: 120_000,
        encoding: "utf-8",
      }
    ).trim();

    // Extract answer from rich-formatted output: "A: ..."
    const answerMatch = stdout.match(/A:\s*(.+)$/m);
    const answer = answerMatch
      ? answerMatch[1].replace(/\x1b\[[0-9;]*m/g, "")
      : stdout.replace(/\x1b\[[0-9;]*m/g, "");

    return NextResponse.json({ question, answer });
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : String(err);
    console.error("Ask error:", message);
    return NextResponse.json({
      question: "",
      answer: `Unable to answer: ${message}`,
    });
  }
}
