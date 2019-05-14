import unittest

from lciafmt.fmap import norm_category as norm


class NormCategoryTest(unittest.TestCase):

    def test_remove_norels(self):
        self.assertEqual(
            norm("Elementary flows / Emission to air / unspecified"), "air")
        self.assertEqual(
            norm("Elementary flows / Emission to water / unspecified"),
            "water")

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


if __name__ == "__main__":
    unittest.main()
