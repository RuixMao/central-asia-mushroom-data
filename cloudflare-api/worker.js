const cors = {
  "access-control-allow-origin": "*",
  "access-control-allow-methods": "GET, POST, OPTIONS",
  "access-control-allow-headers": "Accept, Content-Type, X-Sync-Secret",
};

const countries = { KZ: "哈萨克斯坦", UZ: "乌兹别克斯坦", KG: "吉尔吉斯斯坦", TJ: "塔吉克斯坦", TM: "土库曼斯坦" };
const species = { button_mushroom: "双孢菇", oyster_mushroom: "平菇", shiitake: "香菇", enoki: "金针菇", king_oyster_mushroom: "杏鲍菇" };
const allowedTables = new Set(["platforms", "species", "products", "price_observations", "daily_price_summaries", "collection_runs", "collection_errors"]);

async function authorized(request, env) {
  const supplied = request.headers.get("x-cron-secret") || request.headers.get("x-sync-secret") || "";
  if (!supplied) return false;
  if (env.SYNC_SECRET && supplied === env.SYNC_SECRET) return true;
  const digest = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(supplied));
  return [...new Uint8Array(digest)].map(byte => byte.toString(16).padStart(2, "0")).join("") === env.SYNC_SECRET_SHA256;
}

function response(body, status = 200, headers = {}) {
  return new Response(body, { status, headers: { ...cors, ...headers } });
}

function json(value, status = 200) {
  return response(JSON.stringify(value), status, { "content-type": "application/json; charset=utf-8", "cache-control": "public, max-age=300" });
}

