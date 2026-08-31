import { index, integer, real, sqliteTable, text, uniqueIndex } from "drizzle-orm/sqlite-core";

export const dataSnapshots = sqliteTable("data_snapshots", {
  id: text("id").primaryKey(),
  metric: text("metric", { enum: ["trade", "price", "price_retail", "logistics", "production", "macro", "market_avg_price", "fx", "freight", "port_status", "regulation", "event_calendar", "search_query_health", "source_health"] }).notNull(),
  country: text("country", { enum: ["KZ", "UZ", "KG", "TJ", "TM", "LA", "VN", "TH", "MM", "KH"] }).notNull(),
  data: text("data", { mode: "json" }).$type<Record<string, unknown>>().notNull(),
  source: text("source").notNull(),
  capturedAt: integer("captured_at", { mode: "timestamp_ms" }).notNull(),
  createdAt: integer("created_at", { mode: "timestamp_ms" }).notNull(),
}, table => ({
  metricCountryCapturedIdx: index("idx_snapshots_metric_country_captured").on(table.metric, table.country, table.capturedAt),
  metricCapturedIdx: index("idx_snapshots_metric_captured").on(table.metric, table.capturedAt),
}));

export const reports = sqliteTable("reports", {
  id: text("id").primaryKey(),
  slug: text("slug").notNull().unique(),
  title: text("title").notNull(),
  type: text("type", { enum: ["daily", "weekly", "monthly", "quarterly", "annual"] }).notNull(),
  summary: text("summary").notNull(),
  body: text("body").notNull(),
  country: text("country", { enum: ["KZ", "UZ", "KG", "TJ", "TM", "LA", "VN", "TH", "MM", "KH"] }).notNull(),
  aiGenerated: integer("ai_generated", { mode: "boolean" }).notNull().default(true),
  publishedAt: integer("published_at", { mode: "timestamp_ms" }).notNull(),
  createdAt: integer("created_at", { mode: "timestamp_ms" }).notNull(),
}, table => ({
  typeCountryPublishedIdx: index("idx_reports_type_country_published").on(table.type, table.country, table.publishedAt),
  publishedIdx: index("idx_reports_published").on(table.publishedAt),
}));

export const marketDocuments = sqliteTable("market_documents", {
  id: text("id").primaryKey(),
  country: text("country", { enum: ["KZ", "UZ", "KG", "TJ", "TM", "LA", "VN", "TH", "MM", "KH"] }).notNull(),
  kind: text("kind", { enum: ["news", "policy", "macro"] }).notNull(),
  title: text("title").notNull(),
  publisher: text("publisher").notNull(),
  sourceUrl: text("source_url").notNull().unique(),
  language: text("language").notNull(),
  publishedAt: integer("published_at", { mode: "timestamp_ms" }).notNull(),
  retrievedAt: integer("retrieved_at", { mode: "timestamp_ms" }).notNull(),
  excerpt: text("excerpt").notNull(),
  primarySource: integer("primary_source", { mode: "boolean" }).notNull().default(false),
  verificationStatus: text("verification_status").notNull(),
  relevanceScore: real("relevance_score").notNull().default(0),
  contentHash: text("content_hash").notNull(),
  createdAt: integer("created_at", { mode: "timestamp_ms" }).notNull(),
}, table => ({
  countryPublishedIdx: index("idx_market_documents_country_published").on(table.country, table.publishedAt),
  verifiedPublishedIdx: index("idx_market_documents_verified_published").on(table.verificationStatus, table.publishedAt),
}));

export const reportSources = sqliteTable("report_sources", {
  id: text("id").primaryKey(),
  reportId: text("report_id").notNull().references(() => reports.id),
  evidenceId: text("evidence_id").notNull(),
  documentId: text("document_id").references(() => marketDocuments.id),
  sourceType: text("source_type").notNull(),
  title: text("title").notNull(),
  url: text("url").notNull(),
  publisher: text("publisher").notNull(),
  publishedAt: integer("published_at", { mode: "timestamp_ms" }).notNull(),
  retrievedAt: integer("retrieved_at", { mode: "timestamp_ms" }).notNull(),
}, table => ({
  reportEvidenceIdx: uniqueIndex("idx_report_sources_report_evidence").on(table.reportId, table.evidenceId),
  reportIdx: index("idx_report_sources_report").on(table.reportId),
}));

