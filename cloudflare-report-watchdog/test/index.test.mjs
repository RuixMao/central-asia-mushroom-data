import assert from "node:assert/strict";
import test from "node:test";
import { businessDate, hasReportForDate } from "../src/index.js";

test("uses the China business date across UTC midnight", () => {
  assert.equal(businessDate(new Date("2026-08-25T16:30:00Z")), "2026-08-26");
});

test("recognizes a report by slug or publication date", () => {
  assert.equal(hasReportForDate([{ slug: "2026-08-26-daily-report" }], "2026-08-26"), true);
  assert.equal(hasReportForDate([{ publishedAt: "2026-08-25T03:00:00Z" }], "2026-08-26"), false);
});
