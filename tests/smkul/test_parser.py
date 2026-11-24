"""測試 parser.py 裡 feature 沒有涵蓋的部份。

字元正規化、排版分析、時間碼、族語原句詞素切割比對的規則都寫在對應的
features/*.feature，由 behave 測。這裡只留 feature 測不到的:
自動處理的計數、feature 沒有例子的錯誤分類、病態段。
Fixture 都是從真語料抽出來的。
"""

import os
import unittest

from tests import DATA

from scripts.smkul.entry import IssueKind, NO_TIME, NormKind, NormLog
from scripts.smkul.parser import (
    assemble_entry,
    bare_form,
    build_entry,
    check_segment_punctuation,
    compare_source,
    normalize_en_dash,
    normalize_line,
    parse_text,
    convert_timecode,
    parse_timecode,
    srt_string,
    timecode_milliseconds,
)


def load(name):
    path = os.path.join(DATA, name)
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def parse(name, log=None):
    return parse_text(load(name), path=name, log=log)


class TestTimecode(unittest.TestCase):
    """五種寫法拆成開始、結束,轉成 SRT 字串。規格見 features/時間碼.feature。"""

    def test_編號與時間碼同行(self):
        got = parse_timecode("1. 0:00:00.000,0:00:01.480")
        self.assertEqual(got[0], "1")
        self.assertEqual(got[1], "0:00:00.000")

    def test_不是時間碼(self):
        self.assertIsNone(parse_timecode("Kiya ha, Tku ita mnswayi"))
        self.assertIsNone(parse_timecode("1."))

    def test_五種寫法的格式名(self):
        cases = [
            ("0:00:27.880,0:00:29.567", "逗號式"),
            ("00:00:00,000 --> 00:00:07,228", "SRT 式"),
            ("0:01:07.227 --> 0:01:14.786", "--> 配小數點"),
            ("0:00:00.000–0:00:05.000", "en-dash 式"),
            ("00:04:21-00:07:05", "連字號式"),
        ]
        for line, name in cases:
            with self.subTest(line=line):
                self.assertEqual(parse_timecode(line)[3], name)

    def test_五種寫法都轉成_srt_字串(self):
        cases = [
            ("0:00:27.880,0:00:29.567", "00:00:27,880", "00:00:29,567"),
            ("00:00:00,000 --> 00:00:07,228", "00:00:00,000", "00:00:07,228"),
            ("0:01:07.227 --> 0:01:14.786", "00:01:07,227", "00:01:14,786"),
            ("0:00:00.000–0:00:05.000", "00:00:00,000", "00:00:05,000"),
            ("00:04:21-00:07:05", "00:00:04,700", "00:00:07,167"),
        ]
        for line, start, end in cases:
            with self.subTest(line=line):
                parsed = parse_timecode(line)
                got = convert_timecode(parsed[1], parsed[2], parsed[3])
                self.assertEqual(got, (start, end, None))

    def test_開始與結束的時位數不一樣也接受(self):
        parsed = parse_timecode("00:01:07.227 --> 0:01:14.786")
        got = convert_timecode(parsed[1], parsed[2], parsed[3])
        self.assertEqual(got, ("00:01:07,227", "00:01:14,786", None))

    def test_影格四捨五入成毫秒(self):
        # 5 影格 = 166.67 毫秒 → 167;21 影格 = 700 毫秒;15 影格 = 500 毫秒。
        self.assertEqual(timecode_milliseconds("00:07:05", "連字號式"), 7167)
        self.assertEqual(timecode_milliseconds("00:04:21", "連字號式"), 4700)
        self.assertEqual(timecode_milliseconds("00:00:15", "連字號式"), 500)
        # 1 影格 = 33.33 毫秒 → 33。
        self.assertEqual(timecode_milliseconds("00:00:01", "連字號式"), 33)

    def test_srt_字串補零(self):
        self.assertEqual(srt_string(0), "00:00:00,000")
        self.assertEqual(srt_string(3723004), "01:02:03,004")

    def test_毫秒一位或兩位數_時間不能用(self):
        for line in ("00:01:27,53 --> 00:01:32,726",
                     "00:03:53,733 --> 00:03:54,0",
                     "0:00:37.380,0:00:41.70"):
            with self.subTest(line=line):
                parsed = parse_timecode(line)
                got = convert_timecode(parsed[1], parsed[2], parsed[3])
                self.assertEqual(
                    got, (NO_TIME, NO_TIME, IssueKind.TIMECODE_MS_DIGITS))

    def test_毫秒位數不對就不比先後(self):
        # 照小數讀 12.72 > 12.272 是顛倒;位數不對就只記毫秒位數不對。
        parsed = parse_timecode("00:01:12,72 --> 00:01:12,272")
        got = convert_timecode(parsed[1], parsed[2], parsed[3])
        self.assertEqual(got[2], IssueKind.TIMECODE_MS_DIGITS)

    def test_結束早於開始_時間不能用(self):
        parsed = parse_timecode("18:13:21-13:20:11")
        got = convert_timecode(parsed[1], parsed[2], parsed[3])
        self.assertEqual(got, (NO_TIME, NO_TIME, IssueKind.REVERSED_TIMECODE))

    def test_開始等於結束不算顛倒(self):
        parsed = parse_timecode("00:04:26,066 --> 00:04:26,066")
        got = convert_timecode(parsed[1], parsed[2], parsed[3])
        self.assertEqual(got, ("00:04:26,066", "00:04:26,066", None))