function csvCell(value) {
  const text = value == null ? "" : typeof value === "object" ? JSON.stringify(value) : String(value);
  return /[",\r\n]/.test(text) ? `"${text.replace(/"/g, '""')}"` : text;
}

function toCsv(rows) {
  if (!rows.length) return "";
  const headers = Object.keys(rows[0]);
  return `\uFEFF${headers.join(",")}\r\n${rows.map(row => headers.map(key => csvCell(row[key])).join(",")).join("\r\n")}`;
}

async function powerBi(request, env) {
  const params = new URL(request.url).searchParams;
  const table = params.get("table") || "prices";
  const format = params.get("format") || "json";
  const dateFrom = params.get("date_from");
  let result;

  if (table === "prices") {
    const condition = dateFrom ? "AND po.observation_date >= ?" : "";
    result = await env.DB.prepare(`SELECT po.observation_date, po.observed_at, p.id product_id, p.country,
      p.city, p.species_id, p.product_form, p.original_title, p.brand, pf.id platform_id,
      pf.name platform_name, po.current_price, po.promotion_price, po.currency,
      po.normalized_quantity_kg, po.normalized_price_per_kg,
      CASE WHEN po.normalized_price_per_kg IS NOT NULL AND po.usd_rate_local_per_usd IS NOT NULL
        THEN po.normalized_price_per_kg / po.usd_rate_local_per_usd END normalized_usd_per_kg,
      po.price_usd price_usd_per_package, po.in_stock, po.validation_status
      FROM price_observations po JOIN products p ON p.id=po.product_id
      JOIN platforms pf ON pf.id=p.platform_id WHERE po.validation_status='valid' ${condition}
      ORDER BY po.observed_at DESC LIMIT 5000`)[dateFrom ? "bind" : "bind"](...(dateFrom ? [dateFrom] : [])).all();
  } else if (table === "daily") {
    const condition = dateFrom ? "WHERE date >= ?" : "";
    result = await env.DB.prepare(`SELECT * FROM daily_price_summaries ${condition} ORDER BY date DESC LIMIT 5000`).bind(...(dateFrom ? [dateFrom] : [])).all();
  } else if (table === "runs") result = await env.DB.prepare("SELECT * FROM collection_runs ORDER BY started_at DESC LIMIT 500").all();
  else if (table === "errors") result = await env.DB.prepare("SELECT * FROM collection_errors ORDER BY created_at DESC LIMIT 2000").all();
  else if (table === "products") result = await env.DB.prepare("SELECT * FROM products LIMIT 5000").all();
  else if (table === "species") result = await env.DB.prepare("SELECT * FROM species").all();
  else return json({ error: "不支持的数据表" }, 400);

  const records = result.results.map(row => ({ ...row, country_name: countries[row.country] || row.country, species_name: species[row.species_id] || row.species_id }));
  if (format === "csv") return response(toCsv(records), 200, { "content-type": "text/csv; charset=utf-8", "content-disposition": `inline; filename=${table}.csv` });
  return json({ records, count: records.length, generated_at: new Date().toISOString() });
}

async function sync(request, env) {
  if (!(await authorized(request, env))) return json({ error: "Unauthorized" }, 401);
  const payload = await request.json();
  if (!allowedTables.has(payload.table) || !Array.isArray(payload.records) || payload.records.length > 500) return json({ error: "Invalid sync batch" }, 400);
  if (!payload.records.length) return json({ ok: true, count: 0 });
  const columns = Object.keys(payload.records[0]);
  if (!columns.length || payload.records.some(row => columns.some(column => !(column in row)))) return json({ error: "Inconsistent columns" }, 400);
  const names = columns.map(column => `"${column.replaceAll('"', '""')}"`).join(",");
  const placeholders = columns.map(() => "?").join(",");
  const updates = columns.filter(column => column !== "id").map(column => `"${column.replaceAll('"', '""')}"=excluded."${column.replaceAll('"', '""')}"`).join(",");
  const statement = env.DB.prepare(`INSERT INTO "${payload.table}" (${names}) VALUES (${placeholders}) ON CONFLICT(id) DO UPDATE SET ${updates}`);
  await env.DB.batch(payload.records.map(row => statement.bind(...columns.map(column => typeof row[column] === "object" && row[column] !== null ? JSON.stringify(row[column]) : row[column]))));
  return json({ ok: true, count: payload.records.length });
}

async function ingestPrices(request, env) {
  if (!(await authorized(request, env))) return json({ error: "Unauthorized" }, 401);
  const payload = await request.json();
  const items = Array.isArray(payload.items) ? payload.items : [];
  if (!items.length || items.length > 500) return json({ error: "Invalid price batch" }, 400);
  const now = Date.now();
  const statements = [];
  for (const item of items) {
    const productId = `${item.platform}:${item.collection_point_id}:${item.platform_product_id}`;
    statements.push(
      env.DB.prepare("INSERT INTO platforms(id,name,country,collection_method,status,updated_at) VALUES(?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET name=excluded.name,status='active',updated_at=excluded.updated_at")
        .bind(item.platform, item.platform_name, item.country, item.source_type || "server_html", "active", now),
      env.DB.prepare("INSERT INTO collection_points(id,country,city,platform_id,timezone,active,public_label) VALUES(?,?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET active=1")
        .bind(item.collection_point_id, item.country, item.city, item.platform, "Asia/Almaty", 1, item.city),
      env.DB.prepare(`INSERT INTO products(id,platform_id,platform_product_id,collection_point_id,country,city,product_url,original_title,original_description,original_category,original_language,species_id,product_form,classification_status,classification_confidence,classification_evidence,first_seen_at,last_seen_at,active)
        VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(platform_id,collection_point_id,platform_product_id) DO UPDATE SET product_url=excluded.product_url,original_title=excluded.original_title,species_id=excluded.species_id,product_form=excluded.product_form,classification_status=excluded.classification_status,classification_confidence=excluded.classification_confidence,classification_evidence=excluded.classification_evidence,last_seen_at=excluded.last_seen_at,active=1`)
        .bind(productId,item.platform,item.platform_product_id,item.collection_point_id,item.country,item.city,item.product_url,item.original_title,item.original_description||null,item.original_category||null,item.original_language||null,item.species_id,item.product_form,item.classification_status,item.classification_confidence,JSON.stringify(item.classification_evidence||{}),now,now,1),
      env.DB.prepare(`INSERT INTO price_observations(id,product_id,observed_at,observation_date,current_price,regular_price,promotion_price,currency,package_value,package_unit,package_count,normalized_quantity_kg,normalized_price_per_kg,price_usd,usd_rate_local_per_usd,fx_source,fx_timestamp,in_stock,availability_text,raw_price_text,source_url,source_type,page_fingerprint,collection_run_id,collection_status,validation_status,validation_errors,created_at)
        VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(product_id,observation_date) DO UPDATE SET observed_at=excluded.observed_at,current_price=excluded.current_price,regular_price=excluded.regular_price,promotion_price=excluded.promotion_price,normalized_price_per_kg=excluded.normalized_price_per_kg,price_usd=excluded.price_usd,in_stock=excluded.in_stock,validation_status=excluded.validation_status`)
        .bind(crypto.randomUUID(),productId,Date.parse(item.observed_at),item.observation_date,item.current_price,item.regular_price||null,item.promotion_price||null,item.currency,item.package_value||null,item.package_unit||null,item.package_count||null,item.normalized_quantity_kg||null,item.normalized_price_per_kg||null,item.price_usd||null,item.usd_rate_local_per_usd||null,item.fx_source||null,String(item.fx_timestamp||""),item.in_stock?1:0,item.availability_text||null,item.raw_price_text||null,item.product_url,item.source_type||"server_html",item.page_fingerprint||null,item.collection_run_id||null,"collected",item.validation_status,JSON.stringify(item.validation_errors||[]),now)
    );
  }
  await env.DB.batch(statements);
  return json({ ok: true, count: items.length });
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (request.method === "OPTIONS") return response(null, 204);
    if (request.method === "GET" && url.pathname === "/api/powerbi") return powerBi(request, env);
    if (request.method === "POST" && url.pathname === "/api/sync") return sync(request, env);
    if (request.method === "POST" && url.pathname === "/api/ingest/prices") return ingestPrices(request, env);
    return json({ service: "Yinheng Data API", powerbi: "/api/powerbi?table=prices" }, 404);
  },
};
