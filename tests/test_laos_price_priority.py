import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).parents[1] / "pipeline"))

import fetch_price


class LaosPricePriorityTest(unittest.TestCase):
    def test_laos_has_multiple_online_supermarket_surfaces(self):
        configs = [config for _, config in fetch_price.SOURCES if config.get("country") == "LA"]
        self.assertGreaterEqual(len(configs), 3)
        self.assertEqual({config["platform"] for config in configs},
                         {"foodpanda-champa-market-la", "vgmart-la"})
        self.assertTrue(all(config["currency"] == "LAK" for config in configs))


if __name__ == "__main__":
    unittest.main()
