# Motion Studio · Stage 12 专业空间轨迹视口与镜头 Gizmo — 批处理验收报告

**最终实际 CI 运行：** [GitHub Actions #42791202200](https://github.com/Mrs-zhong1/motion-studio-web/actions/runs/42791202200) — `success`

**范围：** 在 Stage 9–11 的 20 个组件基础上加入共享 Three.js 场景里的真实三维轨迹辅助线、控制球体、X/Y/Z 坐标轴箭头、轴约束拖动、视角切换、张力调节、无需重新加载模型的实时同步，以及完整离线 HTML 和 JSON 工程导出。不是独立建模软件。

## 可直接使用的产物

- [Stage 12 完整离线 HTML 编辑器](https://github.com/Mrs-zhong1/motion-studio-web/blob/main/stage9/output/Motion-Studio-Stage12-Spatial-Gizmo-OFFLINE.html) — 1,734,918 bytes。
- [Stage 12 真实导出网页](https://github.com/Mrs-zhong1/motion-studio-web/blob/main/stage9/output/STAGE12-GIZMO-EXPORTED.html) — 872,763 bytes。
- [可恢复编辑的 JSON 工程](https://github.com/Mrs-zhong1/motion-studio-web/blob/main/stage9/output/STAGE12-GIZMO-PROJECT.json)。
- [云端真实浏览器截图](https://github.com/Mrs-zhong1/motion-studio-web/blob/main/stage9/output/STAGE12-GIZMO-CAPTURE.png)。
- [实际浏览器验收 JSON](https://github.com/Mrs-zhong1/motion-studio-web/blob/main/stage9/output/STAGE12-GIZMO-RESULT.json)。
- [全部发布门禁记录](https://github.com/Mrs-zhong1/motion-studio-web/blob/main/stage9/output/CI_GATE.txt)。

## 用户实际操作

1. 在 Chrome 等 WebGL2 浏览器打开 Stage 12 的离线编辑器。
2. 依次添加至少两个 GLB 三维章节，各上传 GLB（当前单文件最大 2 MB）。
3. 选中第一个 GLB 章节，在右侧 Stage 11 时间轴启用关键帧路径。
4. 在右侧 Stage 12 面板点击**开启空间 Gizmo**。嵌入的共享 3D 预览会显示实际 Three.js 轨迹、球形控制点和红/绿/蓝的 X/Y/Z 三轴箭头。
5. 选择 X、Y 或 Z 轴及前视/顶视/侧视，再直接在预览中拖动球形节点。拖动仅修改所选轴，不修改关键帧时间和其他轴的值。
6. 选择关键帧后，可调节**曲线手柄强度（张力 0–1）**和七个镜头空间参数。张力影响 Hermite/Bezier 等价三次插值的切线幅度。
7. 预览通过 postMessage 热更新同一个 Three.js Scene，不需要重载场景。保存为 JSON 以便再次编辑；导出的单文件 HTML 采用运行模式，不显示编辑控制点和三轴箭头。

## 最终机器验收数据

全部来自 Ubuntu GitHub Actions Chromium **SwiftShader 软件 WebGL**，不是 Mac 硬件 GPU 数据。

| 检查项 | 实测结果 | 结论 |
|---|---|---|
| CI #42791202200 | success | PASS |
| 原有组件数 | 20/20 | PASS |
| 真实 Three.js WebGL2 | true | PASS |
| 共享场景 | 2 GLB、1 Canvas | PASS |
| 轨迹控制球体 | 3 个 | PASS |
| Three.js 真实三轴 ArrowHelper | 3 个 | PASS |
| 三维曲线采样 | 51 点 | PASS |
| 鼠标 Raycaster 点选/拖动 | 7 次有效拖动 | PASS |
| X 轴约束 | X: 0.8 → 1.76；Y=0、Z=5.5 未改 | PASS |
| 三维观察视角切换 | 前视 → 顶视 | PASS |
| 拖动轴选择 | X → Y | PASS |
| 曲线张力编辑 | 0.75 | PASS |
| JSON 保存与重新导入 | 张力、坐标保留 | PASS |
| 预览热更新 | Stage 11 patch 计数增加，Scene UUID 不变 | PASS |
| 独立导出 | 872,763 bytes，无运行错误 | PASS |
| 导出状态 | 编辑模式关闭，三维辅助控制点不显示 | PASS |
| 浏览器 JS 错误 | 0 | PASS |
| Stage 9/10/11 全部旧门禁 | success | PASS |

## 发现并修复的真实问题

- 早期 Stage12 CI 报红：新增的 `tension` 默认属性在首次创建的 Stage11 关键帧里缺失，导致 JSON 保存前后结构不一致。修复为所有新建关键帧明确写入 tension 默认值；原有保存导入回归恢复通过。
- Stage11 旧二维 SVG 路径在滑块变更时替换整个 SVG，丢失原绑定的拖动监听；现改为只更新 SVG 内部曲线与节点，保留原本的指针事件。
- 增加了显式的三轴 Three.js ArrowHelper 图形，CI 必须实际检测到 3 个辅助箭头，不能仅凭按钮存在就通过。

## 尚未完成 / 不能声称通过

- **Apple Silicon Mac Chrome 的真实硬件 GPU、Safari/macOS 和移动 Safari 均未实测**；本批 GPU 测试是 SwiftShader 软件 WebGL。
- 当前三维 Gizmo 使用**球形控制点 + 明确的轴约束 + 红绿蓝方向箭头**，没有实现 Blender/Three.js TransformControls 那样完整的拖拽旋转环、缩放轨道与多对象编辑。
- 现有三次曲线能调节每个节点的张力，但**没有实现分离式贝塞尔入/出手柄的独立拖动**；目前不是完整的专业动画曲线编辑器。
- 预览为嵌入编辑器的共享真实 Three.js iframe，同一渲染器/Scene 内操作；尚未把整个主编辑器画布替换成独立的专业三维布局。
- 大模型、Draco/KTX2/meshopt 压缩扩展、内存泄漏长时间压力、Mac 的 FPS 与热性能仍未通过生产验收。

**阶段结论：** Stage 12 的空间镜头视口、真实 WebGL 控制点、基本 XYZ Gizmo、张力编辑、实时预览和离线导出已经经过云端浏览器严格验收；产品仍是工程测试版，不能标为商业正式版。
