import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "pipeline"))

from publish_wechat_draft import markdown_to_wechat_html


class WeChatDraftTest(unittest.TestCase):
    def test_markdown_is_converted_to_inline_wechat_html(self):
        result = markdown_to_wechat_html("## 今日要点\n\n**价格稳定**\n\n|国家|价格|\n|---|---:|\n|哈萨克斯坦|8.66|")
        self.assertIn("今日要点", result)
        self.assertIn("<table", result)
        self.assertIn("style=", result)
        self.assertNotIn("<script", result)

    def test_heading_and_emphasis_are_customer_facing(self):
        result = markdown_to_wechat_html("### 风险提示\n\n**谨慎备货**")
        self.assertIn("风险提示", result)
        self.assertIn("谨慎备货", result)


if __name__ == "__main__":
    unittest.main()
