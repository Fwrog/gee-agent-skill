# gee-agent-skill

![GEE agent harness social preview](assets/images/gee-agent-social-preview-dark.png)

<p align="center">
  <a href="./README.md">English</a> ·
  <a href="./README.zh-CN.md">简体中文</a> ·
  <a href="https://github.com/Fwrog/gee-agent-skill">GitHub</a>
</p>

`gee-agent-skill` 是一个面向 Google Earth Engine 的 agent-native 命令行工作流框架。它帮助 Codex 或其他代码智能体把自然语言地理空间任务转换为可审查的计划、带证据的数据集与算子选择、经过验证的 Earth Engine Python 脚本、安全的在线预检、显式确认后的导出任务、导出监控以及可复现 trace。

英文 [README.md](README.md) 是默认入口和优先维护版本。本中文版本面向中文读者，覆盖项目定位、安装、认证、demo、输出解读、常见问题和后续验证路线。

## 项目快照

架构流程：

```text
自然语言 -> 计划 -> RAG 证据 -> 渲染脚本 -> 验证 -> 在线预检 -> 导出 -> 监控 -> trace
```

无需 Earth Engine 凭证的最小检查：

```bash
gee-skill smoke-test --json
gee-skill plan from-text "Compute 16-day NDVI for Hong Kong in 2024 and export CSV." --json
```

完成本地 Earth Engine OAuth 后的最小 live-safe 工作流：

```bash
gee-skill plan from-text "Compute 16-day NDVI for Hong Kong in 2024 and export CSV." \
  --out outputs/plans/hk_2024_16day_ndvi.yaml \
  --json
gee-skill preflight outputs/plans/hk_2024_16day_ndvi.yaml --project "$EE_PROJECT" --json
gee-skill run outputs/plans/hk_2024_16day_ndvi.yaml --project "$EE_PROJECT" --confirm-live --json
gee-skill exports list --project "$EE_PROJECT" --json
```

当前 demo 是香港 2024 年 16 天 NDVI CSV 工作流。其他 recipe family 的状态请以 [Capability matrix](docs/capability_matrix.md) 为准。live 命令使用你自己的 Earth Engine project，并且需要显式传入 `--confirm-live`。

## 目录

