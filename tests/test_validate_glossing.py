"""測試 validate_glossing.py 的報告章節，對照 corpus-export「報告內容」。"""

import unittest

from scripts import validate_glossing
from scripts.smkul.entry import Issue, IssueKind

# 「組」改稱「段」。重組、分組、組成、組裝是動詞，不算。
OLD_UNIT = r"(?<![重分])組(?![成裝合起])"


class TestNoMorphology(unittest.TestCase):
    """報告不出現構詞資訊（2026.09 會議案由九）。"""

    def test_總覽沒有構詞(self):
        got = validate_glossing.overview([], [], 0, 0)
        self.assertNotIn("構詞", got)

    def test_請對方處理沒有構詞判斷困難(self):
        got = validate_glossing.todo_section([], total_entries=0)
        self.assertNotIn("構詞判斷困難的詞素要怎麼處理", got)
        self.assertNotIn("構詞", got)

    def test_請對方處理沒有用語討論(self):
        """用語已在 2026.09 會議案由四決議。"""
        got = validate_glossing.todo_section([], total_entries=0)
        self.assertNotIn("用語要不要換成語言學的標準說法", got)


class TestTerms(unittest.TestCase):
    """用語照 2026.09 會議案由四。"""

    def test_總覽用段(self):
        got = validate_glossing.overview([], [], 0, 0)
        self.assertIn("語料段數", got)
        self.assertNotRegex(got, OLD_UNIT)

    def test_依語言別統計表的欄名(self):
        self.assertEqual(
            validate_glossing.VARIANT_HEADERS,
            ["族別", "語言別", "檔數", "段數", "通過", "有問題", "通過率"],
        )

    def test_需要修正的標注用新分類名(self):
        issues = [
            Issue(IssueKind.GLOSS_FEWER, "a.docx", "20"),
            Issue(IssueKind.MISSING_GLOSS_LINE, "a.docx", "98"),
            Issue(IssueKind.SOURCE_SEGMENT_MISMATCH, "a.docx", "8",
                  "只差一個字母:「l」→「r」"),
        ]
        got = validate_glossing.todo_section(issues, total_entries=3)
        self.assertIn("| 詞素翻譯的詞比詞素切割少 | 1 |", got)
        self.assertIn("| 缺詞素翻譯行 | 1 |", got)
        self.assertIn("| 族語原句與詞素切割不符-只差一個字母 | 1 |", got)
        self.assertIn("詞素切割行的句讀慣例", got)

    def test_討論與比對說明沒有舊用語(self):
        got = (validate_glossing.todo_section([], total_entries=0) +
               validate_glossing.COMPARE_NOTE)
        for old in ("切分", "gloss", "原文", "構詞符號"):
            self.assertNotIn(old, got)
        self.assertNotRegex(got, OLD_UNIT)


if __name__ == "__main__":
    unittest.main()
