import { index, integer, sqliteTable, text } from "drizzle-orm/sqlite-core";

export const dataSnapshots = sqliteTable("data_snapshots", {
  id: text("id").primaryKey(),
  metric: text("metric", { enum: ["trade", "price", "price_retail", "logistics"] }).notNull(),
  country: text("country", { enum: ["KZ", "UZ", "KG", "TJ", "TM"] }).notNull(),
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
  type: text("type", { enum: ["daily", "weekly", "monthly"] }).notNull(),
  summary: text("summary").notNull(),
  body: text("body").notNull(),
  country: text("country", { enum: ["KZ", "UZ", "KG", "TJ", "TM"] }).notNull(),
  aiGenerated: integer("ai_generated", { mode: "boolean" }).notNull().default(true),
  publishedAt: integer("published_at", { mode: "timestamp_ms" }).notNull(),
  createdAt: integer("created_at", { mode: "timestamp_ms" }).notNull(),
}, table => ({
  typeCountryPublishedIdx: index("idx_reports_type_country_published").on(table.type, table.country, table.publishedAt),
  publishedIdx: index("idx_reports_published").on(table.publishedAt),
}));
