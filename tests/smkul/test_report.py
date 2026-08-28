"""測試 report.py 的組件。"""

import unittest
from collections import Counter

from scripts.smkul.entry import (
    CorpusFile,
    Issue,
    IssueKind,
    NormKind,
    NormLog,
    Severity,
    code,
)
from scripts.smkul import report


class TestCode(unittest.TestCase):

    def test_語料用反引號包起來(self):
        self.assertEqual(code("s<in>tupa"), "`s<in>tupa`")

    def test_內容裡的反引號換成單引號(self):
        self.assertEqual(code("a`b"), "`a'b`")


class TestTable(unittest.TestCase):

    def test_表格(self):
        got = report.table(["甲", "乙"], [("1", "2")])
        self.assertEqual(
            got.splitlines(),
            ["| 甲 | 乙 |", "| --- | --- |", "| 1 | 2 |"],
        )

    def test_直線要跳脫(self):
        got = report.table(["甲"], [("a|b",)])
        self.assertIn("a\\|b", got)


class TestSections(unittest.TestCase):

    def build_issues(self):
        return [
            Issue(IssueKind.GLUED_LINE, "a.txt", "26", "黏著"),
            Issue(IssueKind.GLUED_LINE, "a.txt", "34", "也黏在一起"),
            Issue(IssueKind.PUNCTUATION_DIFF, "b.txt", "1", "標點"),
            Issue(IssueKind.CHINESE_ONLY, "b.txt", "112", "華語"),
        ]

    def test_依嚴重度分(self):
        errors, warnings, notices = report.severity_split(self.build_issues())
        self.assertEqual(len(errors), 2)
        self.assertEqual(len(warnings), 1)
        self.assertEqual(len(notices), 1)
        for issue in errors:
            self.assertIs(issue.severity, Severity.ERROR)

    def test_依檔案分組(self):
        groups = report.group_by_path(self.build_issues())
        self.assertEqual(list(groups), ["a.txt", "b.txt"])
        self.assertEqual(len(groups["a.txt"]), 2)

    def test_明細有定位到編號(self):
        got = report.detail_section("明細", self.build_issues())
        self.assertIn("### a.txt(2 筆)", got)
        self.assertIn("第26組", got)
        self.assertIn("**行黏在一起**", got)

    def test_沒問題時也有這一章(self):
        got = report.detail_section("明細", [])
        self.assertIn("(無)", got)

    def test_自動處理_沒發生的項目也要列(self):
        log = NormLog()
        log.note(NormKind.EN_DASH, "PI–書", "PI-書", "a.txt", "79")
        got = report.norm_section(log)
        for kind in NormKind:
            self.assertIn(kind.value, got)
        self.assertIn("這次影響:1 筆", got)
        self.assertIn("這次影響:0 筆", got)

    def test_自動處理逐項指去_feature(self):
        """例只寫tī feature,報告干焦指路,兩爿才袂各寫一份。"""
        got = report.norm_section(NormLog())
        self.assertIn("features/字元正規化.feature", got)
        self.assertIn("features/排版分析.feature", got)
        self.assertIn("features/時間碼.feature", got)

    def test_yaml_來源有寫理由(self):
        self.assertIn("docx", report.YAML_SOURCE_WHY)
        self.assertIn("comments.xml", report.YAML_SOURCE_WHY)


class TestTidy(unittest.TestCase):

    def test_連續空行合併成一行(self):
        got = report._tidy("a\n\n\n\nb\n\n")
        self.assertEqual(got, "a\n\nb\n")


if __name__ == "__main__":
    unittest.main()


class TestCompareLines(unittest.TestCase):
    """txt / docx 這款對照要分成獨立的子項,比較好看。"""

    def test_compare_分兩行(self):
        issue = Issue(
            IssueKind.CONTENT_DIFF, "a.txt", "180", "第 5 行不同",
            [("txt", "181. [e]"), ("docx", "")],
        )
        got = report.detail_section("明細", [issue])
        self.assertIn("- 第180組|**內容差異**:第 5 行不同", got)
        self.assertIn("  - txt:`181. [e]`", got)
        self.assertIn("  - docx:``", got)

    def test_無_compare_就一行(self):
        issue = Issue(IssueKind.MISSING_FILE, "a", "", "只有 docx,沒有 txt")
        got = report.detail_section("明細", [issue])
        self.assertIn("- 整個檔案|**缺檔**:只有 docx,沒有 txt", got)
        self.assertNotIn("  - ", got)


