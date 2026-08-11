const REPORTERS = "398,860,417,762,795";
const PRODUCTS = "070951,070959,200310";

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

export async function GET() {
  const apiKey = process.env.UN_COMTRADE_API_KEY;
  if (!apiKey) {
    return Response.json({ error: "UN Comtrade API key is not configured" }, { status: 503 });
  }

  const params = new URLSearchParams({
    period: "2022,2023,2024",
    reporterCode: REPORTERS,
    flowCode: "M",
    partnerCode: "0",
    cmdCode: PRODUCTS,
    partner2Code: "0",
    customsCode: "C00",
    motCode: "0",
    maxRecords: "500",
  });

  const response = await fetch(`https://comtradeapi.un.org/data/v1/get/C/A/HS?${params}`, {
    headers: { "Ocp-Apim-Subscription-Key": apiKey },
  });
  if (!response.ok) {
    return Response.json({ error: `UN Comtrade request failed (${response.status})` }, { status: 502 });
  }

  const payload = await response.json() as { data?: ComtradeRow[]; error?: string };
  const rows = (payload.data ?? []).map(row => ({
    year: Number(row.period),
    reporterCode: row.reporterCode,
    country: row.reporterDesc,
    hs: row.cmdCode,
    product: row.cmdDesc,
    valueUsd: row.primaryValue ?? null,
    netWeightKg: row.netWgt ?? null,
    isAggregate: row.isAggregate ?? false,
  }));

  return Response.json({
    source: "UN Comtrade",
    fetchedAt: new Date().toISOString(),
    records: rows,
    recordCount: rows.length,
  }, { headers: { "Cache-Control": "public, max-age=3600, s-maxage=21600" } });
}
