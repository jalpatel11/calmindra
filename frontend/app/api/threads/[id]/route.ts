import { NextResponse } from "next/server";

const BACKEND_URL = process.env.BACKEND_URL || "http://localhost:8000";

export async function DELETE(
  req: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params;
    const res = await fetch(`${BACKEND_URL}/threads/${id}`, {
      method: "DELETE",
    });
    
    if (!res.ok) {
      return new Response(await res.text(), { status: res.status });
    }
    
    return NextResponse.json({ success: true });
  } catch (error) {
    console.error("DELETE /api/threads/[id] error:", error);
    return new Response("Internal Server Error", { status: 500 });
  }
}
