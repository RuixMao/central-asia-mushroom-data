"""Expose Southeast Asia coverage without turning a blocked retailer into job failure."""
import json
import os
import sys
from pathlib import Path

COUNTRIES = {"LA": "老挝", "VN": "越南", "TH": "泰国", "MM": "缅甸", "KH": "柬埔寨"}


def build_report(payload):
    summary = payload.get("summary") or {}
    counts = summary.get("valid_by_country") or {}
    errors = payload.get("errors") or []
    reasons = {}
    for item in errors:
        platform = item.get("platform", "未知渠道")
        reasons.setdefault(platform, item.get("reason") or "采集未返回价格")
    rows = []
    for code, name in COUNTRIES.items():
        rows.append((name, int(counts.get(code, 0))))
    return rows, reasons


def main(path):
    audit = Path(path)
    if not audit.exists():
        print("::warning title=东南亚采集审计缺失::主采集未生成审计文件，请检查主步骤日志")
        return 0
    rows, reasons = build_report(json.loads(audit.read_text(encoding="utf-8")))
    total = sum(count for _, count in rows)
    lines = ["## 东南亚当日采集覆盖", "", "| 国家 | 新增有效报价 |", "|---|---:|"]
    lines.extend(f"| {name} | {count} |" for name, count in rows)
    lines.extend(["", f"合计：{total} 条。"])
    if reasons:
        lines.extend(["", "受限渠道：" + "；".join(f"{key}（{value}）" for key, value in reasons.items())])
    summary_path = os.getenv("GITHUB_STEP_SUMMARY")
    if summary_path:
        with open(summary_path, "a", encoding="utf-8") as handle:
            handle.write("\n".join(lines) + "\n")
    print("\n".join(lines))
    if total == 0:
        print("::warning title=东南亚当日零新增::动态渠道未返回可发布报价；任务保留成功以避免重复失败邮件，但覆盖告警已写入摘要")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1] if len(sys.argv) > 1 else "tmp/price-pipeline-audit.json"))
