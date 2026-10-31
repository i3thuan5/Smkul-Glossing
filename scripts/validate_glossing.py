"""驗證標注規則，產生 YAML 與報告。

用法(在專案根目錄):

    python -m scripts.validate_glossing [語料目錄]

通過驗證的段匯出到 kithann/out/corpus.yaml，不通過的列進
kithann/out/glossing_report.md，校對表寫到 kithann/out/校對表/。
老師填好的校對表放在 kithann/校對/，重跑時會讀回來。
有錯誤時 exit code 非 0。
"""

import argparse
import os
import sys
from collections import OrderedDict, namedtuple

from scripts.smkul import proofreading, report, yamlout
from scripts.smkul.entry import KIND_WHY, IssueKind, NormLog
from scripts.smkul.markers import ODS_PATH, load_marker_lists
from scripts.smkul.pairing import split_kind
from scripts.smkul.parser import (DISCUSS_DOT, DISCUSS_PLUS,
                                  DISCUSS_SPEAKER, MISMATCH_WHY)
from scripts.smkul.parser import parse_corpus_file
from scripts.smkul.rules import validate

BASE = os.path.join("kithann", "giliau")
# 老師交回的校對表放這裡;程式產生的校對表放 SHEET_DIR,每次重跑都會蓋掉。
PROOF_DIR = os.path.join("kithann", "校對")
SHEET_DIR = os.path.join("kithann", "out", "校對表")

COMPARE_NOTE = (
    "「族語原句與詞素切割不符」這項檢查是**逐字嚴格比對**:"
    "詞素切割行去掉切割符號"
    "(`-`、`=`、`<>`、`~`)之後，要與族語原句逐字相同，"
    "**多一個或少一個字母、漢字、數字、單引號都算錯誤**。\n\n"
    "詞的個數也要一個對一個。**只有依附詞（`=` 這個符號）例外**:"
    "它會把族語原句的兩個詞併成詞素切割的一個詞，這樣算通過。\n\n"
    "比對時忽略兩項:\n\n"
    "1. 族語原句的標點——族語原句保留句讀，詞素切割不留。詞素切割行"
    "本身不能有標點(2026.09 會議案由五)，有的話另外記「詞素切割有標點」，"
    "見 `features/詞素切割標點.feature`。\n"
    "2. 英文大小寫——詞素切割常把專有名詞寫成大寫。\n\n"
    "**空白不忽略**:空白會改變詞的個數，只差空白但詞數不同的"
    "算不符（分類記「詞數不同」）。"
    "單引號(喉塞音)也**不忽略**:排灣語 ODS 1-3 明定詞素切割的 "
    "`[k]` / `[ʔ]` 要跟著族語原句的寫法。"
    "阿美語的 `^` 是《原住民族語言書寫系統》的喉塞音字母，同樣**不忽略**。"
)


# 校對相關的材料:校對表的每一列(含老師確認過的問題)、確認過的
# (Issue, Judgement)、要討論的 (Issue, Judgement)。
Proof = namedtuple("Proof", ["rows", "confirmed", "discussed"])


def collect(base, log, judgements=None):
    """走過語料，解析並驗證。回傳做報告需要的材料。

    語料的來源是 docx，不是 txt。judgements 是讀回來的老師判斷
    {ID: Judgement},「docx 正確，程式判斷錯」的問題不算問題。
    """
    if judgements is None:
        judgements = {}
    files = []
    issues = []
    mismatch = OrderedDict()
    proof = Proof([], [], [])
    book = proofreading.IdBook()
    for root, dirs, names in os.walk(base):
        for name in sorted(names):
            if not name.endswith(".docx"):
                continue
            path = os.path.join(root, name)
            rel = path[len(base) + 1:]
            ethnic, variant = split_kind(rel)
            corpus = parse_corpus_file(
                path, rel, ethnic=ethnic, variant=variant, log=log)
            judge = Judge(corpus, book, judgements, issues, proof)
            judge(corpus.issues, None)
            for entry in corpus.entries:
                judge(entry.issues, entry)
                for issue in entry.issues:
                    # 這一項是解析階段就掠著的,袂經過 validate。
                    if issue.kind is IssueKind.SOURCE_SEGMENT_MISMATCH:
                        _note_mismatch(mismatch, rel, entry, issue)
                if not entry.is_clean():
                    continue
                found = validate(entry)
                judge(found, entry)
                for issue in found:
                    entry.issues.append(issue)
            files.append(corpus)
    return files, issues, mismatch, proof


