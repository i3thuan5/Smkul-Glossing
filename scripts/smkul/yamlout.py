"""把通過驗證的語料匯出成單一 YAML(華語 key)。

結構是 檔案 → 句 → 詞 → 詞素 四層,對照 corpus-export spec。
一個「詞」壓成一行(flow style),對方一眼看得出一句有幾個詞。
"""

import os

import yaml

OUT_DIR = os.path.join("kithann", "out")
FILENAME = "corpus.yaml"
# 壓成一行的那幾行不要被折斷,寬度放到實務上不會踩到的值。
WIDTH = 1 << 30


class FlowMap(dict):
    """要壓成一行的 mapping。內容跟 dict 一樣,只是換個 dump 樣式。"""


class Dumper(yaml.SafeDumper):
    """SafeDumper 加一條規則:FlowMap 走 flow style。"""


def represent_flow_map(dumper, data):
    """FlowMap 印成 `{key: value, ...}`。"""
    return dumper.represent_mapping(
        "tag:yaml.org,2002:map", data, flow_style=True,
    )


Dumper.add_representer(FlowMap, represent_flow_map)


def flow_words(data):
    """把每個「詞」換成 FlowMap,匯出時整個詞縮成一行。"""
    for item in data["檔案"]:
        for sentence in item["句"]:
            words = []
            for word in sentence["詞"]:
                words.append(FlowMap(word))
            sentence["詞"] = words
    return data


def build(corpus_files):
    """把每個 CorpusFile 轉成 YAML 用的結構。只收乾淨的組。"""
    out = []
    for corpus in corpus_files:
        if not corpus.clean_entries():
            continue
        out.append(corpus.to_yaml())
    return flow_words({"檔案": out})


def dump(data):
    """轉成 YAML 字串。華語 key 不轉義,才看得懂。"""
    return yaml.dump(
        data, Dumper=Dumper, allow_unicode=True, sort_keys=False,
        default_flow_style=False, width=WIDTH,
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
