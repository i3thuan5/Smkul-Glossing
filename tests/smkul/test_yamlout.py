"""測試 yamlout.py:單一 YAML、華語 key、檔案 → 段 兩層。"""

import os
import tempfile
import unittest

import yaml

from scripts.smkul.entry import CorpusFile, Entry, Issue, IssueKind
from scripts.smkul.rules import validate
from scripts.smkul import yamlout


def build_corpus():
    """對照 corpus-export spec「YAML 匯出結構」的秀姑巒第 26 段範例。"""
    good = Entry(
        number="26", start="00:02:09,410", end="00:02:12,547",
        path="a.txt",
        source="pisanoAmis a caciyaw awa to matini",
        segmentation="pi-sano-Amis a caciyaw awa=to matini",
        gloss="PI-像-族名 連繫詞 說話 沒有=完成貌 現在",
        translation="使用族語的情況已經少見了",
    )
    validate(good)
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
            list(item),
            ["路徑", "族別", "語言別", "語言別代號", "檔頭註記", "段"])
        self.assertEqual(item["族別"], "阿美")
        self.assertEqual(item["語言別"], "秀姑巒")
        self.assertEqual(item["語言別代號"], "ami-x-skl")

    def test_只收通過驗證的段(self):
        segments = self.data["檔案"][0]["段"]
        self.assertEqual(len(segments), 1)
        self.assertEqual(segments[0]["編號"], "26")

    def test_段層的_key(self):
        segment = self.data["檔案"][0]["段"][0]
        self.assertEqual(
            list(segment),
            ["編號", "開始", "結束", "族語原句", "詞素切割", "詞素翻譯",
             "華語翻譯"],
        )
        self.assertEqual(segment["開始"], "00:02:09,410")
        self.assertEqual(segment["結束"], "00:02:12,547")
        self.assertEqual(
            segment["詞素切割"], "pi-sano-Amis a caciyaw awa=to matini")
        self.assertEqual(segment["華語翻譯"], "使用族語的情況已經少見了")

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
        self.assertEqual(back["檔案"][0]["段"][0]["編號"], "26")

    def test_四行各占一行(self):
        text = yamlout.dump(yamlout.build([build_corpus()]))
        self.assertIn(
            "\n    詞素切割: pi-sano-Amis a caciyaw awa=to matini\n", text)
        self.assertIn(
            "\n    詞素翻譯: PI-像-族名 連繫詞 說話 沒有=完成貌 現在\n", text)

    def test_寫成單一檔案(self):
        with tempfile.TemporaryDirectory() as out_dir:
            path, files, segments = yamlout.write(
                [build_corpus()], out_dir=out_dir)
            self.assertTrue(os.path.exists(path))
            self.assertEqual(files, 1)
            self.assertEqual(segments, 1)
            self.assertEqual(len(os.listdir(out_dir)), 1)


if __name__ == "__main__":
    unittest.main()
