"""測試 yamlout.py:單一 YAML、華語 key、四層結構。"""

import os
import tempfile
import unittest

from tests import ODS

import yaml

from scripts.smkul.entry import CorpusFile, Entry, Issue, IssueKind
from scripts.smkul.markers import load_marker_lists
from scripts.smkul.rules import validate
from scripts.smkul import yamlout


def build_corpus():
    """對照 corpus-export spec 的秀姑巒第 26 組範例。"""
    markers = load_marker_lists(ODS)["阿美語"]
    good = Entry(
        number="26", start="00:02:09,410", end="00:02:12,547",
        path="a.txt",
        source="pisanoAmis a caciyaw awa to matini",
        segmentation="pi-sano-Amis a caciyaw awa=to matini",
        gloss="PI-像-族名 連繫詞 說話 沒有=完成貌 現在",
        translation="使用族語的情況已經少見了",
    )
    validate(good, markers, "阿美語")
    bad = Entry(number="27", start="0", end="1", path="a.txt")
    bad.issues.append(Issue(IssueKind.GLUED_LINE, "a.txt", "27"))
    return CorpusFile(
        path="阿美族/秀姑巒/陳美莉_阿星.阿曼_說族語在大漢部落的過.txt",
        ethnic="阿美", variant="秀姑巒",
        entries=[good, bad],
    )


class TestBuild(unittest.TestCase):

    def setUp(self):
        self.data = yamlout.build([build_corpus()])

    def test_最外層是檔案(self):
        self.assertEqual(list(self.data), ["檔案"])
        self.assertEqual(len(self.data["檔案"]), 1)

    def test_檔案層的_key(self):
        item = self.data["檔案"][0]
        self.assertEqual(
            sorted(item), sorted(["路徑", "族別", "語別", "檔頭註記", "句"]))
        self.assertEqual(item["族別"], "阿美")
        self.assertEqual(item["語別"], "秀姑巒")

    def test_只收通過驗證的組(self):
        sentences = self.data["檔案"][0]["句"]
        self.assertEqual(len(sentences), 1)
        self.assertEqual(sentences[0]["編號"], "26")

    def test_句層的_key(self):
        sentence = self.data["檔案"][0]["句"][0]
        self.assertEqual(sentence["開始"], "00:02:09,410")
        self.assertEqual(sentence["結束"], "00:02:12,547")
        self.assertEqual(sentence["翻譯"], "使用族語的情況已經少見了")

    def test_詞與詞素四層(self):
        words = self.data["檔案"][0]["句"][0]["詞"]
        self.assertEqual(len(words), 5)
        first = words[0]
        self.assertEqual(first["原詞"], "pisanoAmis")
        self.assertEqual(first["切分"], "pi-sano-Amis")
        self.assertEqual(len(first["詞素"]), 3)
        self.assertEqual(
            first["詞素"][2],
            {"形": "Amis", "義": "族名", "構詞": "詞根"},
        )

    def test_附著詞的原詞會併寫(self):
        words = self.data["檔案"][0]["句"][0]["詞"]
        self.assertEqual(words[3]["原詞"], "awato")
        self.assertEqual(words[3]["切分"], "awa=to")

    def test_全部沒過的檔案不出現(self):
        empty = CorpusFile(path="b.txt", ethnic="阿美", variant="海岸")
        data = yamlout.build([empty])
        self.assertEqual(data["檔案"], [])


class TestDump(unittest.TestCase):

    def test_華語不會被轉義(self):
        text = yamlout.dump(yamlout.build([build_corpus()]))
        self.assertIn("族別: 阿美", text)
        self.assertNotIn("\\u", text)

    def test_讀得回來(self):
        text = yamlout.dump(yamlout.build([build_corpus()]))
        back = yaml.safe_load(text)
        self.assertEqual(back["檔案"][0]["句"][0]["編號"], "26")

    def test_寫成單一檔案(self):
        with tempfile.TemporaryDirectory() as out_dir:
            path, files, sentences = yamlout.write(
                [build_corpus()], out_dir=out_dir)
            self.assertTrue(os.path.exists(path))
            self.assertEqual(files, 1)
            self.assertEqual(sentences, 1)
            self.assertEqual(len(os.listdir(out_dir)), 1)


if __name__ == "__main__":
    unittest.main()
