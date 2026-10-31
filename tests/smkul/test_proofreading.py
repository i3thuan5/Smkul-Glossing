"""測試 proofreading.py:問題 ID、讀回老師的判斷、產生校對表。

規格見 openspec 的 proofreading spec。測試一律用暫存資料夾,
不碰真的 kithann/。
"""

import os
import re
import shutil
import tempfile
import unittest

from scripts.smkul import proofreading, xlsx
from scripts.smkul.entry import Entry, Issue, IssueKind

BODY = [
    "avan cu a tja si'uda'udan a sicuayan a qemuqu,",
    "avan cu a tja=si-'uda-'uda-an a sicuayan a q<em>uqu,",
    "就 主格.這 連繫詞 我們.包含.屬格=參焦-重疊-如何-AN 連繫詞 從前 連繫詞 <主焦>洗頭",
    "也就是以前洗頭的文化習俗。",
]
PATH = "排灣族/中排灣/1.廖桂香sakenge_小米梗的用途.docx"


def punctuation(number="12"):
    return Issue(IssueKind.SEGMENT_PUNCTUATION, PATH, number, "提示")


class TestIssueId(unittest.TestCase):

    def assign(self, issue, body=BODY, book=None):
        if book is None:
            book = proofreading.IdBook()
        book.assign(issue, body)
        return issue.id

    def test_格式是_issue_加八碼(self):
        self.assertRegex(self.assign(punctuation()), r"^ISSUE-[0-9a-f]{8}$")

    def test_同樣的輸入同樣的_id(self):
        self.assertEqual(self.assign(punctuation()),
                         self.assign(punctuation()))

    def test_段內容改一個字_id_就變(self):
        changed = list(BODY)
        changed[0] = changed[0].replace("avan", "avang")
        self.assertNotEqual(self.assign(punctuation()),
                            self.assign(punctuation(), changed))

    def test_同一段不同問題種類_id_不同(self):
        other = Issue(IssueKind.SOURCE_SEGMENT_MISMATCH, PATH, "12",
                      "只差一個字母:詞素切割多了「a」")
        self.assertNotEqual(self.assign(punctuation()), self.assign(other))

    def test_沒有段編號的問題也有_id(self):
        first = Issue(IssueKind.ORPHAN_TIMECODE, PATH, "", "孤兒",
                      [("時間碼", "0:01:02.000,0:01:03.000")])
        second = Issue(IssueKind.ORPHAN_TIMECODE, PATH, "", "孤兒",
                       [("時間碼", "0:09:02.000,0:09:03.000")])
        first_id = self.assign(first, [])
        self.assertRegex(first_id, r"^ISSUE-[0-9a-f]{8}$")
        self.assertNotEqual(first_id, self.assign(second, []))

    def test_一模一樣的問題出現兩次_id_仍然不同(self):
        book = proofreading.IdBook()
        self.assertNotEqual(self.assign(punctuation(), book=book),
                            self.assign(punctuation(), book=book))

    def test_撞號會報錯(self):
        book = proofreading.IdBook()
        issue = punctuation()
        taken = self.assign(punctuation())
        book.sources[taken] = "別的內容"
        with self.assertRaises(ValueError):
            book.assign(issue, BODY)

    def test_id_的格式寫在常數(self):
        self.assertTrue(re.match(r"^ISSUE-$", proofreading.ID_PREFIX))


def sheet_row(issue_id, judgement="", note=""):
    """校對表的一列,只填 ID、判斷、備註,其他欄隨便。"""
    row = []
    for header in proofreading.HEADERS:
        if header == "ID":
            row.append(issue_id)
        elif header == "判斷":
            row.append(judgement)
        elif header == "備註":
            row.append(note)
        elif header == "檔案":
            row.append(PATH)
        else:
            row.append("")
    return row


