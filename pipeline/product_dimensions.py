"""从商品页证据生成可展示的细分维度。"""
import re


SHAPES = (
    ("sliced", ("切片", "切块", "резан", "кесил", "kesilen", "sliced")),
    ("whole", ("整粒", "整个", "целы", "бүтеви", "bütewi", "bitin", "bütin", "whole")),
    ("mixed", ("混合", "拼盘", "смесь", "ассорти", "mixed")),
)


def describe_product(title, product_form, package_value=None, package_unit=None, row=None):
    row = row or {}
    text = " ".join((title or "").lower().split())
    shape = next((name for name, terms in SHAPES if any(term in text for term in terms)), "unspecified")
    packaged_markers = r"фасован|ст/б|ж/б|банк|упак|pack|bottle|瓶|罐"
    bulk_markers = r"на вес|,s*вес|цена за (?:1s*)?(?:кг|kg)|сом/кг|散装"
    if re.search(packaged_markers, text):
        packaging = "packaged"
    elif ", вес" in text or re.search(bulk_markers, text):
        packaging = "bulk"
    elif package_value and package_unit:
        packaging = "packaged"
    else:
        packaging = "unspecified"
    return {
        "product_shape": shape,
        "processing_state": product_form,
        "packaging_type": packaging,
        "brand": row.get("brand"),
        "origin_country": row.get("origin_country") or row.get("country_of_origin"),
    }
