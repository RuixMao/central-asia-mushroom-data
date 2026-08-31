ALTER TABLE `price_observations` ADD `country` text NOT NULL DEFAULT '';--> statement-breakpoint
ALTER TABLE `price_observations` ADD `species_id` text;--> statement-breakpoint
ALTER TABLE `price_observations` ADD `status` text DEFAULT 'active' NOT NULL;--> statement-breakpoint
ALTER TABLE `price_observations` ADD `valid_until` text;--> statement-breakpoint
UPDATE `price_observations`
SET `country` = COALESCE((SELECT `country` FROM `products` WHERE `products`.`id` = `price_observations`.`product_id`), ''),
    `species_id` = (SELECT `species_id` FROM `products` WHERE `products`.`id` = `price_observations`.`product_id`);--> statement-breakpoint
CREATE INDEX `idx_prices_country_species_status` ON `price_observations` (`country`,`species_id`,`status`);
