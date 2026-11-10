# Motion Studio · Stage 13 独立贝塞尔入/出手柄与 Mac 实机验收工具

**最终云端 CI：** [GitHub Actions #42793251430](https://github.com/Mrs-zhong1/motion-studio-web/actions/runs/42793251430) — `success`

## 本批交付
- [Stage 13 完整离线 HTML 编辑器](https://github.com/Mrs-zhong1/motion-studio-web/blob/main/stage9/output/Motion-Studio-Stage13-Bezier-OFFLINE.html)（1,738,744 bytes）
- [带独立贝塞尔镜头路径的导出 HTML 示例](https://github.com/Mrs-zhong1/motion-studio-web/blob/main/stage9/output/STAGE13-BEZIER-EXPORTED.html)（874,955 bytes）
- [Stage 13 可恢复 JSON 工程](https://github.com/Mrs-zhong1/motion-studio-web/blob/main/stage9/output/STAGE13-BEZIER-PROJECT.json)
- [真实浏览器截图](https://github.com/Mrs-zhong1/motion-studio-web/blob/main/stage9/output/STAGE13-BEZIER-CAPTURE.png)
- [机器验收 JSON](https://github.com/Mrs-zhong1/motion-studio-web/blob/main/stage9/output/STAGE13-BEZIER-RESULT.json)
- [11 项 CI 门禁](https://github.com/Mrs-zhong1/motion-studio-web/blob/main/stage9/output/CI_GATE.txt)
- [Mac / Safari 离线 WebGL2 诊断页](https://github.com/Mrs-zhong1/motion-studio-web/blob/main/Mac-Safari-GPU-Diagnostic.html)

## 功能变化
- 保留原有 20 个组件、GLB 上传/导出、Stage 9–12 共享 3D 编辑能力。
- Stage 11 相机关键帧新增彼此独立的 `handleIn` / `handleOut` 控制偏移，分别存储 X/Y/Z；支持数值编辑、重置与 JSON 保存。
- 三次 Bézier 曲线依据每段前一关键帧的出手柄与后一关键帧的入手柄计算；缺失时自动沿用原有 Hermite 平滑切线，从而支持旧工程。
- Stage 12 的真实 Three.js 共享视口增加 4 个可 Raycaster 选中的贝塞尔控制球体（3 帧时只显示有效的入/出手柄）、与关键帧连接的可见控制线；鼠标可根据当前选择轴 X/Y/Z 拖动独立手柄。
- 变更通过已有的消息桥实时写回 JSON 工程，不重建共享 WebGL Scene；导出的叙事网页默认隐藏所有编辑辅助线。
- 在 GitHub Actions 的 CI 最后写回文件时增加 `git fetch`、`git rebase` 与最多 3 次安全重试，解决其他提交先行进入 main 时的推送拒绝。

## 真实验收（Ubuntu Chromium + SwiftShader 软件 WebGL）
| 项目 | 实际结果 | 结论 |
|---|---|---|
| GitHub Actions #42793251430 | completed / success | 通过 |
| CI 门禁 | 11/11 success | 通过 |
| 保留组件 | 20/20 | 通过 |
| WebGL2 与独立 GLB | WebGL2=true，2 个模型，1 个共享 Canvas | 通过 |
| 真实三维入/出手柄 | 4 个 | 通过 |
| Raycaster + 鼠标拖动 | 7 次有效移动 | 通过 |
| 中间帧出手柄 X | 1.65 | 通过 |
| 同一帧入手柄 Y | 1.6，独立于出手柄 | 通过 |
| 保存 / 重新导入 | X=1.65、Y=1.6 保留 | 通过 |
| 导出独立 HTML | 874,955 bytes，WebGL2=true，2 个模型 | 通过 |
| 导出页面 Gizmo | 关闭（不显示编辑辅助线） | 通过 |
| 运行时异常 | 0 | 通过 |
| 旧 Stage 9/10/11/12 验收 | 全部 success | 通过 |

曲线单元测试还确认：分别修改入手柄和出手柄，会改变不同路段的空间摄像机轨迹，不只是保存参数。

## Mac/Safari 实机诊断

打开仓库根目录的 `Mac-Safari-GPU-Diagnostic.html`，分别用 **Mac Chrome** 和 **Mac Safari** 本机打开，点击“开始 GPU 渲染测试”，完成后下载 JSON 报告。该页面在浏览器本地测试 WebGL2 着色器、100 帧渲染、读取非空像素，并保留浏览器设备信息；**不会自动上传报告**。需将两个 JSON 报告用于后续生产验收。

**特别注意：** 这个页面仅提供实机验证工具，尚未在用户 Mac 上执行。WebGL2 成功也不能单独证明原生硬件加速或大型 GLB 性能。

## 尚未完成
- Apple Silicon Mac 的真实 Chrome/Safari 硬件 GPU 验收、移动 Safari、长时间渲染稳定性、FPS、显存与温控数据。
- 仍是浏览器内嵌的 Three.js 视口，不是完整 Blender/专业 NLE；没有完整旋转环、多对象编辑、曲线碰撞避障、Undo/Redo 的全部专业行为。
- Draco/KTX2/meshopt 与大型 GLB（原上传上限 2 MB）未通过正式兼容性测试。
- 控制点的屏幕拖动采用轴向位移约束和固定步进比例，没有精确到透视投影几何的统一世界坐标拖拽校正；复杂编辑精度仍需实机测试。

**结论：** Stage 13 的“独立入/出贝塞尔控制柄 + 真实 WebGL 拖动 + JSON/导出链路”已通过云端严格软件 WebGL 门禁，可作为下一轮开发基线；Mac/Safari 真实硬件门禁仍未完成，不可称为商业正式版。
