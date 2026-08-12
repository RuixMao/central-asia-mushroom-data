const authorized = (request: Request) => Boolean(process.env.CRON_SECRET) && request.headers.get("x-cron-secret") === process.env.CRON_SECRET;
export async function POST(request: Request) {
  if (!authorized(request)) return Response.json({ error: "Unauthorized" }, { status: 401 });
  if (process.env.DEPLOY_HOOK_URL) {
    const response = await fetch(process.env.DEPLOY_HOOK_URL, { method: "POST" });
    if (!response.ok) return Response.json({ error: "Deploy hook failed" }, { status: 502 });
    return Response.json({ ok: true, triggered: true });
  }
  return Response.json({ ok: true, triggered: false, note: "D1 data is live; no rebuild is required" });
}
