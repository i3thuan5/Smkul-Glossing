"""測試 rules.py 裡 feature 沒有涵蓋的部份。

詞素切割與詞素翻譯的對應、構詞判定的規則本身都寫在
features/詞素切割與詞素翻譯對應.feature 與 features/構詞判定.feature，
由 behave 測。這裡只留 feature 測不到的:Word.raw、不確定標記的樣式，
以及 validate() 的整合。
"""

import unittest

from tests import ODS

from scripts.smkul.entry import Entry
from scripts.smkul.markers import is_uncertain, load_marker_lists
from scripts.smkul.rules import build_words, split_morphemes, validate


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

    def test_原詞是詞素切割拿掉符號(self):
        entry = make("awa=to", "沒有=完成貌", source="awa to")
        word = build_words(entry, self.markers)[0]
        self.assertEqual(word.raw, "awato")
        self.assertEqual(word.segmentation, "awa=to")


class TestMarkerLookup(unittest.TestCase):

    def test_不確定標記的樣式(self):
        self.assertTrue(is_uncertain("PI"))
        self.assertTrue(is_uncertain("?"))
        self.assertTrue(is_uncertain("'I"))
        self.assertTrue(is_uncertain("AN.主格"))
        self.assertFalse(is_uncertain("主焦"))


class TestValidate(unittest.TestCase):

    def test_整段驗證只回傳問題清單(self):
        entry = make(
            "pi-sano-Amis a caciyaw awa=to matini",
            "PI-像-族名 連繫詞 說話 沒有=完成貌 現在",
            source="pisanoAmis a caciyaw awa to matini",
        )
        self.assertEqual(validate(entry), [])

    def test_不再做構詞判定(self):
        """glossing-validation REMOVED「構詞判定的分類」:驗證不判構詞。"""
        entry = make("pi-sano-Amis", "PI-像-族名")
        validate(entry)
        self.assertEqual(entry.words, [])

    def test_對不起來的段列為錯誤(self):
        entry = make("ma-linah-ay", "主焦-搬遷")
        issues = validate(entry)
        self.assertEqual(len(issues), 1)
        self.assertTrue(issues[0].is_error())

    def test_逐個詞對不起來的說明與對照(self):
        issue = validate(make("ma-linah-ay", "主焦-搬遷"))[0]
        self.assertEqual(issue.detail, "這個詞的切割符號對不起來")
        self.assertEqual(
            issue.compare,
            [("詞素切割", "ma-linah-ay"), ("詞素翻譯", "主焦-搬遷")])

    def test_詞數不同的說明與對照(self):
        issue = validate(make("ma-fana' ci mira", "主焦-會 主格 主格 他.所有格"))[0]
        self.assertEqual(issue.detail, "詞素切割 3 個詞，詞素翻譯 4 個詞")
        self.assertEqual(
            [issue.compare[0][0], issue.compare[1][0]], ["詞素切割", "詞素翻譯"])
