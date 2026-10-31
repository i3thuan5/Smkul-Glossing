"""測試 validate_glossing.py 的報告章節，對照 corpus-export「報告內容」。"""

import os
import shutil
import tempfile
import unittest

from tests import DATA

from scripts import validate_glossing
from scripts.smkul import proofreading, report
from scripts.smkul.entry import Issue, IssueKind, NormLog

# 「組」改稱「段」。重組、分組、組成、組裝是動詞，不算。
OLD_UNIT = r"(?<![重分])組(?![成裝合起])"


class TestNoMorphology(unittest.TestCase):
    """報告不出現構詞資訊（2026.09 會議案由九）。"""

    def test_總覽沒有構詞(self):
        got = validate_glossing.overview([], [], 0, 0)
        self.assertNotIn("構詞", got)


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

    def test_比對說明沒有舊用語(self):
        got = validate_glossing.COMPARE_NOTE
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
               validate_glossing.COMPARE_NOTE)
        self.assertNotIn("標點不同", got)
        self.assertNotIn("句讀慣例", got)
        self.assertNotIn("warning", got)

    def test_待討論章有三節(self):
        got = validate_glossing.discuss_chapter([])
        self.assertIn("待討論：詞素切割的特殊符號", got)
        for label in ("`+`", "詞中間的 `.`", "說話者標記"):
            self.assertIn(label, got)


class TestOverview(unittest.TestCase):
    """總覽:翻譯訓練YAML 的說法、嚴重度對應表(features/分析報告.feature)。"""

    def test_改稱翻譯訓練YAML(self):
        got = validate_glossing.overview([], [], 0, 0)
        self.assertIn("已匯出翻譯訓練YAML", got)
        self.assertNotIn("已匯出 YAML", got)

    def test_有嚴重度對應表(self):
        got = validate_glossing.overview([], [], 0, 0)
        self.assertIn("| 嚴重度 | 翻譯訓練YAML | 報告舉例 | 請老師校對 |", got)
        self.assertIn("| 錯誤（照常匯出） | 匯出 | 舉例 | 要 |", got)
        self.assertIn("| 現象 | 不匯出 | 舉例 | 不要 |", got)

    def test_第7章的順序跟問題表一樣(self):
        issues = [
            Issue(IssueKind.CHINESE_ONLY, "a.docx", "1"),
            Issue(IssueKind.CHINESE_ONLY, "a.docx", "2"),
            Issue(IssueKind.GLUED_LINE, "a.docx", "3"),
            Issue(IssueKind.SOURCE_SEGMENT_MISMATCH, "a.docx", "4",
                  "詞數不同:"),
        ]
        got = validate_glossing.kinds_section(issues)
        titles = []
        for line in got.splitlines():
            if line.startswith("### "):
                titles.append(line[4:].split("(")[0])
        self.assertEqual(titles, report.ordered_labels(issues))


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
        # 老師確認過的問題只留在校對表,報告不另外列(proofreading spec)。
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

    def test_校對流程一節(self):
        got = validate_glossing.proofreading_section([])
        self.assertIn("校對流程", got)
        self.assertIn("kithann/out/校對表/", got)
        self.assertIn("kithann/校對/", got)
        for choice in proofreading.CHOICES:
            self.assertIn(choice, got)

    def test_沒有讀回提醒就不寫(self):
        got = validate_glossing.proofreading_section([])
        self.assertNotIn("讀回校對表時的提醒", got)

    def test_讀回提醒列在校對流程最後(self):
        got = validate_glossing.proofreading_section(
            ["排灣.xlsx 「校對」分頁第 2 列的判斷「誤報」不是三個選項之一"])
        self.assertIn("讀回校對表時的提醒", got)
        self.assertGreater(got.index("「誤報」"), got.index("kithann/校對/"))


class TestChapters(unittest.TestCase):
    """corpus-export「glossing 報告的章節」:用最小範例跑一次 run()。"""

    def test_章節與刪掉的部分(self):
        work = tempfile.mkdtemp()
        try:
            folder = os.path.join(work, "giliau", "阿美族", "秀姑巒")
            os.makedirs(folder)
            shutil.copy(os.path.join(DATA, "最小範例.docx"), folder)
            out_dir = os.path.join(work, "out")
            validate_glossing.run(
                os.path.join(work, "giliau"),
                proof_dir=os.path.join(work, "校對"), out_dir=out_dir)
            with open(os.path.join(out_dir, "glossing_report.md"),
                      encoding="utf-8") as handle:
                got = handle.read()
            names = sorted(os.listdir(out_dir))
        finally:
            shutil.rmtree(work)
        titles = []
        for line in got.splitlines():
            if line.startswith("## "):
                titles.append(line.split(". ", 1)[1])
        self.assertEqual(titles, [
            "總覽", "依語言別統計", "翻譯訓練YAML 輸出", "校對流程",
            "語料格式說明", "自動處理與比對政策", "問題類型說明與例子",
            "待討論：詞素切割的特殊符號",
        ])
        self.assertNotIn("標記清單", got)
        self.assertEqual(names, ["corpus.yaml", "glossing_report.md", "校對表"])


if __name__ == "__main__":
    unittest.main()
