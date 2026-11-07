# Motion Studio — Web R13

纯 Web 产品，无需 macOS 安装包。解压后打开 `Motion-Studio-Editor.html`，可编辑、预览、保存并导出独立网页；当前离线时使用 Canvas 后备三维。

- `Motion-Studio-Editor.html`：可直接打开的单文件网页编辑器，**不是**已打包的 Three.js 离线专业渲染编辑器。
- `ORBIT-R11-editor-export.html`：现有独立网页演示。
- `GPU-3D-Check.html`：在自己的浏览器中测试基础 WebGL/Canvas 能力；基础 WebGL 成功不等同于 PBR 已验收。
- `Sample-Textured-Animated.glb`：用于 Three.js 严格验收的含贴图及动画模型。
- `build-offline-three.mjs`、`package.json`：在**联网环境**运行 npm install / npm run build:offline 后才会产生 `Motion-Studio-Editor-OFFLINE.html`。
- `.github/workflows/build-web-offline.yml`：自动构建、真实模型导出、严格 WebGL/材质贴图/动画测试。
- `R11_TEST.json`、`R13_CONTRACT_TEST.json`、`R12_GPU_TEST.json`、`R12_RELEASE_GATE.json`：实际测试证据及未完成的发布条件。

验证命令（开发者或 CI 使用）：`python test_r13_contract.py`、`python test_r11.py`、`python test_gpu_pbr.py`（只有真正离线构建且 WebGL 可用才应通过）。

**发布状态：NOT_PRODUCTION_READY。** 尚未提供经 GPU 验收的专业 PBR HTML，也未完成 Pear / Grande Charte 视觉对标验收。
