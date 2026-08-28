"""測試的共用路徑。

資料夾照 scripts/ 排:tests/smkul/ 對 scripts/smkul/，
tests/ 這一層放跨模組的整合測試。測試資料一律放 tests/data，
路徑寫在這裡，各個測試檔不必各自算一次。
"""

import os

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
ODS = os.path.join(DATA, "標記清單範例.ods")
