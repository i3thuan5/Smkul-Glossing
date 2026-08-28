"""Markdown 報告。兩支檢查程式的報告都由這裡產生。"""

import datetime
import os
from collections import Counter, OrderedDict

from scripts.smkul.entry import (NORM_FEATURE, IssueKind, Severity,
                                 code)
from scripts.smkul.markers import SHEET_OF
from scripts.smkul.rules import SPECIAL_MARKS, SYMBOL_MEANING

OUT_DIR = os.path.join("kithann", "out")

YAML_SOURCE_WHY = (
    "YAML 一律**由 docx 產生**，不由 txt 產生。理由:\n\n"
    "1. docx 的審閱註解本文放在 `word/comments.xml`，內文"
    "(`word/document.xml`)只留零文字的 `commentRangeStart` 標記，"
    "所以抽內文的時候註解**天生不會混進來**。\n"
    "2. txt 是 docx 匯出的副本，匯出時每條註解會在內文留下兩個 "
    "`[字母]` 錨點，註解本文也被寫成一般文字行，會污染語料。\n"
    "3. 從 docx 直接讀，不需要任何清除步驟，也就沒有「清錯、"
    "把語料的字一起刪掉」的風險。\n\n"
    "docx 的文字顏色與標亮(例如太魯閣 1 有 35 處紅字)兩邊都看不到，"
    "仍請對方說明紅字的意思。"
)


def today():
    """報告的更新日期。每次重跑都會換成當天。"""
    return datetime.date.today().isoformat()


def heading(text, level=2):
    return "#" * level + " " + text


def table(headers, rows):
    """產生一個 markdown 表格。"""
    out = ["| " + " | ".join(headers) + " |"]
    line = []
    for _ in headers:
        line.append("---")
    out.append("| " + " | ".join(line) + " |")
    for row in rows:
        cells = []
        for cell in row:
            cells.append(str(cell).replace("|", "\\|"))
        out.append("| " + " | ".join(cells) + " |")
    return "\n".join(out)


def issue_label(issue):
    """報告上顯示的問題名稱。

    「原文與切分不符」拆到細分類型(只差單引號、只差一個字母……),
    這樣總覽的表格就分得出哪一類要優先處理。
    """
    if issue.kind is IssueKind.SOURCE_SEGMENT_MISMATCH and \
            ":" in issue.detail:
        return issue.kind.value + "-" + issue.detail.split(":", 1)[0]
    return issue.kind.value


def count_kinds(issues):
    counter = Counter()
    for issue in issues:
        counter[issue_label(issue)] += 1
    return counter


def group_by_path(issues):
    """依檔案分組，順序照原本出現的順序。"""
    groups = OrderedDict()
    for issue in issues:
        groups.setdefault(issue.path, []).append(issue)
    return groups


def kind_table(issues):
    counter = count_kinds(issues)
    rows = []
    for label, number in counter.most_common():
        rows.append((label, number))
    if not rows:
        return "(無)"
    return table(["問題", "筆數"], rows)


def norm_section(log, compare_note=""):
    """「自動處理與比對政策」。沒發生的項目也要列，筆數寫 0。

    每一項只寫摘要與筆數，例子不複製進報告——真實例子統一寫在
    對應的 `features/*.feature`，規則與例子只留一份才不會走精。
    """
    lines = [heading("自動處理與比對政策"), ""]
    lines.append(
        "程式讀語料時做過下列轉換與重組。每一項只寫摘要與這次的筆數，"
        "**真實例子(原句子、處理後的句子、檔案與組別)寫在對應的 "
        "`features/*.feature` 裡**，請直接看那裡，規則與例子才只有一份。"
    )
    if compare_note:
        lines.append("")
        lines.append(compare_note)
    for record in log.ordered():
        lines.append("")
        lines.append(heading(record.kind.value, 3))
        lines.append("")
        lines.append("- 為什麼:" + record.why)
        lines.append("- 這次影響:" + str(record.count) + " 筆")
        where = NORM_FEATURE.get(record.kind)
        if where:
            lines.append(
                "- 詳見:`features/" + where[0] + ".feature` 的 Scenario"
                "「" + where[1] + "」")
    return "\n".join(lines)


def severity_split(issues):
    errors = []
    warnings = []
    notices = []
    for issue in issues:
        if issue.severity is Severity.ERROR:
            errors.append(issue)
        elif issue.severity is Severity.WARNING:
            warnings.append(issue)
        else:
            notices.append(issue)
    return errors, warnings, notices


