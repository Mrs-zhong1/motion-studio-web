# Motion Studio — R9 Three.js product studio, batch 1

**Scope:** Web-only, offline-bundled Three.js 0.180.0. This document covers a demonstrated, interactive product *studio scene*, not a final photorealistic asset.

## Changed source
- `three-scene-entry.js`: retained actual `GLTFLoader` and glTF PBR standard materials. Replaced basic ambient + two direct lights with a hemisphere light, warm shadow-casting key, cool fill, rim and a low bounce. ACES tone mapping and sRGB output are preserved.
- Scene stages the model above an original circular product plinth, accent ring and shadow-receiving floor. Three.js `PCFSoftShadowMap` is enabled for the stage.
- The Three.js canvas now takes pointer input. Drag to orbit the object, double-click to reset, and use Ctrl/Command + wheel to change viewing distance. **Ordinary mouse wheel scrolling remains available.**
- Drag orientation persists while scroll-linked rotation progresses; it is not immediately overwritten by the next render frame.
- Additional status fields allow inspection: `studioLighting`, `shadowEnabled`, `studioMeshes`, `modelTriangles`, `dragMoves`, `dragYaw`, `dragPitch`, `zoom`.

## Automated checks
- New `tests/test_r9_studio_3d.py` opens `Motion-Studio-Stage15-Meshopt-OFFLINE.html`, creates a real Product template, exports the standalone HTML and opens that export in headless Chromium.
- It checks the actual Three.js WebGL2 renderer runs, at least 2 model materials are recognized as PBR-capable, all three studio scene decorations exist, scene shadow support is enabled, GLB geometry is parsed, render frames advance and pointer drag changes the orientation.
- Network requests from the exported page are monitored. The test uses SwiftShader software WebGL2 and **is not proof of native GPU hardware performance**.
- Captured scene and full-page screenshots are published in `visual-evidence/README.md` only when the full CI/screenshot persistence workflow succeeds.

## Boundaries
- A flag indicating `pbr: true` confirms glTF standard/physical materials were loaded, **not** proof of photorealism or full image-based lighting. No commercial-grade environment maps, detailed geometry or authored texture sets have yet been installed.
- The default headphone-form GLB is an original low-poly demonstrator from the prior R4 phase. Its approximate geometry, faceted form and surface quality are not final product designs.
- The separate public `motion-studio-web-pages` repo currently distributes **the unbundled editor**. R9 is implemented in the **offline bundled Three.js engine**. Copying `Motion-Studio-Unified-Editor.html` alone does **not** publish this new Three.js scene to the live website.
- Native Safari, real mobile devices, GPU memory stability, material fidelity and subjective art-direction signoff remain open.
- Do not merge to production while those gates or public deployment are unresolved.

## Next R9 batch
1. Replace the demonstrator with a legitimately redistributable, properly modelled GLB and include any normal/roughness/albedo maps locally.
2. Add image-based lighting (locally bundled HDR/environment), measured performance budgets and visible controls for lighting/material selections.
3. Resolve how the **offline bundled** renderer is deployed as a real online browser preview, without requiring a Mac installer.
4. Compare actual screenshots and drag/scroll recordings with reference-quality product showcase pages, then iterate the scene.
