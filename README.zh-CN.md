# gee-agent-skill

![GEE agent closed-loop workflow](assets/images/gee-agent-closed-loop-hero.png)

<p align="center">
  <a href="./README.md">English</a> ·
  <a href="./README.zh-CN.md">简体中文</a> ·
  <a href="https://github.com/Fwrog/gee-agent-skill">GitHub</a>
</p>

<p align="center">
  <a href="https://github.com/Fwrog/gee-agent-skill/actions"><img alt="CI" src="https://img.shields.io/badge/CI-pytest%20%2B%20smoke-2ea44f"></a>
  <a href="./docs/capability_matrix.md"><img alt="Capability" src="https://img.shields.io/badge/capability-matrix-2563eb"></a>
  <a href="./docs/tool_permissions.md"><img alt="Live safe" src="https://img.shields.io/badge/live--export-confirm--live-f59e0b"></a>
  <a href="./LICENSE"><img alt="License" src="https://img.shields.io/badge/license-see%20LICENSE-64748b"></a>
</p>

`gee-agent-skill` 是面向 Google Earth Engine 的 agent-native 命令行工作流框架。它把自然语言地理空间任务转换成可审查 plan、带来源的数据集/算子选择、经过验证的 Earth Engine Python 脚本、安全 preflight、显式确认后的 export、任务监控和可复现 trace。

## 项目快照

```text
自然语言 -> plan -> RAG 证据 -> 渲染脚本 -> 验证 -> preflight -> export -> monitor -> trace -> 通用知识沉淀
```

这是公开 GEE harness，不是私有研究仓库。私有研究问题、未发表结果、私有 asset id、论文草稿和专有输出不进入公开 repo。只有可泛化的 dataset card、rule card、failure case 和 workflow constraint 才适合沉淀到这里。

| 层级 | 公开作用 |
| --- | --- |
| 🧭 Plan-first CLI | 把自然语言 GEE 任务变成可审查的 `gee-plan/v0.3` 合约。 |
| 📚 RAG evidence | 在渲染代码前检索 dataset、operator、recipe、rule、failure cards。 |
| ✅ Validation gates | 阻止不安全导出、缺失 band、未解析模板、占位 AOI 和过度声明。 |
| 📤 Live execution | 使用官方 Earth Engine Python API，并要求 `--project` 和 `--confirm-live`。 |
| 🧠 Learning loop | 经过隐私审查后，只把通用、带来源的经验沉淀到公开 repo。 |

## 5 分钟快速开始

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[earthengine]"

