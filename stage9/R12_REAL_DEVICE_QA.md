# R12-04 / R12-05 · Real-device acceptance runbook

**Not executed as real-device QA in this batch.** CI's headless WebKit is not a substitute for native Safari; SwiftShader is not an Apple/phone GPU.

## Test matrix
| Device | Browser | What to test | Result |
|---|---|---|---|
| macOS Apple Silicon | native Safari (current) | homepage, eight previews, edit/export, 3D and fallback, reduced motion | NOT TESTED |
| macOS Apple Silicon | native Chrome (current) | WebGL hardware renderer, PBR/GLB, frame pacing and context recovery | NOT TESTED |
| physical iPhone | iOS Safari | touch gestures, page scrolling, preview sizing, editor usability | NOT TESTED |
| physical Android | Chrome | touch gestures, scrolling, native WebGL fallback and scene performance | NOT TESTED |
| no-WebGL2 / forced context loss | supported browser/device | user can still navigate gallery, read content and export | CI simulated only |

## Evidence per execution
Capture device model, OS/browser version, software build SHA, **hardware GL renderer** (not SwiftShader), test date, continuous 30-minute interaction log, memory behavior, approximate frame pacing with instrumentation, visible screenshots/video, observed defects, and tester signoff.

Use `window.__motionThreeStatus` for diagnostics: quality, pixelRatio, contextLost, renderMsAvg, renderMsMax, estimatedFps, pausedFrames, reducedMotion, visible. Note that estimatedFps is approximate, not a hardware benchmark.

### Workflow
1. Start with review URL and document exact deployed commit; do not assume newest source = deployed binary.
2. Exercise all eight gallery previews, close/open, edit content/images, save/reopen, export and open exported HTML.
3. Check touch scroll + responsive navigation on physical phones, especially preview/iframe scrolling.
4. Use 3D Product template; rotate, choose materials and camera presets; check fallback by disabling WebGL or triggering lost context.
5. Observe 30-minute active scene with repeat scroll and interaction. Save raw readings and failure timeline; no preapproved numeric performance targets currently exist, so **do not label performance PASS from the instrumented values alone**.
6. Perform visual assessment side-by-side with motion reference examples. If inadequate, keep release HOLD and send specific defects back to the design queue.

## Release decision
Keep PR #1 draft until actual hardware evidence, approved performance thresholds, eight-template creative review and itemized media rights all exist. No unattended CI may attest to human signoff.
