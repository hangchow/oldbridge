# 生成脚本

本目录是生成整个名录（各级 md、README、排行）的脚本和中间数据。

## 运行

```
./scripts/run_all.sh
```

依次做：

1. `build/official.py` 提取政府原件中的桥梁，`build/unlisted.py` 整理老百晓集桥补录条目及人工核对结果。
2. 按名录原始数据生成各市行数据和 md：`build/gen.py`（杭州）、`huz/build.py`、`jx/build.py`、`sh/build.py`、`sz/build.py`、`jh/build.py`、`zj/build.py <城市>`（绍兴、宁波、衢州、台州、温州、丽水、舟山；江苏除苏州外的十二市）。生成后运行 `build/zjsx.py` 和 `build/shlib.py`，分别据浙江省市县级文保名录、上海市不可移动文物名录补正数据。
3. `build/cqlink.py`：匹配“老百晓集桥”页面（桥名后的“?”链接）。
4. `build/cqholes.py`：从老百晓集桥页面、本地云端档案补结构、孔数、长度。
5. `build/erafill.py`：补具体年代。
6. 再生成一次各市数据，然后 `build/cityreadme.py`（乡镇明细、区县、市级、总 README、排行）和 `build/nowrap.py`（表格列不换行）。

## 主要数据文件

- `build/official.py`、`build/official.json`：提取政府原件并保存桥梁条目，供各市生成程序优先采用。
- `build/zjsx.py`、`build/shlib.py`：分别按浙江省市县级文保名录、上海市不可移动文物名录补正等级、公布文号及遗漏条目。
- `build/curated.py`：杭州手工整理的条目。
- `build/unlisted.py`、`build/review_decisions.json`：不在文保名录、据老百晓集桥收录的古桥，以及逐座核对的结果（删除原因或改正的年代）。
- `build/cq_manual2.json`、`build/cqlink.py` 里的 `MANUAL`：人工确认的老百晓集桥同桥链接。
- `build/inscr.json`：桥身题刻纪年（刻字排行）。
- `*/struct.json`、`*/len.json`：各市手工或匹配得到的结构、长度。
- `zj/cities.json`：浙江七市、江苏除苏州外的十二市的区县、统计表工作表号（江苏没有，为 null）、省份、乡镇更正。
- `zj/cqidx.py`、`zj/cqidx16.py`：抓老百晓集桥浙江（ql15）、江苏（ql16）各市目录；`zj/compare.py <城市>`：对比出不在名录的古桥（结果合并进 `build/compare_raw.json`）。
- `build/review_decisions.json` 里的值也可以是对象：`era`、`name`、`town`，以及页面写明的文保等级 `lv`（shi/xian）和 `lvnote`。
- `x/xl/`：浙江省文物局《全省文物保护点》统计表（原件在 `文保名录/浙江省/`）解压后的工作表。

## 说明

- 老百晓集桥页面缓存（`cqv/`、`cq2/*.htm`）没有提交，缺失时脚本会自动重新抓取，第一次运行较慢。
- 脚本里仓库路径写的是 `/Users/sean/workspace/oldbridge`，换机器运行时需要改成实际路径。

## 新增名录的默认处理

新增政府文保清单时，默认提取独立原件并保存来源和页码，录入可重新生成的结构化数据，核对已有条目、按桥梁独立公布的最高等级去重，更新区县、市级和总汇总 Markdown；同时按桥名、乡镇和地址匹配老百晓集桥页面，核对同桥后抓取照片（每桥最多三张，去重并记录来源）。找不到可靠匹配或照片时，保留待补说明，不使用其他同名桥的资料。

- `build/jxprimary.py`：嘉兴第五批政府原件补正及北溪桥撤销记录冲突，在嘉兴生成与省级汇总补全后应用，保留官方年代、地址和来源。

- `tools/download_jxwwbh.py`：完整归档嘉兴市文物保护网栏目（参数 `117` 为市级文物保护单位，`120` 为市级文物保护点，默认 `120`），含分页、原始网页、离线正文、原图及SHA-256清单；兼容旧HTTP图片链接，支持续传。
- `build/jxwwbh.py`：根据归档目录的 `bridge_review.json` 应用已确认的同桥对应，补齐缺失字段；疑似同桥单独保留待核。

