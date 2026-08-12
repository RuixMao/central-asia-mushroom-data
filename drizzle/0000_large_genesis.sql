CREATE TABLE `data_snapshots` (
	`id` text PRIMARY KEY NOT NULL,
	`metric` text NOT NULL,
	`country` text NOT NULL,
	`data` text NOT NULL,
	`source` text NOT NULL,
	`captured_at` integer NOT NULL,
	`created_at` integer NOT NULL
);
--> statement-breakpoint
CREATE INDEX `idx_snapshots_metric_country_captured` ON `data_snapshots` (`metric`,`country`,`captured_at`);--> statement-breakpoint
CREATE INDEX `idx_snapshots_metric_captured` ON `data_snapshots` (`metric`,`captured_at`);--> statement-breakpoint
CREATE TABLE `reports` (
	`id` text PRIMARY KEY NOT NULL,
	`slug` text NOT NULL,
	`title` text NOT NULL,
	`type` text NOT NULL,
	`summary` text NOT NULL,
	`body` text NOT NULL,
	`country` text NOT NULL,
	`ai_generated` integer DEFAULT true NOT NULL,
	`published_at` integer NOT NULL,
	`created_at` integer NOT NULL
);
--> statement-breakpoint
CREATE UNIQUE INDEX `reports_slug_unique` ON `reports` (`slug`);--> statement-breakpoint
CREATE INDEX `idx_reports_type_country_published` ON `reports` (`type`,`country`,`published_at`);--> statement-breakpoint
CREATE INDEX `idx_reports_published` ON `reports` (`published_at`);--> statement-breakpoint
PRAGMA optimize;
