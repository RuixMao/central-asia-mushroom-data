"""把已发布日报转换为视频生产包；不负责平台分发或最终渲染。"""

import json
import os
import re
from datetime import date
from pathlib import Path

import requests


FORBIDDEN = re.compile(r"样本有限|仅供参考|自动复核|待进一步确认|原因待确认|原因待查|详见正文|详见上表")
TABLE_ROW = re.compile(
    r"^\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([0-9]+(?:\.[0-9]+)?)\s*\|\s*([0-9-]+)\s*\|$"
)


def plain(text):
    return re.sub(r"[`#>*_]", "", text).strip()


def load_report(path):
    if path.is_file():
        return json.loads(path.read_text(encoding="utf-8"))
    site_url = os.environ.get("SITE_URL", "").rstrip("/")
    if not site_url:
        raise RuntimeError(f"日报产物不存在：{path}")
    response = requests.get(f"{site_url}/api/ingest/report", timeout=60)
    response.raise_for_status()
    reports = [row for row in response.json().get("records", []) if row.get("type") == "daily"]
    if not reports:
        raise RuntimeError("线上没有可用于生成视频的日报")
    latest = reports[0]
    return {key: latest.get(key, "") for key in ("title", "summary", "body", "slug", "date")}


def extract_points(body):
    match = re.search(r"## 今日要点\s*(.*?)(?=\n## )", body, re.S)
    if not match:
        return []
    points = []
    for line in match.group(1).splitlines():
        item = plain(re.sub(r"^\s*[-+*]\s*", "", line))
        if item and not item.startswith("|"):
            points.append(item)
    return points[:4]


def extract_prices(body):
    rows = []
    for line in body.splitlines():
        match = TABLE_ROW.match(line.strip())
        if not match or match.group(1).strip() == "国家":
            continue
        country, product, channel, local_price, usd, observed = [part.strip() for part in match.groups()]
        rows.append({
            "country": country,
            "product": product,
            "channel": channel,
            "local_price": local_price,
            "usd_per_kg": float(usd),
            "observation_date": observed,
        })
    return rows


def shorten(text, limit=54):
    text = re.sub(r"\s+", "", plain(text))
    return text if len(text) <= limit else text[: limit - 1] + "…"


