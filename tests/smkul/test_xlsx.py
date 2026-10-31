"""測試 xlsx.py:用 stdlib 讀寫校對表需要的 xlsx。"""

import os
import shutil
import tempfile
import unittest
import zipfile
from xml.etree import ElementTree

from scripts.smkul import xlsx

MAIN = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
OPTIONS = ["程式對，docx 要修改", "docx 正確，程式判斷錯", "要討論"]


class TestRoundTrip(unittest.TestCase):

    def setUp(self):
        self.folder = tempfile.mkdtemp()
        self.path = os.path.join(self.folder, "校對表.xlsx")

    def tearDown(self):
        shutil.rmtree(self.folder)

    def sheets(self):
        first = xlsx.Sheet(
            "校對",
            [
                ["ID", "語料", "判斷"],
                ["ISSUE-12e45678", "s<in>tupa & =SUM(A1)", ""],
                ["ISSUE-00000001",
                 [("aji.", True), (" ", False), ("uri.", True),
                  (" o brah", False)],
                 "要討論"],
            ],
            choices={2: OPTIONS},
            widths=[18, 40, 24],
        )
        second = xlsx.Sheet("已不存在的紀錄", [["ID"], ["ISSUE-abcdef01"]])
        return [first, second]

    def test_寫出去再讀回來_文字原樣(self):
        xlsx.write(self.path, self.sheets())
        got = xlsx.read(self.path)
        self.assertEqual(list(got), ["校對", "已不存在的紀錄"])
        self.assertEqual(got["校對"][1],
                         ["ISSUE-12e45678", "s<in>tupa & =SUM(A1)", ""])
        self.assertEqual(got["校對"][2],
                         ["ISSUE-00000001", "aji. uri. o brah", "要討論"])
        self.assertEqual(got["已不存在的紀錄"], [["ID"], ["ISSUE-abcdef01"]])

    def sheet_xml(self):
        xlsx.write(self.path, self.sheets())
        with zipfile.ZipFile(self.path) as archive:
            return ElementTree.fromstring(
                archive.read("xl/worksheets/sheet1.xml"))

    def test_第一列凍結(self):
        pane = self.sheet_xml().find(".//" + MAIN + "pane")
        self.assertEqual(pane.get("state"), "frozen")
        self.assertEqual(pane.get("ySplit"), "1")

    def test_判斷欄是下拉選單(self):
        root = self.sheet_xml()
        rule = root.find(".//" + MAIN + "dataValidation")
        self.assertEqual(rule.get("type"), "list")
        self.assertTrue(rule.get("sqref").startswith("C2:C"))
        formula = rule.find(MAIN + "formula1").text
        self.assertEqual(formula, '"' + ",".join(OPTIONS) + '"')

    def test_部分文字紅色粗體(self):
        root = self.sheet_xml()
        runs = root.findall(".//" + MAIN + "is/" + MAIN + "r")
        marked = []
        for run in runs:
            props = run.find(MAIN + "rPr")
            if props is not None and props.find(MAIN + "b") is not None:
                color = props.find(MAIN + "color").get("rgb")
                marked.append((run.find(MAIN + "t").text, color))
        self.assertEqual(marked, [("aji.", "FFFF0000"), ("uri.", "FFFF0000")])

    def test_有_ooxml_必要的檔案(self):
        xlsx.write(self.path, self.sheets())
        with zipfile.ZipFile(self.path) as archive:
            names = archive.namelist()
        for name in ("[Content_Types].xml", "_rels/.rels",
                     "xl/workbook.xml", "xl/_rels/workbook.xml.rels",
                     "xl/styles.xml", "xl/worksheets/sheet1.xml",
                     "xl/worksheets/sheet2.xml"):
            self.assertIn(name, names)


# Excel 存檔後字串會改放 sharedStrings,也可能有空儲存格被省略。
EXCEL_WORKBOOK = (
    '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/'
    '2006/main" xmlns:r="http://schemas.openxmlformats.org/'
    'officeDocument/2006/relationships"><sheets>'
    '<sheet name="校對" sheetId="1" r:id="rId1"/></sheets></workbook>'
)
EXCEL_RELS = (
    '<Relationships xmlns="http://schemas.openxmlformats.org/package/'
    '2006/relationships"><Relationship Id="rId1" Type="http://schemas.'
    'openxmlformats.org/officeDocument/2006/relationships/worksheet" '
    'Target="worksheets/sheet1.xml"/></Relationships>'
)
EXCEL_SHARED = (
    '<sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/'
    '2006/main"><si><t>ID</t></si><si><t>判斷</t></si>'
    '<si><r><t>docx 正確，</t></r><r><rPr><b/></rPr><t>程式判斷錯</t></r>'
    '</si></sst>'
)
EXCEL_SHEET = (
    '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/'
    '2006/main"><sheetData>'
    '<row r="1"><c r="A1" t="s"><v>0</v></c><c r="C1" t="s"><v>1</v></c>'
    '</row><row r="3"><c r="A3" t="inlineStr"><is><t>ISSUE-1</t></is></c>'
    '<c r="C3" t="s"><v>2</v></c></row>'
    '</sheetData></worksheet>'
)


class TestReadExcel(unittest.TestCase):

    def test_讀得懂_shared_strings_與空儲存格(self):
        folder = tempfile.mkdtemp()
        try:
            path = os.path.join(folder, "excel.xlsx")
            with zipfile.ZipFile(path, "w") as archive:
                archive.writestr("xl/workbook.xml", EXCEL_WORKBOOK)
                archive.writestr("xl/_rels/workbook.xml.rels", EXCEL_RELS)
                archive.writestr("xl/sharedStrings.xml", EXCEL_SHARED)
                archive.writestr("xl/worksheets/sheet1.xml", EXCEL_SHEET)
            got = xlsx.read(path)
        finally:
            shutil.rmtree(folder)
        self.assertEqual(
            got["校對"],
            [["ID", "", "判斷"], [], ["ISSUE-1", "", "docx 正確，程式判斷錯"]],
        )


if __name__ == "__main__":
    unittest.main()
