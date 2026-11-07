# Motion Studio · Web R12 — 离线 3D 发布验收增强版

本批直接继承 R11 单文件 Web 编辑器。没有发布新的 PBR GPU 通过声明。

## 立刻可用
- `Motion-Studio-Editor.html`: 浏览器直接打开的编辑器。支持模板修改和离线 Canvas 3D。
- `ORBIT-R11-editor-export.html`: 编辑器生成的独立网页；可直接打开。
- `ORBIT-R11-textured-animation.html`: 带内嵌纹理/动画 GLB 的导出数据样例。当前离线并未证明 PBR 正常运行。
- `R11_TEST.json`: 本批重新运行的 Chromium 编辑/导出/滚动/响应式回归。
- `R12_GPU_TEST.json`: 严格 WebGL/PBR 测试，当前未通过；列明缺少的运行包。
- `R12_RELEASE_GATE.json`: 正式发布门槛及阻断项。

## 这批真正新增

`test_gpu_pbr.py` 是**导出的成品页面**验收，不只是检查构建脚本存在：
1. 在 `Motion-Studio-Editor-OFFLINE.html` 中选择 ORBIT，上传真实含贴图和动画的 `Sample-Textured-Animated.glb`；
2. 在浏览器里实际点击导出，重新打开独立 HTML；
3. 验证 `#ms-three-canvas` 至少绘制 3 帧且 glTF 动画轨至少 1 个；
4. 拦截所有 HTTP(S) 请求，确认整个过程不依赖 CDN；
5. 捕获所有页面 JS 错误，有任何缺失即失败。

`.github/workflows/build-web-offline.yml` 在有网络的 GitHub Actions 上实际构建 Three.js r180 和 GLTFLoader，执行上述测试，并上传完整结果；即使失败也保留结果和尽可能多的构建工件。**云端流程尚未实际触发。**

云端测试借助 SwiftShader，验证的是**WebGL 软件实现中的渲染管线**，不是用户 Mac 或手机的硬件 GPU。真实 GPU、Safari 和视觉品质仍必须另行验收。

## 联网机器的自动构建和测试

```bash
npm install --no-audit --no-fund
npm run build:offline
python -m pip install playwright
python -m playwright install chromium
python test_r11.py
python test_gpu_pbr.py
python verify_r12.py
```

`test_gpu_pbr.py` 如果当前设备没有 WebGL 会以非零状态退出，正确标记为未通过。

## 当前判定

- 通过：R11 所有基础浏览器回归重新执行通过。
- 未通过：离线 Three.js 依赖包未在当前无网络环境中生成。
- 未通过：WebGL/PBR/贴图/动画的真实运行验收。
- 未通过：Safari/真实硬件 GPU/标杆视觉验收。

**不应以 `npm run build:offline` 脚本存在，推断已构建成功。**
