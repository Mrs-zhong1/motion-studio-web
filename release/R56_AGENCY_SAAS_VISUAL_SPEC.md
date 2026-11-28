# R56.2 — Agency + SaaS flagship visual specifications

Baseline: PR #4 head b9e73693c4ab538f657282149679c797d7f875df (pre-R56.3 product correction baseline)  
Design constraints: R43/R44/R45/R46 remain binding. These are implementation specifications, not approval claims.

## Creative Agency — Project Index / Case Story

### Art direction

- A bold independent creative studio, not a generic corporate agency landing page.
- Use oversized editorial typography, asymmetric project framing, full-bleed case media, sharp alignment changes and one controlled high-chroma accent. Let each case have its own art-directed color/material treatment while retaining a coherent studio shell.
- The opening hero must use the source template's authored headline and primary media. Never inject a second hero title, duplicate status line or second navigation row.

### First-screen hierarchy

1. Studio identity and one concise point of view.
2. One unmistakable primary campaign/portfolio image or scene.
3. A compact project index with case number, project name and a clear selected state; it must not cover the main image or compete with the hero headline.
4. A single inquiry/contact path.

### Narrative and interaction

- Five case chapters, each with a distinct visual treatment and a concise role/outcome line.
- Project-index hover previews selection; click and keyboard activation navigate to the corresponding real chapter. Selection state follows scroll/navigation.
- The first chapter is the hero; do not create a redundant second intro section.
- Each chapter's media region must have a valid loaded asset, canvas or explicitly documented intentional graphic treatment. A dark rectangle without content or design purpose is a defect.

### Responsive / accessible behavior

- Desktop: asymmetric, wide composition with the index integrated into the page rhythm; no fixed editor sidebar.
- Mobile: one-column hero and a two-column project index; 44px minimum touch targets; selected case remains visible; no horizontal overflow.
- Keyboard focus is visible; reduced-motion disables parallax/scroll choreography but preserves all case navigation and content.

### User-editable controls

- Studio name, hero statement, accent color, case titles, case descriptions, case media, chapter order, CTA label and destination.
- Controls modify the real scene content and survive save → reopen → standalone HTML export.

### Explicit anti-patterns

- Duplicate hero text or status/navigation copy.
- Generic cards replacing full-bleed case storytelling.
- Five identical image/title blocks with only different copy.
- Dark empty media slots, placeholder images represented as final assets, or case buttons that do not navigate.

### Observable acceptance

- At 1440×900, the first viewport shows one clear hero, one primary media subject and an unobstructed project index entry point.
- At 390×844 and 360×800, no title/index overlap, no clipped CTA, two-column case index, no horizontal scroll.
- All five case entries navigate to their matching sections; selected state updates; browser console has no uncaught errors.

## SaaS — Capture → Shape → Deliver

### Art direction

- A product-led digital workspace: precise, calm, confident and data-literate. Use a light, warm neutral canvas for explanation and a deep, high-contrast product stage for the actual UI demonstration; one restrained signal accent communicates progress and action.
- Keep the product UI visually dominant. Use typography, alignment and spacing to communicate hierarchy; avoid decorative glass panels that obscure product information.

### First-screen hierarchy

1. A plain-language outcome statement that says what the product helps users accomplish.
2. A short supporting sentence naming the user/job and expected result.
3. One primary action.
4. A real interactive product surface visible without scrolling on desktop; on mobile it follows the value proposition immediately.

### Workflow narrative and interaction

- Three real states: Capture (incoming signals), Shape (grouping/prioritization/ownership), Deliver (review/release/share).
- Selecting a step updates title, supporting explanation, product UI state, progress indicator and next action. The selected state must be programmatically exposed (aria-selected/aria-pressed).
- The final state offers a meaningful completion/next action; it must not be a dead-end decorative label.
- Supporting chapters explain integrations, outcomes, trust/security or use cases; do not repeat the same dark empty panel beside each image.

### Responsive / accessible behavior

- Desktop: explanation and product UI may form one balanced composition inside the workflow module; avoid a permanent editor split view.
- Mobile: explanation, tabs and product stage stack vertically; tabs wrap or scroll without clipping; 44px minimum targets; no horizontal overflow.
- Reduced-motion preserves step state changes without animated transitions. Keyboard users can reach and activate all steps.

### User-editable controls

- Product name, value proposition, supporting copy, workflow step names/descriptions, demo content/state labels, progress state, accent color, feature chapters, CTA label and destination.
- Save/reopen/export must preserve current content and workflow interactions.

### Explicit anti-patterns

- Static dashboard screenshot presented as an interactive demo.
- Tabs that change only their selected styling while product state remains unchanged.
- Multiple competing CTAs or unexplained metrics.
- Repeated blank/near-black rectangles beside media; intentional dark product surfaces must contain visible UI content and have an explicit role.

### Observable acceptance

- At 1440×900, product outcome, primary CTA and a substantial portion of the interactive product stage are visible.
- At 390×844 and 360×800, tabs remain usable, product stage is not clipped, and no horizontal scroll occurs.
- Capture → Shape → Deliver each changes the actual title, description, demo content and progress; all three states work by pointer, touch and keyboard.

## Shared product-quality and export gates

