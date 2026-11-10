# Motion Studio · Stage 9 Three.js offline CI

This is the **Stage 9 (20 components)** editor, separate from the earlier R11 build at repository root.

On push, .github/workflows/stage9-three-offline.yml installs pinned Three.js + esbuild in GitHub Actions, bundles GLTFLoader/PBR/AnimationMixer into a self-contained Stage 9 HTML and uploads it as an Actions artifact. A second job tests actual canvas pixels and a textured animated GLB using software WebGL (SwiftShader). Hardware Apple GPU and Safari still require separate device validation.

**Source root:** stage9/Motion-Studio-Unified-Editor.html

**Build artifact:** Motion-Studio-Stage9-THREE-OFFLINE.html

**Acceptance:** stage9/STAGE9-THREE-BROWSER-RESULT.json (must have gpuAccepted=true). Green software-WebGL CI is *not* hardware-GPU acceptance.

The sample is restored from Sample-Textured-Animated.glb already tracked in the repository root.

The standalone editor/export is designed not to depend on runtime CDNs. See artifact manifests and raw logs for proof.

## Reproduce
Run from stage9/:
```
npm install --no-audit --no-fund
npm run build
python3 tests/check_build.py
python3 tests/test_browser.py
```
