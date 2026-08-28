"""驗證 glossing 規則，產生 YAML 與報告。

用法(在專案根目錄):

    python -m scripts.validate_glossing [語料目錄]

通過驗證的組匯出到 kithann/out/corpus.yaml，不通過的列進
kithann/out/glossing_report.md。有錯誤時 exit code 非 0。
"""

import argparse
import os
import sys
from collections import Counter, OrderedDict

from scripts.smkul import report, yamlout
from scripts.smkul.entry import KIND_WHY, IssueKind, NormLog
from scripts.smkul.markers import (MarkerList, ODS_PATH,
                                   load_marker_lists, sheet_for)
from scripts.smkul.pairing import split_kind
from scripts.smkul.parser import MISMATCH_WHY
from scripts.smkul.parser import parse_corpus_file
from scripts.smkul.rules import validate

BASE = os.path.join("kithann", "giliau")

COMPARE_NOTE = (
    "「原文與切分不符」這項檢查是**逐字嚴格比對**:切分行去掉構詞符號"
    "(`-`、`=`、`<>`、`~`)之後，要與原文逐字相同，"
    "**多一個或少一個字母、漢字、數字、單引號都算錯誤**。\n\n"
    "詞的個數也要一個對一個。**只有依附詞（`=` 這個符號）例外**:"
    "它會把原文的兩個詞併成切分的一個詞，這樣算通過。\n\n"
    "比對時忽略兩項:\n\n"
    "1. 標點——原文保留句讀、切分照慣例不留。這項差異另外統計"
    "(見下面的 warning 章)，請確認切分行的句讀慣例。\n"
    "2. 英文大小寫——切分常把專有名詞寫成大寫。\n\n"
    "**空白不忽略**:空白會改變詞的個數，只差空白但詞數不同的"
    "算不符（分類記「詞數不同」）。"
    "單引號(喉塞音)也**不忽略**:排灣語 ODS 1-3 明定切分的 "
    "`[k]` / `[ʔ]` 要跟著原文的寫法。"
)


def collect(base, marker_lists, log):
    """走過語料，解析並驗證。回傳做報告需要的材料。

    語料的來源是 docx，不是 txt。marker_lists 是
    {sheet 名: MarkerList}，一個語言一份清單。
    """
    files = []
    issues = []
    uncertain = Counter()
    undecided = []
    mismatch = OrderedDict()
    for root, dirs, names in os.walk(base):
        for name in sorted(names):
            if not name.endswith(".docx"):
                continue
            path = os.path.join(root, name)
            rel = path[len(base) + 1:]
            sheet = sheet_for(rel)
            markers = marker_lists.get(sheet, MarkerList.empty())
            ethnic, variant = split_kind(rel)
            corpus = parse_corpus_file(
                path, rel, ethnic=ethnic, variant=variant, log=log)
            for issue in corpus.issues:
                issues.append(issue)
            for entry in corpus.entries:
                for issue in entry.issues:
                    issues.append(issue)
                    # 這一項是解析階段就掠著的,袂經過 validate。
                    if issue.kind is IssueKind.SOURCE_SEGMENT_MISMATCH:
                        _note_mismatch(mismatch, rel, entry, issue)
                if not entry.is_clean():
                    continue
                found, marks, hard = validate(entry, markers, sheet)
                for gloss, name_of in marks:
                    uncertain[(gloss, name_of)] += 1
                for gloss, name_of, case, seg in hard:
                    undecided.append((gloss, name_of, case, seg, rel,
                                      entry.number))
                for issue in found:
                    issues.append(issue)
                    entry.issues.append(issue)
            files.append(corpus)
    return files, issues, uncertain, undecided, mismatch


def _note_mismatch(mismatch, rel, entry, issue):
    """把「原文與切分不符」照細分類型收起來。"""
    kind = issue.detail.split(":", 1)[0]
    mismatch.setdefault(kind, []).append(
        (rel, entry.number, entry.source, entry.segmentation, issue.detail))


MISMATCH_PREFIX = "原文與切分不符-"


def why_of(label):
    """報告顯示的問題名稱 → 說明。"""
    if label.startswith(MISMATCH_PREFIX):
        return MISMATCH_WHY.get(label[len(MISMATCH_PREFIX):], "")
    for kind in IssueKind:
        if kind.value == label:
            return KIND_WHY.get(kind, "")
    return ""


