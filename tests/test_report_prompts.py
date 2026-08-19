import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).parents[1] / "pipeline"))

from report_prompts import load_report_prompt


class ReportPromptTest(unittest.TestCase):
    def test_all_periodic_prompts_inherit_public_rules(self):
        expected = {
            "weekly": "本周速览",
            "monthly": "月度综述",
            "quarterly": "季度摘要",
            "annual": "五年展望",
        }
        for frequency, section in expected.items():
            prompt = load_report_prompt(frequency)
            self.assertIn("不给客户看后厨", prompt)
            self.assertIn("决策参考、采购落地、报价规范", prompt)
            self.assertIn(section, prompt)

    def test_unknown_frequency_is_rejected(self):
        with self.assertRaises(ValueError):
            load_report_prompt("daily")


if __name__ == "__main__":
    unittest.main()
