"""全語料冒煙測試。

語料不在版控內，而且對方會陸續交付新版語料（一版一個目錄），所以
語料目錄由環境變數 SMKUL_CORPUS 指定，沒設就 skip:

    SMKUL_CORPUS=kithann/語料標註語料_20261118 python -m unittest

相對路徑以專案根目錄為準。有設但目錄不存在時測試失敗，不 skip，
免得打錯字卻以為測過了。

這裡只驗換版也要成立的通用性質，不驗某一版語料的檔案數、筆數。
"""

import os
import unittest
from collections import Counter

from scripts.smkul.entry import NormKind, NormLog
from scripts.smkul.parser import parse_corpus_file

ENV = "SMKUL_CORPUS"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def corpus_dir():
    """環境變數指定的語料目錄，轉成絕對路徑。沒設回傳空字串。"""
    value = os.environ.get(ENV, "")
    if not value:
        return ""
    return os.path.join(ROOT, value)


def docx_files(base):
    out = []
    for root, dirs, names in os.walk(base):
        for name in sorted(names):
            if name.endswith(".docx"):
                out.append(os.path.join(root, name))
    out.sort()
    return out


@unittest.skipUnless(corpus_dir(), "沒指定語料目錄（環境變數 " + ENV + "）")
class TestCorpusSmoke(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        base = corpus_dir()
        if not os.path.isdir(base):
            raise AssertionError(ENV + " 指定的語料目錄不存在：" + base)
        cls.log = NormLog()
        cls.files = []
        cls.kinds = Counter()
        for path in docx_files(base):
            rel = path[len(base.rstrip(os.sep)) + 1:]
            corpus = parse_corpus_file(path, rel, log=cls.log)
            cls.files.append(corpus)
            for issue in corpus.issues:
                cls.kinds[issue.kind.value] += 1
            for entry in corpus.entries:
                for issue in entry.issues:
                    cls.kinds[issue.kind.value] += 1

    def test_每個檔案都解析得出段(self):
        self.assertTrue(self.files, "語料目錄裡沒有 docx")
        for corpus in self.files:
            self.assertTrue(corpus.entries, corpus.path)

    def test_每一段都有時間碼(self):
        for corpus in self.files:
            for entry in corpus.entries:
                self.assertTrue(entry.start, corpus.path)
                self.assertTrue(entry.end, corpus.path)

    def test_已知的問題種類都偵測得到(self):
        # 對方把某一種問題全部修好時，這裡會紅，那時候拿掉那一種。
        for label in ("行黏在一起", "缺詞素翻譯行", "缺華語翻譯行", "空段",
                      "孤兒時間碼", "孤立雜訊行", "純華語句",
                      "族語原句與詞素切割不符"):
            self.assertGreater(self.kinds[label], 0, label)

    def test_自動處理都有記下來(self):
        # docx 抽出來的內文沒有 BOM,所以那一項是 0 筆，規則仍然保留。
        self.assertEqual(self.log.records[NormKind.BOM].count, 0)
        self.assertGreater(
            self.log.records[NormKind.LONG_ENTRY_REJOIN].count, 0)
        self.assertGreater(self.log.records[NormKind.APOSTROPHE].count, 0)
        self.assertGreater(self.log.records[NormKind.EN_DASH].count, 0)


if __name__ == "__main__":
    unittest.main()
