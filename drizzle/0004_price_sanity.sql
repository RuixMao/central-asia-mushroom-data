ALTER TABLE `price_observations` ADD `sanity_outlier` integer NOT NULL DEFAULT 0;
--> statement-breakpoint
ALTER TABLE `price_observations` ADD `sanity_reason` text;
--> statement-breakpoint
UPDATE `price_observations`
SET `validation_status` = 'needs_review',
    `sanity_outlier` = 1,
    `sanity_reason` = CASE (SELECT `species_id` FROM `products` WHERE `products`.`id` = `price_observations`.`product_id`)
      WHEN 'button_mushroom' THEN '超出合理区间(2~20 USD/kg)'
      WHEN 'oyster_mushroom' THEN '超出合理区间(1~15 USD/kg)'
      WHEN 'shiitake' THEN '超出合理区间(5~40 USD/kg)'
      ELSE '超出合理区间(1~50 USD/kg)'
    END
WHERE `validation_status` <> 'rejected'
  AND `normalized_price_per_kg` IS NOT NULL
  AND `usd_rate_local_per_usd` > 0
  AND (
    ((SELECT `species_id` FROM `products` WHERE `products`.`id` = `price_observations`.`product_id`) = 'button_mushroom' AND (`normalized_price_per_kg` / `usd_rate_local_per_usd` < 2 OR `normalized_price_per_kg` / `usd_rate_local_per_usd` > 20))
    OR ((SELECT `species_id` FROM `products` WHERE `products`.`id` = `price_observations`.`product_id`) = 'oyster_mushroom' AND (`normalized_price_per_kg` / `usd_rate_local_per_usd` < 1 OR `normalized_price_per_kg` / `usd_rate_local_per_usd` > 15))
    OR ((SELECT `species_id` FROM `products` WHERE `products`.`id` = `price_observations`.`product_id`) = 'shiitake' AND (`normalized_price_per_kg` / `usd_rate_local_per_usd` < 5 OR `normalized_price_per_kg` / `usd_rate_local_per_usd` > 40))
    OR ((SELECT `species_id` FROM `products` WHERE `products`.`id` = `price_observations`.`product_id`) NOT IN ('button_mushroom','oyster_mushroom','shiitake') AND (`normalized_price_per_kg` / `usd_rate_local_per_usd` < 1 OR `normalized_price_per_kg` / `usd_rate_local_per_usd` > 50))
  );