class Judge:
    """一個檔案的問題:算 ID、套老師的判斷,再收進報告與校對表。"""

    def __init__(self, corpus, book, judgements, issues, proof):
        self.corpus = corpus
        self.book = book
        self.judgements = judgements
        self.issues = issues
        self.proof = proof

    def __call__(self, found, entry):
        body = []
        if entry is not None:
            body = entry.body
        for issue in found:
            self.book.assign(issue, body)
        confirmed, discussed = proofreading.apply_judgements(
            found, self.judgements)
        for issue in found:
            self.issues.append(issue)
            self.proof.rows.append(self._row(issue, entry))
        for pair in confirmed:
            self.proof.confirmed.append(pair)
            self.proof.rows.append(self._row(pair[0], entry))
        for pair in discussed:
            self.proof.discussed.append(pair)

    def _row(self, issue, entry):
        return proofreading.SheetRow(
            self.corpus.ethnic, self.corpus.variant, issue, entry)


def _note_mismatch(mismatch, rel, entry, issue):
    """把「族語原句與詞素切割不符」照細分類型收起來。"""
    kind = issue.detail.split(":", 1)[0]
    mismatch.setdefault(kind, []).append(
        (rel, entry.number, entry.source, entry.segmentation, issue.detail))


MISMATCH_PREFIX = IssueKind.SOURCE_SEGMENT_MISMATCH.value + "-"


def why_of(label):
    """報告顯示的問題名稱 → 說明。"""
    if label.startswith(MISMATCH_PREFIX):
        return MISMATCH_WHY.get(label[len(MISMATCH_PREFIX):], "")
    for kind in IssueKind:
        if kind.value == label:
            return KIND_WHY.get(kind, "")
    return ""


# 依語言別統計表的欄名。
VARIANT_HEADERS = ["族別", "語言別", "檔數", "段數", "通過", "有問題", "通過率"]


def kinds_section(issues):
    """每一種問題的說明與例子，順序照總覽表(筆數多的排前面)。"""
    counter = report.count_kinds(issues)
    order = []
    for label, _ in counter.most_common():
        order.append(label)
    # 「族語原句與詞素切割不符」的幾個細分排在一起,才好對照。
    grouped = []
    for label in order:
        if not label.startswith(MISMATCH_PREFIX):
            grouped.append(label)
    for kind in MISMATCH_WHY:
        label = MISMATCH_PREFIX + kind
        if label in order:
            grouped.append(label)
    return report.kind_section("問題類型說明與例子", issues, why_of, grouped)


def entry_total(files):
    """全部語料共幾段。"""
    total = 0
    for corpus in files:
        total += len(corpus.entries)
    return total


def overview(files, issues, exported_files, exported_segments):
    total = entry_total(files)
    errors, exported, warnings, notices = report.severity_split(issues)
    lines = [report.heading("總覽"), ""]
    lines.append("- 語料檔案:" + str(len(files)) + " 個")
    lines.append("- 語料段數:" + str(total) + " 段")
    if total:
        rate = 100.0 * exported_segments / total
    else:
        rate = 0.0
    lines.append(
        "- 通過驗證、已匯出 YAML:" + str(exported_segments) +
        " 段(" + ("%.1f" % rate) + "%)，分布在 " +
        str(exported_files) + " 個檔案"
    )
    lines.append("- 錯誤（不匯出）:" + str(len(errors)) + " 筆")
    lines.append("- 錯誤（照常匯出）:" + str(len(exported)) + " 筆")
    lines.append("- 警告（照常匯出）:" + str(len(warnings)) + " 筆")
    lines.append("- 現象(不算錯誤、也不匯出):" + str(len(notices)) + " 筆")
    lines.append("")
    lines.append(report.kind_table(issues))
    return "\n".join(lines)


