# R56.2 — Agency + SaaS flagship visual specifications

Baseline: PR #4 head 21757995403366f1b977b705caab44142a6eef56 (pre-correction audit baseline)  
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