- Preserve single-canvas preview (R44); no permanent left navigation rail + right preview split.
- Preserve eight distinct template scene compositions (R45); Agency and SaaS must be visibly distinct.
- Preserve focus visibility, 44px touch targets, reduced-motion and safe-area behavior in editor and exported HTML (R46).
- Test the actual standalone HTML produced by exportDocument(), not only editor preview.
- Run Chromium, Firefox and WebKit round-trip tests. Capture desktop and mobile screenshots against the exact commit SHA.
- Report functionality, visual evidence completeness, rights, physical-device and live-deployment gates separately. CI cannot grant human visual or legal approval.


## 2026-11-28 implementation audit — open acceptance gaps

- **R50 capture harness:** the 2026-11-27 run failed before it could produce page-level evidence. The exact error was Playwright `Locator.screenshot` timing out while waiting for the animated child iframe `body` bounding box to become stable. This is a capture-harness failure, not proof that the exported page is blank. The capture path is being changed to a parent-page viewport clip of the live iframe; new screenshots must be inspected before any visual conclusion.
- **Agency project index placement:** R43 inserts the index after the first chapter while R45 positions it against the page container. The latest failed R50 run did not capture the parent page, so first-screen placement is not yet visually verified. Do not move or restyle it based on the child-frame screenshot alone.
- **SaaS product-stage depth:** the current R43 workflow changes its title, explanatory copy, one text card and progress percentage across Capture / Shape / Deliver. That is a valid stateful interaction smoke, but it is not yet a convincing task-level product UI. R56.3 remains HOLD until the stage presents a real, coherent illustrative product surface whose content, ownership/priority and release state visibly change with each step.
- The current R50 and R43/R45/R46 automated contracts are not human art-direction approval. The actual editor/export parity and Chromium/Firefox/WebKit runs must be tied to the exact new head SHA; human visual approval remains a separate gate.


## 2026-11-28 exported-page defect audit and R56.3 correction batch

The following defects were observed in the actual exported HTML on base SHA b9e73693c4ab538f657282149679c797d7f875df, not inferred from editor preview:

### Agency — project index placement

- The exported DOM inserted .r43-agency-index immediately after the first case section, but R45 CSS absolutely positioned it against the entire .page container with bottom:6vh.
- The 1440px and 390px full-page screenshots therefore placed the project index at the end of the final chapter, where it competed with the closing headline/CTA. It was not a first-chapter index.
- R56.3 removes the page-bottom absolute positioning. The index returns to normal document flow between case 01 and case 02, retaining five desktop columns, two mobile columns, visible selected state and the existing click/keyboard/scroll-follow behavior.
- R50 now asserts that the index lies between the first and second chapter boxes and that the opening screenshot is taken after an explicit scroll-to-top. This removes the overlap defect and the mislabeled-last-chapter screenshot.
- Remaining design review: the index is immediately after the hero chapter rather than above the hero headline in the initial viewport. It no longer covers media or the closing CTA, but the exact first-screen hierarchy still needs human art-direction approval.

### SaaS — product stage was only a dark card

- The prior Capture / Shape / Deliver state changed the headline, supporting sentence, one text card and a progress percentage. The real export showed a large dark rectangle with only one line of content; this was not a credible product workflow demonstration.
- R56.3 replaces that single card with an explicitly illustrative product workspace: three changing summary metrics, three source/priority/owner/release records, a contextual side panel, progress semantics and a visible demo-data disclaimer.
- Each step updates the actual product records, supporting copy, status, progress and CTA. The final action restarts the workflow rather than ending at a decorative label.
- Desktop uses a balanced copy + product-stage grid; mobile stacks the copy and product stage, with the three tabs retaining 44px minimum targets.
- R50 now checks the three distinct content fingerprints, three metrics, three records, progress values and final restart action in the exported HTML.

### R50 evidence harness correction

- The prior screenshot harness scrolled each iframe into view to capture it. It did not return to the page top before naming the next screenshot opening, so the Agency opening PNG actually showed the final chapter.
- R50 now explicitly scrolls to 0, waits for layout, asserts the scroll position and only then captures the opening viewport.
- The prior base-SHA artifact contained 20 non-empty chapter-frame screenshots, four full-page composites and 12 viewport/state captures. Those screenshots exposed the index-placement and SaaS-stage defects; they were not visual approval.

### R53 actual page-reference audit

- The 33 R53 PNG/SVG candidate files exist and their file/source hashes and native dimensions are checked by the current validator.
- The real export loader stage9/ai-chapter-assets.mjs reads stage9/ai-assets/manifest.json, which currently contains 39 JPEG chapter assets. The 33 R53 candidate filenames are not present in that manifest and therefore are not embedded into actual exported pages.
- The R53 contact sheet shows repeated generic geometric/city/dashboard motifs across multiple slots. They are original procedural candidates, but not yet convincing replacement media for the flagship pilots.
- R56.3 extends the R53 validator to report live-export-manifest references per slot and keep the gate HOLD when a candidate is not actually referenced. Do not wire these candidates into production exports or mark them eligible until a human has reviewed their visual suitability and explicitly approved them.

### Exact-SHA regression boundary

- On base SHA b9e73693c4ab538f657282149679c797d7f875df, the one-shot run completed R47 save/reopen/export parity and product E2E successfully in Chromium, Firefox and WebKit across all eight templates; R48 was PASS_CANDIDATE_ONLY.
- R50 exported-page screenshots were Chromium-only. The three-engine R47 result is a separate functional/round-trip gate, not a claim that Agency/SaaS visuals passed in all three engines.
- The new R56.3 commit must rerun the build, R43–R46 contracts, R50 actual exports, R52/R53 validators and all three R47/E2E browser engines. Human visual approval, legal review, physical-device testing and live deployment remain separate gates.