gee-skill smoke-test --json
gee-skill ask "Compute January 2024 mean NDVI for Hong Kong and export CSV." --dry-run --json
```

Live export 永远是用户显式选择的步骤：

```bash
export EE_PROJECT="your-google-cloud-project-id"
earthengine authenticate --auth_mode=localhost
gee-skill preflight-plan outputs/runs/<run_id>/task_plan.yaml --project "$EE_PROJECT" --json
gee-skill run-plan outputs/runs/<run_id>/task_plan.yaml --project "$EE_PROJECT" --confirm-live --json
```

## 🧪 Public Demo Gallery

公开 demo 是 harness 的 golden regression examples，不是科学植被产品。

| Demo | 状态 | 证明什么 | 详情 |
| --- | --- | --- | --- |
| v0.1 minimal NDVI CSV | Golden | 最小 Sentinel-2 NDVI 请求可以走完 plan、validation、preflight、export trace。 | [案例](docs/case_studies/hk_ndvi_v01.md) |
| v0.2 land-cover-aware NDVI CSV | Golden | 可以加入 Dynamic World 解释分层，并保留限制说明和 trace。 | [案例](docs/case_studies/hk_ndvi_landcover_v02.md) |
| v0.3 HLS/MODIS NDVI product intercomparison | Golden | 尺度感知产品一致性：HLS NDVI -> MODIS grid -> Drive export -> metrics/figures/report/readiness audit。 | [验证说明](docs/validation/hk_ndvi_product_intercomparison_v03.md) |

更复杂的个人学术 demo 不在公开 README 展示。公开支持范围看 [Capability matrix](docs/capability_matrix.md)，通用 NDVI 合理性验证看 [remote sensing validation ladder](docs/remote_sensing_validation.md)。

## Validation v0.3: Hong Kong NDVI Product Intercomparison

这个 v0.3 demo 用 30 m HLS NDVI 和官方 MODIS MOD13Q1 NDVI 做产品级互检。关键不是宣称“地面真值精度”，而是验证 skill 能否生成一个遥感上合理、可复现、尺度匹配的流程：HLS 先按 MODIS 16-day window 合成，再聚合到 MODIS 250 m grid，最后与 MODIS NDVI 做定量比较。

| 组件 | 选择 |
| --- | --- |
| 高分辨率来源 | `NASA/HLS/HLSL30/v002` 和 `NASA/HLS/HLSS30/v002` |
| 官方对比产品 | `MODIS/061/MOD13Q1`，`NDVI * 0.0001` |
| 分层 | `ESA/WorldCover/v200` purity groups |
| 时间逻辑 | 使用 MODIS 16-day windows 驱动 HLS 时间窗口 |
| 尺度逻辑 | HLS 30 m median NDVI 先聚合到 MODIS projection 再比较 |
| Drive handoff | `GEE_SKILL_V03_HK_NDVI_VALIDATION` |

流程：

```text
发现数据集 -> 生成 GEE workflow -> HLS QA/NDVI -> MODIS QA/scale -> HLS 聚合到 MODIS grid -> 导出到 Drive -> connector 回读 -> 指标和图表
```

当前证据状态：公开 v0.3 demo 已有 `Golden` validation evidence。2024 full-year CSV exports 已通过 Google Drive 回读，年度 GeoTIFF raster 通过整图或 deterministic 2x2 tiled fallback 完成验证，本地 QA 通过，readiness audit 返回 `golden_ready`。

| 指标 | 当前 full-year CSV 结果 |
| --- | --- |
| Matched pixel count | 5,575 个全年匹配样本 |
| Bias / MAE / RMSE | -0.025 / 0.073 / 0.111 NDVI |
| Pearson r / Spearman rho | 0.870 / 0.859 |
| Land-cover finding | 植被主导像元 RMSE 最低 (0.082)；海岸/水体邻近像元 RMSE 最高 (0.193)。 |
| Raster QA | HLS 30 m、MODIS 250 m、HLS aggregated 250 m tiles、difference tiles 和 valid-count tiles 均通过本地 sanity checks。 |

以下图表来自 Drive 下载的 CSV：

![Hong Kong v0.3 regional NDVI time series](outputs/hk_ndvi_product_validation_v03/figures/hk_v03_regional_ndvi_timeseries.png)

![Hong Kong v0.3 HLS MODIS hexbin](outputs/hk_ndvi_product_validation_v03/figures/hk_v03_hls_vs_modis_hexbin.png)

![Hong Kong v0.3 land-cover metrics](outputs/hk_ndvi_product_validation_v03/figures/hk_v03_landcover_metrics.png)

项目状态和后续事项见 [Roadmap and TODO](docs/roadmap.md)。更短的新贡献者任务入口见 [TODO.md](TODO.md)。

复现命令：

```bash
python scripts/hk_ndvi_v03_export.py --mode smoke --year 2024 --drive-folder GEE_SKILL_V03_HK_NDVI_VALIDATION --project "$EE_PROJECT" --confirm-live --json
python scripts/hk_ndvi_v03_export.py --mode full --year 2024 --drive-folder GEE_SKILL_V03_HK_NDVI_VALIDATION --project "$EE_PROJECT" --confirm-live --json
python scripts/hk_ndvi_v03_monitor_tasks.py --manifest outputs/hk_ndvi_product_validation_v03/manifest.json --out outputs/hk_ndvi_product_validation_v03 --json
python scripts/hk_ndvi_v03_analyze_drive_exports.py --raw-dir outputs/hk_ndvi_product_validation_v03/raw_drive --out outputs/hk_ndvi_product_validation_v03 --json
python scripts/hk_ndvi_v03_make_figures.py --input outputs/hk_ndvi_product_validation_v03/analysis --out outputs/hk_ndvi_product_validation_v03/figures --json
python scripts/hk_ndvi_v03_readiness_audit.py --out outputs/hk_ndvi_product_validation_v03 --json
```

限制：这是 product-level consistency 和 workflow reliability 验证，不是 ground-truth accuracy。海岸混合像元、密集城市像元、云/霾、地形、BRDF 差异，以及 2021 静态土地覆盖分层都会造成真实产品差异。

## 🔐 Tool Permissions

![GEE agent toolchain](assets/images/gee-agent-toolchain.png)

| 工具 | 最适合做什么 | 边界 |
| --- | --- | --- |
| Earth Engine Python API / `gee-skill` | GEE plan、render、validate、preflight、export、monitor、trace | 主执行路径；live export 必须显式 `--confirm-live`。 |
| Browser | 官方文档、dataset catalog 核验、README 视觉 QA | API/CLI 可用时，不通过浏览器提交 export。 |
| Google Drive | 结果 handoff、zip/report/CSV/figure 回读 | 只返回 connector 实际返回或回读到的链接。 |
| Data Analytics | 已有表格/图表/报告的数据质量和展示验证 | 不能替代遥感领域审查。 |
| Computer Use | 没有 API/CLI/plugin 路径时的本地 GUI 兜底 | 最后手段，尤其谨慎处理凭证和 live task。 |
| imagegen | README 和文档视觉资产 | 只是沟通素材，不是科学证据。 |

完整说明见 [Tool permissions](docs/tool_permissions.md)。

## 🧠 Learning Loop

![GEE agent knowledge loop](assets/images/gee-agent-knowledge-loop.png)

| 任务中的具体观察 | 公开通用沉淀 |
| --- | --- |
| 某个数据集路径、band 或年份范围变化。 | 带 source URL、`last_checked`、适用范围和限制的 dataset card。 |
| live export 因 band dtype 混合失败。 | failure case 和规则：image export 前统一 band dtype。 |
| 公开边界替代源与权威边界不一致。 | claim-boundary 规则：不能宣称权威本地结论。 |
| 私有研究流程暴露重复摩擦。 | 经过隐私审查和来源核验后，抽象成通用 workflow card。 |

更多说明见 [Closed loop](docs/closed_loop.md) 和 [adaptive browser-backed knowledge loop](references/knowledge_base/workflows/adaptive-browser-backed-knowledge-loop.md)。

## 🗺️ Roadmap And TODO

公开 roadmap 维护在 [docs/roadmap.md](docs/roadmap.md)，按 `Done`、`Now`、`Next`、`Later` 分层组织，并统一使用 `Golden`、`Partial`、`Implementation-ready`、`Planned`、`Blocked` 这些状态标签。

它用来说明一个 demo 还差什么才能成为 public golden evidence。当前重点是把已完成的 v0.3 HLS/MODIS 验证流程泛化成 v0.4 skill generation 能力，保持 release checks 可复现，并且只把经过隐私审查、带来源的通用经验沉淀到知识库。

如果要按 GitHub 项目方式推进，可以使用 [TODO.md](TODO.md)、`.github/ISSUE_TEMPLATE/` 里的模板，以及 `.github/labels.yml` 中建议的标签。项目看板列、标签、triage 节奏和 demo 晋级规则见 [Project Board Guide](docs/project_board.md)。

## 项目能做什么

- 把支持的自然语言 GEE 任务解析成可审查 plan；
- 检索本地 dataset、operator、recipe、rule 和 failure evidence；
- 渲染经过批准的 Jinja2 Earth Engine Python 模板；
- 在 live 前验证脚本；
- 在 export 前运行 dry-run 和 preflight；
- 只有显式 `--confirm-live` 后才提交 live export；
- 监控 export task，并把 trace 写入 `outputs/runs/<run_id>/`；
- 保持公开知识通用化，避免把私有研究内容带进 GitHub。

## Agent-Native 接口

核心命令返回确定性 JSON，便于 agent 编排：

```bash
gee-skill info --json
gee-skill doctor --json
gee-skill catalog search "Sentinel-2 NDVI" --json
gee-skill catalog evidence --category dataset --json
gee-skill recipe list --json
gee-skill plan from-text "Compute NDVI for a supplied AOI in March 2024 and export CSV." --json
gee-skill render <plan.yaml> --script-out <script.py> --json
gee-skill validate <script.py> --json
gee-skill preflight <plan.yaml> --project "$EE_PROJECT" --json
gee-skill run <plan.yaml> --project "$EE_PROJECT" --confirm-live --json
gee-skill exports list --project "$EE_PROJECT" --json
gee-skill trace inspect <run_id> --json
gee-skill eval evals/benchmark_suite.yml --json
```

兼容命令 `ask`、`review-plan`、`preflight-plan`、`run-plan` 和 `monitor-exports` 仍可用于现有公开示例。

## 文档

- [How to start](docs/how_to_start.md)
- [Demo gallery](docs/demo_gallery.md)
- [Tool permissions](docs/tool_permissions.md)
- [Closed loop](docs/closed_loop.md)
- [Remote sensing validation ladder](docs/remote_sensing_validation.md)
- [Capability matrix](docs/capability_matrix.md)
- [Project board guide](docs/project_board.md)
- [Roadmap and TODO](docs/roadmap.md)
- [CLI reference](docs/cli_reference.md)
- [Recipe registry](docs/recipes.md)
- [Benchmark protocol](docs/benchmark_protocol.md)
- [Troubleshooting](docs/troubleshooting.md)
- [Extending workflows](docs/extending.md)

## 参考资料与数据源

- [Earth Engine Python API](https://developers.google.com/earth-engine/guides/python_install)
- [Earth Engine authentication](https://developers.google.com/earth-engine/guides/auth)
- [Sentinel-2 SR Harmonized](https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S2_SR_HARMONIZED)
- [MODIS Terra Vegetation Indices MOD13Q1](https://developers.google.com/earth-engine/datasets/catalog/MODIS_061_MOD13Q1)
- [MODIS Aqua Vegetation Indices MYD13Q1](https://developers.google.com/earth-engine/datasets/catalog/MODIS_061_MYD13Q1)
- [Landsat 8 Collection 2 Level 2](https://developers.google.com/earth-engine/datasets/catalog/LANDSAT_LC08_C02_T1_L2)
- [Landsat 9 Collection 2 Level 2](https://developers.google.com/earth-engine/datasets/catalog/LANDSAT_LC09_C02_T1_L2)
- [Dynamic World V1](https://developers.google.com/earth-engine/datasets/catalog/GOOGLE_DYNAMICWORLD_V1)
- [ESA WorldCover](https://developers.google.com/earth-engine/datasets/catalog/ESA_WorldCover_v200)
- [JRC Global Surface Water](https://developers.google.com/earth-engine/datasets/catalog/JRC_GSW1_4_GlobalSurfaceWater)

本地知识库位于 `references/knowledge_base/`。官方 Earth Engine 文档仍然是 API 行为的最高依据。

## 安全

Live Earth Engine 运行需要你自己的 Earth Engine account、Google Cloud Project 和本地 OAuth authentication。不要提交 service account JSON、OAuth token、本地 credential 文件、refresh token、credential path、private key、client secret、private asset id、论文草稿或未发表研究输出。
