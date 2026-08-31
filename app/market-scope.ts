import scope from "../scope.json";

export const targetMarkets = scope.countries.map(country=>({...country,regionLabel:country.region_name}));

export const targetMarketCodes = targetMarkets.map((market) => market.code);
export const southeastAsiaCodes = scope.countries.filter(country=>country.region==="SEA").map(country=>country.code);
export const centralAsiaCodes = scope.countries.filter(country=>country.region==="CA").map(country=>country.code);
export const targetMarketNames: Record<string, string> = Object.fromEntries(
  targetMarkets.map((market) => [market.code, market.name]),
);

export const marketRegions=Array.from(new Map(scope.countries.map(country=>[country.region,{id:country.region,label:country.region_name,countries:scope.countries.filter(item=>item.region===country.region)}])).values());
export const speciesScope=scope.species;
export const targetMarketTiers:Record<string,number>=Object.fromEntries(scope.countries.map(country=>[country.code,country.tier]));
export const marketScopeLabel = Array.from(new Set(scope.countries.map(country=>country.region_name))).join("与");
export const southeastAsiaPriorityMarket = scope.countries.find(country=>country.region==="SEA"&&country.tier===1)?.code??scope.countries[0]?.code??"";
