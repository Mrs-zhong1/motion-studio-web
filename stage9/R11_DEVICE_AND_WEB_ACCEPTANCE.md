# Motion Studio — R9-06 / R11 Browser Acceptance

**Recorded:** 2026-11-15. **Release status:** Review build; not production signoff.

## What was actually changed

- Removed a disposable WebGL2 probe context, preventing an additional GPU context being allocated just for feature detection.
- Added adaptive WebGL2 rendering settings: at <=600px rendered width (or narrow coarse-pointer view), cap device pixel ratio at 1; use a 512px shadow map versus the desktop's 1024px; target a longer render budget on smaller scenes. Desktop pixel ratio capped at 1.5. These are **quality/energy optimizations**, not guaranteed FPS.
- Added a WebGL context-lost listener that visibly falls back to the existing Canvas renderer and records a diagnostic error rather than pretending rendering succeeded.
- Pause continuous WebGL draws when the Three.js canvas is out of view or the tab is hidden, and resume on visibility. Respect `prefers-reduced-motion` by lowering unprompted continuous render frequency while still allowing interactive controls.
- Instrument runtime `window.__motionThreeStatus` with `renderMsAvg`, `renderMsMax`, `estimatedFps`, `pausedFrames`, `visible`, `contextLost`, `reducedMotion`, `quality`, `pixelRatio`, and `frameBudgetMs`.
- Maintain original PBR lighting, parametric curved headphone GLB, shadowed plinth, material and camera presets, native website scroll, standalone export and editor UX.

## Verified CI (software rendering, not physical hardware)

- Source three-browser run [43702699097](https://github.com/Mrs-zhong1/motion-studio-web/actions/runs/43702699097): **Chromium, Firefox, WebKit PASS**.
- `stage9/tests/test_r11_mobile_acceptance.py` generates a real HTML export and renders it at a **390x780 simulated viewport** with `prefers-reduced-motion=reduce` and device scale factor 2 in headless Chromium + SwiftShader. The runtime reports `quality=mobile`, `pixelRatio=1`, reduced motion true, 4 PBR materials, over 10k GLB triangles and an actual rendered frame. Material/camera controls remain actionable.
- The same test deliberately masks the WebGL2 constructor within an isolated browser context; the existing Canvas fallback remains visible, with the WebGL2-unavailable condition recorded.
- Source tests also exercise template browsing, editor, save/open, standalone export, actual 3D scene, eight templates and screenshot generation.
- The evidence gallery now includes `r11-mobile-product.png`, created by the real software WebGL2 browser during the mobile check.

## Important performance limitations

- **No real native-device benchmark.** Software WebGL2 timings/estimated FPS must **not** be presented as performance readings for an Apple M-series GPU, native Safari or a physical phone.
- Software-rendered first frames can be expensive because Three.js materials, shaders, and PMREM are compiled. A single warm-up spike is not a representative smooth-scroll metric. Instrumentation is present for later hardware measurement but hard pass/fail thresholds have not yet been established.
- Simulated mobile in desktop Playwright validates CSS/window conditions and browser controls, not touch latency, Safari WebKit graphics drivers, battery use, thermals, memory pressure or actual mobile hardware.
- The current fallback demonstrates visibility without WebGL2. It is not equivalent to a photorealistic WebGL alternative.
- Visual design approval against reference websites, final photography licenses, and real Safari/mobile QA remain open.

## Live public review

- Complete bundled Three.js export built from the source branch and published to the separate preview repository as `review-preview.html` **commit `fb6f3f7c2aee505773f5f160e94b6eaf3fbde2aa`**.
- Corresponding GitHub Pages native deployment [43703090768](https://github.com/Mrs-zhong1/motion-studio-web-pages/actions/runs/43703090768) PASS.
- Public review deployment workflow [43703091432](https://github.com/Mrs-zhong1/motion-studio-web-pages/actions/runs/43703091432) PASS.
- Live HTTPS and actual bundled WebGL2 template/export smoke [43703091534](https://github.com/Mrs-zhong1/motion-studio-web-pages/actions/runs/43703091534) PASS.
- https://mrs-zhong1.github.io/motion-studio-web-pages/

## R12 release blockers

1. Real Safari/macOS and physical iPhone/Android tests, across low-power graphics and thermals, with representative frame-time/memory budgets.
2. Human art-direction inspection and model/material visual quality review.
3. Individually clear any image/model distribution licensing in reusable templates.
4. Confirm fallback usability and device interaction with a human on representative hardware.
5. Release review: merge only after quality, source, hosted deployment and commercial rights are approved.
