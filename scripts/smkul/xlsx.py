"""校對表用的 xlsx 讀寫。使用 stdlib 的 zipfile + ElementTree,不依賴第三方套件。

xlsx 是 zip,一個分頁一個 xl/worksheets/sheetN.xml。這裡只做校對表需要的:

- 寫:多個分頁、第一列凍結、欄寬、自動換行、某一欄的下拉選單,
  以及儲存格裡部分文字紅色粗體(rich text)。字串一律用 inline string,
  開頭是 = 的字串也不會被當成公式。
- 讀:每個分頁的文字。Excel 存檔後字串會改放 xl/sharedStrings.xml,
  兩種都讀得懂;rich text 只取文字。
"""

import collections
import re
import zipfile
from xml.etree import ElementTree
from xml.sax.saxutils import escape, quoteattr

MAIN_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
REL_NS = ("http://schemas.openxmlformats.org/officeDocument/2006/"
          "relationships")
PACKAGE_REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
MAIN = "{" + MAIN_NS + "}"
# 下拉選單套用到這一列為止(xlsx 的最後一列)。
LAST_ROW = 1048576
# 標出問題位置用的顏色:紅色。
MARK_COLOR = "FFFF0000"
# XML 不允許的控制字元。
ILLEGAL = re.compile("[\x00-\x08\x0b\x0c\x0e-\x1f]")


class Sheet:
    """一個分頁。

    rows 的每一格是字串,或是 [(文字, 要不要標紅), ...] 的 rich text。
    choices 是 {欄號(從 0 起): 選項清單},從第 2 列起套用下拉選單。
    widths 是每一欄的寬度(字元數)。第一列是標題,會凍結。
    """

    def __init__(self, name, rows, choices=None, widths=None):
        self.name = name
        self.rows = rows
        self.choices = choices or {}
        self.widths = widths or []


def column_name(index):
    """0 → A、25 → Z、26 → AA。"""
    name = ""
    index += 1
    while index:
        index, rest = divmod(index - 1, 26)
        name = chr(ord("A") + rest) + name
    return name


def column_index(name):
    """A → 0、AA → 26。"""
    index = 0
    for char in name:
        index = index * 26 + ord(char) - ord("A") + 1
    return index - 1


def _text(value):
    """<t> 元素。前後有空白時要加 xml:space,Excel 才不會吃掉。"""
    value = ILLEGAL.sub("", value)
    if value != value.strip():
        return '<t xml:space="preserve">' + escape(value) + "</t>"
    return "<t>" + escape(value) + "</t>"


def _cell(ref, value, style):
    if isinstance(value, str):
        inner = _text(value)
    else:
        runs = []
        for text, marked in value:
            props = ""
            if marked:
                props = ('<rPr><b/><color rgb="' + MARK_COLOR + '"/>'
                         "</rPr>")
            runs.append("<r>" + props + _text(text) + "</r>")
        inner = "".join(runs)
    return ('<c r="' + ref + '" s="' + str(style) + '" t="inlineStr"><is>' +
            inner + "</is></c>")


def _sheet_xml(sheet):
    parts = [
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
        '<worksheet xmlns="' + MAIN_NS + '">',
        '<sheetViews><sheetView workbookViewId="0">'
        '<pane ySplit="1" topLeftCell="A2" activePane="bottomLeft" '
        'state="frozen"/></sheetView></sheetViews>',
    ]
    if sheet.widths:
        parts.append("<cols>")
        for index, width in enumerate(sheet.widths):
            number = str(index + 1)
            parts.append('<col min="' + number + '" max="' + number +
                         '" width="' + str(width) + '" customWidth="1"/>')
        parts.append("</cols>")
    parts.append("<sheetData>")
    for row_index, row in enumerate(sheet.rows):
        number = str(row_index + 1)
        # 第一列標題用粗體(樣式 1),其他列自動換行(樣式 2)。
        style = 2
        if row_index == 0:
            style = 1
        parts.append('<row r="' + number + '">')
        for column, value in enumerate(row):
            parts.append(_cell(column_name(column) + number, value, style))
        parts.append("</row>")
    parts.append("</sheetData>")
    if sheet.choices:
        parts.append('<dataValidations count="' + str(len(sheet.choices)) +
                     '">')
        for column in sorted(sheet.choices):
            name = column_name(column)
            formula = '"' + ",".join(sheet.choices[column]) + '"'
            parts.append(
                '<dataValidation type="list" allowBlank="1" '
                'showErrorMessage="1" sqref="' + name + "2:" + name +
                str(LAST_ROW) + '"><formula1>' + escape(formula) +
                "</formula1></dataValidation>")
        parts.append("</dataValidations>")
    parts.append("</worksheet>")
    return "".join(parts)


STYLES = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<styleSheet xmlns="' + MAIN_NS + '">'
    '<fonts count="2"><font><sz val="11"/><name val="Calibri"/></font>'
    '<font><b/><sz val="11"/><name val="Calibri"/></font></fonts>'
    '<fills count="2"><fill><patternFill patternType="none"/></fill>'
    '<fill><patternFill patternType="gray125"/></fill></fills>'
    '<borders count="1"><border><left/><right/><top/><bottom/>'
    '<diagonal/></border></borders>'
    '<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" '
    'borderId="0"/></cellStyleXfs>'
    '<cellXfs count="3">'
    '<xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>'
    '<xf numFmtId="0" fontId="1" fillId="0" borderId="0" xfId="0" '
    'applyFont="1"/>'
    '<xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0" '
    'applyAlignment="1"><alignment vertical="top" wrapText="1"/></xf>'
    '</cellXfs></styleSheet>'
)


