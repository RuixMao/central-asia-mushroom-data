CREATE TABLE `classification_reviews` (
	`id` text PRIMARY KEY NOT NULL,
	`product_id` text NOT NULL,
	`reason` text NOT NULL,
	`status` text NOT NULL,
	`created_at` integer NOT NULL,
	FOREIGN KEY (`product_id`) REFERENCES `products`(`id`) ON UPDATE no action ON DELETE no action
);
--> statement-breakpoint
CREATE TABLE `collection_errors` (
	`id` text PRIMARY KEY NOT NULL,
	`run_id` text NOT NULL,
	`platform_id` text,
	`url` text,
	`code` text NOT NULL,
	`message` text NOT NULL,
	`created_at` integer NOT NULL,
	FOREIGN KEY (`run_id`) REFERENCES `collection_runs`(`id`) ON UPDATE no action ON DELETE no action
);
--> statement-breakpoint
CREATE TABLE `collection_points` (
	`id` text PRIMARY KEY NOT NULL,
	`country` text NOT NULL,
	`city` text NOT NULL,
	`platform_id` text NOT NULL,
	`store_id` text,
	`store_name` text,
	`timezone` text NOT NULL,
	`active` integer DEFAULT true NOT NULL,
	`public_label` text NOT NULL,
	FOREIGN KEY (`platform_id`) REFERENCES `platforms`(`id`) ON UPDATE no action ON DELETE no action
);
--> statement-breakpoint
CREATE TABLE `collection_runs` (
	`id` text PRIMARY KEY NOT NULL,
	`platform_id` text,
	`country` text,
	`status` text NOT NULL,
	`pages_visited` integer DEFAULT 0 NOT NULL,
	`skus_found` integer DEFAULT 0 NOT NULL,
	`valid_records` integer DEFAULT 0 NOT NULL,
	`failed_records` integer DEFAULT 0 NOT NULL,
	`started_at` integer NOT NULL,
	`finished_at` integer
);
--> statement-breakpoint
CREATE TABLE `daily_price_summaries` (
	`id` text PRIMARY KEY NOT NULL,
	`date` text NOT NULL,
	`country` text NOT NULL,
	`city` text NOT NULL,
	`species_id` text NOT NULL,
	`product_form` text NOT NULL,
	`valid_sku_count` integer NOT NULL,
	`in_stock_sku_count` integer NOT NULL,
	`platform_count` integer NOT NULL,
	`min_price` real,
	`median_price` real,
	`max_price` real,
	`average_price` real,
	`currency` text DEFAULT 'USD' NOT NULL,
	`quality_grade` text NOT NULL
);
--> statement-breakpoint
CREATE UNIQUE INDEX `idx_daily_summary_grain` ON `daily_price_summaries` (`date`,`country`,`city`,`species_id`,`product_form`);--> statement-breakpoint
CREATE TABLE `platforms` (
	`id` text PRIMARY KEY NOT NULL,
	`name` text NOT NULL,
	`country` text NOT NULL,
	`collection_method` text NOT NULL,
	`status` text NOT NULL,
	`status_reason` text,
	`updated_at` integer NOT NULL
);
--> statement-breakpoint
CREATE TABLE `price_observations` (
	`id` text PRIMARY KEY NOT NULL,
	`product_id` text NOT NULL,
	`observed_at` integer NOT NULL,
	`observation_date` text NOT NULL,
	`current_price` real,
	`regular_price` real,
	`promotion_price` real,
	`currency` text NOT NULL,
	`package_value` real,
	`package_unit` text,
	`normalized_quantity_kg` real,
	`normalized_price_per_kg` real,
	`price_usd` real,
	`usd_rate_local_per_usd` real,
	`fx_source` text,
	`fx_timestamp` text,
	`in_stock` integer,
	`availability_text` text,
	`raw_price_text` text,
	`source_url` text NOT NULL,
	`source_type` text NOT NULL,
	`page_fingerprint` text,
	`collection_status` text NOT NULL,
	`validation_status` text NOT NULL,
	`created_at` integer NOT NULL,
	FOREIGN KEY (`product_id`) REFERENCES `products`(`id`) ON UPDATE no action ON DELETE no action
);
--> statement-breakpoint
CREATE UNIQUE INDEX `idx_prices_product_date` ON `price_observations` (`product_id`,`observation_date`);--> statement-breakpoint
CREATE INDEX `idx_prices_date` ON `price_observations` (`observation_date`);--> statement-breakpoint
CREATE TABLE `products` (
	`id` text PRIMARY KEY NOT NULL,
	`platform_id` text NOT NULL,
	`platform_product_id` text NOT NULL,
	`collection_point_id` text,
	`country` text NOT NULL,
	`city` text NOT NULL,
	`product_url` text NOT NULL,
	`original_title` text NOT NULL,
	`original_description` text,
	`original_category` text,
	`original_language` text,
	`brand` text,
	`species_id` text,
	`product_form` text NOT NULL,
	`classification_status` text NOT NULL,
	`classification_confidence` real NOT NULL,
	`classification_evidence` text NOT NULL,
	`image_url` text,
	`first_seen_at` integer NOT NULL,
	`last_seen_at` integer NOT NULL,
	`active` integer DEFAULT true NOT NULL,
	FOREIGN KEY (`platform_id`) REFERENCES `platforms`(`id`) ON UPDATE no action ON DELETE no action,
	FOREIGN KEY (`collection_point_id`) REFERENCES `collection_points`(`id`) ON UPDATE no action ON DELETE no action,
	FOREIGN KEY (`species_id`) REFERENCES `species`(`id`) ON UPDATE no action ON DELETE no action
);
--> statement-breakpoint
CREATE UNIQUE INDEX `idx_products_platform_sku` ON `products` (`platform_id`,`collection_point_id`,`platform_product_id`);--> statement-breakpoint
CREATE INDEX `idx_products_filter` ON `products` (`country`,`city`,`species_id`,`product_form`);--> statement-breakpoint
CREATE TABLE `species` (
	`id` text PRIMARY KEY NOT NULL,
	`name_zh` text NOT NULL,
	`name_en` text NOT NULL,
	`scientific_name` text,
	`dictionary_version` text NOT NULL,
	`review_status` text NOT NULL
);
--> statement-breakpoint
CREATE TABLE `species_synonyms` (
	`id` text PRIMARY KEY NOT NULL,
	`species_id` text NOT NULL,
	`language` text NOT NULL,
	`term` text NOT NULL,
	`is_exclusion` integer DEFAULT false NOT NULL,
	FOREIGN KEY (`species_id`) REFERENCES `species`(`id`) ON UPDATE no action ON DELETE no action
);
--> statement-breakpoint
CREATE UNIQUE INDEX `idx_species_synonym_term` ON `species_synonyms` (`language`,`term`);