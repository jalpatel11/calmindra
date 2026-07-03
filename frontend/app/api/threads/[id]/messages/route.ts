import { NextResponse } from "next/server";

const BACKEND_URL = process.env.BACKEND_URL || "http://localhost:8000";

export async function GET(
  req: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params;
    const res = await fetch(`${BACKEND_URL}/threads/${id}/messages`, {
      cache: "no-store",
    });
    
    if (!res.ok) {
      return new Response(await res.text(), { status: res.status });
    }
    
    const data = await res.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error("GET /api/threads/[id]/messages error:", error);
    return new Response("Internal Server Error", { status: 500 });
  }
}
