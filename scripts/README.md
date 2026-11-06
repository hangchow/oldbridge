# 生成脚本

本目录是生成整个名录（各级 md、README、排行）的脚本和中间数据。

## 运行

```
./scripts/run_all.sh
```

依次做：

1. `build/official.py` 提取政府原件中的桥梁，`build/unlisted.py` 整理老百晓集桥补录条目及人工核对结果。
2. 按名录原始数据生成各市结构化行数据：`build/gen.py`（杭州）、`huz/build.py`、`jx/build.py`、`sh/build.py`、`sz/build.py`、`jh/build.py`、`zj/build.py <城市>`（绍兴、宁波、衢州、台州、温州、丽水、舟山；江苏除苏州外的十二市）。生成后运行 `build/zjsx.py` 和 `build/shlib.py`，分别据浙江省市县级文保名录、上海市不可移动文物名录补正数据。
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

## 统一三级目录

全部25市采用 `市/区县/乡镇/乡镇古桥.md`。区县只保留统计、乡镇导航与分类索引；位置、公布文件、逐桥说明、来源及图片来源合并到乡镇页。

- `build/townpages.py` 的 `CITIES` 统一配置25市的数据目录，`cityreadme.py` 按此配置生成乡镇及区县页。杭州既有10个市辖区乡镇页沿用同格式生成，并保留三墩镇手工明细。
- `build/town_context.json` 保存区县共用说明、来源标签及乡镇补充，重复生成不会丢失。
- `build/town_assets.json` 保存图片原路径到乡镇路径的映射；`*/imgsrc.json` 中新来源键为 `区县/乡镇/文件名`，旧键用于追溯。
- `build/town_media_bindings.json` 按位置限定同乡镇同名桥的照片和老百晓链接；区县图片索引使用“乡镇、桥名、位置”三元键。
- `python3 scripts/tools/check_townpages.py` 检查全部25市：明细和位置、区县格式、市级及总统计、本地链接、媒体绑定和迁移图片。

## 旧格式输出已废弃

`huz/build.py`、`jx/build.py`、`sh/build.py`、`sz/build.py`、`jh/build.py`、`zj/build.py` 只负责解析和补充结构化行数据，旧的区县层明细、说明及图片表写出代码已移除。杭州 `build/gen.py` 也停用桐庐、淳安、建德的旧区县明细输出，保留数据解析及原有乡镇明细。`cityreadme.py` 的旧格式回退和合并分支已删除；未配置统一模板时直接报错，不再退回旧模式。

生成顺序为“解析原件及行数据 → 名录和桥梁细节补正 → 统一渲染 → 不换行处理 → 检查”。直接执行数据解析脚本不再产生旧格式Markdown。使用 `./scripts/run_all.sh` 执行完整流程；只重新渲染现有数据可执行：

```bash
python3 scripts/build/cityreadme.py
python3 scripts/build/nowrap.py
python3 scripts/tools/check_townpages.py
```

复查范围、同名桥修复及抽样结果见[结构调整复查记录](结构调整复查.md)。

## 杭州云端档案完整镜像

完整镜像默认保存在仓库同级的 `singdo_云端档案/`，通过 `SINGDO_MIRROR_ROOT` 可以覆盖根目录。`文保单位/`与`历史建筑/`分别对应 wenbao 和 libao 库；包括所有公开目录记录，不限于桥梁。

```bash
python3 scripts/tools/singdo_mirror.py
```

抓取器重新核对各分类目录，续传已有详情页和资源，生成 `离线网页/`、`索引.md`、`档案.json`、`资源清单.json`（含 SHA-256）和 `抓取报告.json`。只有目录和详情数量一致、资源无下载失败时，报告的 `complete` 才为 `true`。可用 `--library wenbao` 或 `--library libao` 单独抓取一个库。`--organize` 用于迁移旧布局及既有缓存，原有文件不重复下载。

`文保名录/杭州市/云端档案/` 仅保留杭州城市、区县和乡镇页面直接使用的档案及关联图片；其余档案保存到完整镜像的 `项目缓存/`，字节校验一致后才移出仓库。整理缓存：

```bash
python3 scripts/tools/singdo_mirror.py --prune-cache
```

`build/mkpage.py <记录号> ...` 从 `文保单位/`生成指定桥梁的项目档案；`tools/libao.py` 从 `历史建筑/`生成 `build/libao.json` 使用的桥梁档案，优先复用完整镜像里的图片。`tools/singdo.py`、`tools/singdo_photo.py`兼容旧命令，统一调用文保库完整抓取器。仓库内 `scripts/singdo/recs.json`、`libao/bridges.json`等小型结构化数据继续供名录生成使用，原始详情页不再重复放在 `scripts/singdo/`。

抓取结束后可运行 `python3 scripts/tools/singdo_mirror.py --verify` 核对两库的原始页、离线页及资源哈希；结果写入完整镜像根目录的 `核验报告.json`。图片原地址失效时会尝试另一官方图片域名，仍不可用的地址如实保留在抓取报告中。`--finish-after <PID>` 可等待已有抓取进程结束，自动重试未完成资源并核验，最后生成 `收尾报告.json`。
