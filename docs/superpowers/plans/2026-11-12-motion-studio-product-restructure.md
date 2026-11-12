# Motion Studio Product Restructure Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship a template-first Motion Studio with eight real templates, immersive previews, a persistent three-pane editor, and verified offline export.

**Architecture:** Keep the existing single-file editor and renderer. Add a discovery shell and normalized template catalog around the current composition model, then reshape the editor DOM/CSS while retaining existing section, layer, camera, GLB, persistence, and export functions. Generate preview and export from the same `exportDocument()` path.

**Tech Stack:** Vanilla HTML/CSS/JavaScript, pinned Three.js r180 injected by esbuild, Python Playwright E2E, GitHub Actions and GitHub Pages.

**Spec:** `docs/superpowers/specs/2026-11-12-motion-studio-product-restructure-design.md`

## Global Constraints

- Preserve the 20-item component registry and all current project JSON, layer, camera, GLB/PBR, timeline, and offline export behavior.
- Preview and export must share the production renderer; no screenshot previews or inert controls.
- Keep the release reversible until browser gates pass.
- Do not claim native Safari, real Apple GPU, or real-device performance from Playwright WebKit.

## Review Focus

- Existing saved projects without `templateId` must still load and export.
- Previewing a template must not overwrite the current draft before “使用此模板”.
- Simple mode must hide advanced controls without deleting project data.
- Sidebars and timeline must remain operable at 1280×800 and collapse safely on narrow screens.
- Every template must export without remote requests or page errors.

---

### Task 1: Template catalog and immersive preview

**Files:**
- Modify: `stage9/Motion-Studio-Unified-Editor.html`
- Test: `stage9/tests/test_product_restructure.py`

**Interfaces:**
- Produces: `templateCatalog`, `createProjectFromTemplate(id)`, `previewTemplate(id)`, `useTemplate(id)` and preview toolbar DOM IDs.

- [ ] Write Playwright assertions for the default discovery view, eight cards, real renderer iframe, device switch, replay, close, and use-template flow.
- [ ] Run the test and verify it fails because the discovery DOM does not exist.
- [ ] Add the catalog, distinct project definitions, discovery page, and preview overlay.
- [ ] Generate preview `srcdoc` through `exportDocument()` using a temporary project object and restore editor state afterward.
- [ ] Run the focused test and verify it passes.
- [ ] Commit the catalog and preview slice.

### Task 2: Three-pane editor and asset hierarchy

**Files:**
- Modify: `stage9/Motion-Studio-Unified-Editor.html`
- Test: `stage9/tests/test_product_restructure.py`

**Interfaces:**
- Consumes: `createProjectFromTemplate(id)` and existing `render()`.
- Produces: `renderChapterList()`, asset tier tabs, simple/pro mode, canvas zoom/fullscreen/panel controls, and timeline collapse controls.

- [ ] Extend E2E assertions for independently scrolling panes, chapter thumbnails, L1/L2/L3 asset tabs, mode switching, canvas controls, and timeline collapse.
- [ ] Run the focused test and verify the editor assertions fail.
- [ ] Restructure the editor markup and targeted CSS without rewriting the renderer.
- [ ] Populate chapter thumbnails from project sections and bind click/drag reorder.
- [ ] Bind mode, zoom, fullscreen, panel and timeline controls.
- [ ] Run the focused test and existing Chromium product journey.
- [ ] Commit the editor workspace slice.

### Task 3: Persistence, export, and all-template coverage

**Files:**
- Modify: `stage9/Motion-Studio-Unified-Editor.html`
- Modify: `stage9/tests/test_web_product_e2e.py`
- Test: `stage9/tests/test_product_restructure.py`

**Interfaces:**
- Consumes: `templateCatalog`, `createProjectFromTemplate`, existing `loadProject` and `exportDocument`.
- Produces: optional `project.templateId` compatibility and `window.MotionStudioUnified.templates/useTemplate` test surface.

- [ ] Add failing assertions that all eight template IDs create non-empty, distinct projects and survive JSON/export round trips.
- [ ] Preserve optional `templateId` during normalization while accepting legacy projects.
- [ ] Update the legacy product journey to enter the editor through the discovery flow.
- [ ] Build the offline editor and run both Playwright suites in Chromium.
- [ ] Commit persistence and regression coverage.

### Task 4: Cross-browser release gate and deployment

**Files:**
- Modify: `.github/workflows/web-product-e2e.yml`
- Modify: `.github/workflows/web-release-pages.yml`
- Regenerate: `stage9/output/Motion-Studio-Stage15-Meshopt-OFFLINE.html`
- Regenerate: `stage9/output/BUILD_MANIFEST.json`

**Interfaces:**
- Consumes: browser-tested offline artifact.
- Produces: GitHub Actions run and published GitHub Pages release manifest.

- [ ] Install local Playwright Firefox and WebKit engines.
- [ ] Run build verification, product E2E, and product restructure E2E in Chromium, Firefox, and WebKit.
- [ ] Run the existing Three.js/GLB regression suite in Chromium.
- [ ] Update workflow path filters and release steps to execute the new product suite.
- [ ] Commit and push the tested candidate.
- [ ] Monitor CI to completion, fix any failing gate, and only then publish/update the Pages repository.
- [ ] Verify the live URL, release manifest SHA, save/export journey, and capture discovery/preview/editor screenshots.

## Self-review

The plan covers R1 discovery/preview, R2 editor usability, the eight L1 templates plus L2/L3 assets, renderer sharing, compatibility, three engines, release safety, and live evidence. Interfaces remain in the existing single-file architecture to avoid a speculative framework migration.