- 海宁2022汇总表的已采纳更新保存在原件同名JSON的 `adopted_updates`，由 `build/jxprimary.py` 重复应用：庆成桥未评级，九曲桥保留原市保，太平桥地址及南石桥年代按2022表；不从所在寺庙、景观、遗址自动继承等级。`未评级`在汇总中归入“尚未定级（已核实）”。

## 嘉兴、湖州、绍兴的乡镇目录

三市采用与杭州相同的三级结构：`市/区县/乡镇/乡镇古桥.md`，照片与乡镇明细放在一起。区县页保留统计和分类索引，乡镇名称链接到明细页；明细含位置、文保等级、公布文件、说明和来源。原始乡镇字段不改，缺失乡镇放入 `乡镇待核/`。

- `build/townpages.py`：由 `build/cityreadme.py` 在汇总前调用，按最终 `rows.json` 生成乡镇明细，迁移区县层图片并修正链接；生成器可重复运行。旧的城市生成脚本仍产生区县层中间页，最终目录以 `cityreadme.py` 输出为准。
- `build/town_assets.json`：原图片路径到乡镇目录路径的映射，用于迁移校验、旧链接重定向；图片内容保持不变。
- `jx/imgsrc.json`、`huz/imgsrc.json`、`sx/imgsrc.json` 增加 `区县/乡镇/文件名` 来源键，旧键兼容原下载脚本。
- `python3 scripts/tools/check_townpages.py`：检查三市及杭州三县市明细与结构化数据一致、位置展示、本地链接及图片迁移完整性。

- `tools/download_jxwwbh_map.py`：归档嘉兴不可移动文物地图的基础接口、目录树、地区查询、全部详情响应和有效图片；保留站点拦截状态，不把拦截页当作详情。`build/jxmap.py` 根据已核对的 `bridge_review.json` 应用桥梁新增、缺项补充与坐标，不自动覆盖既有等级；`zjsx.py` 防止新地图中的异镇同名桥吞掉原省级汇总条目。
- 嘉兴、湖州、绍兴全部区县页采用杭州的简洁索引样式：表格后不再附说明、来源和图片来源；逐桥信息在乡镇明细中，共用说明及来源由 `build/town_context.json` 合并到乡镇页。城市范围由 `townpages.py` 的 `CLEAN_CITIES` 控制，杭州三县市由 `CLEAN_DISTRICTS` 控制。

## 杭州统一三级目录

杭州13个区县均使用 `杭州市/区县/乡镇/乡镇古桥.md`。区县页统一为拱墅区样式：桥梁总数、按级别统计、乡镇数量导航、按级别列出，不附逐桥说明或来源。位置、公布文件、说明、资料来源和图片来源保留在乡镇明细页。

桐庐、淳安、建德的最终乡镇页由 `build/townpages.py` 根据 `build/all_rows.json` 生成，`cityreadme.py` 汇总前调用；其他10个市辖区仍由原杭州生成流程生成乡镇明细。杭州图片来源索引使用 `build/imgsrc.json`，迁移后的新键为 `区县/乡镇/图片名`，旧键仍兼容区县层中间页。`build/gen.py` 生成的三县市区县明细为中间输出，最终结构以 `cityreadme.py` 为准。

三县市共53个乡镇页、175座桥、73张迁移原图；杭州总计仍为773座。桐庐江南镇和富春江镇各有保安桥，原环溪双桥照片只绑定江南镇。检查命令仍为 `python3 scripts/tools/check_townpages.py`。

- `build/town_context.json` 保存区县共用说明、来源标签及特定乡镇补充，生成时合并到乡镇页；`build/town_media_bindings.json` 按村址限定同乡镇同名桥的图片和老百晓链接。区县图片索引使用“乡镇、桥名、位置”三元键，避免同名桥互相覆盖。
- 本轮[结构调整复查记录](结构调整复查.md)列出迁移范围、检查结果及同名桥误挂图修复。
