const REPORTS_URL = "https://data.yinheng.site/api/ingest/report?type=daily";
const DISPATCH_URL = "https://api.github.com/repos/RuixMao/central-asia-mushroom-data/actions/workflows/daily-report.yml/dispatches";

function businessDate(now = new Date()) {
  return new Intl.DateTimeFormat("en-CA", {
    timeZone: "Asia/Shanghai",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).format(now);
}

function hasReportForDate(records, date) {
  return records.some((report) =>
    [report.slug, report.publishedAt, report.createdAt].some((value) =>
      String(value ?? "").startsWith(date),
    ),
  );
}

async function ensureDailyReport(env) {
  const date = businessDate();
  const reportsResponse = await fetch(REPORTS_URL, {
    headers: { accept: "application/json", "user-agent": "Yinheng-Report-Watchdog/1.0" },
  });
  if (!reportsResponse.ok) throw new Error(`Report check failed: ${reportsResponse.status}`);

  const payload = await reportsResponse.json();
  if (hasReportForDate(payload.records ?? [], date)) {
    console.log(JSON.stringify({ ok: true, action: "already_exists", date }));
    return;
  }

  const dispatchResponse = await fetch(DISPATCH_URL, {
    method: "POST",
    headers: {
      accept: "application/vnd.github+json",
      authorization: `Bearer ${env.GITHUB_ACTIONS_TOKEN}`,
      "content-type": "application/json",
      "user-agent": "Yinheng-Report-Watchdog/1.0",
      "x-github-api-version": "2022-11-28",
    },
    body: JSON.stringify({ ref: "main" }),
  });
  if (dispatchResponse.status !== 204) {
    throw new Error(`Recovery dispatch failed: ${dispatchResponse.status}`);
  }
  console.log(JSON.stringify({ ok: true, action: "recovery_dispatched", date }));
}

export default {
  async scheduled(_controller, env, ctx) {
    ctx.waitUntil(ensureDailyReport(env));
  },
};

export { businessDate, hasReportForDate };
