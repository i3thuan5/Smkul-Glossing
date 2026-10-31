"""測試 validate_glossing.py 的報告章節，對照 corpus-export「報告內容」。"""

import os
import shutil
import tempfile
import unittest

from tests import DATA

from scripts import validate_glossing
from scripts.smkul import proofreading
from scripts.smkul.entry import Issue, IssueKind, NormLog

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

    def test_討論與比對說明沒有舊用語(self):
        got = (validate_glossing.todo_section([], total_entries=0) +
               validate_glossing.COMPARE_NOTE)
        for old in ("切分", "gloss", "原文", "構詞符號"):
            self.assertNotIn(old, got)
        self.assertNotRegex(got, OLD_UNIT)


class TestSegmentPunctuation(unittest.TestCase):
    """2026.09 會議案由五:詞素切割行不能有標點。"""

    def issues(self):
        return [
            Issue(IssueKind.SEGMENT_PUNCTUATION, "a.docx", "12", "標點"),
            Issue(IssueKind.MIXED_TIMECODE_FORMAT, "a.docx"),
        ]

    def test_總覽分四級(self):
        got = validate_glossing.overview([], self.issues(), 0, 0)
        self.assertIn("- 錯誤（不匯出）:0 筆", got)
        self.assertIn("- 錯誤（照常匯出）:1 筆", got)
        self.assertIn("- 警告（照常匯出）:1 筆", got)
        self.assertNotIn("warning", got)

    def test_沒有標點不同(self):
        got = (validate_glossing.overview([], self.issues(), 0, 0) +
               validate_glossing.todo_section(self.issues(), 0) +
               validate_glossing.COMPARE_NOTE)
        self.assertNotIn("標點不同", got)
        self.assertNotIn("句讀慣例", got)
        self.assertNotIn("warning", got)

    def test_需要修正的標注列出詞素切割有標點(self):
        got = validate_glossing.todo_section(self.issues(), 0)
        self.assertIn("| 詞素切割有標點 | 1 |", got)

    def test_待討論章有三節(self):
        got = validate_glossing.discuss_chapter([])
        self.assertIn("待討論：詞素切割的特殊符號", got)
        for label in ("`+`", "詞中間的 `.`", "說話者標記"):
            self.assertIn(label, got)


class TestProofreading(unittest.TestCase):
    """校對表的判斷讀回來之後,驗證結果跟著變(proofreading spec)。"""

    def setUp(self):
        self.base = tempfile.mkdtemp()
        folder = os.path.join(self.base, "阿美族", "秀姑巒")
        os.makedirs(folder)
        shutil.copy(os.path.join(DATA, "最小範例.docx"), folder)

    def tearDown(self):
        shutil.rmtree(self.base)

    def collect(self, judgements=None):
        return validate_glossing.collect(self.base, NormLog(), judgements)

    def mismatch_id(self):
        files, issues, mismatch, proof = self.collect()
        for issue in issues:
            if issue.kind is IssueKind.SOURCE_SEGMENT_MISMATCH:
                return issue.id
        self.fail("最小範例第 25 段應該有族語原句與詞素切割不符")

    def judged(self, judgement):
        issue_id = self.mismatch_id()
        return issue_id, {issue_id: proofreading.Judgement(
            issue_id, judgement, "備註", {}, "校對.xlsx", 2, 0)}

    def test_每筆問題都有_id(self):
        files, issues, mismatch, proof = self.collect()
        self.assertTrue(issues)
        for issue in issues:
            self.assertRegex(issue.id, r"^ISSUE-[0-9a-f]{8}$")
        self.assertEqual(len(proof.rows), len(issues))

    def test_程式判斷錯的不算問題_段照常匯出(self):
        issue_id, judgements = self.judged(proofreading.PROGRAM_WRONG)
        files, issues, mismatch, proof = self.collect(judgements)
        for issue in issues:
            self.assertNotEqual(issue.id, issue_id)
        self.assertEqual(len(proof.confirmed), 1)
        for entry in files[0].entries:
            self.assertTrue(entry.is_clean(), entry.number)
        ids = []
        for row in proof.rows:
            ids.append(row.issue.id)
        self.assertIn(issue_id, ids)

    def test_要討論的照常算_另外收起來(self):
        issue_id, judgements = self.judged(proofreading.DISCUSS)
        files, issues, mismatch, proof = self.collect(judgements)
        ids = []
        for issue in issues:
            ids.append(issue.id)
        self.assertIn(issue_id, ids)
        self.assertEqual(len(proof.discussed), 1)

    def test_校對流程一節(self):
        got = validate_glossing.proofreading_section()
        self.assertIn("校對流程", got)
        self.assertIn("kithann/out/校對表/", got)
        self.assertIn("kithann/校對/", got)
        for choice in proofreading.CHOICES:
            self.assertIn(choice, got)

    def test_兩章沒有資料寫無_確認過的在後面(self):
        empty = validate_glossing.Proof([], [], [])
        chapters = validate_glossing.proof_chapters(empty, [])
        self.assertTrue(chapters[0].startswith("## 老師標要討論的項目"))
        self.assertTrue(chapters[1].startswith("## 老師確認過、不是錯誤"))
        for chapter in chapters:
            self.assertIn("（無）", chapter)


if __name__ == "__main__":
    unittest.main()
