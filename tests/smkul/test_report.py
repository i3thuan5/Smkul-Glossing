"""測試 report.py 的組件。"""

import unittest

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
            Issue(IssueKind.MIXED_TIMECODE_FORMAT, "b.txt", "", "混用"),
            Issue(IssueKind.SEGMENT_PUNCTUATION, "b.txt", "1", "標點"),
            Issue(IssueKind.CHINESE_ONLY, "b.txt", "112", "華語"),
        ]

    def test_依嚴重度分四組(self):
        errors, exported, warnings, notices = report.severity_split(
            self.build_issues())
        self.assertEqual(len(errors), 2)
        self.assertEqual(len(exported), 1)
        self.assertEqual(len(warnings), 1)
        self.assertEqual(len(notices), 1)
        for issue in errors:
            self.assertIs(issue.severity, Severity.ERROR)
        self.assertIs(exported[0].kind, IssueKind.SEGMENT_PUNCTUATION)

    def test_依檔案分組(self):
        groups = report.group_by_path(self.build_issues())
        self.assertEqual(list(groups), ["a.txt", "b.txt"])
        self.assertEqual(len(groups["a.txt"]), 2)

    def test_明細有定位到編號(self):
        got = report.detail_section("明細", self.build_issues())
        self.assertIn("### a.txt(2 筆)", got)
        self.assertIn("第26段", got)
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
        """例子只寫在 feature,報告只指路,兩邊才不會各寫一份。"""
        got = report.norm_section(NormLog())
        self.assertIn("features/字元正規化.feature", got)
        self.assertIn("features/排版分析.feature", got)
        self.assertIn("features/時間碼.feature", got)

    def test_明細附_id(self):
        issue = Issue(IssueKind.GLUED_LINE, "a.txt", "26", "黏著")
        issue.id = "ISSUE-00000001"
        got = report.detail_section("明細", [issue])
        self.assertIn("- 第26段（`ISSUE-00000001`）|**行黏在一起**", got)

    def test_例子附_id(self):
        issue = Issue(IssueKind.GLUED_LINE, "阿美族/a.txt", "26", "黏著")
        issue.id = "ISSUE-00000001"
        self.assertEqual(report.render_issue(issue),
                         ["- a.txt 第26段（`ISSUE-00000001`）|黏著"])

    def test_例子定位到段(self):
        issue = Issue(IssueKind.GLUED_LINE, "阿美族/a.txt", "26", "黏著")
        self.assertEqual(report.render_issue(issue), ["- a.txt 第26段|黏著"])

    def test_例子只對族語原句與詞素切割不符切掉分類(self):
        issue = Issue(IssueKind.SOURCE_SEGMENT_MISMATCH, "a.txt", "62",
                      "只差一個字母:「l」→「r」")
        self.assertEqual(
            report.render_issue(issue), ["- a.txt 第62段|「l」→「r」"])

    def test_詞素切割有標點的提示整串保留(self):
        hint = ("詞素切割第 1 個詞的 `Yu:m-uwah` 有標點「:」，程式判斷要刪掉，"
                "因為詞素切割不能有標點，應該寫是 `Yum-uwah`")
        issue = Issue(IssueKind.SEGMENT_PUNCTUATION, "a.txt", "59", hint)
        self.assertEqual(
            report.render_issue(issue), ["- a.txt 第59段|" + hint])


class TestTeacherChapters(unittest.TestCase):
    """老師在校對表填的判斷,報告裡要看得到。"""

    def pairs(self, note):
        issue = Issue(IssueKind.SEGMENT_PUNCTUATION, "泰雅族/賽考利克/1.docx",
                      "59", "詞素切割第 1 個詞的 `Yu:m-uwah` 有標點「:」")
        issue.id = "ISSUE-00000001"
        return [(issue, note)]

    def test_要討論的項目(self):
        got = report.teacher_discuss_section(
            "老師標要討論的項目", self.pairs("Yu: 是說話者"))
        self.assertIn("### 泰雅族/賽考利克/1.docx(1 筆)", got)
        self.assertIn("- 第59段（`ISSUE-00000001`）|**詞素切割有標點**", got)
        self.assertIn("  - 備註:Yu: 是說話者", got)

    def test_沒有要討論的寫無(self):
        got = report.teacher_discuss_section("老師標要討論的項目", [])
        self.assertIn("（無）", got)

    def test_確認過的列總筆數與提示(self):
        got = report.confirmed_section(
            "老師確認過、不是錯誤", self.pairs("是說話者"), [])
        self.assertIn("共 1 筆", got)
        self.assertIn("`Yu:m-uwah`", got)
        self.assertIn("  - 備註:是說話者", got)

    def test_讀取問題列在開頭(self):
        got = report.confirmed_section(
            "老師確認過、不是錯誤", [], ["排灣.xlsx 第 2 列的判斷「誤報」"])
        self.assertLess(got.index("「誤報」"), got.index("（無）"))