class TestTimecodeInEntry(unittest.TestCase):
    """時間碼在段裡:換算結果、問題、時間碼行打錯。"""

    BODY = "kunaku\nkunaku\n我\n我\n"

    def kinds_of(self, entry):
        out = []
        for issue in entry.issues:
            out.append(issue.kind)
        return out

    def test_段的開始結束是_srt_字串(self):
        corpus = parse_text("26\n0:02:09.410,0:02:12.547\n" + self.BODY)
        entry = corpus.entries[0]
        self.assertEqual((entry.start, entry.end),
                         ("00:02:09,410", "00:02:12,547"))
        self.assertEqual(entry.issues, [])

    def test_毫秒位數不對_段記問題_時間是數字(self):
        corpus = parse_text("12\n00:01:27,53 --> 00:01:32,726\n" + self.BODY)
        entry = corpus.entries[0]
        self.assertEqual((entry.start, entry.end), (NO_TIME, NO_TIME))
        self.assertIsInstance(entry.start, float)
        self.assertEqual(self.kinds_of(entry), [IssueKind.TIMECODE_MS_DIGITS])
        self.assertIn("00:01:27,53", entry.issues[0].detail)

    def test_結束早於開始_說明附原字串(self):
        corpus = parse_text("1\n18:13:21-13:20:11\n" + self.BODY)
        issue = corpus.entries[0].issues[0]
        self.assertIs(issue.kind, IssueKind.REVERSED_TIMECODE)
        self.assertEqual(
            issue.compare, [("開始", "18:13:21"), ("結束", "13:20:11")])

    def test_時間碼行打錯(self):
        text = (
            "174\n00:11:30,000 --> 00:11:36,534\n" + self.BODY + "\n"
            "175\n00:11:36,534 --> 00:11:39,486—XL3G \n"
            "vutul nu edu\nvutul nu edu\n睪丸 屬格 老鼠\n老鼠睪丸\n")
        corpus = parse_text(text, path="t.docx")
        self.assertEqual(len(corpus.entries), 2)
        entry = corpus.entries[1]
        self.assertEqual(entry.number, "175")
        self.assertEqual((entry.start, entry.end), (NO_TIME, NO_TIME))
        self.assertEqual(self.kinds_of(entry), [IssueKind.TIMECODE_TYPO])
        self.assertIn("—XL3G", entry.issues[0].detail)
        self.assertEqual(len(entry.body), 4)
        self.assertEqual(corpus.entries[0].issues, [])

    def test_時間打錯的幾種樣子(self):
        for line in ("0:05:00.56–3,0:05:02.563", "01:4607-01:53:28",
                     "11:38:28-11;47:16", "0:03:37.520,0:03:45.",
                     ".0:01:05.370,0:01:07.370", "0:12:16.8102"):
            with self.subTest(line=line):
                corpus = parse_text("157.\n" + line + "\n" + self.BODY)
                self.assertEqual(len(corpus.entries), 1)
                entry = corpus.entries[0]
                self.assertEqual(entry.number, "157")
                self.assertEqual(
                    self.kinds_of(entry), [IssueKind.TIMECODE_TYPO])

    def test_前面不是編號行_不算時間碼行打錯(self):
        text = (
            "81\n00:07:13,308 --> 00:07:18,410\n" + self.BODY + "\n"
            "82_00:07:18,410 --> 00:07:23,806\n" + self.BODY)
        corpus = parse_text(text, path="t.docx")
        self.assertEqual(len(corpus.entries), 1)
        self.assertEqual(corpus.entries[0].issues, [])

    def test_第一段時間碼行前面的_bom_拿掉後切得出第一段(self):
        # 魯凱霧台 3、泰雅俚語(上):BOM 在第一段時間碼行的最前面,
        # 前面還有檔頭與編號行。以前第一段整段被當成檔頭。
        log = NormLog()
        text = "3.包鳳嬌\n1.\n﻿0:00:00.000,0:00:05.580\n" + self.BODY
        corpus = parse_text(text, path="t.docx", log=log)
        self.assertEqual(corpus.header_notes, ["3.包鳳嬌"])
        self.assertEqual(len(corpus.entries), 1)
        entry = corpus.entries[0]
        self.assertEqual((entry.number, entry.start),
                         ("1", "00:00:00,000"))
        self.assertEqual(entry.issues, [])
        self.assertEqual(log.records[NormKind.BOM].count, 1)

    def test_內文的數字冒號不會被當成時間碼行(self):
        # 前一行不是編號行,就算有「數字:數字」也不是段的起頭。
        text = "1\n0:00:01.000,0:00:02.000\nkunaku 3:20\nkunaku\n我\n我\n"
        corpus = parse_text(text)
        self.assertEqual(len(corpus.entries), 1)
        self.assertEqual(corpus.entries[0].issues, [])


