import unittest

from scholar_retrieval.baseline import naive_query, naive_rank
from scholar_retrieval.models import EvidenceItem


class BaselineTests(unittest.TestCase):
    def test_naive_query_strips_input(self):
        self.assertEqual(
            naive_query("  graph neural network geoscience  "),
            ["graph neural network geoscience"],
        )

    def test_naive_rank_score_descending(self):
        items = [
            EvidenceItem(title="B", source_id="b", score=0.2),
            EvidenceItem(title="A", source_id="a", score=0.9),
        ]
        self.assertEqual([item.title for item in naive_rank(items)], ["A", "B"])


if __name__ == "__main__":
    unittest.main()
