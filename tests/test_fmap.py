import unittest

import lciafmt.fmap as fmap
from lciafmt.fmap import norm_category as norm


class NormCategoryTest(unittest.TestCase):

    def test_remove_norels(self):
        self.assertEqual(
            norm("Elementary flows / Emission to air / unspecified"),
            "air/unspecified")
        self.assertEqual(
            norm("Elementary flows / Emission to water / unspecified"),
            "water/unspecified")

    def test_skip_duplicates(self):
        self.assertEqual(
            norm("Emission to water / water"), "water")
        self.assertEqual(
            norm("Emission to water / ground water"), "water/ground")
        self.assertEqual(
            norm("Emission to water / fossil-water"), "water/fossil")

    def test_qualifiers(self):
        self.assertEqual(
            norm("Emission to air / high population density, long-term"),
            "air/urban, long-term")

    def test_get_systems(self):
        systems = fmap.supported_mapping_systems()
        self.assertTrue(len(systems) > 0)


if __name__ == "__main__":
    unittest.main()
