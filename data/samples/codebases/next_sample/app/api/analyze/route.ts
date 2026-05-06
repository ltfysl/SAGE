import { NextRequest, NextResponse } from "next/server";
import { analyzeLog } from "@/services/incidentService";
export async function POST(req: NextRequest) {
  const data = await req.formData();
  const result = await analyzeLog(data);
  return NextResponse.json(result);
}