class TestAggregation(unittest.TestCase):
    """glossing 報告專屬的兩個統計區。"""

    def test_不確定標記統計(self):
        counter = Counter()
        counter[("PI", "阿美語")] = 95
        counter[("AN", "排灣語")] = 213
        got = report.uncertain_section(counter)
        self.assertIn("| `AN` | 排灣語 | 213 |", got)
        self.assertIn("不算錯誤", got)

    def test_不確定標記無資料(self):
        self.assertIn("(無)", report.uncertain_section(Counter()))

    def test_構詞判斷困難依次數排序(self):
        case = "每一段都被標成詞綴"
        records = [
            ("還", "布農語", case, "na-還", "a.docx", "8"),
            ("還", "布農語", case, "na-還", "a.docx", "9"),
            ("還", "布農語", case, "na-還", "b.docx", "3"),
            ("還", "布農語", case, "na-還", "b.docx", "5"),
            ("媽媽", "排灣語", case, "tja=媽媽", "c.docx", "1"),
        ]
        got = report.hard_morphology_section(records)
        first = got.index("`還`")
        second = got.index("`媽媽`")
        self.assertLess(first, second)
        self.assertIn("| `還` | 布農語 | 4 | 2 |", got)
        self.assertIn("features/構詞判定.feature", got)
        self.assertIn("建議補充到《常用構詞標記清單》", got)

    def test_構詞判斷困難最多列三個實例(self):
        records = []
        for number in range(10):
            records.append(
                ("還", "布農語", "每一段都被標成詞綴", "na-還",
                 "a.docx", str(number)))
        got = report.hard_morphology_section(records)
        self.assertEqual(got.count("a.docx 第"), 3)

    def test_構詞判斷困難無資料(self):
        self.assertIn("(無)", report.hard_morphology_section([]))


class TestNumbering(unittest.TestCase):
    """章節編號:開會時可以直接說「第 5.3 節」。"""

    def test_大小章節編號(self):
        body = "# 標題\n\n## 總覽\n\n## 明細\n\n### 甲檔\n\n### 乙檔"
        got = report.number_headings(body).splitlines()
        self.assertEqual(got[0], "# 標題")
        self.assertEqual(got[2], "## 1. 總覽")
        self.assertEqual(got[4], "## 2. 明細")
        self.assertEqual(got[6], "### 2.1 甲檔")
        self.assertEqual(got[8], "### 2.2 乙檔")

    def test_小節編號會跟著大節重來(self):
        body = "## 甲\n\n### 一\n\n## 乙\n\n### 二"
        got = report.number_headings(body).splitlines()
        self.assertEqual(got[2], "### 1.1 一")
        self.assertEqual(got[6], "### 2.1 二")

    def test_程式碼區塊內的井號不動(self):
        body = "## 甲\n\n```text\n## 這不是章節\n```\n\n## 乙"
        got = report.number_headings(body).splitlines()
        self.assertEqual(got[3], "## 這不是章節")
        self.assertEqual(got[6], "## 2. 乙")


class TestToday(unittest.TestCase):
    """報告開頭的更新日期。"""

    def test_是_iso_格式的日期(self):
        got = report.today()
        self.assertRegex(got, r"^\d{4}-\d{2}-\d{2}$")


class TestFormatSection(unittest.TestCase):
    """語料格式說明:檔數要由本次執行算出來，不可以寫死。"""

    def 假語料(self, 格式們):
        files = []
        for order, formats in enumerate(格式們):
            files.append(CorpusFile(
                path="阿美族/秀姑巒/" + str(order) + ".docx",
                timecode_formats=formats,
            ))
        return files

    def test_時間碼檔數是算出來的(self):
        files = self.假語料([
            {"逗號式": "0:00:02.000,0:00:04.842"},
            {"逗號式": "0:00:05.000,0:00:06.000"},
            {"SRT 式": "00:00:00,000 --> 00:00:07,228"},
        ])
        got = report.format_section(files, ["阿美語"])
        self.assertIn("| 逗號式 | `0:00:02.000,0:00:04.842` | 2 |", got)
        self.assertIn("| SRT 式 | `00:00:00,000 --> 00:00:07,228` | 1 |",
                      got)

    def test_檔數變了表格就跟著變(self):
        少 = report.format_section(
            self.假語料([{"逗號式": "0:00:02.000,0:00:04.842"}]), [])
        多 = report.format_section(
            self.假語料([
                {"逗號式": "0:00:02.000,0:00:04.842"},
                {"逗號式": "0:00:05.000,0:00:06.000"},
            ]), [])
        self.assertIn("| 逗號式 | `0:00:02.000,0:00:04.842` | 1 |", 少)
        self.assertIn("| 逗號式 | `0:00:02.000,0:00:04.842` | 2 |", 多)

    def test_連字號式註明單位不明(self):
        got = report.format_section(
            self.假語料([{"連字號式": "00:00:00-00:04:21"}]), [])
        self.assertIn("單位不明", got)

    def test_特殊符號表與程式用同一份(self):
        from scripts.smkul.rules import SPECIAL, SPECIAL_MARKS
        got = report.format_section(self.假語料([{}]), [])
        for mark in SPECIAL_MARKS:
            self.assertIn(code(mark), got)
        for mark in SPECIAL:
            self.assertIn(mark, SPECIAL_MARKS)

    def test_尚未交付的_sheet_會列出來(self):
        got = report.format_section(self.假語料([{}]), ["阿美語", "鄒語"])
        self.assertIn("鄒語", got)

    def test_不重抄判定規則(self):
        got = report.format_section(self.假語料([{}]), [])
        self.assertIn("features/", got)
        self.assertNotIn("判斷方法", got)