class TestNormalize(unittest.TestCase):

    def test_沒有_endash_就不計數(self):
        log = NormLog()
        got = normalize_en_dash("PI-書-處焦", log, "a.txt", "79")
        self.assertEqual(got, "PI-書-處焦")
        self.assertEqual(log.records[NormKind.EN_DASH].count, 0)

    def test_引號轉成_u02bc_才計數(self):
        log = NormLog()
        got = normalize_line("mi-do’do to i loma'", log, "a.txt", "1")
        self.assertEqual(got, "mi-doʼdo to i lomaʼ")
        self.assertEqual(log.records[NormKind.APOSTROPHE].count, 1)

    def test_只有引用符號_沒轉就不計數(self):
        log = NormLog()
        got = normalize_line('"Bikuy \' sun mu.', log, "a.txt", "143")
        self.assertEqual(got, '"Bikuy \' sun mu.')
        self.assertEqual(log.records[NormKind.APOSTROPHE].count, 0)

    def test_已經是_u02bc_不計數(self):
        log = NormLog()
        normalize_line("lomaʼ", log, "a.txt", "1")
        self.assertEqual(log.records[NormKind.APOSTROPHE].count, 0)


class TestSplitEntries(unittest.TestCase):

    def test_典型_連字號式_會記單位不明(self):
        corpus = parse("典型_連字號式.txt")
        kinds = []
        for issue in corpus.issues:
            kinds.append(issue.kind)
        self.assertIn(IssueKind.UNKNOWN_TIMECODE_UNIT, kinds)
        self.assertEqual(corpus.entries[0].end, "00:00:04,700")

    def test_編號同行(self):
        corpus = parse("編號同行.txt")
        self.assertEqual(len(corpus.entries), 2)
        self.assertEqual(corpus.entries[0].number, "1")
        self.assertEqual(corpus.entries[1].number, "2")

    def test_格式中途切換不記問題(self):
        corpus = parse("格式中途切換.txt")
        self.assertGreater(len(corpus.timecode_formats), 1)
        self.assertEqual(corpus.issues, [])
        for entry in corpus.entries:
            self.assertIsInstance(entry.start, str)

    def test_孤兒時間碼(self):
        corpus = parse("病態_孤兒時間碼.txt")
        orphans = []
        for entry in corpus.entries:
            for issue in entry.issues:
                if issue.kind is IssueKind.ORPHAN_TIMECODE:
                    orphans.append(issue)
        self.assertEqual(len(orphans), 1)

    def test_全形等號_解析後沒有全形(self):
        log = NormLog()
        corpus = parse("正規化_全形等號.txt", log)
        for entry in corpus.entries:
            for line in entry.body:
                self.assertNotIn("＝", line)
        self.assertTrue(log.records[NormKind.FULLWIDTH_EQUALS].count >= 1)


