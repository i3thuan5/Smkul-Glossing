"""測試 rules.py 裡 feature 沒有涵蓋的部份。

切分與 gloss 的對應、構詞判定的規則本身都寫在
features/切分與glossing對應.feature 與 features/構詞判定.feature，
由 behave 測。這裡只留 feature 測不到的:Word.raw、不確定標記的
統計，以及 validate() 的整合。
"""

import unittest

from tests import ODS

from scripts.smkul.entry import Entry
from scripts.smkul.markers import is_uncertain, load_marker_lists
from scripts.smkul.rules import (
    build_words,
    collect_uncertain,
    split_morphemes,
    validate,
)


def make(segmentation, gloss, source=""):
    return Entry(
        number="1", start="0", end="1", path="t.txt", source=source,
        segmentation=segmentation, gloss=gloss,
    )


class TestSplitMorphemes(unittest.TestCase):

    def test_兩個中綴(self):
        got = split_morphemes("q<m><n>ita=su")
        self.assertEqual(len(got), 4)
        self.assertEqual(got[0][0], "m")
        self.assertEqual(got[1][0], "n")
        self.assertEqual(got[2][0], "qita")


class TestBuildWords(unittest.TestCase):

    def setUp(self):
        self.markers = load_marker_lists(ODS)["阿美語"]

    def test_原詞是切分提掉符號(self):
        entry = make("awa=to", "沒有=完成貌", source="awa to")
        word = build_words(entry, self.markers)[0]
        self.assertEqual(word.raw, "awato")
        self.assertEqual(word.segmentation, "awa=to")


class TestMarkerLookup(unittest.TestCase):

    def setUp(self):
        self.markers = load_marker_lists(ODS)["阿美語"]

    def test_大寫的不確定標記放行且統計(self):
        entry = make("pi-codad-an", "PI-書-處焦")
        entry.words = build_words(entry, self.markers)
        uncertain = collect_uncertain(entry, "阿美語")
        self.assertIn(("PI", "阿美語"), uncertain)

    def test_不確定標記的樣式(self):
        self.assertTrue(is_uncertain("PI"))
        self.assertTrue(is_uncertain("?"))
        self.assertTrue(is_uncertain("'I"))
        self.assertTrue(is_uncertain("AN.主格"))
        self.assertFalse(is_uncertain("主焦"))


class TestValidate(unittest.TestCase):

    def test_整組驗證(self):
        markers = load_marker_lists(ODS)["阿美語"]
        entry = make(
            "pi-sano-Amis a caciyaw awa=to matini",
            "PI-像-族名 連繫詞 說話 沒有=完成貌 現在",
            source="pisanoAmis a caciyaw awa to matini",
        )
        issues, uncertain, hard = validate(entry, markers, "阿美語")
        self.assertEqual(issues, [])
        self.assertEqual(len(entry.words), 5)
        self.assertEqual(entry.words[0].morphemes[2].gloss, "族名")


class TestCorrespondence(unittest.TestCase):
    """切分行佮 gloss 行對會起來袂,分類ê名佮 feature 仝款。"""
