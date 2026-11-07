# Motion Studio Web R15

**打开网页编辑器**：`Motion-Studio-Editor.html`（单文件，无需命令行；标准 Three.js 模块本次尚未离线打包）。

**查看已有示例**：`ORBIT-R11-editor-export.html`；注意本文件是此前测试生成的离线 Canvas 演示，不代表真实 PBR 画面。

**查看测试**：`R15_REPORT.md`、`R15_TEST.json`。源码中 `three-pbr-module.js` 已修复根节点自动居中逻辑；`test_r15_pipeline.py` 会在支持 Playwright/Chromium 的测试环境验证 GLB 文件往返不变。

**标准 3D**：需要在一个联网的新 Motion Studio 专属 GitHub 仓库中将工程内容放到仓库根目录（包含隐藏 `.github/` 目录），然后 GitHub Actions → `Motion Studio - offline Three.js Web validation` → Run workflow。生成离线编辑器后仍需查看严格 PBR 和真实 GPU 结果。

R15 **未**打通真实 GPU/Three.js 发布门禁。不要将 `Motion-Studio-Editor.html` 宣传为完全离线的标准 PBR 编辑器。