def speakers(*lines, number="114", time="0:09:55.806,0:09:58.812"):
    """一段語料的全文:編號、時間碼、內文。"""
    return number + ".\n" + time + "\n" + "\n".join(lines) + "\n"


class TestSpeakers(unittest.TestCase):
    """兩位說話者照說話者切段。feature 有對話段、兩位發音人與組數對不起來
    各一例,這裡補 feature 沒有的邊界。例子都是南排灣 4_張枝妹。"""

    def numbers(self, text):
        out = []
        for entry in parse_text(text, path="t.docx").entries:
            out.append(entry.number)
        return out

    def test_族語原句與華語翻譯有說話者標記_照標記切(self):
        # 第 151 段。
        corpus = parse_text(speakers(
            "K: tu sikuda azua? Lj: ʼu qentj-an== e 漫畫",
            "K: tu si-kuda azua?",
            "K: 補語連詞 參焦.工具-如何 斜格.那",
            "Lj: ʼu=qentj-an e 漫畫",
            "Lj: 我.屬格=看-AN 填補詞 漫畫",
            "(那是做什麼的?) 我拿來看啊...漫畫",
        ), path="t.docx")
        bodies = []
        for entry in corpus.entries:
            bodies.append(entry.body[0])
        self.assertEqual(
            bodies, ["K: tu sikuda azua?", "Lj: ʼu qentj-an== e 漫畫"])

    def test_換手兩次以上_切更多段(self):
        # 第 23 段:K → Lj → K → Lj。原本的華語翻譯
        # 「(你母親?) 叫laus, 也是一樣patalaq家」少了 K 第二句的翻譯,
        # 切不成四份;這裡補上「(laus?)」,只測換手兩次的切法。
        text = speakers(
            "(a su kina? ) ti laus== (laus? ) ui a patalaq== mamaw.",
            "K: a su=kina", "K: 你.屬格=媽媽",
            "Lj: ti laus", "Lj: 主格 人名",
            "K: laus", "K: 人名",
            "Lj: ui a patalaq mamaw", "Lj: 是 連繫詞 家名 一樣",
            "(你母親?) 叫laus (laus?) 也是一樣patalaq家",
            number="23")
        self.assertEqual(self.numbers(text), ["23-1", "23-2", "23-3", "23-4"])

    def test_華語翻譯少一份_整段不切(self):
        # 第 23 段原本的華語翻譯。
        text = speakers(
            "(a su kina? ) ti laus== (laus? ) ui a patalaq== mamaw.",
            "K: a su=kina", "K: 你.屬格=媽媽",
            "Lj: ti laus", "Lj: 主格 人名",
            "K: laus", "K: 人名",
            "Lj: ui a patalaq mamaw", "Lj: 是 連繫詞 家名 一樣",
            "(你母親?) 叫laus, 也是一樣patalaq家",
            number="23")
        self.assertEqual(self.numbers(text), ["23"])

    def test_同一組寫了兩次_標記也重複_不切(self):
        # 第 169 段:族語原句的標記是 Lj: Lj: K: K:,跟分組的順序對不起來。
        text = speakers(
            "Lj: Lj: a sema  inu? K: K: a sema  gade== a== tima?",
            "Lj: a s<em>a inu", "Lj: 主格 <主焦>去 哪",
            "K: a s<em>a gade a tima", "K: 主格 <主焦>去 山 填補詞 誰",
            "Lj: a s<em>a inu", "Lj: 主格 <主焦>去 哪",
            "K: a s<em>a gade a tima", "K: 主格 <主焦>去 山 填補詞 誰",
            "去哪裡? (比如去山上...是誰教妳的? )",
            number="169")
        self.assertEqual(self.numbers(text), ["169"])

    def test_只有一位說話者_不切(self):
        text = speakers(
            "A: na mahau i tama tina)", "A: na=mahau' i tama tina",
            "A: 非實現=主焦.罵 斜格 父親 母親", "爸媽會罵", number="12")
        self.assertEqual(self.numbers(text), ["12"])

    def test_時間碼的問題留在第一段(self):
        text = speakers(
            "(anema?) 電土", "K: anema", "K: 什麼", "Lj: 電土", "Lj: 電土",
            "(那是什麼?) 電土", time="0:09:58.812,0:09:55.806")
        corpus = parse_text(text, path="t.docx")
        kinds = []
        for entry in corpus.entries:
            found = []
            for issue in entry.issues:
                found.append((issue.kind, issue.number))
            kinds.append(found)
        self.assertEqual(kinds, [
            [(IssueKind.REVERSED_TIMECODE, "114-1")], []])
        for entry in corpus.entries:
            self.assertEqual((entry.start, entry.end), (NO_TIME, NO_TIME))

    def test_切開的段時間一樣(self):
        text = speakers(
            "(anema?) 電土", "K: anema", "K: 什麼", "Lj: 電土", "Lj: 電土",
            "(那是什麼?) 電土")
        corpus = parse_text(text, path="t.docx")
        times = []
        for entry in corpus.entries:
            times.append((entry.start, entry.end))
        self.assertEqual(times, [("00:09:55,806", "00:09:58,812")] * 2)


