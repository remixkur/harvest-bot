interface Env {
  WEBHOOK_SECRET: string;
  UPSTREAM_SECRET: string;
  UPSTREAM_URL: string;
}

async function forwardUpdate(
  env: Env,
  body: ArrayBuffer,
  contentType: string,
): Promise<void> {
  const response = await fetch(env.UPSTREAM_URL, {
    method: "POST",
    headers: {
      "content-type": contentType,
      "x-telegram-bot-api-secret-token": env.UPSTREAM_SECRET,
    },
    body,
  });

  if (!response.ok) {
    const errorBody = await response.text();
    console.error("REG.RU webhook failed", response.status, errorBody.slice(0, 500));
  }
}

export default {
  async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
    const url = new URL(request.url);

    if (request.method === "GET" && url.pathname === "/") {
      return Response.json({
        ok: true,
        service: "HarvestYouth Telegram relay",
        upstream: "REG.RU",
      });
    }

    if (request.method !== "POST" || url.pathname !== "/webhook") {
      return new Response("Not found", { status: 404 });
    }

    const secret = request.headers.get("x-telegram-bot-api-secret-token");
    if (!env.WEBHOOK_SECRET || secret !== env.WEBHOOK_SECRET) {
      return new Response("Unauthorized", { status: 401 });
    }

    const body = await request.arrayBuffer();
    const contentType = request.headers.get("content-type") ?? "application/json";
    ctx.waitUntil(forwardUpdate(env, body, contentType));

    return Response.json({ ok: true });
  },
} satisfies ExportedHandler<Env>;
