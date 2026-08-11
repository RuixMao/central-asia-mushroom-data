const REPORTERS = "398,860,417,762,795";
const PRODUCTS = "070951,070959,200310";

type Frequency = "A" | "M";
type ComtradeRow = {
  period?: string;
  reporterCode?: number;
  reporterDesc?: string | null;
  cmdCode?: string;
  cmdDesc?: string | null;
  primaryValue?: number | null;
  netWgt?: number | null;
  isAggregate?: boolean;
};

const currentYear = () => new Date().getUTCFullYear();

function annualPeriods(start: number, end: number) {
  return Array.from({ length: end - start + 1 }, (_, index) => String(start + index));
}

function monthlyPeriods(start: number, end: number) {
  const now = new Date();
  const periods: string[] = [];
  for (let year = start; year <= end; year += 1) {
    const lastMonth = year === now.getUTCFullYear() ? now.getUTCMonth() + 1 : 12;
    for (let month = 1; month <= lastMonth; month += 1) periods.push(`${year}${String(month).padStart(2, "0")}`);
  }
  return periods;
}

export async function GET(request: Request) {
  const apiKey = process.env.UN_COMTRADE_API_KEY;
  if (!apiKey) return Response.json({ error: "UN Comtrade API key is not configured" }, { status: 503 });

  const url = new URL(request.url);
  const frequency: Frequency = url.searchParams.get("frequency") === "M" ? "M" : "A";
  const start = Math.max(2000, Number(url.searchParams.get("start") ?? (frequency === "A" ? 2022 : currentYear() - 1)));
  const end = Math.min(currentYear(), Number(url.searchParams.get("end") ?? currentYear()));
  if (!Number.isInteger(start) || !Number.isInteger(end) || start > end) {
    return Response.json({ error: "Invalid period range" }, { status: 400 });
  }

  const periods = frequency === "A" ? annualPeriods(start, end) : monthlyPeriods(start, end);
  const batches: string[][] = [];
  for (let index = 0; index < periods.length; index += frequency === "A" ? 8 : 12) {
    batches.push(periods.slice(index, index + (frequency === "A" ? 8 : 12)));
  }

  try {
    const payloads = await Promise.all(batches.map(async batch => {
      const params = new URLSearchParams({
        period: batch.join(","), reporterCode: REPORTERS, flowCode: "M", partnerCode: "0",
        cmdCode: PRODUCTS, partner2Code: "0", customsCode: "C00", motCode: "0", maxRecords: "500",
      });
      const response = await fetch(`https://comtradeapi.un.org/data/v1/get/C/${frequency}/HS?${params}`, {
        headers: { "Ocp-Apim-Subscription-Key": apiKey },
      });
      if (!response.ok) throw new Error(`UN Comtrade request failed (${response.status})`);
      return response.json() as Promise<{ data?: ComtradeRow[] }>;
    }));

    const rows = payloads.flatMap(payload => payload.data ?? []).map(row => ({
      period: String(row.period ?? ""),
      year: Number(String(row.period ?? "").slice(0, 4)),
      reporterCode: row.reporterCode,
      country: row.reporterDesc,
      hs: row.cmdCode,
      product: row.cmdDesc,
      valueUsd: row.primaryValue ?? null,
      netWeightKg: row.netWgt ?? null,
      isAggregate: row.isAggregate ?? false,
    }));

    return Response.json({ source: "UN Comtrade", frequency, fetchedAt: new Date().toISOString(), records: rows, recordCount: rows.length }, {
      headers: { "Cache-Control": "public, max-age=3600, s-maxage=21600" },
    });
  } catch (error) {
    return Response.json({ error: error instanceof Error ? error.message : "UN Comtrade request failed" }, { status: 502 });
  }
}
