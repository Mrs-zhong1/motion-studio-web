# Stage 16 · Apple Silicon 真实硬件与 Safari 验收（未完成）

本阶段**不把 GitHub Actions Linux SwiftShader 软件 WebGL 当作 Apple GPU**，也不把 Playwright WebKit 当作 macOS 原生 Safari。

## 已确认的证据

- Stage 9–15：GitHub Actions 软件 WebGL 通过；见 `stage9/output/CI_GATE.txt`。
- 20 个组件保留；Stage 15 真正 Meshopt 压缩 GLB 在单场景和共享场景通过。
- Apple Silicon Chrome 真实硬件 GPU：**待目标 Mac 实测**。
- 原生 Safari、长运行 GPU 内存：**待目标 Mac 实测**。

## Mac 上运行 Chrome 实测

从仓库下载完整工程，在 Mac 上安装 Python 3 与 Playwright，确保已安装 Google Chrome：

```bash
python3 -m pip install playwright
python3 stage9/tests/test_stage16_mac_hardware.py
```

推荐将命令运行目录设为项目根目录。脚本**不使用 SwiftShader 启动参数**，将打开已安装的 Google Chrome，加载 Stage15 实际离线导出的 HTML，推进多帧动画，记录 PBR/WebGL2/材质/像素差异/请求错误、GPU 厂商和渲染器，保存截图。

输出：`stage9/output/STAGE16-MAC-HARDWARE-RESULT.json` 与 `STAGE16-MAC-HARDWARE-CAPTURE.png`。若 WebGL 调试扩展不提供真实 GPU 名称，结论为 **inconclusive**，不能擅自标为通过。

## 原生 Safari（必须单独实测）

使用 Safari **直接打开** `stage9/output/STAGE15-MESHOPT-SINGLE-EXPORTED.html` 及 `STAGE15-MESHOPT-SHARED-EXPORTED.html`。验证动画、贴图、PBR 外观、滚动变化、双模型与无远程依赖；保留 Safari 浏览器版本、macOS 版本、屏幕录制/截图、Web Inspector 错误及复测步骤。未经实际运行，不得填写 PASS。

## 长时间稳定性（必须单独实测）

在 Mac GPU 下连续播放及滚动至少 30 分钟，记录活动监视器 GPU/内存变化、WebGL context loss、应用崩溃或卡顿、前后屏幕截图；必须有前后对比及可追溯日志。只有真实硬件测试满足预先定义阈值，才能宣称稳定性通过。

## 生产发布阻断项

必须同时具备：GitHub Actions 软件验收通过、Chrome 真实硬件验收通过、原生 Safari 实测通过、长运行 GPU 内存验收通过、20 个组件不退化。这些证据不齐时：**releaseAccepted=false**。
