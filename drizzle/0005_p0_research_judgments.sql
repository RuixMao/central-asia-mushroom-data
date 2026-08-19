CREATE TABLE `research_judgments` (
 `id` text PRIMARY KEY NOT NULL,
 `frequency` text NOT NULL,
 `period_key` text NOT NULL,
 `country` text,
 `species_id` text,
 `judgment` text NOT NULL,
 `evidence` text NOT NULL,
 `expected_by` text,
 `status` text DEFAULT 'open' NOT NULL,
 `outcome` text,
 `impact` text,
 `source_report_id` text,
 `resolved_at` integer,
 `created_at` integer NOT NULL,
 `updated_at` integer NOT NULL,
 FOREIGN KEY (`source_report_id`) REFERENCES `reports`(`id`) ON UPDATE no action ON DELETE no action
);
--> statement-breakpoint
CREATE INDEX `idx_research_judgments_period` ON `research_judgments` (`frequency`,`period_key`);
--> statement-breakpoint
CREATE INDEX `idx_research_judgments_status` ON `research_judgments` (`status`);
--> statement-breakpoint
CREATE INDEX `idx_research_judgments_country_species` ON `research_judgments` (`country`,`species_id`);
