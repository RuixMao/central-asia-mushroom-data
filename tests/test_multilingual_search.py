import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).parents[1] / "pipeline"))

from search_queries import COUNTRY_SEARCH_TERMS, iter_country_queries
from taxonomy import classify


class MultilingualSearchTest(unittest.TestCase):
    def test_every_country_has_local_language_and_russian(self):
        expected_local = {"KZ": "kk", "UZ": "uz", "KG": "ky", "TJ": "tg", "TM": "tk"}
        for country, local in expected_local.items():
            self.assertIn(local, COUNTRY_SEARCH_TERMS[country])
            self.assertIn("ru", COUNTRY_SEARCH_TERMS[country])

    def test_query_tasks_are_deduplicated_and_traceable(self):
        tasks = list(iter_country_queries("UZ", ("mushrooms", "button_mushroom")))
        keys = {(task.language, task.term.casefold()) for task in tasks}
        self.assertEqual(len(tasks), len(keys))
        self.assertEqual({task.language for task in tasks}, {"uz", "ru"})
        self.assertTrue(all(task.country == "UZ" and task.species_id for task in tasks))

    def test_all_target_species_exist_in_both_languages(self):
        target = {"button_mushroom", "oyster_mushroom", "shiitake", "enoki", "king_oyster_mushroom"}
        for country, languages in COUNTRY_SEARCH_TERMS.items():
            for language, species in languages.items():
                with self.subTest(country=country, language=language):
                    self.assertTrue(target.issubset(species))

    def test_daily_generic_queries_cover_both_languages(self):
        for country in COUNTRY_SEARCH_TERMS:
            tasks = list(iter_country_queries(country, ("mushrooms",)))
            self.assertEqual(len({task.language for task in tasks}), 2)
            self.assertTrue(all(task.species_id == "mushrooms" for task in tasks))

    def test_local_language_titles_reach_taxonomy(self):
        cases = (
            ("KZ", "Шампиньон саңырауқұлақтары 500 г", "button_mushroom"),
            ("UZ", "Qo'ziqorin shampinyon 1 kg", "button_mushroom"),
            ("KG", "Кесилген шампиньондор 425 г", "button_mushroom"),
            ("TJ", "Шампиньон тару тоза 1 кг", "button_mushroom"),
            ("TM", "Şampinýon kömelekleri 400 gr", "button_mushroom"),
        )
        for country, title, species in cases:
            with self.subTest(country=country):
                result = classify(title)
                self.assertEqual(result["status"], "classified")
                self.assertEqual(result["species_id"], species)


if __name__ == "__main__":
    unittest.main()
