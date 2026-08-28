"""測試 entry.py 的資料型別。"""

import unittest

from scripts.smkul.entry import (
    SEVERITY,
    Attachment,
    CorpusFile,
    Entry,
    Issue,
    IssueKind,
    Morpheme,
    NormKind,
    NormLog,
    Severity,
    Word,
)


class TestIssue(unittest.TestCase):

    def test_每個_kind_都有_severity(self):
        for kind in IssueKind:
            self.assertIn(kind, SEVERITY)

    def test_error_與_warning(self):
        error = Issue(IssueKind.GLUED_LINE, "a.txt", "5")
        warning = Issue(IssueKind.MIXED_TIMECODE_FORMAT, "a.txt")
        self.assertTrue(error.is_error())
        self.assertFalse(warning.is_error())

    def test_純華語句_是現象_不是錯誤(self):
        issue = Issue(IssueKind.CHINESE_ONLY, "a.txt", "112")
        self.assertIs(issue.severity, Severity.NOTICE)
        self.assertFalse(issue.is_error())


class TestYaml(unittest.TestCase):
    """對照 corpus-export spec 的秀姑巒第 26 組範例。"""

    def build_entry(self):
        awato = Word("awato", "awa=to", [
            Morpheme("awa", "沒有", Attachment.ROOT),
            Morpheme("to", "完成貌", Attachment.CLITIC),
        ])
        return Entry(
            number="26",
            start="00:02:09,410",
            end="00:02:12,547",
            source="pisanoAmis a caciyaw awa to matini",
            translation="使用族語的情況已經少見了",
            words=[awato],
        )

    def test_詞素_yaml(self):
        morpheme = Morpheme("to", "完成貌", Attachment.CLITIC)
        self.assertEqual(
            morpheme.to_yaml(),
            {"形": "to", "義": "完成貌", "構詞": "依附詞"},
        )

    def test_句_yaml_的_key(self):
        data = self.build_entry().to_yaml()
        self.assertEqual(data["編號"], "26")
        self.assertEqual(data["開始"], "00:02:09,410")
        self.assertEqual(data["結束"], "00:02:12,547")
        self.assertEqual(data["詞"][0]["切分"], "awa=to")
        self.assertEqual(data["詞"][0]["詞素"][1]["義"], "完成貌")

    def test_檔案_yaml_只收乾淨的組(self):
        good = self.build_entry()
        bad = Entry("27", "0", "1")
        bad.issues.append(Issue(IssueKind.GLUED_LINE, "a.txt", "27"))
        corpus = CorpusFile(
            path="阿美族/秀姑巒/a.txt",
            ethnic="阿美",
            variant="秀姑巒",
            entries=[good, bad],
        )
        data = corpus.to_yaml()
        self.assertEqual(len(data["句"]), 1)
        self.assertEqual(data["句"][0]["編號"], "26")
        self.assertEqual(data["族別"], "阿美")

    def test_warning_不擋匯出(self):
        entry = self.build_entry()
        entry.issues.append(
            Issue(IssueKind.MIXED_TIMECODE_FORMAT, "a.txt", "26")
        )
        self.assertTrue(entry.is_clean())


class TestNormLog(unittest.TestCase):

    def test_沒發生的項目也要列出來(self):
        log = NormLog()
        records = log.ordered()
        self.assertEqual(len(records), len(list(NormKind)))
        for record in records:
            self.assertEqual(record.count, 0)

    def test_最多留三組例(self):
        log = NormLog()
        for index in range(5):
            log.note(
                NormKind.EN_DASH, "PI–書" + str(index),
                "PI-書" + str(index), "a.txt", str(index),
            )
        record = log.records[NormKind.EN_DASH]
        self.assertEqual(record.count, 5)
        self.assertEqual(len(record.examples), 3)
        self.assertEqual(record.examples[0]["原句子"], "PI–書0")
        self.assertEqual(record.examples[0]["處理後"], "PI-書0")
        self.assertEqual(record.examples[0]["編號"], "0")
        self.assertIn("en-dash", record.kind.value)
        self.assertTrue(record.why)


if __name__ == "__main__":
    unittest.main()
