"""utils 工具函数单测:统一价格解析与 UTF-8 解码。"""
import datetime as dt
import sys, pathlib, unittest
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "pipeline"))

from utils import parse_price_text, response_text, today_str


class TestBusinessDate(unittest.TestCase):
    def test_utc_runner_uses_beijing_business_date(self):
        now = dt.datetime(2026, 8, 24, 23, 41, tzinfo=dt.timezone.utc)
        self.assertEqual(today_str(now), "2026-08-25")

    def test_naive_runner_time_is_treated_as_utc(self):
        now = dt.datetime(2026, 8, 24, 23, 41)
        self.assertEqual(today_str(now), "2026-08-25")


class TestParsePriceText(unittest.TestCase):
    def test_thousands_comma(self):
        """千分位逗号:45,000 -> 45000(不是 45.0)。"""
        self.assertEqual(parse_price_text("45,000"), 45000.0)

    def test_decimal_point(self):
        """小数点:45.50 -> 45.5。"""
        self.assertEqual(parse_price_text("45.50"), 45.5)

    def test_decimal_comma(self):
        """小数点逗号:128,70 -> 128.7(中亚习惯)。"""
        self.assertEqual(parse_price_text("128,70"), 128.7)

    def test_thousands_and_decimal(self):
        """千分位+小数点:1,234.56 -> 1234.56。"""
        self.assertEqual(parse_price_text("1,234.56"), 1234.56)

    def test_space_thousands(self):
        """空格千分位:45 000 -> 45000。"""
        self.assertEqual(parse_price_text("45 000"), 45000.0)

    def test_narrow_space(self):
        """窄空格:45\u202f000 -> 45000。"""
        self.assertEqual(parse_price_text("45\u202f000"), 45000.0)

    def test_none_and_invalid(self):
        """None 与非法输入返回 None(不抛异常)。"""
        self.assertIsNone(parse_price_text(None))
        self.assertIsNone(parse_price_text("abc"))
        self.assertIsNone(parse_price_text(""))


class TestResponseText(unittest.TestCase):
    def test_utf8_bytes_preferred(self):
        """有 UTF-8 bytes 时按 UTF-8 解码(治 mojibake)。"""
        class R:
            content = "Gelinkömelek".encode("utf-8")
            text = "GelinkÃ¶melek"  # 模拟 requests 按 latin-1 误解码
        self.assertEqual(response_text(R()), "Gelinkömelek")

    def test_mock_without_content_falls_back(self):
        """测试 mock 无 content bytes 时回退 .text。"""
        class R:
            text = "<html>Шампиньоны</html>"
        self.assertEqual(response_text(R()), "<html>Шампиньоны</html>")

    def test_latin1_bytes_fallback(self):
        """bytes 无法按 UTF-8 解码时回退 .text。"""
        class R:
            content = b"\xff\xfe invalid utf8"
            text = "fallback text"
        self.assertEqual(response_text(R()), "fallback text")


if __name__ == "__main__":
    unittest.main()
