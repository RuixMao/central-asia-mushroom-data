const REPORTERS = "398,860,417,762,795,418,704,764,104,116";
const PRODUCTS = "070951,070959,200310";

type Frequency = "A" | "M";
type ComtradeRow = {
  period?: string;
  reporterCode?: number;
  reporterDesc?: string | null;
  partnerCode?: number;
  cmdCode?: string;
  cmdDesc?: string | null;
  primaryValue?: number | null;
  netWgt?: number | null;
  isAggregate?: boolean;
};

const COUNTRY_META = [
  { code: "KZ", name: "哈萨克斯坦", reporter: 398 }, { code: "UZ", name: "乌兹别克斯坦", reporter: 860 },
  { code: "KG", name: "吉尔吉斯斯坦", reporter: 417 }, { code: "TJ", name: "塔吉克斯坦", reporter: 762 },
  { code: "TM", name: "土库曼斯坦", reporter: 795 },
  { code: "LA", name: "老挝", reporter: 418 }, { code: "VN", name: "越南", reporter: 704 },
  { code: "TH", name: "泰国", reporter: 764 }, { code: "MM", name: "缅甸", reporter: 104 },
  { code: "KH", name: "柬埔寨", reporter: 116 },
] as const;
const PRODUCT_NAMES: Record<string, string> = { "070951": "鲜或冷藏双孢蘑菇", "070959": "其他鲜或冷藏蘑菇", "200310": "加工保藏蘑菇" };

async function comtrade(params: URLSearchParams, apiKey: string) {
  const response = await fetch(`https://comtradeapi.un.org/data/v1/get/C/A/HS?${params}`, { headers: { "Ocp-Apim-Subscription-Key": apiKey } });
  if (!response.ok) throw new Error(`UN Comtrade request failed (${response.status})`);
  return response.json() as Promise<{ data?: ComtradeRow[] }>;
}

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
  if (url.searchParams.get("mode") === "mirror") {
    const year = Math.min(currentYear(), Math.max(2000, Number(url.searchParams.get("year") ?? currentYear() - 1)));
    const base = { period: String(year), cmdCode: PRODUCTS, partner2Code: "0", customsCode: "C00", motCode: "0", maxRecords: "500" };
    try {
      const countryPayloads = await Promise.all(COUNTRY_META.map(async country => {
        const [imports, exports] = await Promise.all([
          comtrade(new URLSearchParams({ ...base, reporterCode: String(country.reporter), flowCode: "M", partnerCode: "0" }), apiKey),
          comtrade(new URLSearchParams({ ...base, reporterCode: "156", flowCode: "X", partnerCode: String(country.reporter) }), apiKey),
        ]);
        return { country, importRows: imports.data ?? [], exportRows: exports.data ?? [] };
      }));
      const records = COUNTRY_META.flatMap(country => PRODUCTS.split(",").map(hs => {
        const payload = countryPayloads.find(item => item.country.code === country.code)!;
        const importer = payload.importRows.find(row => row.cmdCode === hs);
        const mirror = payload.exportRows.find(row => row.cmdCode === hs);
        const importerValue = importer?.primaryValue ?? null; const mirrorValue = mirror?.primaryValue ?? null;
        return { countryCode: country.code, country: country.name, hs, product: PRODUCT_NAMES[hs], year, importerCifUsd: importerValue, chinaFobUsd: mirrorValue, importerSource: "进口国申报（UN Comtrade）", mirrorSource: "中国出口镜像（中国海关经 UN Comtrade）", confidence: importerValue !== null && mirrorValue !== null ? "A−" : mirrorValue !== null ? "B+" : importerValue !== null ? "B" : "C" };
      }));
      return Response.json({ sourceStrategy: "reporter-first-with-china-mirror", year, fetchedAt: new Date().toISOString(), records }, { headers: { "Cache-Control": "public, max-age=3600, s-maxage=21600" } });
    } catch (error) { return Response.json({ error: error instanceof Error ? error.message : "Mirror data request failed" }, { status: 502 }); }
  }
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