class TestAssemble(unittest.TestCase):
    """組四行:標準段、長句換行重組、重複標註。"""

    def assemble_all(self, name, log=None):
        corpus = parse(name, log)
        out = []
        for entry in corpus.entries:
            out.append((entry, assemble_entry(entry, log)))
        return out

    def test_endash_詞素翻譯_重組後換半形(self):
        log = NormLog()
        entry, ok = self.assemble_all("正規化_endash_詞素翻譯.txt", log)[0]
        self.assertTrue(ok)
        self.assertNotIn("–", entry.gloss)
        self.assertIn("PI-書-處焦", entry.gloss)
        self.assertEqual(log.records[NormKind.EN_DASH].count, 1)

    def test_重複標註_不可以組起來(self):
        """南排灣 4 第 156、157 段是同一句留兩版,不是換行。"""
        results = self.assemble_all("病態_重複標註.txt")
        self.assertEqual(len(results), 2)
        for entry, ok in results:
            self.assertFalse(ok)
            kinds = []
            for issue in entry.issues:
                kinds.append(issue.kind)
            self.assertIn(IssueKind.DUPLICATE_ANNOTATION, kinds)
            self.assertFalse(entry.is_clean())

    def test_病態段都組不起來(self):
        names = [
            "病態_黏行.txt",
            "病態_缺詞素翻譯行.txt",
            "病態_缺華語翻譯行.txt",
            "病態_雜訊行.txt",
        ]
        for name in names:
            for entry, ok in self.assemble_all(name):
                self.assertFalse(ok, name + " 第" + entry.number + "段")


class TestSourceSegmentation(unittest.TestCase):
    """嚴格用族語原句檢查詞素切割:差一個字母或單引號就算錯誤。"""

    def check(self, name, index=0):
        corpus = parse(name)
        entry = corpus.entries[index]
        assemble_entry(entry)
        kinds = []
        for issue in entry.issues:
            kinds.append(issue.kind)
        return entry, kinds

    def test_bare_form_留單引號_去掉標點大小寫(self):
        self.assertEqual(bare_form("Kiya ha, Tku"), "kiyahatku")
        self.assertEqual(bare_form("’ana ne’a"), "'anane'a")
        self.assertEqual(
            bare_form("pi-sano-Amis a caciyaw awa=to"),
            "pisanoamisacaciyawawato",
        )

    def test_bare_form_留阿美語的_喉塞音字母(self):
        # 《原住民族語言書寫系統》的阿美語，^ 是喉塞音字母。
        self.assertEqual(bare_form("pa^tang"), "pa^tang")

    def test_bare_form_去掉書寫系統的符號(self):
        # 阿美語以外的 :、泰雅語的 _ 是符號，不是字母。
        self.assertEqual(bare_form("iti:raw"), "itiraw")
        self.assertEqual(bare_form("m_yan"), "myan")

    def test_bare_form_u02bc_也是喉塞音(self):
        self.assertEqual(bare_form("ʼana neʼa"), "'anane'a")


