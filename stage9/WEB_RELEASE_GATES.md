# Motion Studio Web · P0–P5 产品交付门槛

更新时间：2026-11-10。本文件区分**代码已提交**与**真实测试通过**。禁止把 CI 编译成功等同于产品发布通过。

| 批次 | 验收要求 | 当前可核实证据 | 结论 |
|---|---|---|---|
| P0 工程统一 | Stage 9–15 统一构建，20 组件不丢失；原生 Web 发布规则 | Stage 9–15 输出已存档，发布 manifest 修改已提交，待新 CI | 部分完成 |
| P1 编辑器 | 无代码模板→编辑→项目保存→新建→重新导入→预览 | `tests/test_web_product_e2e.py` 已提交，待 CI 结果 | 待验收 |
| P2 3D 素材 | GLB/PBR/纹理/关键帧、异常模型恢复、资源释放 | 旧 Stage 9–15 SwiftShader 软件 WebGL 测试通过；浏览器矩阵未覆盖深度 3D | 部分通过 |
| P3 导出 | 同一工程编辑与导出，HTML 无远程依赖，章节一致 | 旧 Stage 9–15 导出测试通过；新增端到端待 CI | 待验收 |
| P4 Web 质量 | Chromium、Firefox、WebKit 的主要流程，移动设备与易用性 | `web-product-e2e.yml` 三浏览器自动化已提交，未核实结果；WebKit≠原生 Safari | 待验收 |
| P5 部署 | 用户访问 HTTPS 网址，创建、保存和导出成功，具备发布回滚 | 尚无实测生产 URL 或部署环境验收证据 | 未完成 |

## 已提交的新增自动化测试

- `.github/workflows/web-product-e2e.yml`：Node 22 构建 Stage 15 离线编辑器；Chromium/Firefox/WebKit 分别执行真实浏览器 E2E；按浏览器上传测试 JSON、工程 JSON、独立导出的 HTML 和构建 manifest。
- `stage9/tests/test_web_product_e2e.py`：组件数、模板、编辑项目标题、JSON 保存和导入、移动与桌面预览、导出章节数、网络零请求和 JS pageerror。
- `stage9/build-offline.mjs`：发布模型从“必须 Apple Silicon GPU”改成 “Web 跨浏览器与端到端验收”。

## 发布规则

- **基础 Web 产品发布阻断项**：P0–P5 全部通过，至少主流桌面浏览器关键流程、正式部署 smoke、导出真实产物、异常恢复和安全检查有可核验证据。
- **3D 高级能力发布阻断项**：真实浏览器 WebGL、GLB/PBR、资源占用、兼容性可靠；软件 SwiftShader 是基础证据而非所有设备通用结论。
- **非必需项**：Apple Silicon 特定型号 GPU、macOS 单一机型验收；只作为额外覆盖。
- **不能混淆**：Playwright WebKit 的通过不等于 Apple Safari 本机/手机实测；Chromium SwiftShader 软件 WebGL 也不是独立 GPU 硬件确认。
- 最终总体状态：**NOT RELEASED / NOT VERIFIED FOR PRODUCTION**，直到确有生产网址和端到端验收。

## 执行入口

