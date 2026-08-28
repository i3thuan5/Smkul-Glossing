"""測試 parser.py 裡 feature 沒有涵蓋的部份。

字元正規化、排版分析、時間碼、原文切分比對的規則都寫在對應的
features/*.feature，由 behave 測。這裡只留 feature 測不到的:
自動處理的計數、feature 沒有例子的錯誤分類、病態組。
Fixture 都是從真語料抽出來的。
"""

import os
import unittest

from tests import DATA

from scripts.smkul.entry import IssueKind, NormKind, NormLog
from scripts.smkul.parser import (
    assemble_entry,
    bare_form,
    build_entry,
    normalize_en_dash,
    parse_text,
    parse_timecode,
    timecode_parts,
)


def load(name):
    path = os.path.join(DATA, name)
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def parse(name, log=None):
    return parse_text(load(name), path=name, log=log)


class TestTimecode(unittest.TestCase):
    """四種格式都要拆成開始/結束,而且保留原字串。"""

    def test_編號與時間碼同行(self):
        got = parse_timecode("1. 0:00:00.000,0:00:01.480")
        self.assertEqual(got[0], "1")
        self.assertEqual(got[1], "0:00:00.000")

    def test_不是時間碼(self):
        self.assertIsNone(parse_timecode("Kiya ha, Tku ita mnswayi"))
        self.assertIsNone(parse_timecode("1."))


class TestNormalize(unittest.TestCase):

    def test_沒有_endash_就不計數(self):
        log = NormLog()
        got = normalize_en_dash("PI-書-處焦", log, "a.txt", "79")
        self.assertEqual(got, "PI-書-處焦")
        self.assertEqual(log.records[NormKind.EN_DASH].count, 0)


class TestSplitEntries(unittest.TestCase):

    def test_典型_連字號式_會記單位不明(self):
        corpus = parse("典型_連字號式.txt")
        kinds = []
        for issue in corpus.issues:
            kinds.append(issue.kind)
        self.assertIn(IssueKind.UNKNOWN_TIMECODE_UNIT, kinds)
        self.assertEqual(corpus.entries[0].end, "00:04:21")

    def test_編號同行(self):
        corpus = parse("編號同行.txt")
        self.assertEqual(len(corpus.entries), 2)
        self.assertEqual(corpus.entries[0].number, "1")
        self.assertEqual(corpus.entries[1].number, "2")

    def test_格式中途切換會記_warning(self):
        corpus = parse("格式中途切換.txt")
        kinds = []
        for issue in corpus.issues:
            kinds.append(issue.kind)
        self.assertIn(IssueKind.MIXED_TIMECODE_FORMAT, kinds)

    def test_孤兒時間碼(self):
        corpus = parse("病態_孤兒時間碼.txt")
        orphans = []
        for entry in corpus.entries:
            for issue in entry.issues:
                if issue.kind is IssueKind.ORPHAN_TIMECODE:
                    orphans.append(issue)
        self.assertEqual(len(orphans), 1)

    def test_全形等號_解析後沒有全形(self):
        log = NormLog()
        corpus = parse("正規化_全形等號.txt", log)
        for entry in corpus.entries:
            for line in entry.body:
                self.assertNotIn("＝", line)
        self.assertTrue(log.records[NormKind.FULLWIDTH_EQUALS].count >= 1)


class TestAssemble(unittest.TestCase):
    """組四行:標準組、長句分段重組、重複標註。"""

    def assemble_all(self, name, log=None):
        corpus = parse(name, log)
        out = []
        for entry in corpus.entries:
            out.append((entry, assemble_entry(entry, log)))
        return out

    def test_endash_gloss_重組後換半形(self):
        log = NormLog()
        entry, ok = self.assemble_all("正規化_endash_gloss.txt", log)[0]
        self.assertTrue(ok)
        self.assertNotIn("–", entry.gloss)
        self.assertIn("PI-書-處焦", entry.gloss)
        self.assertEqual(log.records[NormKind.EN_DASH].count, 1)

    def test_重複標註_不可以組起來(self):
        """南排灣 4 第 156、157 組是同一句留兩版,不是換行。"""
        results = self.assemble_all("病態_重複標註.txt")
        self.assertEqual(len(results), 2)
        for entry, ok in results:
            self.assertFalse(ok)
            kinds = []
            for issue in entry.issues:
                kinds.append(issue.kind)
            self.assertIn(IssueKind.DUPLICATE_ANNOTATION, kinds)
            self.assertFalse(entry.is_clean())

    def test_病態組都組不起來(self):
        names = [
            "病態_黏行.txt",
            "病態_缺gloss段.txt",
            "病態_缺翻譯行.txt",
            "病態_雜訊行.txt",
        ]
        for name in names:
            for entry, ok in self.assemble_all(name):
                self.assertFalse(ok, name + " 第" + entry.number + "組")