def _workbook_files(sheets):
    content = [
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/'
        'content-types">',
        '<Default Extension="rels" ContentType="application/'
        'vnd.openxmlformats-package.relationships+xml"/>',
        '<Default Extension="xml" ContentType="application/xml"/>',
        '<Override PartName="/xl/workbook.xml" ContentType="application/'
        'vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>',
        '<Override PartName="/xl/styles.xml" ContentType="application/'
        'vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>',
    ]
    workbook = [
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
        '<workbook xmlns="' + MAIN_NS + '" xmlns:r="' + REL_NS + '">',
        "<sheets>",
    ]
    rels = [
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
        '<Relationships xmlns="' + PACKAGE_REL_NS + '">',
    ]
    for index, sheet in enumerate(sheets):
        number = str(index + 1)
        content.append(
            '<Override PartName="/xl/worksheets/sheet' + number +
            '.xml" ContentType="application/vnd.openxmlformats-'
            'officedocument.spreadsheetml.worksheet+xml"/>')
        workbook.append('<sheet name=' + quoteattr(sheet.name[:31]) +
                        ' sheetId="' + number + '" r:id="rId' + number +
                        '"/>')
        rels.append('<Relationship Id="rId' + number + '" Type="' +
                    REL_NS + '/worksheet" Target="worksheets/sheet' +
                    number + '.xml"/>')
    styles_id = "rId" + str(len(sheets) + 1)
    rels.append('<Relationship Id="' + styles_id + '" Type="' + REL_NS +
                '/styles" Target="styles.xml"/>')
    content.append("</Types>")
    workbook.append("</sheets></workbook>")
    rels.append("</Relationships>")
    root_rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="' + PACKAGE_REL_NS + '">'
        '<Relationship Id="rId1" Type="' + REL_NS + '/officeDocument" '
        'Target="xl/workbook.xml"/></Relationships>'
    )
    return [
        ("[Content_Types].xml", "".join(content)),
        ("_rels/.rels", root_rels),
        ("xl/workbook.xml", "".join(workbook)),
        ("xl/_rels/workbook.xml.rels", "".join(rels)),
        ("xl/styles.xml", STYLES),
    ]


def write(path, sheets):
    """把幾個分頁寫成一個 xlsx。"""
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, data in _workbook_files(sheets):
            archive.writestr(name, data)
        for index, sheet in enumerate(sheets):
            archive.writestr(
                "xl/worksheets/sheet" + str(index + 1) + ".xml",
                _sheet_xml(sheet))


def _joined_text(node):
    """<si> 或 <is> 裡面所有 <t> 的文字接起來(rich text 只取文字)。"""
    parts = []
    for child in node.iter(MAIN + "t"):
        if child.text:
            parts.append(child.text)
    return "".join(parts)


def _shared_strings(archive):
    try:
        data = archive.read("xl/sharedStrings.xml")
    except KeyError:
        return []
    out = []
    for item in ElementTree.fromstring(data).iter(MAIN + "si"):
        out.append(_joined_text(item))
    return out


def _sheet_paths(archive):
    """[(分頁名稱, 檔案路徑)],照活頁簿裡的順序。"""
    rels = ElementTree.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
    targets = {}
    for rel in rels:
        target = rel.get("Target")
        if target.startswith("/"):
            target = target[1:]
        else:
            target = "xl/" + target
        targets[rel.get("Id")] = target
    workbook = ElementTree.fromstring(archive.read("xl/workbook.xml"))
    out = []
    for sheet in workbook.iter(MAIN + "sheet"):
        rel_id = sheet.get("{" + REL_NS + "}id")
        out.append((sheet.get("name"), targets[rel_id]))
    return out


def _cell_value(cell, shared):
    kind = cell.get("t")
    if kind == "inlineStr":
        found = cell.find(MAIN + "is")
        if found is None:
            return ""
        return _joined_text(found)
    value = cell.find(MAIN + "v")
    if value is None or value.text is None:
        return ""
    if kind == "s":
        return shared[int(value.text)]
    return value.text


def _rows(data, shared):
    rows = []
    for row in ElementTree.fromstring(data).iter(MAIN + "row"):
        number = int(row.get("r", len(rows) + 1))
        while len(rows) < number - 1:
            rows.append([])
        values = []
        for cell in row.iter(MAIN + "c"):
            ref = cell.get("r")
            if ref:
                column = column_index(re.match("[A-Z]+", ref).group(0))
            else:
                column = len(values)
            while len(values) < column:
                values.append("")
            values.append(_cell_value(cell, shared))
        rows.append(values)
    return rows


def read(path):
    """讀 xlsx,回傳 {分頁名稱: 每一列的文字清單},照分頁順序。"""
    out = collections.OrderedDict()
    with zipfile.ZipFile(path) as archive:
        shared = _shared_strings(archive)
        for name, sheet_path in _sheet_paths(archive):
            out[name] = _rows(archive.read(sheet_path), shared)
    return out
