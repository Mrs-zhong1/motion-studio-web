# Motion Studio · Stage 9 共享 Three.js 场景和连续镜头批处理报告

验收日期：2026-11-10

GitHub Actions 完整通过记录：https://github.com/Mrs-zhong1/motion-studio-web/actions/runs/42769051170

## 本批真正实现

1. **多 GLB 导出网页的单一共享 WebGL Canvas**：当工程内包含至少 2 个已经导入的 GLB 章节时，独立 HTML 页面只使用一个共享 Three.js Scene/Renderer/Camera 来承载这些模型；原 3D 章节的 iframe 在导出时变成静态占位，不重复创建 GLB GPU 渲染器。单 GLB 编辑与导出保持旧逻辑，其他 19 类动效组件保持原逻辑。
2. **基于整页滚动位置的连续镜头**：所有已导入模型位于同一 3D 场景；在章节中心点之间采用 smoothstep 插值相机 X 坐标和模型显示权重。切换章节时不销毁 WebGL context，也不重新创建 Scene/Camera。
3. **模型复用、动画与离线打包**：标准 GLB 由 Three.js r180/GLTFLoader 读取，整页嵌入序列化的 Base64 模型和共享 Three.js JS bundle。验证网络请求为 0。
4. **失败降级提示**：当共享上下文丢失，隐藏共享 Canvas 并恢复章节提示。不将模拟丢失测试称为真实硬件失效测试。
5. **持续自动化**：GitHub Actions 新增严格的两模型跨章节场景测试，旧 20 组件/三种 GLB/五种错误文件回归不放宽，通过后持久化产物和结果。

## 实际可复核的测试结果

来源：`stage9/output/STAGE9-SHARED-SCENE-RESULT.json`，CI run `42769051170`。

| 指标 | 值 | 结果 |
|---|---:|---|
| 组件注册 | 20/20 | PASS |
| 多 GLB 章节 | 2 | PASS |
| 共享 WebGL Canvas | 1 | PASS |
| 同一共享 Scene UUID | 不变 | PASS |
| 模型加载数量 | 2 | PASS |
| WebGL2 上下文 | true（云端软件） | PASS |
| 绘制次数 | 30 | PASS |
| 非空像素采样点 | 10 | PASS |
| 相机实际连续位置 | 0 → 0.5039 → 1.6052 → 2.7039 → 3.1397 | PASS |
| 模拟 WebGL 上下文丢失降级 | 画布隐藏 + 章节提示恢复 | PASS |
| 新测试中的脚本异常 | 0 | PASS |
| 导出页面外部网络请求 | 0 | PASS |

原有测试：三类 GLB（双材质、带纹理动画、骨骼 Morph 双动画）**3/3 PASS**，异常 GLB **5/5 PASS**，390px 视口无横向溢出。来源：`stage9/output/STAGE9-MATRIX-RESULT.json`、`STAGE9-INVALID-GLB-RESULT.json`。

## 获取产物

- 主编辑器（离线单 HTML）：`stage9/output/Motion-Studio-Stage9-THREE-OFFLINE.html`
- 已导出的共享场景示范（包含两个真实 GLB）：`stage9/output/STAGE9-SHARED-TWO-GLB-EXPORTED.html`
- 共享场景运行截图：`stage9/output/STAGE9-SHARED-SCENE.png`
- 完整 JSON 验收：`stage9/output/STAGE9-SHARED-SCENE-RESULT.json`
- 构建清单：`stage9/output/BUILD_MANIFEST.json`

## 未达到商业正式版的点

- **编辑器内部不是共享三维场景实时预览**：本批共享场景能力落在“导出后的多 GLB 网页”，编辑器预览仍按章节展示。
- 仅实现相机 X 轴移动及模型渐隐切换，**不是**可任意设定的 6DOF 摄像机曲线、多轨灯光物理动画或商业级镜头编辑。
- 没有真实 Apple Silicon Mac/Chrome GPU/Safari/iPhone 的图形、帧率、温控测试。所有云端 WebGL 数据源于 **Chromium SwiftShader 软件渲染**。
- 模型仍受原有 2 MB 上传限制，Draco/KTX2/meshopt 未单独验收。
- 回退模式在丢失 WebGL 时显示说明，不等于无 GPU 时继续完整 3D 动画。

**结论：** Stage 9 “多 GLB 共享场景 + 连续滚动镜头”云端软件 WebGL 版本完成验收，原有组件及 GLB 兼容性回归仍通过；尚非商业正式版。
