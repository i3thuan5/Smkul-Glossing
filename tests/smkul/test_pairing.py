"""測試 pairing.py 的逐段比對訊息，用語照 2026.09 會議案由四。"""

import unittest

from scripts.smkul.entry import CorpusFile, Entry
from scripts.smkul.pairing import compare_entries


def corpus(*numbers):
    entries = []
    for number in numbers:
        entries.append(Entry(number=number, start="0", end="1"))
    return CorpusFile(path="a", entries=entries)


class TestCompareEntries(unittest.TestCase):

    def test_段數不同(self):
        issues = compare_entries("a", corpus("1", "2"), corpus("1"))
        self.assertEqual(issues[0].detail, "txt 2 段，docx 1 段")

    def test_找不到這一段(self):
        issues = compare_entries("a", corpus("1"), corpus("1", "2"))
        details = []
        for issue in issues:
            details.append(issue.detail)
        self.assertIn("txt 裡找不到這一段", details)
        issues = compare_entries("a", corpus("1", "2"), corpus("1"))
        details = []
        for issue in issues:
            details.append(issue.detail)
        self.assertIn("docx 裡找不到這一段", details)


if __name__ == "__main__":
    unittest.main()
