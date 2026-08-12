ALTER TABLE `price_observations` ADD `package_count` integer;
--> statement-breakpoint
ALTER TABLE `price_observations` ADD `collection_run_id` text;
--> statement-breakpoint
ALTER TABLE `price_observations` ADD `validation_errors` text;
--> statement-breakpoint
ALTER TABLE `daily_price_summaries` ADD `store_count` integer NOT NULL DEFAULT 0;
--> statement-breakpoint
ALTER TABLE `daily_price_summaries` ADD `regular_median_price` real;
--> statement-breakpoint
ALTER TABLE `daily_price_summaries` ADD `promotion_median_price` real;
--> statement-breakpoint
ALTER TABLE `daily_price_summaries` ADD `promotion_share` real;
--> statement-breakpoint
ALTER TABLE `daily_price_summaries` ADD `out_of_stock_rate` real;
--> statement-breakpoint
ALTER TABLE `daily_price_summaries` ADD `day_change` real;
--> statement-breakpoint
ALTER TABLE `daily_price_summaries` ADD `seven_day_change` real;
--> statement-breakpoint
ALTER TABLE `daily_price_summaries` ADD `created_at` integer;
--> statement-breakpoint
ALTER TABLE `daily_price_summaries` ADD `updated_at` integer;
--> statement-breakpoint
CREATE UNIQUE INDEX `idx_daily_summary_grain_v2` ON `daily_price_summaries` (`date`,`country`,`city`,`species_id`,`product_form`,`currency`);