def variant_rows(files):
    rows = {}
    for corpus in files:
        key = (corpus.ethnic, corpus.variant)
        slot = rows.setdefault(key, [0, 0, 0, 0])
        slot[0] += 1
        slot[1] += len(corpus.entries)
        for entry in corpus.entries:
            if entry.is_clean():
                slot[2] += 1
            else:
                slot[3] += 1
    out = []
    for (ethnic, variant), (files_n, total, good, bad) in sorted(rows.items()):
        if total:
            rate = "%.1f%%" % (100.0 * good / total)
        else:
            rate = "-"
        out.append((ethnic, variant, files_n, total, good, bad, rate))
    return out


def todo_section(issues, total_entries=0):
    """討論事項。逐項先寫「說明」(事實)，才寫「討論」(欲問對方ê)。"""
    lines = [report.heading("討論"), ""]
    counter = report.count_kinds(issues)

    lines.append(report.heading("需要修正的標注", 3))
    lines.append("")
    lines.append("說明:")
    lines.append("")
    lines.append(
        "每一項的意思與例子請看「問題類型說明與例子」那一章。"
        "「族語原句與詞素切割不符」照差異大小分開列，才好判斷先修哪一類。"
    )
    lines.append("")
    order = []
    for kind in MISMATCH_WHY:
        order.append(MISMATCH_PREFIX + kind)
    for kind in (IssueKind.SEGMENT_PUNCTUATION,
                 IssueKind.GLOSS_FEWER, IssueKind.GLOSS_MORE,
                 IssueKind.GLOSS_CUT_MORE, IssueKind.GLOSS_CUT_FEWER,
                 IssueKind.SYMBOL_KIND_DIFF, IssueKind.GLUED_LINE,
                 IssueKind.MISSING_TRANSLATION, IssueKind.ORPHAN_TIMECODE,
                 IssueKind.REVERSED_TIMECODE, IssueKind.EMPTY_ENTRY,
                 IssueKind.DUPLICATE_ANNOTATION, IssueKind.STRAY_LINE,
                 IssueKind.MISSING_GLOSS_LINE):
        order.append(kind.value)
    rows = []
    for label in order:
        count = counter.get(label, 0)
        if not count:
            continue
        rows.append((label, count, why_of(label)))
    lines.append(report.table(["項目", "筆數", "說明"], rows))
    lines.append("")
    lines.append("討論:")
    lines.append("")
    lines.append(
        "除了「詞素切割有標點」與「結束時間早於開始」以外，這些段目前都"
        "不匯出 YAML(這兩類是資料錯，但標注還用得上，所以照常匯出)。"
        "要先修哪一類?「族語原句與詞素切割不符」細分之後，哪幾類是真的要改、"
        "哪幾類其實是可以接受的拼寫慣例?"
    )

    lines.append("")
    lines.append(report.heading("純華語句要怎麼處理", 3))
    lines.append("")
    lines.append("說明:")
    lines.append("")
    lines.append(
        "受訪者講華語的句子有 " + str(counter.get("純華語句", 0)) +
        " 段，而且有三種表法:只有 1 行、族語原句+華語翻譯 2 行、"
        "4 行全是同一句華語。"
        "目前一律不匯出。"
    )
    lines.append("")
    lines.append("討論:")
    lines.append("")
    lines.append("要統一成哪一種表法?還是這些句子本來就不需要收進語料?")

    lines.append("")
    lines.append(report.heading("有沒有原始的影片或音檔", 3))
    lines.append("")
    lines.append("說明:")
    lines.append("")
    lines.append(
        "每一段都帶著時間碼(共 " + str(total_entries) + " 段)，"
        "表示標注時有原始的錄影或錄音。我們手上只有 docx 與 txt，"
        "沒有拿到影音檔。有幾件事非得對照原始檔案才判斷得了:"
    )
    lines.append("")
    lines.append(
        "1. ODS 排灣語 1-3 明文寫著:第一行沒寫 `[k]` 或 `[']` 的時候"
        "「要聽音檔」才知道要補哪一個。「族語原句與詞素切割不符-只差單引號」"
        "那 189 段就是這一類。"
    )
    lines.append(
        "2. 拉長音(`==`、`:`)、聽不清(`...`)、笑聲(`＠`)、咳嗽這些標記"
        "都是聽出來的，沒有音檔就沒辦法覆核。"
    )
    lines.append(
        "3. 魯凱霧台那兩個檔案的時間碼單位不明，對照音檔長度就能確認。"
    )
    lines.append(
        "4. 「孤兒時間碼」與「空段」那幾段的內容可能遺失，"
        "有音檔就補得回來。"
    )
    lines.append("")
    lines.append("討論:")
    lines.append("")
    lines.append(
        "有原始的影片或音檔嗎?可以一起提供嗎?"
        "如果不能提供，上面這幾類就只能靠對方那邊處理。"
    )

    lines.append("")
    lines.append(report.heading("魯凱霧台的時間碼單位", 3))
    lines.append("")
    lines.append("說明:")
    lines.append("")
    lines.append(
        "魯凱霧台 1、2 的時間碼是 `00:00:00-00:04:21`，沒有毫秒，"
        "單位不明(可能是 時:分:秒，也可能是 分:秒:frame)。"
        "程式一律保留原字串不換算。"
    )
    lines.append("")
    lines.append("討論:")
    lines.append("")
    lines.append("這個格式的單位是什麼?")

    return "\n".join(lines)