class TestCompareSource(unittest.TestCase):
    """族語原句詞素切割比對 feature 沒有例子的邊界。"""

    def test_沒給族別_泰雅語群的放寬不套用(self):
        got = compare_source("Shngiun da.", "shungi-un da")
        self.assertFalse(got.passed)
        self.assertEqual(got.kind, "只差一個字母")

    def test_沒給族別_加號不能接詞(self):
        got = compare_source("la ga", "la+ga")
        self.assertEqual(got.kind, "詞數不同")

    def test_泰雅語群也不放寬單引號(self):
        got = compare_source("haan", "ha'an", "太魯閣")
        self.assertEqual(got.kind, "只差單引號")

    def test_阿美語詞素切割少了長音(self):
        got = compare_source("Raka:t sa haw", "Rakat sa haw", "阿美")
        self.assertEqual(got.kind, "只差長音符號")
        self.assertEqual(got.detail, "詞素切割少了「:」")

    def test_阿美語以外的長音不比(self):
        self.assertTrue(compare_source("Raka:t sa", "Rakat sa", "排灣").passed)

    def test_阿美語句讀的冒號不算長音(self):
        self.assertTrue(
            compare_source("sowal sa: pina kiya", "sowal sa pina kiya",
                           "阿美").passed)

    def test_長音之外還差字母_照原本的分類(self):
        got = compare_source("Raka:t sa", "Rakot sa", "阿美")
        self.assertEqual(got.kind, "只差一個字母")

    def test_族語和華語不一致_詞數不一樣就不判(self):
        got = compare_source("awaay to no moyi", "awa-ay=to no 母語")
        self.assertNotEqual(got.kind, "族語和華語不一致")

    def test_拉長音最先判(self):
        got = compare_source("lja tutang", "lja== tutang 母語")
        self.assertEqual(got.kind, "詞素切割有拉長音")


class TestClassify(unittest.TestCase):
    """組不起來的段,要分得出是哪一種異常。"""

    def kinds_of(self, name):
        corpus = parse(name)
        out = []
        for entry in corpus.entries:
            build_entry(entry)
            labels = []
            for issue in entry.issues:
                labels.append(issue.kind)
            out.append((entry.number, labels))
        return out

    def test_空段(self):
        got = self.kinds_of("病態_空段.txt")
        self.assertIn(IssueKind.EMPTY_ENTRY, got[0][1])
        # 第 2 段是正常的段,但族語原句 `O na` 詞素切割寫成 `Ona`,
        # 詞數對不起來——照族語原句詞素切割比對.feature「只差空白，
        # 先算不通過」那條,這算「族語原句與詞素切割不符-詞數不同」。
        self.assertEqual(got[1][1], [IssueKind.MISMATCH_WORDS])

    def test_孤兒時間碼(self):
        got = self.kinds_of("病態_孤兒時間碼.txt")
        self.assertIn(IssueKind.ORPHAN_TIMECODE, got[2][1])

    def test_雜訊行(self):
        got = self.kinds_of("病態_雜訊行.txt")
        self.assertIn(IssueKind.STRAY_LINE, got[0][1])

    def test_布農的_0000_也是雜訊(self):
        got = self.kinds_of("布農雜訊.txt")
        self.assertIn(IssueKind.STRAY_LINE, got[0][1])

    def test_純華語句_三種表法(self):
        got = self.kinds_of("病態_純華語句.txt")
        for number, labels in got:
            self.assertIn(IssueKind.CHINESE_ONLY, labels, number)

    def test_缺華語翻譯行(self):
        got = self.kinds_of("病態_缺華語翻譯行.txt")
        for number, labels in got:
            self.assertIn(IssueKind.MISSING_TRANSLATION, labels, number)

    def test_行黏在一起(self):
        got = self.kinds_of("病態_黏行.txt")
        for number, labels in got:
            self.assertIn(IssueKind.GLUED_LINE, labels, number)

    def test_缺詞素翻譯行(self):
        got = self.kinds_of("病態_缺詞素翻譯行.txt")
        self.assertIn(IssueKind.MISSING_GLOSS_LINE, got[0][1])

    def test_重複標註不會再分成別種(self):
        got = self.kinds_of("病態_重複標註.txt")
        for number, labels in got:
            self.assertEqual(labels, [IssueKind.DUPLICATE_ANNOTATION])

    def test_正常的段沒問題(self):
        for name in ("典型_srt式.txt", "長句換行.txt"):
            corpus = parse(name)
            for entry in corpus.entries:
                build_entry(entry)
                for issue in entry.issues:
                    self.assertIsNot(issue.kind, IssueKind.GLUED_LINE)