- [项目快照](#项目快照)
- [这个项目做什么](#这个项目做什么)
- [Agent-native 接口](#agent-native-接口)
- [能力概览](#能力概览)
- [Recipe family](#recipe-family)
- [评估与研究定位](#评估与研究定位)
- [复杂任务验证 TODO](#复杂任务验证-todo)
- [快速开始](#快速开始)
- [安装](#安装)
  - [Windows PowerShell](#windows-powershell)
  - [macOS / Linux zsh 或 bash](#macos--linux-zsh-或-bash)
- [Earth Engine 认证](#earth-engine-认证)
- [无需 Earth Engine 凭证运行](#无需-earth-engine-凭证运行)
- [运行 demo](#运行-demo)
- [Demo 输出：v0.3 CSV](#demo-输出v03-csv)
- [Plan-first 工作流](#plan-first-工作流)
- [常见错误与修复](#常见错误与修复)
- [仓库结构](#仓库结构)
- [参考资料与数据源](#参考资料与数据源)
- [安全与凭证](#安全与凭证)

## 这个项目做什么

这个项目提供一条 CLI-first 的 Earth Engine 工作路径：

- 把自然语言请求转换为可审查的计划；
- 检索本地 Earth Engine 笔记、dataset card、operator rule 和 failure guidance；
- 渲染经过批准的 Jinja2 Earth Engine Python 模板；
- 在 live 使用前验证生成脚本；
- 在导出前运行 dry-run 和在线 preflight；
- 只有在显式 `--confirm-live` 后才提交 live export；
- 监控导出任务，并把 trace 写入 `outputs/runs/<run_id>/`。

| 阶段 | 作用 |
| --- | --- |
| 自然语言 | 用户或 agent 输入任务，例如 `Compute 16-day NDVI for Hong Kong in 2024 and export CSV.` |
| v0.3 plan | CLI 将 AOI、时间范围、指标、时间步长、输出类型、候选数据集、规则和模板选择解析为可编辑 YAML。 |
| Python 渲染 | `gee-skill render <plan.yaml> --json` 将已审查计划转换为 Earth Engine Python 脚本。 |
| 验证 | 静态和语义检查会在 live 前阻止未解析模板、缺失 import、不安全导出、错误 band 和缺失 reducer。 |
| 在线预检 | `gee-skill preflight <plan.yaml> --project <id> --json` 检查认证、project、AOI、影像数量、必要 band 和小型 sanity statistics。 |
| 导出 | 只有 `gee-skill run <plan.yaml> --project <id> --confirm-live --json` 会启动 Earth Engine export。 |
| 监控 | `gee-skill exports list/watch --project <id> --json` 返回 task id、description、state、timestamp 和 error。 |

README 中的 demo 使用香港 2024 年 16 天 NDVI CSV 工作流，作为完整链路的紧凑示例。

![Hong Kong 2024 16-day NDVI workflow](assets/images/hk-2024-16day-ndvi-workflow.png)

## Agent-native 接口

该 harness 面向 coding agent 和直接 CLI 用户。稳定命令面包括：

```text
auth / catalog / aoi / recipe / plan / render / validate / preflight / run / exports / trace / eval
```

核心命令返回确定性的 JSON，便于 agent 编排：

```bash
gee-skill info --json
gee-skill doctor --json
gee-skill aoi resolve "Compute NDVI for Hong Kong in January 2024." --json
gee-skill catalog search "Sentinel-2 NDVI" --json
gee-skill catalog evidence --category operator --json
gee-skill catalog evidence --category failure --json
gee-skill recipe list --json
gee-skill plan from-text "Compute 16-day NDVI for Hong Kong in 2024 and export CSV." --json
gee-skill render outputs/plans/hk_2024_16day_ndvi.yaml --json
gee-skill validate outputs/scripts/hk_2024_16day_ndvi_csv.py --json
gee-skill trace inspect <run_id> --json
gee-skill eval evals/benchmark_suite.yml --json
```

兼容命令 `ask`、`review-plan`、`preflight-plan`、`run-plan` 和 `monitor-exports` 仍然可用于现有示例工作流。

## 能力概览

| 能力 | 当前展示方式 |
| --- | --- |
| Agent 工程 | 结构化命令、显式 `gee-plan/v0.3` 状态、确定性 JSON、review-before-run、`--confirm-live` 和可追踪产物。 |
| RAG 与知识工程 | Dataset cards、operator notes、recipe cards、failure cards、retrieval traces 和 `evals/benchmark_suite.yml` 中的 coverage check。 |
| GEE / 遥感 | 数据集选择、band/QA 检查、scale/CRS 字段、server-side reducer/export 模式、`getInfo()` 安全规则、空 collection 防护和 export task lifecycle 监控。 |
| 可复现与评估 | Parse/plan tests、render/validate tests、mocked preflight failure、示例工作流、本地 benchmark runner 和脱敏 evidence bundle。 |
| 工程产品化 | 跨平台安装文档、CLI reference、CI、packaging metadata、changelog、security policy、roadmap、issue templates 和 wheel build check。 |

## Recipe family

当前 registry 不只覆盖香港 NDVI demo。能力状态请查看 [Capability matrix](docs/capability_matrix.md)。

| Recipe family | 当前角色 |
| --- | --- |
| Vegetation indices | NDVI/EVI planning、Sentinel-2 CSV render/validation，以及香港 demo。 |
| Water indices | NDWI/MNDWI planning、Sentinel-2 GeoTIFF render、generic preflight gate 和 band/export validation。 |
| Built-up indices | NDBI planning、Sentinel-2 CSV render、generic preflight gate 和 semantic band checks。 |
| Land surface temperature | Landsat LST CSV/Image render、generic preflight gate、validation 和 MODIS LST catalog evidence。 |
| Land cover summaries | Dynamic World / ESA WorldCover evidence、Dynamic World CSV render/validation，以及香港 land-cover-aware demo。 |
| Sentinel-1 flood/change | Before/after SAR planning、GeoTIFF render、generic preflight gate 和 validation rules。 |
| Zonal statistics | Table-export templates 和 reducer/export safety rules。 |
| Image/table export | 显式 selectors、region、scale、CRS、`maxPixels` 和 confirmed live gates。 |

不同 recipe family 的完成度不同。有些路径目前是 plan/render/validate，有些路径包含 live preflight 和 export evidence。具体以 [Capability matrix](docs/capability_matrix.md) 为准。

## 评估与研究定位

仓库包含一个紧凑的本地回归 benchmark：

```bash
gee-skill eval evals/benchmark_suite.yml --json
```

默认 offline benchmark 目前包含 22 个 case，覆盖 EVI、NDWI、NDBI、Landsat LST、Sentinel-1 flood mapping、Dynamic World land-cover summary、zonal statistics、GeoTIFF image export、模糊请求、未知 dataset id、不支持请求、RAG evidence coverage、mocked empty-collection preflight blocking，以及示例 render/validation case。

相关文档：

- [Benchmark protocol](docs/benchmark_protocol.md)
- [Research positioning](docs/research_positioning.md)
- [Paper outline](docs/paper.md)
- [Plan schema](schemas/gee-plan-v0.3.schema.json)

## 复杂任务验证 TODO

下一步是让更多复杂工作流走完当前 demo 使用的证据阶梯。这些是 TODO，不是已完成工作流声明。

| TODO | 更复杂任务 | 需要验证什么 | 当前状态 | 晋级门槛 |
| --- | --- | --- | --- | --- |
| [ ] | 香港 land-only / vegetation-only 16 天 NDVI | 水体/陆地 mask、land-cover strata、all-surface 与 vegetation-only 的解释边界 | 从 v0.3 demo 输出继续推进 | 增加 recipe-specific preflight、export selectors、CSV sanity checks 和 domain notes |
| [ ] | 区级 16 天 NDVI 时间序列 | Multi-zone `reduceRegions`、稳定 district id、更大 table export、null class 处理 | Planned | 通过 render/validate、mocked empty-zone/empty-collection tests，然后做一次确认后的 live export |
| [ ] | NDVI + EVI + NDWI 多指数光学工作流 | 共享 AOI/date parsing、多 band formula、一致 cloud masking、单一 trace | 单独 plan/render/validate 已存在 | 增加 composite recipe、全部 formula 的 semantic checks 和 benchmark cases |
| [ ] | Landsat LST 城市热环境 CSV / GeoTIFF | QA_PIXEL masking、ST_B10 scale/offset、thermal units、coarser scale warning | Render/validate only | 增加 LST-specific live preflight 和 temperature sanity ranges |
| [ ] | Sentinel-1 flood/change before-after GeoTIFF | SAR filtering、polarization/orbit review、before/after window checks、image export safety | Render/validate with generic preflight gate | 增加 Sentinel-1 preflight 和 event-specific threshold review |
| [ ] | Dynamic World land-cover summary | Probabilistic class aggregation、confidence thresholds、area/fraction outputs | Render/validate only | 增加 land-cover preflight 和 class-fraction sanity checks |
| [ ] | 用户 GeoJSON 的 generic zonal statistics | 用户 zones、reducer scale、selector stability、大表导出行为 | Plan-only / partial template coverage | 补齐 template context、validators、mocked geometry failure tests |
| [ ] | 成对 image + table export | 一个 reviewed plan 同时协调 GeoTIFF 和 CSV 输出 | Planned | 增加 multi-export trace、quota warnings 和 one-export-at-a-time safeguards |

## 快速开始

先克隆仓库，或进入已有本地 checkout。

```bash
git clone https://github.com/Fwrog/gee-agent-skill.git
cd gee-agent-skill
```

如果你已经有这个仓库，先进入项目根目录：

```bash
cd /path/to/gee-agent-skill
```

你应该能看到：

```text
pyproject.toml
README.md
SKILL.md
src/
assets/
docs/
```

如果没有 `pyproject.toml`，说明你不在正确目录。不要在 home directory 里直接运行 `pip install -e ".[earthengine]"`。

## 安装

从仓库根目录安装，而不是从 home directory 安装。推荐使用 `python -m pip ...`，这样可以确保使用的是当前激活的 Python 环境。

需要测试和构建工具的 contributor 可以安装 `".[dev,earthengine]"`。

### Windows PowerShell

```powershell
cd E:\projects\gee-agent-skill

python -m venv .venv
.\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
python -m pip install -e ".[earthengine]"

where python
where earthengine
python -c "import ee; print('ee import ok')"
earthengine -h
```

期望路径应指向 `.venv`，例如：

```text
E:\projects\gee-agent-skill\.venv\Scripts\python.exe
E:\projects\gee-agent-skill\.venv\Scripts\earthengine.exe
```

如果 Anaconda 处于 active 状态，终端里可能出现 `(base)`。关键不是 `(base)` 是否出现，而是 `python` 和 `earthengine` 是否解析到项目 `.venv`。

### macOS / Linux zsh 或 bash

```bash
cd /Users/yikai/Documents/GitHub/gee-agent-skill
# 或：
# cd ~/Documents/GitHub/gee-agent-skill

python3 -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install -e ".[earthengine]"

which python
which earthengine
python -c "import ee; print('ee import ok')"
earthengine -h
```

期望路径类似：

```text
.../gee-agent-skill/.venv/bin/python
.../gee-agent-skill/.venv/bin/earthengine
```

## Earth Engine 认证

Live Earth Engine 命令需要：

1. 已注册的 Earth Engine account；
2. 一个启用了 Earth Engine API access 的 Google Cloud Project；
3. 本地 OAuth authentication。

使用你自己的 account 和 project，并把 OAuth credential 保留在本地，不要提交 credential 文件。

Windows PowerShell：

```powershell
$env:EE_PROJECT="your-google-cloud-project-id"

earthengine authenticate --auth_mode=localhost
earthengine set_project $env:EE_PROJECT

python -c "import os, ee; ee.Initialize(project=os.environ['EE_PROJECT']); print(ee.Number(1).getInfo())"
```

macOS / Linux：

```bash
export EE_PROJECT="your-google-cloud-project-id"

earthengine authenticate --auth_mode=localhost
earthengine set_project "$EE_PROJECT"

python -c 'import os, ee; ee.Initialize(project=os.environ["EE_PROJECT"]); print(ee.Number(1).getInfo())'
```

如果最后一条命令打印 `1`，说明本地 OAuth 和 project 初始化可用。

macOS zsh 下，`import ee` 成功并不等于 OAuth 已经完成。如果 live initialization 报：

```text
EEException: Please authorize access to your Earth Engine account by running

earthengine authenticate
```

按顺序运行：

```bash
cd /path/to/gee-agent-skill
source .venv/bin/activate

which python
which earthengine
python -c "import ee; print('ee import ok')"

earthengine authenticate --auth_mode=localhost

export EE_PROJECT="your-google-cloud-project-id"
earthengine set_project "$EE_PROJECT"

python -c 'import os, ee; print("EE_PROJECT=", os.environ["EE_PROJECT"]); ee.Initialize(project=os.environ["EE_PROJECT"]); print(ee.Number(1).getInfo())'
```

成功输出应包含：

```text
.../gee-agent-skill/.venv/bin/python
.../gee-agent-skill/.venv/bin/earthengine
ee import ok
Successfully saved authorization token.
Successfully saved project id
EE_PROJECT= your-google-cloud-project-id
1
```

## 无需 Earth Engine 凭证运行

这些命令不会连接 Earth Engine：

```bash
gee-skill tools
gee-skill smoke-test --json
gee-skill catalog evidence --category operator --json
gee-skill catalog evidence --category failure --json
gee-skill observe "Compute 16-day NDVI for Hong Kong in 2024 and export CSV." --json
gee-skill plan from-text "Compute 16-day NDVI for Hong Kong in 2024 and export CSV." --out outputs/plans/hk_2024_16day_ndvi.yaml --json
gee-skill plan from-yaml outputs/plans/hk_2024_16day_ndvi.yaml --script-out outputs/scripts/hk_2024_16day_ndvi_csv.py --json
```

它们适合在登录 Google 前检查本地安装、parser behavior、plan creation、template rendering、validation 和 trace output。

## 运行 demo

当前 v0.3 editable-plan demo 任务是：

```text
Compute 16-day NDVI for Hong Kong in 2024 and export CSV.
```

该路径从自然语言开始，生成可编辑 `gee-plan/v0.3` YAML，渲染 Python 脚本，进行本地验证，执行 live preflight，然后在显式确认后提交一次 Earth Engine Drive CSV export。

不连接 Earth Engine 的 plan/render/validate：

```bash
gee-skill observe "Compute 16-day NDVI for Hong Kong in 2024 and export CSV." --json

gee-skill plan from-text "Compute 16-day NDVI for Hong Kong in 2024 and export CSV." \
  --out outputs/plans/hk_2024_16day_ndvi.yaml \
  --json

gee-skill plan review outputs/plans/hk_2024_16day_ndvi.yaml --json

gee-skill plan from-yaml outputs/plans/hk_2024_16day_ndvi.yaml \
  --script-out outputs/scripts/hk_2024_16day_ndvi_csv.py \
  --json

gee-skill validate outputs/scripts/hk_2024_16day_ndvi_csv.py --json
```

完成 OAuth 和 project setup 后运行 live preflight：

```bash
gee-skill preflight-plan outputs/plans/hk_2024_16day_ndvi.yaml \
  --project "$EE_PROJECT" \
  --json
```

Preflight 会连接 Earth Engine，但不会提交 export。通过的 v0.3 preflight 应报告 `expected_export_rows: 23`。

提交一次已审查的 export：

```bash
gee-skill run-plan outputs/plans/hk_2024_16day_ndvi.yaml \
  --project "$EE_PROJECT" \
  --confirm-live \
  --run-id hk-2024-16day-ndvi-v03-live-export-check \
  --json
```

监控任务：

```bash
gee-skill monitor-exports --project "$EE_PROJECT" --timeout 0 --json
```

预期 export metadata：

```text
description: hk_2024_16day_ndvi
Drive folder: gee_exports
file prefix: hk_2024_16day_ndvi
rows: 23
```

Windows PowerShell 版本使用反引号续行，并使用 `$env:EE_PROJECT`：

```powershell
gee-skill run-plan outputs\plans\hk_2024_16day_ndvi.yaml `
  --project $env:EE_PROJECT `
  --confirm-live `
  --run-id hk-2024-16day-ndvi-v03-live-export-check `
  --json
```

## Demo 输出：v0.3 CSV

这个 demo 展示 v0.3 香港 2024 年 16 天 NDVI 工作流导出的完整 CSV 形态。读者无需先运行 Earth Engine，也可以检查字段、时间步长、数值范围和影像数量诊断。

脱敏 evidence bundle 位于 [docs/evidence/v03_hk_2024_16day_ndvi](docs/evidence/v03_hk_2024_16day_ndvi/README.md)。

摘要：

```text
rows: 23
date coverage: 2024-01-01 to 2025-01-01
mean_ndvi range: -0.066 to 0.358
mean of period means: 0.109
minimum image_count_after_cloud_filter: 2
low-image-count periods: 5, 8
null mean_ndvi rows: 0
```

固定字段：

| CSV 字段 | 值 |
| --- | --- |
| `aoi_name` | `Hong Kong` |
| `year` | `2024` |
| `temporal_cadence_days` | `16` |
| `dataset_id` | `COPERNICUS/S2_SR_HARMONIZED` |
| `scale_m` | `10` |
| `crs` | `EPSG:4326` |
| `aoi_source` | `Home Affairs Department Hong Kong administrative district boundary GeoJSON` |
| `export_description` | `hk_2024_16day_ndvi` |

23 个 period-specific rows：

| Period | Start | End | Mean NDVI | Images before cloud filter | Images after cloud filter |
| ---: | --- | --- | ---: | ---: | ---: |
| 1 | 2024-01-01 | 2024-01-17 | 0.06137939316458223 | 34 | 34 |
| 2 | 2024-01-17 | 2024-02-02 | 0.021682486591865075 | 34 | 15 |
| 3 | 2024-02-02 | 2024-02-18 | -0.008787025242330054 | 30 | 16 |
| 4 | 2024-02-18 | 2024-03-05 | 0.018605165810100164 | 36 | 5 |
| 5 | 2024-03-05 | 2024-03-21 | 0.3583391891617482 | 30 | 2 |
| 6 | 2024-03-21 | 2024-04-06 | 0.09820961451352254 | 34 | 17 |
| 7 | 2024-04-06 | 2024-04-22 | 0.15836690001841133 | 30 | 10 |
| 8 | 2024-04-22 | 2024-05-08 | -0.0664235578099966 | 30 | 2 |
| 9 | 2024-05-08 | 2024-05-24 | 0.17030485358920375 | 39 | 4 |
| 10 | 2024-05-24 | 2024-06-09 | 0.25214183736529805 | 30 | 6 |
| 11 | 2024-06-09 | 2024-06-25 | 0.1821216212020888 | 34 | 6 |
| 12 | 2024-06-25 | 2024-07-11 | 0.10028333128041216 | 32 | 22 |
| 13 | 2024-07-11 | 2024-07-27 | 0.25195509572253405 | 30 | 19 |
| 14 | 2024-07-27 | 2024-08-12 | 0.08885762249481123 | 36 | 20 |
| 15 | 2024-08-12 | 2024-08-28 | 0.11989745428671472 | 30 | 12 |
| 16 | 2024-08-28 | 2024-09-13 | 0.15124974656199455 | 34 | 20 |
| 17 | 2024-09-13 | 2024-09-29 | 0.14508491985008928 | 30 | 21 |
| 18 | 2024-09-29 | 2024-10-15 | 0.1376690685869499 | 30 | 28 |
| 19 | 2024-10-15 | 2024-10-31 | 0.100211664616846 | 35 | 32 |
| 20 | 2024-10-31 | 2024-11-16 | 0.005387772561937038 | 33 | 16 |
| 21 | 2024-11-16 | 2024-12-02 | 0.014769201455417689 | 37 | 14 |
| 22 | 2024-12-02 | 2024-12-18 | 0.07812940745081513 | 40 | 26 |
| 23 | 2024-12-18 | 2025-01-01 | 0.07055101818908434 | 34 | 24 |

如何理解这个 demo：

- 这是整个香港 AOI 的 all-surface mean NDVI 示例。
- 香港行政边界包含水域和高密度建成区，因此 period mean 可能接近 0，甚至短期为负。
- Period 5 和 8 在云过滤后只有 2 景影像，适合被视作需要重点检查的 confidence rows。
- 该示例展示的是 v0.3 agent loop：自然语言 -> `gee-plan/v0.3` YAML -> 渲染 `.py` -> validation -> live preflight -> Earth Engine export task -> Drive CSV。

后续更细化的示例可以在同一 adapter pattern 上扩展：

- 加 water mask 的 land-only NDVI；
- 使用 Dynamic World 或 WorldCover mask 的 vegetation-only NDVI；
- 区级 16 天 NDVI，而不是整个香港聚合；
- 每个 period 的 image-count 和 cloud-confidence diagnostics；
- chart-ready CSV 加快速 visual QA report。

## Plan-first 工作流

默认工作流把 intent interpretation、review、preflight 和 live execution 分开：

1. Plan：`gee-skill plan from-text "<request>" --out <plan.yaml> --json` 写出可编辑 YAML，不连接 Earth Engine。
2. Review：`gee-skill plan review <plan.yaml> --json` 查看日期、AOI、数据集、mask、reducer、输出和限制。
3. Render：`gee-skill render <plan.yaml> --script-out <script.py> --json` 生成 Earth Engine Python 脚本。
4. Validate：`gee-skill validate <script.py> --json` 阻止不安全或不一致脚本。
5. Preflight：`gee-skill preflight <plan.yaml> --project <id> --json` 在导出前检查 live data availability。
6. Run：`gee-skill run <plan.yaml> --project <id> --confirm-live --json` 只在 review 和确认后提交 export。
7. Monitor：`gee-skill exports list --project <id> --json` 和 `gee-skill exports watch --project <id> --task-id <id> --json` 查看 task state。
8. Trace：`gee-skill trace inspect <run_id> --json` 查看可复现产物。

## 常见错误与修复

### `file:///Users/<name> does not appear to be a Python project`

原因：你在 home directory 里运行了 `pip install -e ".[earthengine]"`，而不是在仓库根目录运行。

修复：

```bash
cd /path/to/gee-agent-skill
ls pyproject.toml
python -m pip install -e ".[earthengine]"
```

### `zsh: permission denied: /path/to/gee-agent-skill`

原因：你把目录路径当成命令输入了。

修复：

```bash
cd /path/to/gee-agent-skill
```

### `zsh: command not found: earthengine`

原因：active environment 没安装 `earthengine-api`，或者 `.venv` 没有激活。

修复：

```bash
source .venv/bin/activate
python -m pip install -e ".[earthengine]"
which earthengine
```

### PowerShell 和 zsh 的环境变量写法不同

Windows：

```powershell
$env:EE_PROJECT="your-project-id"
```

macOS/Linux：

```bash
export EE_PROJECT="your-project-id"
```

## 仓库结构

```text
SKILL.md                         面向模型的 skill 入口
assets/templates/                Jinja2 Earth Engine Python workflow templates
docs/                            入门、概念、live workflow、troubleshooting 文档
examples/                        Task YAML examples
references/knowledge_base/       Curated docs、dataset cards、operator chains、failure cases
references/boundaries/           Curated Hong Kong district boundary GeoJSON
references/corpus/               Pattern-only GitHub corpus inventories and review notes
references/index/                Generated local retrieval index
src/geeskill/                    CLI、registry、retrieval、validation、runtime、trace code
evals/                           Benchmark suite and contexts
tests/                           Offline regression tests
outputs/runs/                    Generated run traces
```

更多文档：

- [How to start](docs/how_to_start.md)
- [CLI reference](docs/cli_reference.md)
- [Recipe registry](docs/recipes.md)
- [Capability matrix](docs/capability_matrix.md)
- [Benchmark protocol](docs/benchmark_protocol.md)
- [Research positioning](docs/research_positioning.md)
- [Paper outline](docs/paper.md)
- [Roadmap](ROADMAP.md)
- [Troubleshooting](docs/troubleshooting.md)
- [Harness trace model](docs/harness.md)
- [v0.3 Hong Kong 2024 16-day NDVI workflow](docs/v03_hk_2024_16day_ndvi.md)
- [v0.3 Hong Kong 2024 16-day NDVI case study](docs/case_studies/hk_ndvi_v03.md)
- [v0.3 sanitized evidence bundle](docs/evidence/v03_hk_2024_16day_ndvi/README.md)
- [Extending workflows](docs/extending.md)

## 参考资料与数据源

- [Earth Engine Python API](https://developers.google.com/earth-engine/guides/python_install)
- [Earth Engine authentication](https://developers.google.com/earth-engine/guides/auth)
- [Sentinel-2 SR Harmonized](https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S2_SR_HARMONIZED)
- [Dynamic World V1](https://developers.google.com/earth-engine/datasets/catalog/GOOGLE_DYNAMICWORLD_V1)
- [ESA WorldCover](https://developers.google.com/earth-engine/datasets/catalog/ESA_WorldCover_v200)
- [geemap](https://geemap.org/)
- [giswqs GitHub](https://github.com/giswqs)
- [GEE Community GitHub](https://github.com/gee-community)

本地知识库位于 `references/knowledge_base/`。`references/corpus/` 中列出的 GitHub 仓库用于模式发现，不用于整段复制第三方代码。

## 安全与凭证

Live Earth Engine 运行需要你自己的 Earth Engine account、Google Cloud Project 和本地 OAuth authentication。请把认证信息保留在本地，不要进入版本控制。

不要提交 service account JSON、OAuth token、本地 credential 文件、refresh token、credential path、private key 或 client secret。

Live 命令需要 Google Cloud Project 和显式确认：

```bash
gee-skill run-plan outputs/runs/<run_id>/task_plan.yaml \
  --project "$EE_PROJECT" \
  --confirm-live \
  --json
```

Dry-run 和 plan 命令可以在没有凭证的情况下运行。
