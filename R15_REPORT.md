# Motion Studio · Web R15 工程结果与真实阻断

日期：2026-11-06。本批在 **R14 源码基础上实际修改及复测**；未生成包含 Three.js 的离线 PBR 运行库，未声称硬件 GPU 或标杆视觉验收通过。

## 本批实际代码变更
1. `three-pbr-module.js`：修复非原点 GLB 根节点的自动居中和比例缩放。原实现先平移、后缩放，导致根节点原本具有 translation 的模型在标准 3D 层里仍偏离画面中心；现在用 `(rootPosition - worldBoundingCenter) × factor` 计算根节点位置，保持三维模型和中心对齐。
2. `Motion-Studio-Editor.html`、`index.html`：同步内嵌的 Three.js 模块源码，避免导出的模块与本地构建源内容不一致。
3. 同两份编辑器 HTML：修复离线渲染器状态判断中的旧变量：构建脚本注入 `MotionThreeOfflineModule`，UI 现在会识别这个字段，不再把已经注入的离线模块错误报告为仅 CDN 可用。此修复需在真正构建后进一步浏览器确认。
4. 新增 `test_r15_pipeline.py`，执行：上传真实含 PNG 贴图和旋转动画的 GLB；编辑器导出 HTML；从 HTML 反向解析内嵌 GLB；对比原始 GLB 与导出 GLB SHA-256；验证 GLB 元数据及页面滚动、手机宽度、浏览器异常。

## 本批复测

| 测试 | 结果 |
| --- | --- |
| R11 编辑器 / 章节 / 移动端 / HTML 导出 | PASS |
| R13 源码、导出及 CI 契约 | PASS |
| R14 渲染指标一致性 | PASS |
| R15 GLB 原始字节、SHA-256、重新打开、滚动等 | PASS |
| 离线 Three.js PBR + GLTFLoader + 动画 | **FAIL**：尚无 npm 离线依赖构建产物 |
| 真实 GPU、Safari 或移动端图形渲染 | **NOT TESTED** |
| 视觉对标 Pear / Grande Charte | **NOT ACCEPTED** |

实际结构化结果 `R15_TEST.json`；控制台日志 `R15_*TEST.log`。

## 网络与 GitHub 现实情况
- 本容器访问 `registry.npmjs.org` / `github.com` / `cdn.jsdelivr.net` 的 DNS 失败，错误为 `EAI_AGAIN`，无法安装 Three.js 或构建真正离线包。当前环境无 WebGL 图形上下文。
- 已检查已连接 GitHub 仓库：目前 **没有 Motion Studio 专属仓库**。现有仓库属于其他项目，不能在未指定目标时将 Motion Studio 代码放进其他仓库。
- 工作流位于 `.github/workflows/build-web-offline.yml`，专用 GitHub 仓库创建并上传解压内容后即可运行；CI 成功亦不能替代 Safari 和真实设备人工视觉验收。

## 剩余发布门禁（顺序）
1. 在正常联网的构建环境执行 `npm install`、`npm run build:offline`，生成 `Motion-Studio-Editor-OFFLINE.html` 和内嵌 Three.js 包。
2. 严格运行 `test_gpu_pbr.py`；模型贴图、材质、动画和绘制指标全部有证据，失败不得发布。
3. Mac Safari/Chrome 与至少一台手机上实际检查 GPU/帧率/内存、编辑、导出及交互。
4. ORBIT 与选定设计标杆逐章节截图、滚动视频和可编辑性验收，记录差距后修复。

**结论：R15 为修复与数据完整性验收批次。A 阶段尚未发布合格。**
