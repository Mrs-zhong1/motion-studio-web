# Motion Studio · Stage 14 剩余工程批处理与发布验收总报告

**最终 CI 运行：** [GitHub Actions #42807275750](https://github.com/Mrs-zhong1/motion-studio-web/actions/runs/42807275750) — `completed / success`

**结论：Stage 9–14 软件验收门禁 12/12 SUCCESS。** 此结论不包含 Apple Silicon 真机硬件 GPU、Safari、内存泄漏或压缩 GLB 生产兼容性；商业正式版发布门禁 **NOT READY**。

## 可获取的实物交付

- [Stage 14 最新版独立离线编辑器](https://github.com/Mrs-zhong1/motion-studio-web/blob/main/stage9/output/Motion-Studio-Stage14-Stability-OFFLINE.html) — 1,740,002 bytes，完整保留 20 组件。
- [3 MB 实际 GLB + 另一模型生成的独立离线网页](https://github.com/Mrs-zhong1/motion-studio-web/blob/main/stage9/output/STAGE14-STRESS-EXPORTED.html) — 5,057,487 bytes。
- [真实云端软件 WebGL 测试截图](https://github.com/Mrs-zhong1/motion-studio-web/blob/main/stage9/output/STAGE14-STRESS-CAPTURE.png)。
- [Stage 14 机器测试数据](https://github.com/Mrs-zhong1/motion-studio-web/blob/main/stage9/output/STAGE14-STRESS-RESULT.json)。
- [全部 12 项测试门禁与 CI 源码 SHA](https://github.com/Mrs-zhong1/motion-studio-web/blob/main/stage9/output/CI_GATE.txt)。
- [无需安装的 Mac/Safari 实机 GPU 诊断页](https://github.com/Mrs-zhong1/motion-studio-web/blob/main/Mac-Safari-GPU-Diagnostic.html)。

## 这一批真正开发和修复的内容

1. **精度改进：** Stage 12/13 的三维拖拽从固定的“每像素多少世界单位”改为基于当前摄像机投影与轴向在屏幕上导数的位移求解，并对朝向摄像机的退化轴提供安全回退；原有球体选择、XYZ 约束、入/出贝塞尔控制柄仍通过回归。
2. **撤销/重做验收：** 重用工程已有的历史栈，真实浏览器测出贝塞尔 Y 偏移 `1.3 → null → 1.3`，无需新增另一套冲突的 Undo/Redo 实现。
3. **4 MB GLB：** 统一导入、预览和项目归一化的限制。原本仅上传处提高大小、而工程读取仍按旧 2 MB 限制，造成撤销后无声删除模型；已根据测试失败定位并修复。3,145,728-byte 标准 GLB 能在共享场景最终导出并加载。
4. **明确扩展能力边界：** 需要 `KHR_draco_mesh_compression`、`EXT_meshopt_compression`、`KHR_texture_basisu` 的文件会得到不支持该离线解码器的明确错误提示，不默默声称可加载；超过 4 MB 的输入正确拒绝且不覆盖原模型。
5. **共享 WebGL 压力回归：** 反复滚动、窗口大小改变后，同一个 WebGL2 Canvas / 两份模型维持运行。总计 134 次绘制，`contextLost=false`、`error=null`。
6. **CI 仓库写回：** 解决历史流程在远端 `main` 更新时 rebase 与 `CI_GATE.txt` 冲突；改为获取最新远端索引、只暂存生成文件并带上限重试。最终运行成功把 HTML 和 JSON 证据写入 GitHub。

## 最终真实数据（GitHub Actions Ubuntu Chromium + SwiftShader 软件渲染）

| 项目 | 实测 |
|---|---|
| Actions #42807275750 | success |
| Stage 9–14 门禁 | 12/12 success |
| 原有组件 | 20 |
| 合规较大 GLB | 3,145,728 bytes，导入成功 |
| Draco / KTX2 / meshopt 必需扩展 | 明确拒绝，旧模型保留 |
| 超过 4 MB 文件 | 拒绝，旧模型保留 |
| Camera Undo | 1.3 → null |
| Camera Redo | null → 1.3 |
| 双模型共享场景 | 2 模型，1 Canvas，WebGL2=true |
| 滚动 / 尺寸变化压力回归 | 134 帧，contextLost=false |
| 生成独立网页 | 5,057,487 bytes |
| 测试捕获错误 | 0 |

## 生产发布尚需真实验收

- **Apple Silicon Mac Chrome / Safari：尚未执行。** 用户需要在自己的 Mac 上分别打开根目录 `Mac-Safari-GPU-Diagnostic.html`，点击“开始 GPU 渲染测试”，保存两份 JSON。此工具不自动上传信息。该基础测试仍无法单独证明具体 GPU 加速和复杂模型性能。
- **移动 Safari / 多浏览器触控：未验收。** 需要 iPhone/iPad 或设备实验室。
- **GPU 长时稳定性、内存泄漏 / 大型场景：未证明。** 134 次同步绘制不是持续数小时运行，不能替代真实内存/功耗压力测试。
- **压缩 GLB 生产兼容性：未开发解码器。** Draco/KTX2/meshopt 是拒绝提示，而非支持。需要离线 WASM/解码器打包与各自真实模型测试后才能标记支持。
- **最终视觉品质：未达商业发布门槛。** 需要以真实设计参考逐章节进行人工视觉验收、鼠标/滚动体验、GPU 性能和无障碍验证。
- **Mac .dmg 安装包：未制作。** 当前成果是无需安装即可使用的离线 HTML；不能称为已交付 macOS 原生安装包。

**总体状态：工程软件验收 SUCCESS，设备/生产发布门禁 NOT READY。** 阻碍不再是云端脚本是否能构建，而是实际硬件执行、压缩格式支持、视觉品质和长期性能验证。该状态不应被误报为完整商业正式版完成。
