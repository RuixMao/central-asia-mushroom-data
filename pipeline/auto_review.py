"""价格采集后的自动复核闭环。

复核只使用可追溯的页面字段和同批次有效记录，不调用生成式模型猜测。
能够被证据解释的异常自动放行；证据仍不足的记录自动隔离，避免长期堆在
``needs_review``，同时完整保留原因，供适配器后续修复。
"""

from collections import Counter


def _unique(values):
    return list(dict.fromkeys(value for value in values if value))


def resolve_pending_reviews(items, *, quarantine_unresolved=True):
    """就地完成复核并返回本轮统计。

    前置步骤应已执行 ``review_sanity_outliers``。只有“唯一问题是价格区间，
    且小包装溢价已由同国/同品类/同形态有效样本解释”的记录会自动通过。
    其余记录不会伪造重量或品类；默认标为 rejected，并由入库接口从正式库
    删除。下一轮采集仍会从源页面重新解析，因此证据恢复后可重新进入正式库。
    """
    stats = Counter(scanned=len(items))
    for item in items:
        if item.get("validation_status") != "needs_review":
            continue
        stats["pending_found"] += 1
        reasons = _unique(item.get("review_reasons") or [])
        explainable_outlier = (
            item.get("sanity_review_status") == "explained"
            and set(reasons).issubset({"sanity_outlier"})
            and item.get("normalized_quantity_kg")
            and item.get("normalized_price_usd_per_kg")
        )
        if explainable_outlier:
            item["validation_status"] = "valid"
            item["review_decision"] = "auto_approve_after_review"
            item["review_reasons"] = []
            item["review_actions"] = []
            item["sanity_outlier_original"] = True
            # sanity_outlier 是消费端排除开关；解释完成后不能继续把它显示成待复核。
            item["sanity_outlier"] = False
            item["auto_review_status"] = "resolved"
            item["auto_review_reason"] = item.get("sanity_review_reason")
            stats["resolved"] += 1
            continue
        if quarantine_unresolved:
            item["validation_status"] = "rejected"
            item["review_decision"] = "auto_quarantine"
            item["auto_review_status"] = "quarantined"
            item["auto_review_reason"] = "；".join(reasons) or "insufficient_verifiable_evidence"
            item["review_actions"] = _unique([
                *(item.get("review_actions") or []),
                "retry_from_source_on_next_scheduled_collection",
            ])
            stats["quarantined"] += 1
        else:
            item["auto_review_status"] = "pending"
            stats["remaining_pending"] += 1
    stats["valid"] = sum(x.get("validation_status") == "valid" for x in items)
    stats["rejected"] = sum(x.get("validation_status") == "rejected" for x in items)
    return dict(stats)