def build_package(report):
    title = report.get("title", "").strip()
    body = report.get("body", "").strip()
    if not title or not body:
        raise RuntimeError("日报标题或正文为空")
    if FORBIDDEN.search(title + "\n" + body):
        raise RuntimeError("日报含客户版禁用表达，停止生成视频内容包")
    points = extract_points(body)
    prices = extract_prices(body)
    if len(points) < 3 or not prices:
        raise RuntimeError("日报缺少至少 3 条今日要点或可复算价格表")

    report_date = report.get("date") or prices[0]["observation_date"] or date.today().isoformat()
    display_date = f"{int(report_date[5:7])}月{int(report_date[8:10])}日"
    headline = title.split("：", 1)[-1]
    featured = sorted(prices, key=lambda row: row["usd_per_kg"], reverse=True)[:3]
    price_lines = [
        f'{row["country"]}{re.sub(r"（.*?）", "", row["product"])}，{row["usd_per_kg"]:.2f}美元每公斤，来自{row["channel"]}。'
        for row in featured
    ]
    narration_parts = [
        f"这里是因恒科技菌情播报。{display_date}，今天的核心看点是：{headline}。",
        *[shorten(item, 62) for item in points[:3]],
        "今天价格表中，" + "".join(price_lines),
        "企业比价时，应先统一品类、形态、净重和等级，再核算批量报价与到岸成本。",
        "以上是今日菌情播报。完整数据与行动建议，请查看因恒科技中亚食用菌市场日报。",
    ]
    narration = "\n".join(narration_parts)
    if len(narration) < 180:
        raise RuntimeError("播报稿过短，无法形成完整视频")

    scenes = [
        {"id": "opening", "seconds": 4, "eyebrow": "因恒科技 · 菌情播报", "title": display_date, "body": headline},
    ] + [
        {"id": f"point-{index}", "seconds": 9, "eyebrow": f"今日要点 {index}", "title": shorten(point, 22), "body": shorten(point, 54)}
        for index, point in enumerate(points[:3], 1)
    ]
    scenes += [
        {"id": "prices", "seconds": 15, "eyebrow": "今日价格", "title": "三条重点挂牌价", "rows": featured},
        {"id": "action", "seconds": 9, "eyebrow": "操作提示", "title": "规格一致，再做比价", "body": "先统一品类、形态、净重和等级，再核算批量报价与到岸成本。"},
        {"id": "ending", "seconds": 5, "eyebrow": "因恒科技", "title": "每天3分钟看清中亚菌市", "body": "完整数据与行动建议，请查看今日市场日报。"},
    ]
    duration = sum(scene["seconds"] for scene in scenes)
    source_numbers = set(re.findall(r"\d+(?:\.\d+)?", title + "\n" + body))
    narrated_prices = {f'{row["usd_per_kg"]:.2f}' for row in featured}
    checks = {
        "report_gate_passed": True,
        "three_to_five_key_points": 3 <= len(points) <= 5,
        "price_numbers_reproducible": narrated_prices <= source_numbers,
        "forbidden_copy_absent": FORBIDDEN.search(narration) is None,
        "vertical_video": True,
        "target_duration_seconds": duration,
    }
    if not all(checks[key] for key in ("report_gate_passed", "three_to_five_key_points", "price_numbers_reproducible", "forbidden_copy_absent", "vertical_video")):
        raise RuntimeError("视频内容包自检失败")
    return {
        "schema_version": "1.0",
        "report": {"title": title, "slug": report.get("slug"), "date": report_date},
        "video": {"width": 1080, "height": 1920, "fps": 30, "duration_seconds": duration, "scenes": scenes},
        "voice": {
            "provider": "doubao",
            "voice_id": os.environ.get("VIDEO_VOICE_ID", "zhixingnv"),
            "display_name": "知性女声",
            "speed_ratio": 1.05,
            "direction": "专业、克制、清晰，像财经资讯栏目播报；数字读准，语气自然，不夸张",
        },
        "narration": narration,
        "social": {
            "title": f"菌情播报｜{display_date} {headline}",
            "description": f"{display_date}中亚食用菌市场重点价格与操作提示。完整日报：data.yinheng.site/reports/{report.get('slug', '')}",
            "hashtags": ["中亚市场", "食用菌出口", "外贸", "菌情播报", "因恒科技"],
        },
        "checks": checks,
    }


def write_package(package, output_dir):
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "content-package.json").write_text(json.dumps(package, ensure_ascii=False, indent=2), encoding="utf-8")
    (output_dir / "voiceover.txt").write_text(package["narration"] + "\n", encoding="utf-8")
    storyboard = [f'# {package["social"]["title"]}', "", f'画幅：1080×1920｜{package["video"]["fps"]}fps｜约 {package["video"]["duration_seconds"]} 秒', ""]
    for scene in package["video"]["scenes"]:
        storyboard += [f'## {scene["id"]}（{scene["seconds"]}秒）', "", scene.get("title", ""), "", scene.get("body", "")]
        for row in scene.get("rows", []):
            storyboard.append(f'- {row["country"]}｜{row["product"]}｜{row["channel"]}｜{row["usd_per_kg"]:.2f} 美元/公斤')
        storyboard.append("")
    (output_dir / "storyboard.md").write_text("\n".join(storyboard), encoding="utf-8")
    (output_dir / "social-copy.txt").write_text(package["social"]["title"] + "\n\n" + package["social"]["description"] + "\n\n" + " ".join("#" + tag for tag in package["social"]["hashtags"]) + "\n", encoding="utf-8")


def run():
    report_path = Path(os.environ.get("REPORT_ARTIFACT_OUTPUT", "tmp/daily-report.json"))
    output_dir = Path(os.environ.get("CONTENT_PACKAGE_DIR", "tmp/daily-content-package"))
    package = build_package(load_report(report_path))
    write_package(package, output_dir)
    print(f'视频内容包完成：{len(package["video"]["scenes"])} 个分镜，约 {package["video"]["duration_seconds"]} 秒，目录={output_dir}')


if __name__ == "__main__":
    run()
