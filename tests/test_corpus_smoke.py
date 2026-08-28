"""全語料冒煙測試。語料不在版控內,所以找不到時 skip。"""

import os
import unittest
from collections import Counter

from scripts.smkul.entry import NormKind, NormLog
from scripts.smkul.parser import parse_corpus_file

BASE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "kithann", "giliau",
)


def docx_files():
    out = []
    for root, dirs, names in os.walk(BASE):
        for name in sorted(names):
            if name.endswith(".docx"):
                out.append(os.path.join(root, name))
    out.sort()
    return out


@unittest.skipUnless(os.path.isdir(BASE), "找不到語料 kithann/giliau")
class TestCorpusSmoke(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.log = NormLog()
        cls.files = []
        cls.kinds = Counter()
        cls.total = 0
        cls.clean = 0
        for path in docx_files():
            rel = path[len(BASE) + 1:]
            corpus = parse_corpus_file(path, rel, log=cls.log)
            cls.files.append(corpus)
            for issue in corpus.issues:
                cls.kinds[issue.kind.value] += 1
            for entry in corpus.entries:
                cls.total += 1
                if entry.is_clean():
                    cls.clean += 1
                for issue in entry.issues:
                    cls.kinds[issue.kind.value] += 1

    def test_三十一个檔案攏解析會過(self):
        # 語料ê來源是 docx:31 个,比 txt 加一个太魯閣 2。
        self.assertEqual(len(self.files), 31)
        for corpus in self.files:
            self.assertTrue(corpus.entries, corpus.path)

    def test_組數(self):
        self.assertGreater(self.total, 7000)
        self.assertGreater(self.clean, self.total // 2)

    def test_每一組都有時間碼(self):
        for corpus in self.files:
            for entry in corpus.entries:
                self.assertTrue(entry.start, corpus.path)
                self.assertTrue(entry.end, corpus.path)

    def test_已知的異常都找得到(self):
        self.assertEqual(self.kinds["重複標註"], 13)
        self.assertEqual(self.kinds["時間碼單位不明"], 2)
        self.assertEqual(self.kinds["時間碼格式混用"], 1)
        for label in ("行黏在一起", "缺 gloss 段", "缺翻譯行", "空組",
                      "孤兒時間碼", "孤立雜訊行", "純華語句",
                      "原文與切分不符"):
            self.assertGreater(self.kinds[label], 0, label)

    def test_重複標註都在南排灣四(self):
        for corpus in self.files:
            for entry in corpus.entries:
                for issue in entry.issues:
                    if issue.kind.value == "重複標註":
                        self.assertIn("南排灣/4_", corpus.path)

    def test_海岸二有十二個孤兒時間碼(self):
        found = 0
        for corpus in self.files:
            if "海岸/2_" not in corpus.path:
                continue
            for entry in corpus.entries:
                for issue in entry.issues:
                    if issue.kind.value == "孤兒時間碼":
                        found += 1
        self.assertEqual(found, 12)

    def test_自動處理都有記下來(self):
        # docx 抽出來ê內文無 BOM,所以彼項是 0 筆,規則猶原留咧。
        self.assertEqual(self.log.records[NormKind.BOM].count, 0)
        self.assertGreater(
            self.log.records[NormKind.LONG_ENTRY_REJOIN].count, 800)
        self.assertGreater(self.log.records[NormKind.APOSTROPHE].count, 0)
        self.assertGreater(self.log.records[NormKind.EN_DASH].count, 0)


if __name__ == "__main__":
    unittest.main()
