"""測試 docx2text.py。Fixture 是最小的 docx,內容取自秀姑巒真語料。"""

import os
import unittest

from tests import DATA

from scripts.smkul.docx2text import (
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


WITH_COMMENTS = os.path.join(DATA, "有註解.docx")


class TestNoComments(unittest.TestCase):
    """docx 的審閱註解不會混進內文(corpus-parsing「語料來源為 docx」)。

    審閱註解抽取(docx_comments)隨 docx／txt 一致性檢查一起刪掉
    (docx-txt-consistency 全部 REMOVED,2026.09 會議案由二忽略註解)。
    """

    def test_內文沒有註解本文(self):
        text = docx_text(WITH_COMMENTS)
        self.assertNotIn("加 完成貌", text)
        self.assertNotIn("Megan G", text)
        self.assertIn("qadjaw ka liaw nia=aya", text)


if __name__ == "__main__":
    unittest.main()
