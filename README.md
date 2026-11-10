# Motion Studio · Web R11（工程验证版）

这是 **纯 Web 产品**，不需要 Mac 安装包。主要产物是可直接在 Chrome/Safari 打开的 HTML。

## 现在可以体验的内容

- `Motion-Studio-Editor.html` — 双击打开即可使用的单文件编辑器，支持 ORBIT 等模板、文字编辑、3D 模型导入、镜头控制和 HTML 导出。无需安装、登录或 API。
- `ORBIT-R11-editor-export.html` — 从编辑器实际导出的原创 ORBIT 页面，带完整章节视觉叙事和本批增强的滚动分镜。
- `ORBIT-R11-textured-animation.html` — 真实导入带内嵌 PNG 贴图与动画的 GLB 后导出的网页。
- `R11-desktop.png` / `R11-mobile.png` — Chromium 实际截图（Canvas 软件 3D，不是 PBR GPU 截图）。
- `R11_TEST.json` / `R11_RELEASE_GATE.json` — 可复核的验收结果。

**提示：** 当前独立 HTML 编辑器的基础编辑、导出和 Canvas 动态预览是离线的。标准 Three.js / GLTFLoader 模块仍通过固定版本 CDN 加载；联网且 WebGL 可用时才尝试 PBR。不能把“代码存在”理解为 GPU 路径已通过验收。

## 在联网构建环境生成真正离线的 Three.js HTML

本包包含 `package.json` 和 `build-offline-three.mjs`。将完整工程上传到 GitHub 仓库，可通过 `.github/workflows/build-web-offline.yml` 手动启动 GitHub Actions 流程并获取 **Motion-Studio-Editor-OFFLINE.html** 构建产物（目前尚未实跑该云流程）。或在有 Node.js 22 和网络的环境下，在本目录执行：

```bash
npm install --no-audit --no-fund
npm run build:offline
```

生成时会固定采用 `three@0.180.0` 和 `esbuild@0.25.12`，并写出 Three.js 的 MIT 许可文件。成功构建后仍必须在真实 WebGL 设备上测试模型贴图、动画、材质和导出网页。

## 测试

```bash
python -m pip install playwright
python -m playwright install chromium
python test_r11.py
python verify_r11.py
```

`verify_r11.py --require-production` 是严格发布检查：目前会**按预期拒绝**正式发布，因为标准 Three.js 离线运行包、真实 GPU、Safari/移动设备和对标视觉验收尚未通过。不能更改“未通过”为“通过”来解除门槛。

## 对模型的兼容范围

- GLB v2、内嵌 Buffer/Image；限制 2 MB；拒绝远程、相对路径外部引用。
- Canvas 后备引擎支持部分静态网格和简化材质，不等价于完整 glTF。
- 标准 GLTFLoader 代码支持读取 GLB 内嵌贴图与动画，并带有 PBR 灯光场景，但尚缺可复核 GPU 画面和跨设备性能证据。

这是可继续研发的 A 阶段工程版，**不是商业正式版**。


## 2026-11-10 · Stage 9–16 最新状态（优先于上方 R11 历史说明）

- Stage 9–15 已有 **GitHub Actions Chromium SwiftShader 软件 WebGL** 实测产物：`stage9/output/CI_GATE.txt`（Run `42811399978`），以及各阶段 JSON、截图、离线 HTML。原有组件计数为 20。
- Stage 16 新增 `stage9/tests/test_stage16_mac_hardware.py` 与 `stage9/STAGE16_MAC_ACCEPTANCE.md`，用于在目标 Apple Silicon Mac 的原生 Chrome 检查真实 GPU 渲染器、PBR/GLB、动画像素变化和离线请求。
- `.github/workflows/stage16-mac-acceptance.yml` 只验证脚本语法与防伪通过守卫，**绝不代表 macOS 实测成功**。
- **真实 Apple GPU、原生 Safari、30 分钟 GPU 稳定性仍未通过验收；不得宣称正式生产就绪。**

运行方式和必要验收证据请阅读 [Stage 16 本地硬件验收说明](stage9/STAGE16_MAC_ACCEPTANCE.md)。
