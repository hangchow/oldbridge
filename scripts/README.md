# 生成脚本

本目录是生成整个名录（各级 md、README、排行）的脚本和中间数据。

## 运行

```
./scripts/run_all.sh
```

依次做：

1. 按名录原始数据生成各市行数据和 md：`build/gen.py`（杭州）、`huz/build.py`、`jx/build.py`、`sh/build.py`、`sz/build.py`、`jh/build.py`、`zj/build.py <城市>`（绍兴、宁波、衢州、台州、温州、丽水、舟山；江苏的无锡、南京、常州、镇江）。
2. `build/cqlink.py`：匹配“老百晓集桥”页面（桥名后的“?”链接）。
3. `build/cqholes.py`：从老百晓集桥页面、本地云端档案补结构、孔数、长度。
4. `build/erafill.py`：补具体年代。
5. 再生成一次各市数据，然后 `build/cityreadme.py`（市级、总 README、排行）和 `build/nowrap.py`（表格列不换行）。

## 主要数据文件

- `build/curated.py`：杭州手工整理的条目。
- `build/unlisted.py`、`build/review_decisions.json`：不在文保名录、据老百晓集桥收录的古桥，以及逐座核对的结果（删除原因或改正的年代）。
- `build/cq_manual2.json`、`build/cqlink.py` 里的 `MANUAL`：人工确认的老百晓集桥同桥链接。
- `build/inscr.json`：桥身题刻纪年（刻字排行）。
- `*/struct.json`、`*/len.json`：各市手工或匹配得到的结构、长度。
- `zj/cities.json`：浙江七市、江苏四市的区县、统计表工作表号（江苏没有，为 null）、省份、乡镇更正。
- `zj/cqidx.py`、`zj/cqidx16.py`：抓老百晓集桥浙江（ql15）、江苏（ql16）各市目录；`zj/compare.py <城市>`：对比出不在名录的古桥（结果合并进 `build/compare_raw.json`）。
- `build/review_decisions.json` 里的值也可以是对象：`era`、`name`、`town`，以及页面写明的文保等级 `lv`（shi/xian）和 `lvnote`。
- `x/xl/`：浙江省文物局《全省文物保护点》统计表（原件在 `文保名录/浙江省/`）解压后的工作表。

## 说明

- 老百晓集桥页面缓存（`cqv/`、`cq2/*.htm`）没有提交，缺失时脚本会自动重新抓取，第一次运行较慢。
- 脚本里仓库路径写的是 `/Users/sean/workspace/oldbridge`，换机器运行时需要改成实际路径。
