import { NextRequest } from "next/server";

const BACKEND_URL = process.env.BACKEND_URL ?? "http://localhost:8000";

export async function POST(req: NextRequest) {
  const body = await req.text();

  let response: Response;
  try {
    response = await fetch(`${BACKEND_URL}/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body,
    });
  } catch {
    return new Response(JSON.stringify({ error: "Could not reach backend" }), {
      status: 502,
      headers: { "Content-Type": "application/json" },
    });
  }

  if (!response.ok) {
    return new Response(JSON.stringify({ error: "Backend error" }), {
      status: response.status,
      headers: { "Content-Type": "application/json" },
    });
  }

  // Stream the response back to the client
  return new Response(response.body, {
    headers: {
      "Content-Type": response.headers.get("Content-Type") ?? "text/event-stream",
      "Cache-Control": "no-cache",
    },
  });
}