DISCUSS_INTRO = (
    "下面三種符號現在**不算錯誤**，也照常匯出，要跟承辦討論:保留，"
    "還是提示要改。每種列最多 " + str(report.DISCUSS_LIMIT) + " 段，"
    "在語言別、檔案之間輪流挑。規格見 `features/詞素切割標點.feature`。"
)

# 待討論章的三節:(entry.discuss 的名稱, 小節名稱, 說明)。
DISCUSS_PARTS = [
    (DISCUSS_PLUS, "`+`",
     "例如泰雅的 `la+ga`、`yan+ka`，詞素翻譯也用 `+`(`助詞+助詞`)，"
     "看起來是表示縮約。《原住民族語言書寫系統》沒有這個符號。"),
    (DISCUSS_DOT, "詞中間的 `.`",
     "前後都緊接字母的 `.`，例如 `i.maza`、`kiya.ga`，看起來是把兩個詞"
     "連寫。書寫系統只有邵語用 `.` 區辨字母。詞頭、詞尾的 `.` 照樣算"
     "「詞素切割有標點」。"),
    (DISCUSS_SPEAKER, "說話者標記",
     "整個詞是 1 到 3 個字母加冒號，例如 `G:`、`Lj:`、`Yu:`。跟"
     "「對話組」是同一個現象。黏在詞前面的(`Yu:m-uwah`)當成一般的"
     "族語詞，冒號照樣算「詞素切割有標點」。"),
]


def discuss_chapter(files):
    """待討論:詞素切割的特殊符號。"""
    parts = []
    for name, label, why in DISCUSS_PARTS:
        rows = []
        for corpus in files:
            for entry in corpus.entries:
                count = entry.discuss.get(name, 0)
                if count:
                    rows.append(report.DiscussRow(
                        corpus.ethnic, corpus.variant, corpus.path,
                        entry.number, entry.source, entry.segmentation,
                        count))
        parts.append((label, why, rows))
    return report.discuss_section(
        "待討論：詞素切割的特殊符號", DISCUSS_INTRO, parts)


