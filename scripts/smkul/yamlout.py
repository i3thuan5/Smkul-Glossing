"""把通過驗證的語料匯出成單一 YAML(華語 key)。

結構是 檔案 → 句 → 詞 → 詞素 四層,對照 corpus-export spec。
"""

import os

import yaml

OUT_DIR = os.path.join("kithann", "out")
FILENAME = "corpus.yaml"


def build(corpus_files):
    """把每個 CorpusFile 轉成 YAML 用的結構。只收乾淨的組。"""
    out = []
    for corpus in corpus_files:
        if not corpus.clean_entries():
            continue
        out.append(corpus.to_yaml())
    return {"檔案": out}


def dump(data):
    """轉成 YAML 字串。華語 key 不轉義,才看得懂。"""
    return yaml.safe_dump(
        data, allow_unicode=True, sort_keys=False, default_flow_style=False,
    )


def write(corpus_files, name=FILENAME, out_dir=OUT_DIR):
    """寫出單一 YAML,回傳 (路徑, 檔案數, 句數)。"""
    data = build(corpus_files)
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, name)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(dump(data))
    sentences = 0
    for item in data["檔案"]:
        sentences += len(item["句"])
    return path, len(data["檔案"]), sentences
