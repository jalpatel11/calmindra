import { NextResponse } from "next/server";

const BACKEND_URL = process.env.BACKEND_URL || "http://localhost:8000";

export async function GET(req: Request) {
  try {
    const userId = req.headers.get("x-user-id") || "default_user";
    const res = await fetch(`${BACKEND_URL}/threads/`, {
      headers: {
        "x-user-id": userId,
      },
      cache: "no-store",
    });
    
    if (!res.ok) {
      return new Response(await res.text(), { status: res.status });
    }
    
    const data = await res.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error("GET /api/threads error:", error);
    return new Response("Internal Server Error", { status: 500 });
  }
}

export async function POST(req: Request) {
  try {
    const userId = req.headers.get("x-user-id") || "default_user";
    const body = await req.json();
    
    const res = await fetch(`${BACKEND_URL}/threads/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "x-user-id": userId,
      },
      body: JSON.stringify(body),
    });
    
    if (!res.ok) {
      return new Response(await res.text(), { status: res.status });
    }
    
    const data = await res.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error("POST /api/threads error:", error);
    return new Response("Internal Server Error", { status: 500 });
  }
}
