# Motion Studio · Stage 11 3D 镜头轨迹与时间轴 — 批处理验收报告

**本批最终成功的 GitHub Actions：** https://github.com/Mrs-zhong1/motion-studio-web/actions/runs/42782305215

**范围：** 现有 Motion Studio 20 组件编辑器上的增量 Stage 11。云端 Ubuntu Chromium + SwiftShader 软件 WebGL 已测试；真实 Apple Silicon Mac GPU 和 Safari 未测试。

## 正式交付
- [Stage 11 离线编辑器（单 HTML）](https://github.com/Mrs-zhong1/motion-studio-web/blob/main/stage9/output/Motion-Studio-Stage11-Timeline-OFFLINE.html)：1,716,400 bytes。
- [Stage 11 镜头轨迹导出网页](https://github.com/Mrs-zhong1/motion-studio-web/blob/main/stage9/output/STAGE11-TIMELINE-EXPORTED.html)：859,022 bytes。
- [可重新导入的 Stage 11 JSON 工程](https://github.com/Mrs-zhong1/motion-studio-web/blob/main/stage9/output/STAGE11-TIMELINE-PROJECT.json)。
- [真实云端渲染截图](https://github.com/Mrs-zhong1/motion-studio-web/blob/main/stage9/output/STAGE11-TIMELINE-CAPTURE.png)。
- [机器可读的严格验收数据](https://github.com/Mrs-zhong1/motion-studio-web/blob/main/stage9/output/STAGE11-TIMELINE-RESULT.json)。
- [完整 CI 门禁](https://github.com/Mrs-zhong1/motion-studio-web/blob/main/stage9/output/CI_GATE.txt)。

## 具体能力与使用

1. 至少添加两个已导入 GLB 的三维章节，选择前一个 GLB 章节。
2. 在右侧“Stage 11 · 3D 镜头轨迹与时间轴”点击启用轨迹。默认创建 0%、50%、100% 三个镜头点，最多 8 个关键帧；可新增中间帧、删除非端点帧。
3. 拖动 SVG 轨迹节点：水平改变时间百分比（两端点固定），垂直改变 X 镜头偏移；选择节点后也可调节其 X、Y、Z、Yaw、Pitch、Roll、FOV 七个字段。
4. 打开 Stage 10 的“预览共享 3D 网页”，后续修改 Stage 11 路径会通过 postMessage 给同一个共享 Three.js 场景，**无需重新加载模型或销毁 WebGL 上下文**。
5. 保存 JSON 或直接导出单 HTML。相机采用与章节滚动关联的 **Cubic Hermite（与三次 Bézier 等价形式）** 分段曲线；0% 与 100% 端点约束、路径参数校验、有限值与范围限制在测试中验证。
6. Stage 11 路径是从**当前 GLB 章节到下一 GLB 章节**的过渡路径；最后一个 GLB 章节的轨迹没有后续目标段。

## 最终真实验收数据（CI 42782305215）

| 项目 | 实测 | 结果 |
|---|---|---|
| GitHub Actions build-and-test | success | PASS |
| 组件数 | 20/20 | PASS |
| GLB 章节 | 2 | PASS |
| 新建轨迹 | 3 点 | PASS |
| 增加关键帧 | 3 → 4 | PASS |
| 删除关键帧 | 4 → 3 | PASS |
| SVG 拖动方向 | 向右 50% → 61.82%；向上 X 0.8 → 1.72 | PASS |
| 预览实时消息更新 | 0 → 1 条，场景 UUID 未变 | PASS |
| JSON 保存/重新导入 | 路径、时间与 7 参数一致 | PASS |
| 独立导出 HTML | 859,022 bytes | PASS |
| 导出 WebGL2 共享场景 | 2 模型，1 画布 | PASS |
| 实际 WebGL 绘制 | 27 帧，5 个有效像素采样点 | PASS |
| 自定义轨迹中段 | X≈5.105、Y≈1.400、Z≈7.300、FOV≈68、Yaw≈28 | PASS |
| 脚本异常 | 0 | PASS |
| 旧 Stage 9 PBR/复杂 GLB/异常文件/共享场景 | 所有门禁 success | PASS |
| 旧 Stage 10 编辑/导出摄像机 | success | PASS |

### 曾经发生且已修复的问题
- 首次 Stage 11 回归仅因缺失 `stage11Custom` 返回字段被拒绝；补齐字段后 GPU 曲线验收通过。
- 更严格的定向拖拽回归发现 SVG Y 坐标被提前乘以视图高度，拖动时把 X 错误钳制为 -4；现已修正比例归一化，并重新执行整套 CI，达到最终 success。
- 此前的 Stage 8 GLB 预览竞态修复仍保留。

## 未完成 / 发布门禁
- 真实 Apple Silicon Mac Chrome 硬件 GPU / Safari / iOS 实机没有测试；云端绘制次数不代表设备 FPS。
- 目前的 SVG 时间轴展示时间与 X 位置二维投影，**不是**可以在 3D 视口直接拖拽三维坐标轴的专业 gizmo。
- 插值算法为三次 Hermite / Bézier 等价曲线，但没有供用户调节每个关键点独立入/出 Bezier 手柄；也没有复杂镜头碰撞检测和镜头运动约束。
- 当前每个 GLB 章节的时间轴只作用于它到下一 GLB 章节的过渡，编辑器依然是网页式 UI。
- Draco/KTX2/meshopt、较大 GLB/真实硬件性能仍未验收。

**结论：Stage 11 已完成开发、云端真实软件 WebGL 渲染与严格自动化回归；仍是工程验收版本，不是完整商业正式版。**
