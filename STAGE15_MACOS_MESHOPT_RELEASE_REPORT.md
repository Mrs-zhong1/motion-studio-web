# Motion Studio · Stage 15 — macOS Apple Silicon DMG、真实 WebKit 运行和压缩 GLB 批处理报告

**状态：工程版本可下载并通过 CI；未达到商业生产发行门槛。**

## 最终交付

- **macOS M1/M5 Apple Silicon 原生安装包（未公证测试版）**：[Motion-Studio-Stage15-macOS-AppleSilicon-UNSIGNED.dmg](https://github.com/Mrs-zhong1/motion-studio-web/blob/main/macos/dist/Motion-Studio-Stage15-macOS-AppleSilicon-UNSIGNED.dmg)；920,295 bytes。
- [macOS M1 实机托管 runner 构建/启动/绘制/打包成功日志](https://github.com/Mrs-zhong1/motion-studio-web/actions/runs/42812037644)。
- [macOS DMG 校验和与真实构建证据](https://github.com/Mrs-zhong1/motion-studio-web/blob/main/macos/dist/MACOS_DMG_BUILD_EVIDENCE.json)。
- [Stage15 最新离线 HTML 编辑器](https://github.com/Mrs-zhong1/motion-studio-web/blob/main/stage9/output/Motion-Studio-Stage15-Meshopt-OFFLINE.html)；1,799,579 bytes。
- [全部软件 WebGL CI（14/14 门禁通过）](https://github.com/Mrs-zhong1/motion-studio-web/actions/runs/42811399978)。
- [真实 meshopt 压缩模型 WebGL 测试结果](https://github.com/Mrs-zhong1/motion-studio-web/blob/main/stage9/output/STAGE15-MESHOPT-RESULT.json)。
- [单 GLB 压缩模型渲染截图](https://github.com/Mrs-zhong1/motion-studio-web/blob/main/stage9/output/STAGE15-MESHOPT-CAPTURE.png)；[共享场景压缩模型渲染截图](https://github.com/Mrs-zhong1/motion-studio-web/blob/main/stage9/output/STAGE15-MESHOPT-SHARED-CAPTURE.png)。

## 真实验收记录

### macOS 原生应用 / DMG

GitHub macOS 15.8.2 M1 arm64 环境：Swift 原生 WKWebView 应用 **实际编译**；内嵌 Stage15 离线 HTML；临时签名、代码签名结构验证、DMG 压缩与校验、挂载/校验内置文件并卸载均通过。

在该 macOS M1 上**实际运行原生应用**，WKWebView 加载本地 file: HTML，`registry.length=20`，导出函数调用成功，两个离线 Three.js 引擎变量存在，WebGL2 上下文创建成功，着色器编译与绘制/像素读取成功（`drawnPixel=1`）。

最新 DMG SHA-256：`5d66430d6c9ada455eed76fee0ffc8423da3da280dbdaaa06f8cfdb991e72ef9`；大小：920,295 bytes。证据来源：`macos/dist/MACOS_DMG_BUILD_EVIDENCE.json`，CI #42812037644。

注意：**这是 GitHub 的 Mac M1 托管运行环境，而非用户个人 Mac 或 Safari 浏览器**。原生应用是 WKWebView 内嵌，不能把它等同于所有用户 Safari 交互表现或真实硬件加速性能验收。

### Stage15 meshopt 离线压缩 GLB

- 使用 pin 版本 meshoptimizer 编码器真实压缩生成 `EXT_meshopt_compression` GLB，经解码器校验原始字节一致。
- 普通单章 GLTFLoader + 内嵌 MeshoptDecoder：`webgl2=true`、1 网格、PBR 材质、6 次绘制、非空像素 6、pixelDifference=3444，error=null。
- 共享 Three.js 场景：meshopt GLB + 普通 GLB，2 模型、1 WebGL Canvas、模型网格数量分别 1、2，error=null。
- 不使用外部网络请求，20 个原组件继续通过。
- **Draco 和 KTX2/Basis 不支持**，且编辑器继续对不支持的必需压缩扩展给出明确提示，不能因为 meshopt 成功就宣称三种格式全部完成。

### 软件回归

GitHub Actions #42811399978：Stage 9–15 的 14/14 项门禁成功；包括 Three.js 离线包、PBR、纹理/骨骼/Morph、异常 GLB、共享场景、镜头路径、真实 XYZ 控制点、贝塞尔入出手柄、4MB GLB、撤销重做、软件 WebGL 压力与 meshopt 压缩模型渲染。

## Mac 安装步骤与限制

1. 在上方安装包文件页点击 **Download raw file**。
2. 双击 DMG，将 `Motion Studio.app` 拖入 `Applications`。
3. 此版仅作测试使用：**没有 Apple Developer ID 正式签名，也没有 Apple 公证**，macOS Gatekeeper 可能提示无法验证开发者或阻止打开。仅在信任该来源时，可通过“系统设置 → 隐私与安全性 → 仍要打开”（不同系统版本措辞可能不同）尝试允许。
4. 启动后可直接使用内置离线编辑器，无需在个人 Mac 上安装 Node、Python 或执行命令。

## 仍未完成 / 生产门禁

- 用户自己的 Mac（例如 Apple M5）上真实执行安装包、交互、文件导入/导出、性能和崩溃恢复：未验证。
- Safari 独立浏览器、iPhone/iPad Safari、多触控：未验证。
- Mac 长时间 WebGL 3D 场景压力、GPU 显存和泄漏检测：未验证。现有 Mac smoke 测试只证明基本绘制/像素读取。
- Draco 压缩几何、KTX2 Basis 纹理离线解码及真实压缩样本：未完成。
- Apple Developer ID 签名、公证和稳定用户安装发布：缺少开发者证书/Apple 授权，未完成。
- 商业级视觉细节和真实用户体验验收：未完成。

**实际阶段结论：** Stage15 已有真正可下载的 Apple Silicon DMG，可运行的 macOS WKWebView 原生包、可反复验证的真实 meshopt 压缩 GLB 支持和 14/14 旧版+新增软件回归。但不能把“Mac M1 runner 通过基础 WebGL”推断为“用户 Apple M5 GPU 性能通过”，也不能宣称生产正式版已经签名公证。