def detail_section(title, issues, limit=40):
    """錯誤明細，依檔案分組，每組定位到編號。

    有 compare 的(txt/docx、原文/切分)分成獨立的子項，較好對照。
    """
    lines = [heading(title), ""]
    if not issues:
        lines.append("(無)")
        return "\n".join(lines)
    groups = group_by_path(issues)
    for path, found in groups.items():
        lines.append("")
        lines.append(heading(path + "(" + str(len(found)) + " 筆)", 3))
        lines.append("")
        for issue in found[:limit]:
            if issue.number:
                where = "第" + issue.number + "組"
            else:
                where = "整個檔案"
            head = "- " + where + "|**" + issue_label(issue) + "**"
            if issue.detail:
                head = head + ":" + issue.detail
            lines.append(head)
            for label, value in issue.compare:
                lines.append("  - " + label + ":" + code(value))
        if len(found) > limit:
            lines.append(
                "- (其餘 " + str(len(found) - limit) + " 筆未列出，"
                "總數請看上面的統計)"
            )
    return "\n".join(lines)


def number_headings(body):
    """幫章節加編號:## 變成 ## 1.、### 變成 ## 1.1，才好在會議上指位置。

    程式碼區塊裡面的 # 不動。
    """
    out = []
    major = 0
    minor = 0
    fenced = False
    for line in body.split("\n"):
        if line.startswith("```"):
            fenced = not fenced
        if fenced:
            out.append(line)
            continue
        if line.startswith("### "):
            minor += 1
            out.append(
                "### " + str(major) + "." + str(minor) + " " + line[4:])
        elif line.startswith("## "):
            major += 1
            minor = 0
            out.append("## " + str(major) + ". " + line[3:])
        else:
            out.append(line)
    return "\n".join(out)


def _tidy(body):
    """連續空行合併成一行，結尾留一個換行。"""
    out = []
    blank = False
    for line in body.split("\n"):
        if line.strip():
            out.append(line.rstrip())
            blank = False
        elif not blank:
            out.append("")
            blank = True
    while out and not out[-1]:
        out.pop()
    return "\n".join(out) + "\n"


def write(name, sections):
    """把每一章接成一篇，寫進 kithann/out/。"""
    os.makedirs(OUT_DIR, exist_ok=True)
    path = os.path.join(OUT_DIR, name)
    body = _tidy(number_headings("\n\n".join(sections)))
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(body)
    return path


def uncertain_section(counter):
    """「不確定」標記統計:全大寫拉丁 gloss，依 ODS 1-2 合法但要呈現。"""
    lines = [heading("「不確定」標記統計"), ""]
    lines.append(
        "依 ODS 各 sheet 的 1-2 條，標注者不確定某個詞綴是什麼時，"
        "用全大寫拉丁字母(或 `?`)代替 gloss。這些**不算錯誤**，"
        "但列在這裡讓您看到規模與分布。建議補充到"
        "《常用構詞標記清單》。"
    )
    lines.append("")
    if not counter:
        lines.append("(無)")
        return "\n".join(lines)
    rows = []
    for (marker, sheet), number in counter.most_common():
        rows.append((code(marker), sheet, number))
    lines.append(table(["標記", "語言", "出現次數"], rows))
    return "\n".join(lines)


def hard_morphology_section(records, limit=60):
    """「構詞判斷困難」:詞根判袂出來ê詞素,依詞素×語言彙總。

    這毋是錯誤——YAML ê「構詞」欄記做「無法判斷」,規組照常匯出。
    分類佮例攏tī features/構詞判定.feature,這搭干焦寫摘要佮統計。
    """
    lines = [heading("構詞判斷困難"), ""]
    lines.append(
        "下面這些詞素，程式判不出哪一段是詞根，YAML 的「構詞」欄"
        "記成 `無法判斷`。這**不算錯誤，也不擋匯出**——整組照常"
        "進 YAML，只是那一段還沒有定論。\n\n"
        "判定的完整流程、每一種情形的真實例子，寫在 "
        "`features/構詞判定.feature` 的「判斷方法」與各 Scenario，"
        "這一章只寫摘要與統計。"
    )
    lines.append("")
    if not records:
        lines.append("(無)")
        return "\n".join(lines)

    cases = OrderedDict()
    for gloss, sheet, case, seg, path, number in records:
        cases.setdefault(case, []).append((gloss, sheet, path, number))
    for case, found in cases.items():
        lines.append("")
        lines.append(heading(case, 3))
        lines.append("")
        lines.append(
            "共 " + str(len(found)) + " 個詞素。詳見 "
            "`features/構詞判定.feature`。")

    lines.append("")
    lines.append(heading("依詞素與語言彙總", 3))
    lines.append("")
    lines.append(
        "次數高又跨多個檔案的，多半是《常用構詞標記清單》缺這一條;"
        "次數少又零星的，多半是標注筆誤。")
    lines.append("")
    counts = OrderedDict()
    for gloss, sheet, case, seg, path, number in records:
        counts.setdefault((gloss, sheet), []).append((path, number))
    ordered = sorted(counts.items(), key=lambda item: -len(item[1]))
    rows = []
    for (gloss, sheet), places in ordered[:limit]:
        files = set()
        for path, number in places:
            files.add(path)
        sample = []
        for path, number in places[:3]:
            sample.append(path.split("/")[-1] + " 第" + number + "組")
        rows.append((
            code(gloss), sheet, len(places), len(files), "、".join(sample),
        ))
    lines.append(
        table(["詞素", "語言", "次數", "檔案數", "實例(最多 3 個)"], rows))
    if len(ordered) > limit:
        lines.append("")
        lines.append(
            "(其餘 " + str(len(ordered) - limit) + " 種詞素未列出)")
    lines.append("")
    lines.append("建議補充到《常用構詞標記清單》。")
    return "\n".join(lines)