class TestPunctuation(unittest.TestCase):
    """族語原句有標點、詞素切割沒有，算通過，不記任何問題。"""

    def test_族語原句有標點_詞素切割沒有_不記任何問題(self):
        corpus = parse("典型_逗號式.txt")
        entry = corpus.entries[0]
        build_entry(entry)
        self.assertIn(",", entry.source)
        self.assertNotIn(",", entry.segmentation)
        self.assertEqual(entry.issues, [])


def segment_entry(segmentation, source=None, ethnic=""):
    """用一段四行的語料組出 Entry，跑過 build_entry。"""
    if source is None:
        source = segmentation
    text = "1\n0:00:00.000,0:00:02.000\n" + source + "\n" + \
        segmentation + "\n詞\n華語\n"
    corpus = parse_text(text, path="t.txt", ethnic=ethnic)
    entry = corpus.entries[0]
    build_entry(entry, ethnic=ethnic)
    return entry


class TestSegmentPunctuation(unittest.TestCase):
    """詞素切割行不能有標點。規格見 features/詞素切割標點.feature。"""

    def hint(self, segmentation, ethnic):
        return check_segment_punctuation(segmentation, ethnic).hint

    def test_詞尾標點_刪掉(self):
        self.assertEqual(
            self.hint("iq kiya.", "太魯閣"),
            "詞素切割第 2 個詞的 `kiya.` 有標點 `.`，程式判斷要刪掉，"
            "因為詞素切割不能有標點，應該寫是 `kiya`",
        )

    def test_一個詞好幾種標點_依出現順序列(self):
        self.assertEqual(
            self.hint("azua?!", "排灣"),
            "詞素切割第 1 個詞的 `azua?!` 有標點 `?`、`!`，程式判斷要刪掉，"
            "因為詞素切割不能有標點，應該寫是 `azua`",
        )

    def test_全形小老鼠是笑聲_不算標點(self):
        self.assertEqual(self.hint("pa-'a-pazangal ＠", "排灣"), "")

    def test_只有符號的詞_整個詞刪掉_寫整行(self):
        self.assertEqual(
            self.hint("pa-'a-pazangal |", "排灣"),
            "詞素切割第 2 個詞的 `|` 有符號 `|`，程式判斷要整個詞刪掉，"
            "因為詞素切割不能有標點，應該寫是 `pa-'a-pazangal`",
        )

    def test_括號_程式無法判斷(self):
        self.assertEqual(
            self.hint("nu a(ne)ma.aya-a(ne)ma.aya='en", "排灣"),
            "詞素切割第 2 個詞的 `a(ne)ma.aya-a(ne)ma.aya='en` 有括號 `()`，"
            "程式無法判斷，請標注者確認",
        )

    def test_好幾個詞_用分號接起來(self):
        self.assertEqual(
            self.hint("aji. uri. o brah", "太魯閣"),
            "詞素切割第 1 個詞的 `aji.` 有標點 `.`，程式判斷要刪掉，"
            "因為詞素切割不能有標點，應該寫是 `aji`；"
            "詞素切割第 2 個詞的 `uri.` 有標點 `.`，程式判斷要刪掉，"
            "因為詞素切割不能有標點，應該寫是 `uri`",
        )

    def test_阿美語的_喉塞音與長音不算標點(self):
        self.assertEqual(self.hint("Ma-so^so haw", "阿美"), "")
        self.assertEqual(self.hint("O no iti:ya-ay=ho sanay", "阿美"), "")

    def test_別的語言的_喉塞音符號算標點(self):
        self.assertIn("有標點 `^`", self.hint("pa^tang", "排灣"))

    def test_泰雅語的底線不算標點(self):
        self.assertEqual(self.hint("k_yaqih hi=nya", "泰雅"), "")

    def test_別的語言的底線算標點(self):
        self.assertIn("有標點 `_`", self.hint("k_yaqih", "排灣"))

    def test_邵語的點與賽夏語的冒號不算標點(self):
        self.assertEqual(self.hint("put.huum", "邵"), "")
        self.assertEqual(self.hint("lamo:", "賽夏"), "")

    def test_泰雅語的加號不算標點(self):
        result = check_segment_punctuation("la+ga yan+ka", "泰雅")
        self.assertEqual(result.hint, "")
        self.assertEqual(dict(result.findings), {})

    def test_泰雅語以外的加號_建議改成點(self):
        result = check_segment_punctuation("qani la+ga", "太魯閣")
        self.assertEqual(list(result.findings), [IssueKind.SEGMENT_PLUS])
        self.assertEqual(
            result.hint,
            "詞素切割第 2 個詞的 `la+ga` 有標點 `+`，程式判斷要改成 `.`，"
            "因為只有泰雅語可以用 + 標示詞組，應該寫是 `la.ga`",
        )

    def test_詞中間的點不算標點(self):
        result = check_segment_punctuation("kika kiya.ga", "太魯閣")
        self.assertEqual(result.hint, "")

    def test_詞頭的點仍算標點(self):
        result = check_segment_punctuation("nanu.yasa .qu", "泰雅")
        self.assertEqual(
            list(result.findings), [IssueKind.SEGMENT_PUNCTUATION])
        self.assertIn("`.qu` 有標點 `.`", result.hint)
        self.assertNotIn("nanu.yasa", result.hint)

    def test_獨立的說話者標記不算標點(self):
        result = check_segment_punctuation(
            "K: anema ta azua? Lj: 電土", "排灣")
        self.assertEqual(
            result.hint,
            "詞素切割第 4 個詞的 `azua?` 有標點 `?`，程式判斷要刪掉，"
            "因為詞素切割不能有標點，應該寫是 `azua`",
        )

    def test_泰雅語第一個詞的冒號_另一種問題(self):
        result = check_segment_punctuation("Yu:m-uwah kekong", "泰雅")
        self.assertEqual(
            list(result.findings), [IssueKind.SEGMENT_SPEAKER_COLON])
        self.assertEqual(
            result.hint,
            "詞素切割第 1 個詞的 `Yu:m-uwah` 有標點 `:`，程式判斷要刪掉，"
            "因為詞素切割不能有標點，應該寫是 `Yum-uwah`",
        )

    def test_泰雅語不是第一個詞的冒號_是一般標點(self):
        result = check_segment_punctuation("yan=sami Yu:qani ga", "泰雅")
        self.assertEqual(
            list(result.findings), [IssueKind.SEGMENT_PUNCTUATION])

    def test_沒有標點(self):
        result = check_segment_punctuation("masa-maan i to", "阿美")
        self.assertEqual(result.hint, "")
        self.assertEqual(dict(result.findings), {})

    def test_一段只記一筆_照常匯出(self):
        entry = segment_entry("aji. uri. o brah", "Aji uri o brah", "太魯閣")
        found = []
        for issue in entry.issues:
            if issue.kind is IssueKind.SEGMENT_PUNCTUATION:
                found.append(issue)
        self.assertEqual(len(found), 1)
        self.assertIn("`aji.`", found[0].detail)
        self.assertIn("`uri.`", found[0].detail)
        self.assertTrue(entry.is_clean())

    def test_同一段兩種標點問題_各記一筆(self):
        entry = segment_entry("kiya. yan+ka", "kiya yaka", "太魯閣")
        kinds = []
        for issue in entry.issues:
            kinds.append(issue.kind)
        self.assertIn(IssueKind.SEGMENT_PUNCTUATION, kinds)
        self.assertIn(IssueKind.SEGMENT_PLUS, kinds)
        self.assertFalse(entry.is_clean())

    def test_純華語句不檢查(self):
        entry = segment_entry("好，這個時候", ethnic="排灣")
        for issue in entry.issues:
            self.assertIsNot(issue.kind, IssueKind.SEGMENT_PUNCTUATION)


class TestReversedTimecode(unittest.TestCase):
    """結束時間比開始還早,是打錯的。"""

    def test_時間碼換成總毫秒數(self):
        self.assertEqual(timecode_milliseconds("0:00:27.880", "逗號式"), 27880)
        self.assertEqual(timecode_milliseconds("00:04:21", "連字號式"), 4700)
        self.assertIsNone(timecode_milliseconds("00:04:21", "逗號式"))

    def test_正常的時間碼沒問題(self):
        text = "1\n00:00:00-00:04:21\nkunaku\nkunaku\n我\n我\n"
        corpus = parse_text(text, path="t.txt")
        for issue in corpus.entries[0].issues:
            self.assertIsNot(issue.kind, IssueKind.REVERSED_TIMECODE)
