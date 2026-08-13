CREATE TABLE `market_documents` (
	`id` text PRIMARY KEY NOT NULL,
	`country` text NOT NULL,
	`kind` text NOT NULL,
	`title` text NOT NULL,
	`publisher` text NOT NULL,
	`source_url` text NOT NULL,
	`language` text NOT NULL,
	`published_at` integer NOT NULL,
	`retrieved_at` integer NOT NULL,
	`excerpt` text NOT NULL,
	`primary_source` integer DEFAULT false NOT NULL,
	`verification_status` text NOT NULL,
	`relevance_score` real DEFAULT 0 NOT NULL,
	`content_hash` text NOT NULL,
	`created_at` integer NOT NULL
);
--> statement-breakpoint
CREATE UNIQUE INDEX `market_documents_source_url_unique` ON `market_documents` (`source_url`);
--> statement-breakpoint
CREATE INDEX `idx_market_documents_country_published` ON `market_documents` (`country`,`published_at`);
--> statement-breakpoint
CREATE INDEX `idx_market_documents_verified_published` ON `market_documents` (`verification_status`,`published_at`);
--> statement-breakpoint
CREATE TABLE `report_sources` (
	`id` text PRIMARY KEY NOT NULL,
	`report_id` text NOT NULL,
	`evidence_id` text NOT NULL,
	`document_id` text,
	`source_type` text NOT NULL,
	`title` text NOT NULL,
	`url` text NOT NULL,
	`publisher` text NOT NULL,
	`published_at` integer NOT NULL,
	`retrieved_at` integer NOT NULL,
	FOREIGN KEY (`report_id`) REFERENCES `reports`(`id`) ON UPDATE no action ON DELETE no action,
	FOREIGN KEY (`document_id`) REFERENCES `market_documents`(`id`) ON UPDATE no action ON DELETE no action
);
--> statement-breakpoint
CREATE UNIQUE INDEX `idx_report_sources_report_evidence` ON `report_sources` (`report_id`,`evidence_id`);
--> statement-breakpoint
CREATE INDEX `idx_report_sources_report` ON `report_sources` (`report_id`);
