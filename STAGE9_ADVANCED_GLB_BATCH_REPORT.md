# Motion Studio Stage 9 — Advanced GLB & Failure Recovery Batch

**验收流水线**：https://github.com/Mrs-zhong1/motion-studio-web/actions/runs/42741605979

**本批状态：云端软件 WebGL 回归通过；真实 Apple Silicon GPU / Safari 尚未验收。**

## 交付

- 完整 Three.js r180 + GLTFLoader 离线编辑器：`stage9/output/Motion-Studio-Stage9-THREE-OFFLINE.html`
- 三种 GLB 的真实渲染矩阵：`stage9/output/STAGE9-MATRIX-RESULT.json`
- 五种错误输入与项目恢复：`stage9/output/STAGE9-INVALID-GLB-RESULT.json`
- 浏览器图形烟雾验收：`stage9/output/STAGE9-THREE-BROWSER-RESULT.json`
- 生成实际导出页面和截图：`stage9/output/STAGE9-Sample-*-EXPORTED.html`，`stage9/output/STAGE9-Sample-*-CAPTURE.png`
- CI 配置：`.github/workflows/stage9-three-offline.yml`

## 实测结果

| 验收样本 | WebGL2 | PBR | 网格 | 骨骼 | Morph | 动画片段 | 真实变换/像素 | 结果 |
|---|---|---|---:|---:|---:|---:|---|---|
| 双材质 GLB | PASS | PASS | 2 | 0 | 0 | 0 | 6 帧、非空像素 | PASS |
| 贴图旋转 GLB | PASS | PASS | 1 | 0 | 0 | 1 | 纹理和旋转变化 | PASS |
| 两骨骼 + Morph + 双动画 GLB | PASS | PASS | 1 | 2 | 1 | 2 | 骨骼四元数、Morph 权重变化，6 帧渲染 | PASS |

5 项异常模型输入：空文件、无效文件头、JSON 损坏、引用外部文件、超过 2 MB — **全部拒绝；原工程模型未被覆盖；恢复导出通过**。

原有 20 个组件仍在；移动端 390px 视口无横向滚动；测试模型导出页面未访问外部 HTTP(S) 资源。CI 写回冲突通过并发控制避免。

## 重要界限

1. 使用 GitHub Actions Ubuntu Chromium + **SwiftShader 软件 WebGL2**，不代表真实 Mac Apple Silicon GPU 帧率或热性能。
2. 只通过了生成的小型规范 GLB：不能据此承诺支持 Draco、KTX2、meshopt、复杂纹理、多个蒙皮、较大模型（目前上传上限 2 MB）或其他异常扩展。
3. `BUILD_MANIFEST.json` 中 `gpuTested:false` 是构建时生成的静态字段；实际云端软件 WebGL 证据以 **CI_GATE.txt** 和上述浏览器 JSON 为准。
4. 独立 iframe 模型渲染仍未变成全站共享 Three.js 场景；正式视觉验收、Safari 和真实手机尚未完成。
5. 不能据此称为商业正式版。

**下一批优先**：Mac/Safari 本机诊断与回传 → 压缩格式兼容性/加载失败界面 → 共享 3D 场景和跨章节连续镜头。
