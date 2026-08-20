import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "pipeline"))

from generate_content_package import build_package


BODY = """## 今日要点

- **双孢菇价差明显。** 哈萨克斯坦 8.20 美元/公斤，建议规格一致后比价。
- **精品包装价格更高。** 吉尔吉斯斯坦 27.62 美元/公斤，建议分开报价。
- **今日无需调整备货。** 无新增政策事件，建议按原计划推进。

## 市场动态

### 鲜品

| 国家 | 品类（中文，注明规格） | 渠道 | 当地挂牌价 | 折合美元/公斤 | 观察日期 |
|---|---|---|---:|---:|---:|
| 哈萨克斯坦 | 双孢菇（400 g装） | Arbuz.kz | 1515 KZT | 8.20 | 2026-08-20 |
| 吉尔吉斯斯坦 | 双孢菇（精品300 g装） | Globus | 720 KGS | 27.62 | 2026-08-20 |

## 机会与风险

按规格比较。

## 行动建议

建议统一规格。

## 数据说明

数据来源：因恒科技监测。
"""


def test_build_package_is_vertical_and_reproducible():
    package = build_package({"title": "中亚食用菌市场日报｜8月20日：双孢菇价差3.4倍", "body": BODY, "slug": "daily", "date": "2026-08-20"})
    assert package["video"]["width"] == 1080
    assert package["video"]["height"] == 1920
    assert package["voice"]["voice_id"] == "zhixingnv"
    assert package["checks"]["price_numbers_reproducible"]
    assert "27.62美元每公斤" in package["narration"]


def test_build_package_rejects_customer_forbidden_copy():
    try:
        build_package({"title": "日报", "body": BODY.replace("今日无需调整备货", "原因待确认"), "date": "2026-08-20"})
    except RuntimeError as exc:
        assert "禁用表达" in str(exc)
    else:
        raise AssertionError("应拒绝含禁用表达的日报")
