"""多频次市场报告 Prompt 装配器。"""

from pathlib import Path

PROMPT_DIR = Path(__file__).with_name("prompts")
REPORT_FREQUENCIES = {"weekly", "monthly", "quarterly", "annual"}


def load_report_prompt(frequency):
    """返回公共 v4.1 规则与指定频率模板，供生成端直接拼接当期数据。"""
    if frequency not in REPORT_FREQUENCIES:
        raise ValueError(f"Unsupported report frequency: {frequency}")
    common = (PROMPT_DIR / "common_v4_1.md").read_text(encoding="utf-8").strip()
    specific = (PROMPT_DIR / f"{frequency}_v4_1.md").read_text(encoding="utf-8").strip()
    return f"{common}\n\n---\n\n{specific}"