class TestReadBack(unittest.TestCase):

    def setUp(self):
        self.folder = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.folder)

    def save(self, name, rows, mtime=None):
        path = os.path.join(self.folder, name)
        table = [list(proofreading.HEADERS)]
        for row in rows:
            table.append(row)
        xlsx.write(path, [xlsx.Sheet("校對", table)])
        if mtime is not None:
            os.utime(path, (mtime, mtime))
        return path

    def test_資料夾不存在(self):
        got = proofreading.read_judgements(
            os.path.join(self.folder, "沒有這個資料夾"))
        self.assertEqual(got.judgements, {})
        self.assertEqual(got.problems, [])

    def test_空資料夾(self):
        got = proofreading.read_judgements(self.folder)
        self.assertEqual(got.judgements, {})

    def test_一個檔(self):
        self.save("阿美.xlsx", [
            sheet_row("ISSUE-00000001", proofreading.PROGRAM_WRONG, "是長音"),
            sheet_row("ISSUE-00000002"),
            sheet_row("ISSUE-00000003", "", "只寫備註也留著"),
        ])
        got = proofreading.read_judgements(self.folder)
        self.assertEqual(sorted(got.judgements),
                         ["ISSUE-00000001", "ISSUE-00000003"])
        first = got.judgements["ISSUE-00000001"]
        self.assertEqual(first.judgement, proofreading.PROGRAM_WRONG)
        self.assertEqual(first.note, "是長音")
        self.assertEqual(first.values["檔案"], PATH)

    def test_兩個檔判斷不一樣_取較新的(self):
        self.save("舊.xlsx", [sheet_row("ISSUE-00000001", "要討論")],
                  mtime=1000000000)
        self.save("新.xlsx", [
            sheet_row("ISSUE-00000001", proofreading.FIX_DOCX)],
            mtime=1100000000)
        got = proofreading.read_judgements(self.folder)
        self.assertEqual(got.judgements["ISSUE-00000001"].judgement,
                         proofreading.FIX_DOCX)
        self.assertEqual(len(got.problems), 1)
        self.assertIn("ISSUE-00000001", got.problems[0])
        self.assertIn("新.xlsx", got.problems[0])

    def test_判斷欄寫錯字_當作沒有判斷(self):
        self.save("排灣.xlsx", [sheet_row("ISSUE-00000001", "誤報")])
        got = proofreading.read_judgements(self.folder)
        self.assertNotIn("ISSUE-00000001", got.judgements)
        self.assertEqual(len(got.problems), 1)
        self.assertIn("排灣.xlsx", got.problems[0])
        self.assertIn("第 2 列", got.problems[0])
        self.assertIn("「誤報」", got.problems[0])


class TestApply(unittest.TestCase):

    def judgement(self, issue_id, judgement, note=""):
        return proofreading.Judgement(
            issue_id, judgement, note, {}, "校對.xlsx", 2, 0)

    def entry(self):
        entry = Entry("12", "0", "1", path=PATH)
        mismatch = Issue(IssueKind.SOURCE_SEGMENT_MISMATCH, PATH, "12",
                         "只差一個字母:詞素切割多了「a」")
        mismatch.id = "ISSUE-00000001"
        punct = punctuation()
        punct.id = "ISSUE-00000002"
        entry.issues.append(mismatch)
        entry.issues.append(punct)
        return entry

    def test_程式判斷錯的移走_段就乾淨了(self):
        entry = self.entry()
        self.assertFalse(entry.is_clean())
        judgements = {
            "ISSUE-00000001": self.judgement(
                "ISSUE-00000001", proofreading.PROGRAM_WRONG, "拼法慣例"),
        }
        confirmed, discussed = proofreading.apply_judgements(
            entry.issues, judgements)
        self.assertEqual(len(confirmed), 1)
        self.assertEqual(confirmed[0][0].id, "ISSUE-00000001")
        self.assertEqual(confirmed[0][1].note, "拼法慣例")
        self.assertEqual(discussed, [])
        self.assertEqual(len(entry.issues), 1)
        self.assertTrue(entry.is_clean())

    def test_要討論與要改_docx_的照常留著(self):
        entry = self.entry()
        judgements = {
            "ISSUE-00000001": self.judgement(
                "ISSUE-00000001", proofreading.FIX_DOCX),
            "ISSUE-00000002": self.judgement(
                "ISSUE-00000002", proofreading.DISCUSS, "Yu: 是說話者"),
        }
        confirmed, discussed = proofreading.apply_judgements(
            entry.issues, judgements)
        self.assertEqual(confirmed, [])
        self.assertEqual(len(discussed), 1)
        self.assertEqual(discussed[0][0].id, "ISSUE-00000002")
        self.assertEqual(len(entry.issues), 2)

    def test_id_對不上的判斷不套用(self):
        entry = self.entry()
        judgements = {
            "ISSUE-ffffffff": self.judgement(
                "ISSUE-ffffffff", proofreading.PROGRAM_WRONG),
        }
        confirmed, discussed = proofreading.apply_judgements(
            entry.issues, judgements)
        self.assertEqual(confirmed, [])
        self.assertEqual(len(entry.issues), 2)


