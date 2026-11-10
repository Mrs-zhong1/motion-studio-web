# Motion Studio · Stage 10 共享三维摄像机可视化编辑器 — 批处理验收报告

**最终云端执行记录**：[GitHub Actions #42778849533](https://github.com/Mrs-zhong1/motion-studio-web/actions/runs/42778849533) · success

## 可用文件

- **Stage 10 离线 HTML 编辑器**：[Motion-Studio-Stage10-Camera-Editor-OFFLINE.html](https://github.com/Mrs-zhong1/motion-studio-web/blob/main/stage9/output/Motion-Studio-Stage10-Camera-Editor-OFFLINE.html) (1,706,559 bytes)
- **Stage 10 导出的共享 3D 示例**：[STAGE10-CAMERA-EXPORTED.html](https://github.com/Mrs-zhong1/motion-studio-web/blob/main/stage9/output/STAGE10-CAMERA-EXPORTED.html)
- **浏览器机器验收**：[STAGE10-CAMERA-RESULT.json](https://github.com/Mrs-zhong1/motion-studio-web/blob/main/stage9/output/STAGE10-CAMERA-RESULT.json)
- **真实 WebGL 测试截图**：[STAGE10-CAMERA-CAPTURE.png](https://github.com/Mrs-zhong1/motion-studio-web/blob/main/stage9/output/STAGE10-CAMERA-CAPTURE.png)
- **工程保存回归样本**：[STAGE10-CAMERA-PROJECT.json](https://github.com/Mrs-zhong1/motion-studio-web/blob/main/stage9/output/STAGE10-CAMERA-PROJECT.json)
- **原始 CI 门禁**：[CI_GATE.txt](https://github.com/Mrs-zhong1/motion-studio-web/blob/main/stage9/output/CI_GATE.txt)

## 用户操作方式

1. 下载并在 Chrome 等兼容浏览器中打开 Stage 10 的独立 HTML 编辑器，不需在最终用户电脑安装 Node/npm。
2. 在左侧组件库添加至少两个「GLB 离线三维章节」，分别上传本地 GLB（目前单个最大 2 MB）。
3. 选择任意一个 GLB 章节，在右侧 **Stage 10 · 共享 Three.js 镜头关键帧** 调整 7 个滑块：X、Y、Z、Yaw、Pitch、Roll、FOV。一个 GLB 章节对应一个共享相机关键帧。
4. 点击「预览共享 3D 网页」；调整参数后点击「刷新预览」。这是加载实际导出 HTML 的嵌入预览，不是拖拽三维坐标轴式视口。
5. 保存 JSON 工程或导出 HTML；后者将加载一个共享 Three.js Scene/Camera/Renderer，并随页面滚动在各章节镜头关键帧之间进行 smoothstep 插值。

## Stage 10 真正完成的工程能力

- 在 **既有 20 个组件上增加镜头编辑，不新增第 21 个组件**。
- 7 项空间相机参数范围归一化并与旧工程兼容（旧工程缺省使用 X=0、Y=0、Z=5.5、Yaw/Pitch/Roll=0、FOV=42）。
- 相机参数写入项目 JSON；重新导入恢复相同数值。
- 多 GLB 导出页面使用同一 Three.js 摄像机，在相邻章节中心之间插值 **位置、朝向和 FOV**；模型仍在同一个共享 Scene。
- 右侧面板提供按需刷新内嵌预览，浏览器实测可创建共享 WebGL2 画布并加载两个模型。
- 修复 Stage 8 遗留 iframe Canvas WebGL 绘制竞态（异步加载模型前访问 null mesh.groups），后续完整浏览器回归无脚本异常。
- 保留原有多图层、章节序列、单 GLB 场景与完整 HTML 导出。

## 实际验收证据（GitHub Actions Ubuntu Chromium + SwiftShader）

| 检查项 | 实际结果 |
| --- | --- |
| GitHub Actions #42778849533 | success |
| 组件注册 | 20/20 |
| GLB 章节 | 2 |
| 空间相机输入滑块 | 7 |
| 相机编辑值 | X=1.5，Y=0.8，Z=7.2，Yaw=26°，Pitch=-14°，Roll=12°，FOV=59° |
| JSON 保存后重新导入 | 七个值逐一一致 |
| 编辑器内预览共享 GPU | WebGL2=true，2 模型，1 画布，error=null |
| 导出网页共享场景 | WebGL2=true，2 模型，1 画布 |
| 导出网页绘制 | 29 帧、10 个非空像素采样点 |
| 末端摄像机采样 | X≈4.345、Y≈0.740、Z≈7.071、Yaw≈24.035°、Pitch≈-12.942°、Roll≈11.093°、FOV≈57.715° |
| Stage 10 脚本异常 | 0 |
| Stage 9 复杂 GLB 三样本矩阵 | PASS |
| Stage 9 非法 GLB 五样本回归 | PASS |
| Stage 9 共享 WebGL 场景回归 | PASS |
| Stage 9 PBR 纹理/GLB 动画 | PASS |

证据依据 `stage9/output/STAGE10-CAMERA-RESULT.json` 和 `CI_GATE.txt`。注意绘制帧数不是 FPS。

## 未完成 / 产品边界

- 编辑器镜头参数以右侧滑块操作，**未实现**可拖拽 3D gizmo、Bezier 曲线路径或任意时间点自定义数量的关键帧（目前每个 GLB 章节一个空间关键帧）。
- 预览通过嵌入最终 HTML 方式运行；修改镜头参数后需主动刷新预览，尚不是自动实时双向同步。
- 共享模型与场景镜头只在含两个或以上 GLB 的导出/嵌入预览中启用；编辑器普通章节画布仍使用原方式。
- **真实 Apple Silicon Mac 的 Chrome 硬件 GPU / Safari、移动 Safari、长时间压力和视觉品质验收均未完成**。所有本批 3D 证据来自 GitHub Actions Chromium SwiftShader（软件 WebGL）。
- Draco/KTX2/meshopt、>2 MB 大型 GLB、各类复杂生产模型仍未通过兼容性验收。

**结论：Stage 10 可编辑 7 参数共享 3D 镜头 + 项目回存 + 导出效果一致性 + 嵌入预览，云端软件 WebGL 测试通过；仍为工程验收版本而非商业正式版。**