class TestDiscuss(unittest.TestCase):
    """待討論章的挑法:語言別、檔案輪流挑，最多 20 段，重跑一樣。"""

    def rows(self):
        out = []
        for path, count in (("泰雅族/賽考利克/1.docx", 30),
                            ("泰雅族/賽考利克/2.docx", 3),
                            ("排灣族/中排灣/1.docx", 5)):
            ethnic = path.split("/")[0][:-1]
            variant = path.split("/")[1]
            for number in range(1, count + 1):
                out.append(report.DiscussRow(
                    ethnic, variant, path, str(number), "原句", "切割", 1))
        return out

    def test_最多二十段(self):
        self.assertEqual(len(report.pick_rows(self.rows())), 20)

    def test_輪流挑(self):
        picked = report.pick_rows(self.rows())
        paths = []
        for row in picked[:3]:
            paths.append(row.path)
        self.assertEqual(
            paths,
            ["排灣族/中排灣/1.docx", "泰雅族/賽考利克/1.docx",
             "泰雅族/賽考利克/2.docx"],
        )
        numbers = []
        for row in picked:
            if row.path == "泰雅族/賽考利克/2.docx":
                numbers.append(row.number)
        self.assertEqual(numbers, ["1", "2", "3"])

    def test_重跑一樣(self):
        self.assertEqual(
            report.pick_rows(self.rows()), report.pick_rows(self.rows()))

    def test_章節寫段數與處數(self):
        rows = [report.DiscussRow(
            "泰雅", "賽考利克", "泰雅族/賽考利克/1.docx", "9",
            "nanu yasa lga,", "nanu.yasa la+ga", 2)]
        got = report.discuss_section(
            "待討論", "說明", [("`+`", "加號的說明", rows)])
        self.assertIn("### `+`(1 段，2 處)", got)
        self.assertIn("加號的說明", got)
        self.assertIn("- 1.docx 第9段", got)
        self.assertIn("  - 詞素切割:`nanu.yasa la+ga`", got)

    def test_沒有的時候寫無(self):
        got = report.discuss_section("待討論", "說明", [("`+`", "說明", [])])
        self.assertIn("(無)", got)

    def test_依語言別統計(self):
        got = report.variant_section(
            [("阿美", "秀姑巒", 1)], ["族別", "語言別", "檔數"])
        self.assertIn("## 依語言別統計", got)

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
        self.assertIn("- 第180段|**內容差異**:第 5 行不同", got)
        self.assertIn("  - txt:`181. [e]`", got)
        self.assertIn("  - docx:``", got)

    def test_無_compare_就一行(self):
        issue = Issue(IssueKind.MISSING_FILE, "a", "", "只有 docx,沒有 txt")
        got = report.detail_section("明細", [issue])
        self.assertIn("- 整個檔案|**缺檔**:只有 docx,沒有 txt", got)
        self.assertNotIn("  - ", got)


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

    def test_四行用會議決議的名稱(self):
        """2026.09 會議案由四。"""
        got = report.format_section(self.假語料([{}]), [])
        for name in ("族語原句", "詞素切割", "詞素翻譯", "華語翻譯"):
            self.assertIn(name, got)
        self.assertIn("### 一段語料的結構", got)
        self.assertIn("### 第二行的切割符號", got)
        self.assertIn("features/詞素切割與詞素翻譯對應.feature", got)
        for old in ("切分", "gloss", "族語原文", "一組語料"):
            self.assertNotIn(old, got)

    def test_不重抄判定規則(self):
        got = report.format_section(self.假語料([{}]), [])
        self.assertIn("features/", got)
        self.assertNotIn("判斷方法", got)
