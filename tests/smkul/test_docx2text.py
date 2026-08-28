"""測試 docx2text.py。Fixture 是最小的 docx,內容取自秀姑巒真語料。"""

import os
import unittest

from tests import DATA

from scripts.smkul.docx2text import (
    docx_comments,
    docx_paragraphs,
    docx_text,
)
from scripts.smkul.parser import build_entry, parse_text

SMALL = os.path.join(DATA, "最小範例.docx")


class TestDocxParagraphs(unittest.TestCase):

    def test_每段照順序(self):
        paras = docx_paragraphs(SMALL)
        self.assertEqual(paras[0], "25")
        self.assertEqual(paras[1], "00:02:03,146 --> 00:02:09,410")
        self.assertEqual(paras[7], "26")

    def test_空段也要保留(self):
        paras = docx_paragraphs(SMALL)
        self.assertEqual(paras[6], "")

    def test_同一段的_run_會合併(self):
        """docx 常把一行拆成好幾個 run,要接回來。"""
        paras = docx_paragraphs(SMALL)
        self.assertEqual(
            paras[10], "pi-sano-Amis a caciyaw awa=to matini")

    def test_寬空白保留給_parser_去合併(self):
        paras = docx_paragraphs(SMALL)
        self.assertIn("     ", paras[11])

    def test_docx_text_是一行一行(self):
        text = docx_text(SMALL)
        self.assertEqual(len(text.splitlines()), 13)


class TestDocxIntoParser(unittest.TestCase):
    """docx 抽出來的文字要用同一個 parser。"""

    def test_docx_解析結果與_txt_同構(self):
        corpus = parse_text(docx_text(SMALL), path="最小範例.docx")
        self.assertEqual(len(corpus.entries), 2)
        for entry in corpus.entries:
            build_entry(entry)
        second = corpus.entries[1]
        self.assertEqual(second.number, "26")
        self.assertEqual(second.start, "00:02:09,410")
        self.assertEqual(
            second.segmentation, "pi-sano-Amis a caciyaw awa=to matini")
        self.assertEqual(
            second.gloss, "PI-像-族名 連繫詞 說話 沒有=完成貌 現在")
        self.assertTrue(second.is_clean())


if __name__ == "__main__":
    unittest.main()


WITH_COMMENTS = os.path.join(DATA, "有註解.docx")


class TestDocxComments(unittest.TestCase):
    """docx 有審閱註解,txt 只留 [a] 這種錨點,註解本身不見了。"""

    def test_沒有註解的檔案回傳空的(self):
        self.assertEqual(docx_comments(SMALL), [])

    def test_照文件順序配字母(self):
        found = docx_comments(WITH_COMMENTS)
        self.assertEqual(len(found), 2)
        self.assertEqual(found[0]["字母"], "a")
        self.assertEqual(found[0]["內容"], "主焦.來")
        self.assertEqual(found[0]["作者"], "Megan G")
        self.assertEqual(found[0]["日期"], "2026-04-08")
        self.assertEqual(found[1]["字母"], "b")
        self.assertEqual(found[1]["內容"], "加 完成貌")

    def test_錨點字母對得上註解(self):
        found = docx_comments(WITH_COMMENTS)
        letters = []
        for item in found:
            letters.append("[" + item["字母"] + "]")
        with open(os.path.join(DATA, "有錨點.txt"), encoding="utf-8") as f:
            text = f.read()
        for letter in letters:
            self.assertIn(letter, text)
