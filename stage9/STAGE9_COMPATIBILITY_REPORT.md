# Motion Studio Stage 9 · GLB compatibility and rendering regression

**Run:** [GitHub Actions #42738009716](https://github.com/Mrs-zhong1/motion-studio-web/actions/runs/42738009716)

**Verified**: The Stage 9 standalone editor with **20 registered components** builds with pinned Three.js 0.180.0 / GLTFLoader and esbuild. The built page and exported GLB chapter render in cloud Chromium via **SwiftShader software WebGL2**. No native Apple hardware GPU or Safari was tested.

## Actual matrix results

| Test fixture | Materials | Textures | Animation clips | Render frames | Nonblank pixels | Draw time samples (mean; max) | Result |
|---|---:|---:|---:|---:|---:|---:|---|
| Sample-Dual-Material.glb | 2 | 0 | 0 | 6 | 6 | 4.367 ms; 23.7 ms | PASS |
| Sample-Textured-Animated.glb | 1 | 1 | 1 | 6 | 12 | 5.7 ms; 31.7 ms | PASS |

All values above come from `stage9/output/STAGE9-MATRIX-RESULT.json`. They describe draw calls in a synthetic cloud test, **not measured FPS or real Mac GPU performance**. The report's renderer label reads `WebKit WebGL`; the run passes Chromium launch flags enabling software SwiftShader and makes no hardware GPU assertion.

## Additional verified conditions

- Baseline PBR, GLB texture, animation, and scroll-driven transform test: PASS; `gpuAccepted: true`.
- Offline exports requested **zero HTTP(S)** resources in each matrix case.
- No captured JS page errors in either case.
- Mobile editor at viewport width 390 px: document scroll width 390 px, **no horizontal overflow**, all 20 components registered.
- Exported models are tested in a fresh page, not only within the editor.
- Results and actual generated single-file HTML committed to `stage9/output`, because Actions artifact quota was exhausted.

## Scope limitations / release blockers

1. Hardware WebGL2 on Apple Silicon Mac Chrome: **not tested**.
2. Safari desktop and iPhone/iPad: **not tested**.
3. Broader glTF extension/texture compatibility (Draco, KTX2, meshopt, skinning, morph targets, multiple clips, complex multi-MB scenes): **not accepted**.
4. Visual fidelity to premium interactive design references and cross-chapter shared physical 3D scene: **not accepted**.
5. Frame budget / thermal performance on Mac and mobile GPU: **not tested**. SwiftShader draw timings here are diagnostic only.
6. Accessibility, input and scroll edge cases on real devices: **not tested**.

**Verdict**: Stage 9 dual-fixture **software-WebGL compatibility regression passes**. Production GPU/visual release gate remains **NOT READY** pending hardware/Safari and expanded asset tests.