def proofreading_section():
    """校對流程:給業務單位看校對表在哪裡、怎麼填、怎麼交回。"""
    lines = [report.heading("校對流程"), ""]
    lines.append(
        "每次產生報告，程式也會在 `" + SHEET_DIR.replace(os.sep, "/") +
        "/` 產生校對表，一個語言別一個 Excel 檔"
        "（例如 `校對表_阿美_秀姑巒.xlsx`），可以直接用 Excel 開，也可以上傳"
        "Google 雲端硬碟用 Google 試算表開。報告裡的每一筆問題都附有 ID"
        "（例如 `ISSUE-3f9a2c1b`），對得到校對表的同一列。")
    lines.append("")
    lines.append(
        "校對表一筆問題一列，列出問題、程式的提示與四行語料，程式認為有"
        "問題的地方標成紅色粗體。請族語老師在「判斷」欄的下拉選單選一個:")
    lines.append("")
    lines.append(
        "1. **" + proofreading.FIX_DOCX + "**:程式判斷正確，請改 docx。"
        "docx 改好之後重跑，這一筆就不會再出現。")
    lines.append(
        "2. **" + proofreading.PROGRAM_WRONG + "**:docx 的寫法是對的。"
        "重跑之後這一筆不再算問題，移到報告最後一章「老師確認過、不是錯誤」；"
        "一段如果只剩這種問題，就照常匯出 YAML。")
    lines.append(
        "3. **" + proofreading.DISCUSS + "**:不確定，留到下次開會。"
        "這一筆照常算問題，另外列在「老師標要討論的項目」那一章。")
    lines.append("")
    lines.append(
        "「備註」欄可以寫理由。填好的校對表請交回，放進 `" +
        PROOF_DIR.replace(os.sep, "/") + "/`(檔名不限)，再重跑一次。"
        "重跑時程式會把老師的判斷與備註帶進新的校對表；docx 那一段改過"
        "的話，舊的判斷會失效、重新檢查，原本的判斷與備註移到「已不存在的"
        "紀錄」分頁，不會不見。")
    return "\n".join(lines)


def proof_chapters(proof, problems):
    """報告最後兩章:老師標要討論的項目、老師確認過、不是錯誤。"""
    discussed = []
    for issue, found in proof.discussed:
        discussed.append((issue, found.note))
    confirmed = []
    for issue, found in proof.confirmed:
        confirmed.append((issue, found.note))
    return [
        report.teacher_discuss_section("老師標要討論的項目", discussed),
        report.confirmed_section(
            "老師確認過、不是錯誤", confirmed, problems),
    ]


def run(base, ods_path=ODS_PATH, proof_dir=PROOF_DIR, sheet_dir=SHEET_DIR):
    log = NormLog()
    marker_lists = load_marker_lists(ods_path)
    readback = proofreading.read_judgements(proof_dir)
    files, issues, mismatch, proof = collect(
        base, log, readback.judgements)
    yaml_path, yaml_files, yaml_segments = yamlout.write(files)
    proofreading.write_sheets(sheet_dir, proof.rows, readback.judgements)

    sections = [
        "# Glossing 驗證報告",
        "更新日期:" + report.today() + "\n\n標記清單:`" +
        os.path.basename(ods_path) + "`",
        overview(files, issues, yaml_files, yaml_segments),
        report.variant_section(
            variant_rows(files),
            VARIANT_HEADERS,
        ),
        report.heading("YAML 輸出") + "\n\n" +
        "通過驗證的段匯出到 `" + yaml_path + "`，共 " +
        str(yaml_segments) + " 段。\n\n" + report.YAML_SOURCE_WHY,
        proofreading_section(),
        report.format_section(files, marker_lists.keys()),
        report.norm_section(log, COMPARE_NOTE),
        kinds_section(issues),
        report.detail_section("問題明細", issues),
        discuss_chapter(files),
        todo_section(issues, entry_total(files)),
    ]
    # 「老師確認過、不是錯誤」一定是最後一章。
    for chapter in proof_chapters(proof, readback.problems):
        sections.append(chapter)
    path = report.write("glossing_report.md", sections)
    errors, exported, warnings, notices = report.severity_split(issues)
    return path, yaml_path, len(errors)


def main(argv=None):
    parser = argparse.ArgumentParser(description="驗證標注規則")
    parser.add_argument("base", nargs="?", default=BASE, help="語料目錄")
    parser.add_argument(
        "--ods", default=ODS_PATH, help="構詞標記清單 ODS")
    args = parser.parse_args(argv)
    path, yaml_path, errors = run(args.base, args.ods)
    print("報告:" + path)
    print("YAML:" + yaml_path)
    print("錯誤:" + str(errors) + " 筆")
    if errors:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