def make_entry(path, number, source, segmentation, gloss="詞", tr="華語"):
    entry = Entry(number, "0", "1", path=path)
    entry.source = source
    entry.segmentation = segmentation
    entry.gloss = gloss
    entry.translation = tr
    return entry


TAROKO = "太魯閣族/1_黃麗俐Miring_胡月英Tku_生活中的氣候啟示.docx"
AMIS = "阿美族/秀姑巒/陳美莉_阿星.阿曼_說族語在大漢部落的過.docx"


class TestMarks(unittest.TestCase):
    """校對表把問題的位置標成紅色粗體。"""

    def test_標出有標點的詞(self):
        entry = make_entry(TAROKO, "418", "Aji uri o brah", "aji. uri. o brah")
        issue = Issue(IssueKind.SEGMENT_PUNCTUATION, TAROKO, "418", "提示")
        got = proofreading.marked_cells(issue, entry, "太魯閣")
        self.assertEqual(got, {"詞素切割": [
            ("aji.", True), (" ", False), ("uri.", True), (" o brah", False),
        ]})

    def test_標出不一樣的字母(self):
        entry = make_entry(AMIS, "62", "caay katama masa mahatila",
                           "caay ka-tama masa ma-ha-tira")
        issue = Issue(IssueKind.SOURCE_SEGMENT_MISMATCH, AMIS, "62",
                      "只差一個字母:「l」→「r」")
        got = proofreading.marked_cells(issue, entry, "阿美")
        self.assertEqual(got["族語原句"], [
            ("caay katama masa mahati", False), ("l", True), ("a", False)])
        self.assertEqual(got["詞素切割"], [
            ("caay ka-tama masa ma-ha-ti", False), ("r", True),
            ("a", False)])

    def test_其他種類不標(self):
        entry = make_entry(AMIS, "20", "a", "a")
        issue = Issue(IssueKind.GLOSS_FEWER, AMIS, "20", "")
        self.assertEqual(proofreading.marked_cells(issue, entry, "阿美"), {})