export const species = sqliteTable("species",{id:text("id").primaryKey(),nameZh:text("name_zh").notNull(),nameEn:text("name_en").notNull(),scientificName:text("scientific_name"),dictionaryVersion:text("dictionary_version").notNull(),reviewStatus:text("review_status").notNull()});
export const speciesSynonyms=sqliteTable("species_synonyms",{id:text("id").primaryKey(),speciesId:text("species_id").notNull().references(()=>species.id),language:text("language").notNull(),term:text("term").notNull(),isExclusion:integer("is_exclusion",{mode:"boolean"}).notNull().default(false)},t=>({termIdx:uniqueIndex("idx_species_synonym_term").on(t.language,t.term)}));
export const platforms=sqliteTable("platforms",{id:text("id").primaryKey(),name:text("name").notNull(),country:text("country").notNull(),collectionMethod:text("collection_method").notNull(),status:text("status").notNull(),statusReason:text("status_reason"),updatedAt:integer("updated_at",{mode:"timestamp_ms"}).notNull()});
export const collectionPoints=sqliteTable("collection_points",{id:text("id").primaryKey(),country:text("country").notNull(),city:text("city").notNull(),platformId:text("platform_id").notNull().references(()=>platforms.id),storeId:text("store_id"),storeName:text("store_name"),timezone:text("timezone").notNull(),active:integer("active",{mode:"boolean"}).notNull().default(true),publicLabel:text("public_label").notNull()});
export const products=sqliteTable("products",{id:text("id").primaryKey(),platformId:text("platform_id").notNull().references(()=>platforms.id),platformProductId:text("platform_product_id").notNull(),collectionPointId:text("collection_point_id").references(()=>collectionPoints.id),country:text("country").notNull(),city:text("city").notNull(),productUrl:text("product_url").notNull(),originalTitle:text("original_title").notNull(),originalDescription:text("original_description"),originalCategory:text("original_category"),originalLanguage:text("original_language"),brand:text("brand"),speciesId:text("species_id").references(()=>species.id),productForm:text("product_form").notNull(),classificationStatus:text("classification_status").notNull(),classificationConfidence:real("classification_confidence").notNull(),classificationEvidence:text("classification_evidence",{mode:"json"}).$type<Record<string,unknown>>().notNull(),imageUrl:text("image_url"),firstSeenAt:integer("first_seen_at",{mode:"timestamp_ms"}).notNull(),lastSeenAt:integer("last_seen_at",{mode:"timestamp_ms"}).notNull(),active:integer("active",{mode:"boolean"}).notNull().default(true)},t=>({sku:uniqueIndex("idx_products_platform_sku").on(t.platformId,t.collectionPointId,t.platformProductId),filter:index("idx_products_filter").on(t.country,t.city,t.speciesId,t.productForm)}));
export const priceObservations=sqliteTable("price_observations",{id:text("id").primaryKey(),productId:text("product_id").notNull().references(()=>products.id),country:text("country").notNull(),speciesId:text("species_id"),status:text("status",{enum:["active","archived","deleted"]}).notNull().default("active"),validUntil:text("valid_until"),observedAt:integer("observed_at",{mode:"timestamp_ms"}).notNull(),observationDate:text("observation_date").notNull(),currentPrice:real("current_price"),regularPrice:real("regular_price"),promotionPrice:real("promotion_price"),currency:text("currency").notNull(),packageValue:real("package_value"),packageUnit:text("package_unit"),packageCount:integer("package_count"),normalizedQuantityKg:real("normalized_quantity_kg"),normalizedPricePerKg:real("normalized_price_per_kg"),priceUsd:real("price_usd"),usdRateLocalPerUsd:real("usd_rate_local_per_usd"),fxSource:text("fx_source"),fxTimestamp:text("fx_timestamp"),inStock:integer("in_stock",{mode:"boolean"}),availabilityText:text("availability_text"),rawPriceText:text("raw_price_text"),sourceUrl:text("source_url").notNull(),sourceType:text("source_type").notNull(),pageFingerprint:text("page_fingerprint"),collectionRunId:text("collection_run_id"),collectionStatus:text("collection_status").notNull(),validationStatus:text("validation_status").notNull(),validationErrors:text("validation_errors",{mode:"json"}).$type<string[]>(),sanityOutlier:integer("sanity_outlier",{mode:"boolean"}).notNull().default(false),sanityReason:text("sanity_reason"),createdAt:integer("created_at",{mode:"timestamp_ms"}).notNull()},t=>({daily:uniqueIndex("idx_prices_product_date").on(t.productId,t.observationDate),date:index("idx_prices_date").on(t.observationDate),market:index("idx_prices_country_species_status").on(t.country,t.speciesId,t.status)}));
export const collectionRuns=sqliteTable("collection_runs",{id:text("id").primaryKey(),platformId:text("platform_id"),country:text("country"),status:text("status").notNull(),pagesVisited:integer("pages_visited").notNull().default(0),skusFound:integer("skus_found").notNull().default(0),validRecords:integer("valid_records").notNull().default(0),failedRecords:integer("failed_records").notNull().default(0),startedAt:integer("started_at",{mode:"timestamp_ms"}).notNull(),finishedAt:integer("finished_at",{mode:"timestamp_ms"})});
export const collectionErrors=sqliteTable("collection_errors",{id:text("id").primaryKey(),runId:text("run_id").notNull().references(()=>collectionRuns.id),platformId:text("platform_id"),url:text("url"),code:text("code").notNull(),message:text("message").notNull(),createdAt:integer("created_at",{mode:"timestamp_ms"}).notNull()});
export const classificationReviews=sqliteTable("classification_reviews",{id:text("id").primaryKey(),productId:text("product_id").notNull().references(()=>products.id),reason:text("reason").notNull(),status:text("status").notNull(),createdAt:integer("created_at",{mode:"timestamp_ms"}).notNull()});
export const researchJudgments=sqliteTable("research_judgments",{
 id:text("id").primaryKey(),frequency:text("frequency",{enum:["daily","weekly","monthly","quarterly","annual"]}).notNull(),periodKey:text("period_key").notNull(),country:text("country"),speciesId:text("species_id"),judgment:text("judgment").notNull(),evidence:text("evidence",{mode:"json"}).$type<Record<string,unknown>[]>().notNull(),expectedBy:text("expected_by"),status:text("status",{enum:["open","confirmed","partially_confirmed","rejected","expired"]}).notNull().default("open"),outcome:text("outcome"),impact:text("impact"),sourceReportId:text("source_report_id").references(()=>reports.id),resolvedAt:integer("resolved_at",{mode:"timestamp_ms"}),createdAt:integer("created_at",{mode:"timestamp_ms"}).notNull(),updatedAt:integer("updated_at",{mode:"timestamp_ms"}).notNull()
},t=>({period:index("idx_research_judgments_period").on(t.frequency,t.periodKey),status:index("idx_research_judgments_status").on(t.status),countrySpecies:index("idx_research_judgments_country_species").on(t.country,t.speciesId)}));
export const dailyPriceSummaries=sqliteTable("daily_price_summaries",{id:text("id").primaryKey(),date:text("date").notNull(),country:text("country").notNull(),city:text("city").notNull(),speciesId:text("species_id").notNull(),productForm:text("product_form").notNull(),validSkuCount:integer("valid_sku_count").notNull(),inStockSkuCount:integer("in_stock_sku_count").notNull(),platformCount:integer("platform_count").notNull(),storeCount:integer("store_count").notNull().default(0),minPrice:real("min_price"),medianPrice:real("median_price"),maxPrice:real("max_price"),averagePrice:real("average_price"),regularMedianPrice:real("regular_median_price"),promotionMedianPrice:real("promotion_median_price"),promotionShare:real("promotion_share"),outOfStockRate:real("out_of_stock_rate"),dayChange:real("day_change"),sevenDayChange:real("seven_day_change"),currency:text("currency").notNull().default("USD"),qualityGrade:text("quality_grade").notNull(),createdAt:integer("created_at",{mode:"timestamp_ms"}),updatedAt:integer("updated_at",{mode:"timestamp_ms"})},t=>({grain:uniqueIndex("idx_daily_summary_grain_v2").on(t.date,t.country,t.city,t.speciesId,t.productForm,t.currency)}));