class TestSourceSegmentation(unittest.TestCase):
    """嚴格用原文檢查切分:差一個字母或單引號就算錯誤。"""

    def check(self, name, index=0):
        corpus = parse(name)
        entry = corpus.entries[index]
        assemble_entry(entry)
        kinds = []
        for issue in entry.issues:
            kinds.append(issue.kind)
        return entry, kinds

    def test_bare_form_留單引號_去掉標點大小寫(self):
        self.assertEqual(bare_form("Kiya ha, Tku"), "kiyahatku")
        self.assertEqual(bare_form("’ana ne’a"), "'anane'a")
        self.assertEqual(
            bare_form("pi-sano-Amis a caciyaw awa=to"),
            "pisanoamisacaciyawawato",
        )


class TestClassify(unittest.TestCase):
    """組不起來的組,要分得出是哪一種異常。"""

    def kinds_of(self, name):
        corpus = parse(name)
        out = []
        for entry in corpus.entries:
            build_entry(entry)
            labels = []
            for issue in entry.issues:
                labels.append(issue.kind)
            out.append((entry.number, labels))
        return out

    def test_空組(self):
        got = self.kinds_of("病態_空組.txt")
        self.assertIn(IssueKind.EMPTY_ENTRY, got[0][1])
        # 第 2 組是正常ê組,毋過原文 `O na` 切分寫做 `Ona`,
        # 詞數對袂起來——照原文切分比對.feature「只差空白，先算
        # 不通過」彼條,這算「原文與切分不符」。
        self.assertEqual(
            got[1][1], [IssueKind.SOURCE_SEGMENT_MISMATCH])

    def test_孤兒時間碼(self):
        got = self.kinds_of("病態_孤兒時間碼.txt")
        self.assertIn(IssueKind.ORPHAN_TIMECODE, got[2][1])

    def test_雜訊行(self):
        got = self.kinds_of("病態_雜訊行.txt")
        self.assertIn(IssueKind.STRAY_LINE, got[0][1])

    def test_布農的_0000_也是雜訊(self):
        got = self.kinds_of("布農雜訊.txt")
        self.assertIn(IssueKind.STRAY_LINE, got[0][1])

    def test_純華語句_三種表法(self):
        got = self.kinds_of("病態_純華語句.txt")
        for number, labels in got:
            self.assertIn(IssueKind.CHINESE_ONLY, labels, number)

    def test_缺翻譯行(self):
        got = self.kinds_of("病態_缺翻譯行.txt")
        for number, labels in got:
            self.assertIn(IssueKind.MISSING_TRANSLATION, labels, number)

    def test_黏行(self):
        got = self.kinds_of("病態_黏行.txt")
        for number, labels in got:
            self.assertIn(IssueKind.GLUED_LINE, labels, number)

    def test_缺gloss段(self):
        got = self.kinds_of("病態_缺gloss段.txt")
        self.assertIn(IssueKind.MISSING_GLOSS_SEGMENT, got[0][1])

    def test_重複標註不會再分成別種(self):
        got = self.kinds_of("病態_重複標註.txt")
        for number, labels in got:
            self.assertEqual(labels, [IssueKind.DUPLICATE_ANNOTATION])

    def test_正常的組沒問題(self):
        for name in ("典型_srt式.txt", "長句分段.txt"):
            corpus = parse(name)
            for entry in corpus.entries:
                build_entry(entry)
                for issue in entry.issues:
                    self.assertIsNot(issue.kind, IssueKind.GLUED_LINE)


class TestPunctuation(unittest.TestCase):
    """標點不同:不擋匯出,但要記下來提出討論。"""

    def test_標點不同是_warning_不擋匯出(self):
        corpus = parse("典型_逗號式.txt")
        entry = corpus.entries[0]
        build_entry(entry)
        self.assertIn(",", entry.source)
        self.assertNotIn(",", entry.segmentation)
        kinds = []
        for issue in entry.issues:
            kinds.append(issue.kind)
        self.assertIn(IssueKind.PUNCTUATION_DIFF, kinds)
        self.assertNotIn(IssueKind.SOURCE_SEGMENT_MISMATCH, kinds)
        self.assertTrue(entry.is_clean())

    def test_標點相同就不記(self):
        corpus = parse("典型_srt式.txt")
        entry = corpus.entries[1]
        build_entry(entry)
        for issue in entry.issues:
            self.assertIsNot(issue.kind, IssueKind.PUNCTUATION_DIFF)


class TestReversedTimecode(unittest.TestCase):
    """結束時間比開始還早,是打錯ê。"""

    def test_時間碼拆做數字(self):
        self.assertEqual(timecode_parts("0:00:27.880"), (0, 0, 27, 880))
        self.assertEqual(timecode_parts("00:04:21"), (0, 4, 21))

    def test_正常ê時間碼無代誌(self):
        text = "1\n00:00:00-00:04:21\nkunaku\nkunaku\n我\n我\n"
        corpus = parse_text(text, path="t.txt")
        for issue in corpus.entries[0].issues:
            self.assertIsNot(issue.kind, IssueKind.REVERSED_TIMECODE)