SAMPLE_LIMIT = 3


def collect_samples(issues, limit=SAMPLE_LIMIT):
    """逐種問題留前幾筆當例子。"""
    samples = OrderedDict()
    for issue in issues:
        label = issue_label(issue)
        found = samples.setdefault(label, [])
        if len(found) < limit:
            found.append(issue)
    return samples


def render_issue(issue):
    """一筆例子:位置、原因，兩邊對照分開列。"""
    lines = []
    where = issue.path.split("/")[-1]
    if issue.number:
        where = where + " 第" + issue.number + "組"
    detail = issue.detail
    if ":" in detail:
        detail = detail.split(":", 1)[-1]
    if detail:
        lines.append("- " + where + "|" + detail)
    else:
        lines.append("- " + where)
    for label, value in issue.compare:
        lines.append("  - " + label + ":" + code(value))
    return lines


def kind_section(title, issues, why_of, order=None):
    """逐種問題:說明 + 最多 3 組例。"""
    lines = [heading(title), ""]
    lines.append(
        "總覽表裡的每一種問題，這裡說明它是什麼意思，並附最多 " +
        str(SAMPLE_LIMIT) + " 組真實例子。"
    )
    counter = count_kinds(issues)
    samples = collect_samples(issues)
    if order is None:
        order = []
        for label, _ in counter.most_common():
            order.append(label)
    for label in order:
        lines.append("")
        lines.append(
            heading(label + "(" + str(counter.get(label, 0)) + " 筆)", 3))
        lines.append("")
        why = why_of(label)
        if why:
            lines.append(why)
            lines.append("")
        found = samples.get(label, [])
        if not found:
            lines.append("(這次沒有發生)")
            continue
        for issue in found:
            for line in render_issue(issue):
                lines.append(line)
    return "\n".join(lines)


def variant_section(rows, headers):
    """依語別統計表。"""
    lines = [heading("依語別統計"), ""]
    lines.append(table(headers, rows))
    return "\n".join(lines)


# 語料目錄與 ODS sheet 的對應之外，還沒有交付語料的 sheet 也要列。
FORMAT_INTRO = (
    "這一章寫的是**語料長什麼樣**，讓對方不必另外讀文件就知道程式"
    "怎麼讀語料。判定的規則不寫在這裡——規則是 `features/*.feature`，"
    "一條規則只有一份。"
)

ENTRY_SHAPE = (
    "一組語料（一個句子）由「編號 + 時間碼 + 四行標註」組成。四行的"
    "角色:\n\n"
    "1. **第一行 族語原文**:原始書寫形式，依各族現行書寫系統。\n"
    "2. **第二行 構詞切分**:把每個詞切成詞素，用構詞符號標示每個"
    "詞素怎麼接。\n"
    "3. **第三行 gloss**:逐詞素的華語對譯，詞數與符號位置要與第二行"
    "呼應（見 `features/切分與glossing對應.feature`）。\n"
    "4. **第四行 華語翻譯**:整句自由翻譯，不受前三行的切分限制。\n\n"
    "編號通常自己一行，也有編號與時間碼同行的（東排灣 1）。組與組"
    "之間通常空一行，但語料裡有缺空行的情形，所以組界一律以"
    "「編號行 + 時間碼行」判斷，不依賴空行"
    "（見 `features/排版分析.feature`）。"
)

REDUPLICATION_NOTE = (
    "重疊的標法依語言而異，三種都出現在語料與 ODS 裡:用 `~`"
    "（太魯閣 `m~m-iyah` / `即將~主焦-來`）、用 `-`（南排灣 "
    "`bula-bulay` / `重疊-好`）、用 `<>`（排灣 `pa<quli>qulid` / "
    "`<重疊>真`）。"
)

CLITIC_NOTE = (
    "依附詞會把第一行分寫的兩個詞併成第二行同一個 token"
    "（第一行 `awa to` → 第二行 `awa=to`），所以第一行與第二行的"
    "詞數不一定相同;第二行與第三行才必須一個詞對一個詞。"
)

