# R12 — Final release readiness gate

**Status: BLOCKED — review build only (2026-11-15).** This document does not grant production approval.

## Source and actual prior evidence
- Source review PR: https://github.com/Mrs-zhong1/motion-studio-web/pull/1 (draft, unmerged).
- Source browser E2E, software GL tests: https://github.com/Mrs-zhong1/motion-studio-web/actions/runs/43702699097 (Chromium/Firefox/WebKit PASS).
- Public review deployment: https://mrs-zhong1.github.io/motion-studio-web-pages/
- Pages live smoke reported passing: https://github.com/Mrs-zhong1/motion-studio-web-pages/actions/runs/43703091534
- Existing detailed limitations: [R11](R11_DEVICE_AND_WEB_ACCEPTANCE.md), [R9](R9_3D_ACCEPTANCE.md).
- The tests above used headless software WebGL and simulated mobile; **not native Safari or hardware GPU certification**.

## Release blocks, all mandatory
1. **Current-SHA CI:** all template, save/edit/export, offline Three.js, PBR/GLB, fallback and 3-browser regression passes for exact candidate commit.
2. **Deployment:** live HTTPS Pages smoke with editor + preview + standalone 3D export against the same candidate.
3. **Native macOS Safari:** actual macOS Safari hands-on UX, visual and fallback evidence.
4. **Physical mobile:** iPhone and Android real touch/scroll/responsive behavior checks.
5. **Hardware GPU:** at least 30-minute representative live-use test documenting frame pacing, memory, context loss and thermal behavior; thresholds should be approved before testing, not invented retrospectively.
6. **Design:** human art-direction review of homepage, all eight templates, meaningful internal sections, template preview, editorial hierarchy, and original 3D asset/material fidelity against quality references.
7. **Rights:** asset-by-asset provenance and permitted commercial redistribution for photographs, models, fonts and reusable template media.

## Machine-readable control
`python3 stage9/check_r12_release.py --evidence stage9/R12_RELEASE_EVIDENCE.json`

The checker **fails closed** for absent/unverified gates, missing reviewer/evidence URL, and evidence linked to a different release SHA. A pass means *metadata completeness only*, not authenticity; reviewers must inspect the referenced proof. Do not invent a PASS file to bypass blockers.

## Decision
Keep PR #1 in draft and keep the hosted site designated **public review**, not production. Do not merge until all seven evidence categories are independently approved and their source commit matches. If visual signoff fails, return to visual refinements instead of marking it complete.