def kinds_section(issues):
    """每一種問題的說明與例子，順序照總覽表(筆數多的排前面)。"""
    counter = report.count_kinds(issues)
    order = []
    for label, _ in counter.most_common():
        order.append(label)
    # 「原文與切分不符」的幾個細分排在一起,才好對照。
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
    """全部語料共幾組。"""
    total = 0
    for corpus in files:
        total += len(corpus.entries)
    return total


def overview(files, issues, exported_files, exported_sentences,
             undecided=None):
    total = entry_total(files)
    errors, warnings, notices = report.severity_split(issues)
    lines = [report.heading("總覽"), ""]
    lines.append("- 語料檔案:" + str(len(files)) + " 個")
    lines.append("- 語料組數:" + str(total) + " 組")
    if total:
        rate = 100.0 * exported_sentences / total
    else:
        rate = 0.0
    lines.append(
        "- 通過驗證、已匯出 YAML:" + str(exported_sentences) +
        " 組(" + ("%.1f" % rate) + "%)，分布在 " +
        str(exported_files) + " 個檔案"
    )
    lines.append("- 錯誤:" + str(len(errors)) + " 筆")
    lines.append("- warning:" + str(len(warnings)) + " 筆")
    lines.append("- 現象(不算錯誤、也不匯出):" + str(len(notices)) + " 筆")
    if undecided:
        lines.append(
            "- 構詞無法判斷:" + str(len(undecided)) +
            " 個詞素(不算錯誤、照常匯出，見「構詞判斷困難」那一章)")
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