[Web E2E Actions](https://github.com/Mrs-zhong1/motion-studio-web/actions/workflows/web-product-e2e.yml)

[Stage9–15 software WebGL Actions](https://github.com/Mrs-zhong1/motion-studio-web/actions/workflows/stage9-three-offline.yml)


## P5 新增自动化发布链（2026-11-10）

- `.github/workflows/web-release-pages.yml`：真实 Stage15 Web 编辑器构建 → Chromium / Firefox / WebKit 真实浏览器用户流程测试（任一失败则不能部署）→ 生成独立 `dist/index.html`、`THREE_LICENSE.txt`、`WEB_RELEASE.json` 与 SHA256 → 通过 `actions/deploy-pages@v4` 发布 → 在线 HTTPS 浏览器 smoke。
- `stage9/tests/test_live_deployment.py`：直接访问部署后正式 URL，验证 HTTP 200、20 组件、模板加载、项目 JSON 下载、HTML 下载、JS 页面错误，并上传产物。
- **注意**：仓库的 GitHub Pages 需由仓库管理员在 Settings → Pages 设置 GitHub Actions 作为 Source；如未启用或仓库权限不足，部署任务会失败，不能视为已上线。
- 当前状态：发布脚本与工作流**已提交但未取得成功运行证据**。正式 URL 尚未验证。
- GitHub Actions 工作流入口：https://github.com/Mrs-zhong1/motion-studio-web/actions/workflows/web-release-pages.yml
- 正式交付须留存：三浏览器 E2E artifacts、Pages deploy URL、`P5_LIVE_SMOKE.json` 全部通过、导出的真实 HTML、SHA256 校验。


## P1 数据恢复修复与回归（本轮）

- 修复 `Motion-Studio-Unified-Editor.html`：新建工程时立即清空并写回自动草稿，同时清理旧项目撤销/重做历史；导入 JSON 工程时写回草稿；加载模板时立即存储草稿。
- 扩展 `tests/test_web_product_e2e.py`：通过实际 `file://` 加载离线编辑器，验证新建空工程和导入工程均能在浏览器刷新后保持；同时保留模板、保存、移动预览、HTML 导出检查。
- 修改 `web-product-e2e.yml` 触发范围：核心编辑器源码变更时自动触发，避免只测试测试脚本变更。
- **状态：已提交代码和测试；尚未取得新浏览器 CI 成功结果。**


## P1 可靠性补充（后续批次）

- 自动草稿写入浏览器存储失败时，不再静默忽略；显示需要手动导出 JSON 的警告，并在存在未写入草稿时尝试提示用户避免意外关闭页面。**仅警告，不是无限存储或云同步能力。**
- E2E 新增组件库完整计数为 20、通过真实 UI 添加组件、添加后草稿写入、浏览器刷新恢复测试。
- 此批修改已提交 GitHub；新工作流尚无可访问的成功记录，**不能将新增用例标为通过**。
- 若计划正式公开用户使用，仍需对 localStorage 容量限制、不同浏览器、上传资产和项目备份体验作实际验收。


## 发布流水线安全修正（最新）

- `web-release-pages.yml` 已取消 push 自动部署触发，仅在 GitHub Actions 手动启动时运行，避免未验收源码提交即被当作正式版发布。
- 同次发布必须同时通过 **Chromium / Firefox / WebKit** 编辑器端到端测试和独立的 **Three.js/GLB WebGL** 回归任务（真实 PBR 动画/像素、模型矩阵、异常 GLB、共享 3D 场景）。任何一个任务失败则 `publish` 不执行。
- `test_web_product_e2e.py` 已对异步 JSON 导入增加等待，并验证手动导入不会带入上一工程的撤销/重做历史。
- `Motion-Studio-Unified-Editor.html` 已区分用户显式导入与内部 undo/redo 载入：前者重置撤销历史，后者保留。
- **仍未得到新 GitHub Actions 执行证据。** CI 配置提交不等于通过；Pages 部署在真实运行和完成线上 smoke 前保持未验收。
- 注意：Pages 在部署后才运行 live-smoke；部署后一旦 smoke 失败，需回滚/撤销发布或修复后重新部署，不能把该设计描述为“未验证前绝不公开”。


## 本批次用户编辑器故障修复（2026-11-10）

- 修复：首次向没有章节背景图的组件上传图片时，先动态创建 `.section-art`，避免空元素引用异常；移除图片时同步删除该节点。
- 修复：新增和复制章节时强制不超过 40 章，与项目 JSON 导入上限一致，避免编辑器能创建却不能重新打开的工程。
- 新增真实浏览器回归用例：新建组件 → 上传本地 PNG → 断言背景节点存在 → 清除图片 → 断言背景节点删除。
- 已确认相关源代码和测试代码通过 GitHub 文件读取回查；最新新测试 **尚未有 CI 执行通过证据**。
- 当前 GitHub 连接没有新 workflow dispatch API；工作流执行由 GitHub Actions 触发器完成，只有收到实际运行 ID 和日志才能认定完成。
- Vercel 项目列表中没有 `Mrs-zhong1/motion-studio-web` 绑定项目；当前未直接创建自动公开部署，避免绕过浏览器与 3D 发布门槛。


## P5 发布产物一致性加强（2026-11-10）

- 修复“浏览器验证一份 HTML，部署时又重新构建另一份 HTML”的风险：Chromium E2E 作业将其**实际测试的 Stage15 HTML、Three.js 许可和构建清单**作为 `release-candidate-tested-html` artifact 保存；`publish` 通过 `actions/download-artifact@v4` 原样取回并部署，不再执行第二次 npm 构建。
- `publish` 仍依赖独立的三浏览器 Web 产品测试和 PBR/GLB 回归；两者全通过才运行。
- `test_live_deployment.py` 新增远端 `WEB_RELEASE.json` 校验：对线上响应 HTML 计算 SHA256 并与该发布清单的 SHA256 对比，检查**实际对外服务的字节**是否匹配候选产物。
- `test_web_product_e2e.py` 改为使用临时 `127.0.0.1` HTTP 服务打开单文件编辑器；使浏览器的 localStorage 草稿测试有稳定的 HTTP origin。离线导出页依旧独立检查零 HTTP(S) 请求。
- 此批有 GitHub 提交和文件回查证据，但**无新的 CI run ID、未获得实际三浏览器通过报告、未上线**。本地受沙箱浏览器访问策略限制，不能用其页面访问结果替代 GitHub Actions 测试。
