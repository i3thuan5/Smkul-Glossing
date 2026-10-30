"""測試 check_docx_txt.py 的報告章節，用語照 2026.09 會議案由四。"""

import unittest

from scripts import check_docx_txt


class TestTerms(unittest.TestCase):

    def test_依語言別統計表的欄名(self):
        got = check_docx_txt.variant_table([])
        self.assertEqual(
            got.splitlines()[0],
            "| 族別 | 語言別 | 檔數 | 有差異的段數 | 差異筆數 |",
        )

    def test_統計說明用段(self):
        self.assertIn("「有差異的段數」", check_docx_txt.VARIANT_NOTE)
        self.assertNotIn("組", check_docx_txt.VARIANT_NOTE)

    def test_章名是依語言別統計(self):
        self.assertEqual(check_docx_txt.VARIANT_TITLE, "依語言別統計")


if __name__ == "__main__":
    unittest.main()
