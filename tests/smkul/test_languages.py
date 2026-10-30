"""測試 languages.py:語言別代號查表，對照 corpus-export「語言別代號」。"""

import os
import unittest

from scripts.smkul import languages

DATA = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__)))),
    "scripts", "smkul", "data",
)


class TestCode(unittest.TestCase):

    def test_語言別只寫地區(self):
        self.assertEqual(languages.code("阿美", "秀姑巒"), "ami-x-skl")

    def test_語言別本身含族名(self):
        self.assertEqual(languages.code("排灣", "中排灣"), "pwn-x-pnvn")

    def test_族別與語言別相同(self):
        self.assertEqual(languages.code("太魯閣", "太魯閣"), "trv-x-truku")

    def test_台臺異體字(self):
        self.assertEqual(languages.code("魯凱", "霧台"), "dru-x-ngdr")

    def test_查不到代號回空字串(self):
        self.assertEqual(languages.code("阿美", "不存在"), "")


class TestCsv(unittest.TestCase):

    def test_csv_在版控內(self):
        path = os.path.abspath(languages.CSV_PATH)
        self.assertEqual(os.path.dirname(path), DATA)
        self.assertTrue(os.path.exists(path))


if __name__ == "__main__":
    unittest.main()
