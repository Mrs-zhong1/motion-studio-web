# Motion Studio Web R14

## Open without installation

- `Motion-Studio-Editor.html`: standalone offline editor. Its **Canvas** 3D path works without the Three.js bundle.
- `ORBIT-R11-editor-export.html`: editable-template output from the browser regression test.
- `GPU-3D-Check.html`: check WebGL capabilities on your own machine.

## Three.js offline build on a network-enabled computer / GitHub Actions

This package does **not** contain the built Three.js offline editor. To produce one, a network-enabled environment must install packages pinned in `package.json` and run `npm run build:offline`.

The repository includes `.github/workflows/build-web-offline.yml`, which installs dependencies, builds, runs tests and uploads artifacts. A dedicated repository must contain the unpacked project files, including hidden `.github/workflows/` directory. On GitHub, use the repository's **Actions** tab, select **Motion Studio - offline Three.js Web validation**, then **Run workflow**. Check the job logs and the artifact named `motion-studio-web-offline-validation`.

**Important:** a red CI status for the strict PBR test is a genuine failed/missing proof, not permission to distribute this as a verified PBR build. Even a passing SwiftShader test does not substitute for real GPU/Safari visual acceptance.

## Local automated checks

`python test_r14_instrumentation.py` verifies test/renderer telemetry data compatibility. `python test_r13_contract.py` checks project contracts. `python test_r11.py` runs headless browser editing/export regression. `python test_gpu_pbr.py` intentionally exits nonzero if there is no offline Three editor and WebGL runtime.

`diagnose-registry.py` reports DNS resolution on the *machine executing it*. It cannot change DNS configuration and is not a test of your own Mac unless run there.

See `R14_REPORT.md` and `R12_RELEASE_GATE.json` for complete release limitations.