def todo_section(issues, undecided, total_entries=0):
    """討論事項。逐項先寫「說明」(事實)，才寫「討論」(欲問對方ê)。"""
    lines = [report.heading("討論"), ""]
    counter = report.count_kinds(issues)

    lines.append(report.heading("需要修正的標注", 3))
    lines.append("")
    lines.append("說明:")
    lines.append("")
    lines.append(
        "每一項的意思與例子請看「問題類型說明與例子」那一章。"
        "「原文與切分不符」照差異大小分開列，才好判斷先修哪一類。"
    )
    lines.append("")
    order = []
    for kind in MISMATCH_WHY:
        order.append(MISMATCH_PREFIX + kind)
    for name in ("gloss 的詞比切分少", "gloss 的詞比切分多",
                 "切分沒有切，gloss 有切", "切分有切，gloss 沒有切",
                 "符號的種類不一樣", "行黏在一起", "缺翻譯行",
                 "孤兒時間碼", "結束時間早於開始", "空組",
                 "重複標註", "孤立雜訊行", "缺 gloss 段"):
        order.append(name)
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
        "除了「結束時間早於開始」以外，這些組目前都不匯出 YAML"
        "(時間碼顛倒是資料錯，標注本身沒問題，所以照常匯出)。"
        "要先修哪一類?「原文與切分不符」細分之後，哪幾類是真的要改、"
        "哪幾類其實是可以接受的拼寫慣例?"
    )

    lines.append("")
    lines.append(report.heading("構詞判斷困難的詞素要怎麼處理", 3))
    lines.append("")
    lines.append("說明:")
    lines.append("")
    lines.append(
        "有 " + str(len(undecided)) +
        " 個詞素判不出是不是詞根，YAML 的「構詞」欄記成 `無法判斷`。"
        "這不算錯誤、照常匯出。逐項統計與分類請看「構詞判斷困難」"
        "那一章，判定流程與例子在 `features/構詞判定.feature`。"
    )
    lines.append("")
    lines.append("討論:")
    lines.append("")
    lines.append(
        "統計表裡次數高又跨多個檔案的詞素，要補進"
        "《常用構詞標記清單》嗎?")

    lines.append("")
    lines.append(report.heading("純華語句要怎麼處理", 3))
    lines.append("")
    lines.append("說明:")
    lines.append("")
    lines.append(
        "受訪者講華語的句子有 " + str(counter.get("純華語句", 0)) +
        " 組，而且有三種表法:只有 1 行、原文+翻譯 2 行、4 行全是同一句華語。"
        "目前一律不匯出。"
    )
    lines.append("")
    lines.append("討論:")
    lines.append("")
    lines.append("要統一成哪一種表法?還是這些句子本來就不需要收進語料?")

    lines.append("")
    lines.append(report.heading("切分行的句讀慣例", 3))
    lines.append("")
    lines.append("說明:")
    lines.append("")
    lines.append(
        "有 " + str(counter.get("標點不同", 0)) +
        " 組是原文保留句讀、切分沒有。這不算錯誤，也不擋匯出。"
    )
    lines.append("")
    lines.append("討論:")
    lines.append("")
    lines.append("切分行不留句讀是預期的慣例嗎?")

    lines.append("")
    lines.append(report.heading("用語要不要換成語言學的標準說法", 3))
    lines.append("")
    lines.append("說明:")
    lines.append("")
    lines.append(
        "報告與 YAML 的用語是照語料的四行結構取的，不一定是語言學上"
        "通行的說法。下表列出現在用的詞、出現的地方，以及可能的替代。"
        "四行結構在文獻上叫 interlinear glossed text，各行都有慣用名稱。"
    )
    lines.append("")
    rows = [
        ("切分", "報告、YAML 的 `切分`、第二行",
         "語素切分、詞素分析、morpheme segmentation"),
        ("gloss", "報告、第三行",
         "逐語素註解、詞素註解、glossing"),
        ("族語", "YAML 的 `族語`、第一行",
         "原文、轉寫、族語原文、transcription"),
        ("翻譯", "YAML 的 `翻譯`、第四行",
         "自由翻譯、華語翻譯、free translation"),
        ("組", "報告全部，指一個編號加時間碼的單位",
         "句、語段、標註單位、entry"),
        ("構詞", "YAML 的 `構詞`，記這個詞素怎麼接上去的",
         "接法、構詞方式、詞素類型"),
        ("標記", "報告的「標記不在清單」等處",
         "語法標記、gloss 標籤"),
        ("詞根、詞綴、附著、中綴、重疊", "YAML 的 `構詞` 的值",
         "這幾個本來就是標準術語，應該不用改"),
    ]
    lines.append(
        report.table(["現在用的詞", "出現在哪裡", "可能的替代"], rows))
    lines.append("")
    lines.append("討論:")
    lines.append("")
    lines.append(
        "「切分」要不要換成語言學的說法?其他幾個詞呢?"
        "這些詞同時是 YAML 的 key，改名會動到已經匯出的資料，"
        "所以最好一次決定。"
    )

    lines.append("")
    lines.append(report.heading("有沒有原始的影片或音檔", 3))
    lines.append("")
    lines.append("說明:")
    lines.append("")
    lines.append(
        "每一組都帶著時間碼(共 " + str(total_entries) + " 組)，"
        "表示標注時有原始的錄影或錄音。我們手上只有 docx 與 txt，"
        "沒有拿到影音檔。有幾件事非得對照原始檔案才判斷得了:"
    )
    lines.append("")
    lines.append(
        "1. ODS 排灣語 1-3 明文寫著:第一行沒寫 `[k]` 或 `[']` 的時候"
        "「要聽音檔」才知道要補哪一個。「原文與切分不符-只差單引號」"
        "那 189 組就是這一類。"
    )
    lines.append(
        "2. 拉長音(`==`、`:`)、聽不清(`...`)、笑聲(`＠`)、咳嗽這些標記"
        "都是聽出來的，沒有音檔就沒辦法覆核。"
    )
    lines.append(
        "3. 魯凱霧台那兩個檔案的時間碼單位不明，對照音檔長度就能確認。"
    )
    lines.append(
        "4. 「孤兒時間碼」與「空組」那幾組的內容可能遺失，"
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


def run(base, ods_path=ODS_PATH):
    log = NormLog()
    marker_lists = load_marker_lists(ods_path)
    files, issues, uncertain, undecided, mismatch = collect(
        base, marker_lists, log)
    yaml_path, yaml_files, yaml_sentences = yamlout.write(files)

    sections = [
        "# Glossing 驗證報告",
        "更新日期:" + report.today() + "\n\n標記清單:`" +
        os.path.basename(ods_path) + "`",
        overview(files, issues, yaml_files, yaml_sentences, undecided),
        report.variant_section(
            variant_rows(files),
            ["族別", "語別", "檔數", "組數", "通過", "有問題", "通過率"],
        ),
        report.heading("YAML 輸出") + "\n\n" +
        "通過驗證的組匯出到 `" + yaml_path + "`，共 " +
        str(yaml_sentences) + " 組。\n\n" + report.YAML_SOURCE_WHY,
        report.format_section(files, marker_lists.keys()),
        report.norm_section(log, COMPARE_NOTE),
        kinds_section(issues),
        report.detail_section("問題明細", issues),
        report.hard_morphology_section(undecided),
        report.uncertain_section(uncertain),
        todo_section(issues, undecided, entry_total(files)),
    ]
    path = report.write("glossing_report.md", sections)
    errors, warnings, notices = report.severity_split(issues)
    return path, yaml_path, len(errors)


def main(argv=None):
    parser = argparse.ArgumentParser(description="驗證 glossing 規則")
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