LOANWORD_NOTE = (
    "外來語借詞在第三行的 gloss 後面加語言標籤:`.日語`、`.華語`、"
    "`.台語`、`.英語`。例如 `sanzyuici` / `三十一.日語`、"
    "`ping-en` / `冰.華語-受焦`。第一行依實際發音書寫（可含連字號，"
    "如 `san-zyu-ici`），第二行合併成一個 token。`.` 不是切分符號，"
    "不影響詞素的數量。"
)


def _timecode_rows(files):
    """各種時間碼格式的檔數與一個例子。數字由本次執行算出來。"""
    counts = OrderedDict()
    samples = {}
    for corpus in files:
        for name, sample in corpus.timecode_formats.items():
            counts[name] = counts.get(name, 0) + 1
            if name not in samples:
                samples[name] = sample
    rows = []
    for name, count in sorted(counts.items(), key=lambda item: -item[1]):
        note = ""
        if name == "連字號式":
            note = "沒有毫秒，單位不明，待對方確認"
        rows.append((name, code(samples[name]), count, note))
    return rows


def _sheet_rows(files, sheet_names):
    """語料目錄與 ODS sheet 的對應。回傳 (對應表, 還沒交付語料的 sheet)。"""
    delivered = OrderedDict()
    for corpus in files:
        top = corpus.path.split("/")[0]
        sheet = SHEET_OF.get(top, "")
        if sheet:
            delivered.setdefault(sheet, set()).add(top)
    rows = []
    for folder, sheet in sorted(SHEET_OF.items()):
        if sheet in delivered:
            state = "已交付"
        else:
            state = "尚未交付"
        rows.append((code(folder + "/"), sheet, state))
    waiting = []
    for name in sorted(sheet_names or []):
        if name not in delivered:
            waiting.append(name)
    return rows, waiting


def format_section(files, sheet_names=None):
    """「語料格式說明」:語料長什麼樣。規則本身在 features/。"""
    lines = [heading("語料格式說明"), "", FORMAT_INTRO, ""]

    lines.append(heading("一組語料的結構", 3))
    lines.append("")
    lines.append(ENTRY_SHAPE)
    lines.append("")

    lines.append(heading("時間碼的格式", 3))
    lines.append("")
    lines.append(
        "語料裡並存下面幾種格式，程式一律拆成「開始」「結束」兩欄並"
        "保留原字串，不做單位換算（見 `features/時間碼.feature`）。"
        "檔數是本次執行算出來的。")
    lines.append("")
    rows = _timecode_rows(files)
    lines.append(table(["格式", "例子", "檔數", "備註"], rows))
    總和 = 0
    for name, sample, count, note in rows:
        總和 += count
    if 總和 > len(files):
        lines.append("")
        lines.append(
            "檔數加起來比檔案總數（" + str(len(files)) +
            " 個）多，因為有檔案在同一份裡混用兩種格式"
            "（南排灣 3 前段 SRT 式、後段逗號式），兩種各算一次。")
    lines.append("")

    lines.append(heading("第二行的切分符號", 3))
    lines.append("")
    rows = []
    for symbol, (meaning, sample) in SYMBOL_MEANING.items():
        rows.append((code(symbol), meaning, sample))
    lines.append(table(["符號", "意義", "例子（第二行 / 第三行）"], rows))
    lines.append("")
    lines.append(REDUPLICATION_NOTE)
    lines.append("")
    lines.append(CLITIC_NOTE)
    lines.append("")

    lines.append(heading("特殊符號與言談現象", 3))
    lines.append("")
    lines.append(
        "整理自 ODS 各 sheet 的「言談標記」章，13 個語言的規則大致"
        "一致。這一份就是程式視為合法、不列錯誤的那一份。")
    lines.append("")
    rows = []
    for mark, (where, why, legal) in SPECIAL_MARKS.items():
        rows.append((code(mark), where, why))
    lines.append(table(["標記", "標在第幾行", "說明"], rows))
    lines.append("")

    lines.append(heading("外來語標籤", 3))
    lines.append("")
    lines.append(LOANWORD_NOTE)
    lines.append("")

    lines.append(heading("語料目錄與標記清單 sheet 的對應", 3))
    lines.append("")
    rows, waiting = _sheet_rows(files, sheet_names)
    lines.append(table(["語料目錄", "ODS sheet", "狀態"], rows))
    if waiting:
        lines.append("")
        lines.append(
            "《常用構詞標記清單》還有這幾個 sheet 尚未交付語料:" +
            "、".join(waiting) + "。魯凱族若日後交付茂林、萬山的語料，"
            "需另建對應。")
    return "\n".join(lines)