class TestWriteSheets(unittest.TestCase):

    def setUp(self):
        self.folder = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.folder)

    def rows(self):
        out = []
        cases = [
            (TAROKO, "10", IssueKind.SEGMENT_PUNCTUATION, "太魯閣", "太魯閣"),
            (TAROKO, "9", IssueKind.SOURCE_SEGMENT_MISMATCH, "太魯閣",
             "太魯閣"),
            (TAROKO, "9", IssueKind.CHINESE_ONLY, "太魯閣", "太魯閣"),
            (AMIS, "26", IssueKind.REVERSED_TIMECODE, "阿美", "秀姑巒"),
            (AMIS, "27", IssueKind.GLUED_LINE, "阿美", "秀姑巒"),
        ]
        for index, (path, number, kind, ethnic, variant) in enumerate(cases):
            issue = Issue(kind, path, number, "提示" + str(index))
            issue.id = "ISSUE-0000000" + str(index)
            entry = make_entry(path, number, "iq kiya", "iq kiya")
            out.append(proofreading.SheetRow(ethnic, variant, issue, entry))
        return out

    def read(self, name):
        return xlsx.read(os.path.join(self.folder, name))

    def test_一個語言別一個檔(self):
        proofreading.write_sheets(self.folder, self.rows(), {})
        self.assertEqual(
            sorted(os.listdir(self.folder)),
            ["校對表_太魯閣_太魯閣.xlsx", "校對表_阿美_秀姑巒.xlsx"])

    def test_欄位與排序(self):
        proofreading.write_sheets(self.folder, self.rows(), {})
        rows = self.read("校對表_太魯閣_太魯閣.xlsx")["校對"]
        self.assertEqual(rows[0], proofreading.HEADERS)
        numbers = []
        for row in rows[1:]:
            numbers.append(row[2])
        self.assertEqual(numbers, ["9", "9", "10"])
        first = dict(zip(proofreading.HEADERS, rows[1]))
        self.assertEqual(first["檔案"], TAROKO)
        self.assertEqual(first["族語原句"], "iq kiya")
        self.assertEqual(first["華語翻譯"], "華語")

    def test_四級嚴重度都有(self):
        proofreading.write_sheets(self.folder, self.rows(), {})
        kinds = []
        for name in os.listdir(self.folder):
            for row in self.read(name)["校對"][1:]:
                kinds.append(row[3])
        for kind in ("詞素切割有標點", "純華語句", "結束時間早於開始",
                     "行黏在一起"):
            self.assertIn(kind, kinds)

    def test_帶入舊判斷與備註(self):
        judgements = {"ISSUE-00000000": proofreading.Judgement(
            "ISSUE-00000000", proofreading.PROGRAM_WRONG, "老師的備註",
            {}, "舊.xlsx", 2, 0)}
        proofreading.write_sheets(self.folder, self.rows(), judgements)
        rows = self.read("校對表_太魯閣_太魯閣.xlsx")["校對"]
        last = dict(zip(proofreading.HEADERS, rows[-1]))
        self.assertEqual(last["ID"], "ISSUE-00000000")
        self.assertEqual(last["判斷"], proofreading.PROGRAM_WRONG)
        self.assertEqual(last["備註"], "老師的備註")

    def test_對不到的舊判斷進已不存在的紀錄(self):
        values = {"ID": "ISSUE-ffffffff", "檔案": AMIS, "段": "99",
                  "問題": "行黏在一起", "判斷": proofreading.FIX_DOCX,
                  "備註": "改好了"}
        judgements = {"ISSUE-ffffffff": proofreading.Judgement(
            "ISSUE-ffffffff", proofreading.FIX_DOCX, "改好了", values,
            "舊.xlsx", 5, 0)}
        proofreading.write_sheets(self.folder, self.rows(), judgements)
        gone = self.read("校對表_阿美_秀姑巒.xlsx")["已不存在的紀錄"]
        self.assertEqual(gone[0], proofreading.HEADERS)
        row = dict(zip(proofreading.HEADERS, gone[1]))
        self.assertEqual(row["ID"], "ISSUE-ffffffff")
        self.assertEqual(row["段"], "99")
        self.assertEqual(row["備註"], "改好了")

    def test_先清掉舊的校對表(self):
        old = os.path.join(self.folder, "校對表_舊語言_舊.xlsx")
        with open(old, "w", encoding="utf-8") as handle:
            handle.write("舊")
        proofreading.write_sheets(self.folder, self.rows(), {})
        self.assertFalse(os.path.exists(old))


if __name__ == "__main__":
    unittest.main()
