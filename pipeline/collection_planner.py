"""根据待验证价格动态安排下一轮采集顺序。"""


def pending_targets(records):
    """每个商品只取最新状态，返回仍需主动验证的目标。"""
    latest = {}
    for record in records or []:
        data = record.get("data") or {}
        key = data.get("product_key")
        if not key or key in latest:
            continue
        latest[key] = {
            "product_key": key,
            "platform": data.get("platform_id") or record.get("source"),
            "country": record.get("country"),
            "species_id": data.get("species_id"),
            "attempt": int(data.get("candidate_attempt") or 0),
            "state": data.get("candidate_state"),
            "status": data.get("cross_validation_status"),
        }
    return [target for target in latest.values()
            if target["status"] == "pending" and target["state"] != "deleted_unqualified"]


def prioritize_sources(sources, targets):
    """原商品复采第一，同国独立渠道第二，普通扩展采集最后。"""
    targets = list(targets or [])

    def priority(entry):
        _, config = entry
        platform = config.get("platform")
        country = config.get("country")
        query_species = config.get("query_species")
        if any(target["platform"] == platform for target in targets):
            return (0, -max(target["attempt"] for target in targets if target["platform"] == platform))
        if any(target["country"] == country and target["species_id"] == query_species
               for target in targets if query_species):
            return (1, 0)
        if any(target["country"] == country and target["platform"] != platform for target in targets):
            return (2, 0)
        return (3, 0)

    return sorted(sources, key=priority)
