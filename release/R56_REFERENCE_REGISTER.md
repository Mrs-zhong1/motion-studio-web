# R56.1 — Reference register (verified 2026-11-28)

Branch: design/r43-immersive-template-system  
Research baseline: PR #4 head b9e73693c4ab538f657282149679c797d7f875df (pre-R56.3 product correction baseline)  
Purpose: record real, inspectable references for visual and interaction study. This is not a license grant and does not authorize copying assets, source code, layouts, text, brand identifiers, or client work.

## How to use threejs.cc

- Index: https://threejs.cc/en/ and https://threejs.cc/en/catalog/
- The live English catalog reported 1,172 projects on 2026-11-28, with visible categories including Sites (65), Showcase (49), Tools (52), and Visual art (404). Counts are dynamic and should be rechecked.
- It is a discovery/index layer, not a ready-made template pack. Open a listing, inspect the creator's original live site, and follow its source-code link only when present.
- A listing or an outbound link is not a license. Reuse requires a separate review of the exact repository/file and its license; otherwise the item remains visual inspiration only.

## Creative Agency — five references

| Reference | URL | Observed mechanism / useful lesson | Mobile / complexity | Rights disposition |
|---|---|---|---|---|
| Pear | https://pear.no/ | Strong commercial positioning in the first screen; revenue-share offer, clear qualification, proof/measurement explanation, and service narrative. Useful for turning an agency story into a differentiated business proposition rather than a generic studio slogan. | Content-first page; medium | Reference only. Site copy, visual assets and implementation are not cleared for reuse. |
| Grande Charte | https://grandecharte.co/en | B2B agency hierarchy: positioning, capability groups, latest case studies, proof, collaboration model, and contact. Useful for case-study order and clear service taxonomy. | Responsive content layout; low–medium | Legal notice states site elements are protected and reproduction/exploitation requires authorization. No reuse. |
| Locomotive — Work | https://locomotive.ca/en/work | A filterable project archive with category counts, client context, concise case summaries and direct case-study paths. Useful for the Agency project index and case navigation. | Responsive project grid; medium | Reference only; no source/asset license verified. |
| Noomo — Work | https://noomoagency.com/work | Case-led portfolio that tags projects by medium (3D, storytelling, SaaS, WebGL, brand activation) and ties each to a business/brand outcome. Useful for varied case-card metadata and immersive case narratives. | Responsive case archive; medium–high | Reference only; client marks and case imagery remain third-party/protected. |
| Bruno Simon portfolio | https://bruno-simon.com/ | Navigable 3D world with explicit keyboard, touch, tablet and gamepad controls; quality/performance options and a non-3D fallback route. Useful for progressive enhancement and discoverable interaction affordances, not as the default Agency layout. | Desktop interaction is demanding; mobile/tablet controls are documented; high | Site says its source is on GitHub under MIT; exact repository and dependencies must be checked before any code reuse. This project uses interaction principles only. |

## SaaS — five references

| Reference | URL | Observed mechanism / useful lesson | Mobile / complexity | Rights disposition |
|---|---|---|---|---|
| Vercel Product Tour | https://vercel.com/product-tour | Self-guided product tour with staged steps, visible progress and an in-context product UI. Demonstrates product value before account creation. | Responsive tour; medium | Reference only; no implementation or visual asset reuse. |
| Vercel — designing the virtual product tour | https://vercel.com/blog/designing-the-vercel-virtual-product-tour | Explains the intent behind a self-paced tour: lower effort to experience the product, reveal otherwise hidden capabilities, and guide users to an “aha” moment. | Interaction design reference; low | Editorial reference only. |
| ThreeUI | https://threeui.com/ | Large source-backed component and template index across landing pages, product showcases, motion, 3D assets and UI. Useful for identifying discrete, editable interaction patterns rather than copying an entire page. | Components vary; low–high | Check the exact component's license/terms before reuse; current register treats all items as inspiration only. |
| Framer Product Demo Builder | https://www.framer.com/marketplace/plugins/product-demo-builder/ | Storyboard workflow: import screens, place hotspots, create short chapters, reopen and update demos, and preview desktop/phone. Useful for authoring controls and maintainable demo steps. | Desktop/mobile preview; medium | Marketplace/plugin terms apply; no reuse assumed. |
| Noomo — Salesforce Platform case | https://noomoagency.com/work | Case listing identifies a Salesforce platform experience as SaaS/enterprise storytelling with interactive 3D. Useful for translating complex product architecture into an explorable narrative. | Responsive case presentation; high | Reference only; client marks and case assets are not cleared for reuse. |

## R56 implementation translation

- Agency references support a project-first portfolio: one authored hero, distinct case chapters, a visible project index, proof and a clear inquiry path. The case index must navigate the real chapter, not merely change a selected button state.
- SaaS references support a guided product story: plain-language value proposition, one primary CTA, proof close to the claim, then a user-operated Capture → Shape → Deliver demo with meaningful state changes. A static dashboard image or decorative tab strip is insufficient.
- The two templates must not share a generic hero/section skeleton with only color changes.
- No reference image, logo, copy, client work, code, or downloadable media is to be copied into production without an item-specific rights check.

## 2026-11-28 live revalidation

The following pages were opened and inspected on 2026-11-28. These notes describe observable structure and interaction intent; they do not grant rights to copy the underlying site, client assets, copy, models, textures, or source code.

### Three.js project discovery index

- [threejs.cc English catalog](https://threejs.cc/en/catalog/) currently reports **1,172 projects**. Its visible taxonomy includes **Sites (65), Showcase (49), Tools (52), and Visual art (404)**. Counts are dynamic and should be rechecked when selecting new references.
- The catalog is a discovery index, not a template marketplace. The most useful Agency-facing entries currently include:
  - [Noomo Storytelling](https://threejs.cc/en/item/x-archive-auth-2102816849092378776-f95f8be0/) — glowing abstract forms, a glass phoenix, scroll-driven transitions and dramatic lighting; high-value reference for a single authored case narrative.
  - [Noomo — Immersive Showcase](https://threejs.cc/en/item/x-archive-auth-2067340550521696688-109ffcd5/) — rotating geometry and animated imagery used to present projects instead of a conventional showreel; useful for a restrained 3D project transition.
  - [Locomotive Agency Website](https://threejs.cc/en/item/x-archive-auth-2061252490826555706-4516d9fd/) — human/monitor 3D character paired with minimal typography; useful as a hero-art direction, not a whole page skeleton.
  - [Bruno Simon Portfolio](https://threejs.cc/en/item/bruno-simon-com/) and [Active Theory](https://threejs.cc/en/item/activetheory-net/) — examples of navigable 3D portfolio storytelling and cinematic WebGL work.
- The live [Locomotive work archive](https://locomotive.ca/en/work) exposes category filters with project counts and case cards containing client, location, concise context and case-study/visit links. The live [Noomo work archive](https://noomoagency.com/work) groups work with explicit tags such as 3D, storytelling, SaaS, enterprise and brand activation. These are useful for case metadata and portfolio information architecture.

### Creative Agency — live site observations

- [Pear](https://pear.no/) leads with a differentiated commercial model (no upfront/hourly fees; revenue share) and supports the claim with baseline measurement, attribution, service explanation, qualification and a short application path. Its chapter navigation separates Model / Work / Terms / Questions. Transfer the clarity of the proposition and evidence order, not its copy or revenue-share positioning.
- [Grande Charte](https://grandecharte.co/en) currently leads with an 8+ years positioning statement for websites, AI products, brands and systems, followed by a featured business-intelligence case, client proof, service categories, case studies and a direct project-contact path. Its [legal notice](https://grandecharte.co/en/legal-notice) explicitly protects text, photographs, illustrations, video, graphics, logos, trademarks, interfaces, navigation, site structure, developments and source code; reproduction or exploitation without prior authorization is prohibited. Use only the information hierarchy as inspiration; do not reproduce its brand, copy, imagery or implementation.
- [Bruno Simon](https://bruno-simon.com/) is an interactive 3D world with published mouse/keyboard, mobile/tablet and gamepad controls, plus quality/renderer options and a behind-the-scenes explanation. The page states that its public source is under MIT; this does not clear third-party dependencies, fonts, models, music or any other asset for reuse. Motion Studio uses only the interaction principle of progressive controls and a graceful non-3D route.

### SaaS — live product-tour observations

- [Vercel Product Tour](https://vercel.com/product-tour) presents a multi-step product journey with visible actions including Develop, Import, Commit, Check build, View deployment, Monitor, Preview, Comment, Ship and Inspect.
- [Vercel's tour design article](https://vercel.com/blog/designing-the-vercel-virtual-product-tour) explains the self-paced slideshow/progress model and the goal of letting prospective users experience product UI before sign-in, reducing friction until an "aha" moment.
- [ThreeUI](https://threeui.com/) indexes sections, landing pages, buttons, 3D assets, backgrounds, text animation and UI effects, with source-backed component examples. Treat it as a component discovery source only; each component's actual license/terms must be checked before reuse.
- [Framer Product Demo Builder](https://www.framer.com/marketplace/plugins/product-demo-builder/) advertises clickable hotspots, chapters, multiple visual skins, phone layouts and reopen/update workflows. The marketplace listing currently marks its license **Limited** and lists a one-time price; this is a workflow/competitor reference, not a reusable asset or implementation license.
- [Noomo's Salesforce Platform case](https://noomoagency.com/work) is tagged Website / 3D / Storytelling / SaaS / Enterprise and is useful for presenting a complex platform as a guided story rather than a static dashboard.

### Rights and evidence disposition

- All ten curated references remain **reference-only**. No page image, logo, client mark, text, video, model, texture, font, source code or downloadable asset was copied into Motion Studio by this research.
- Bruno Simon's stated MIT source license is a lead for a future exact-repository/dependency audit, not a blanket license for the live site or its media.
- The initial text/HTML revalidation recorded live-page structure and catalog metadata but did not itself capture reference screenshots. The current R43–R55 one-shot pipeline now performs the separate browser capture at desktop and mobile viewports, records exact candidate SHA and image hashes, and archives the review copies under stage9/visual-evidence/r43-r55/<candidate SHA>. Do not treat those screenshots as visual approval or reuse permission.

## Exact-SHA screenshot capture

- Script: stage9/tests/capture_r56_references.py.
- The R50 workflow now captures first-screen reference screenshots at 1440×900 and 390×844 for the ten unique URLs above, records response status/title/text sample/visible media counts/page errors, and hashes every PNG.
- The reference captures are uploaded in the R43–R55 exact-SHA artifact and persisted as compressed review copies with their original PNG SHA-256 values in stage9/visual-evidence/r43-r55/<candidate SHA>/.
- This capture step is best-effort because third-party pages may block automation or change. A missing/blocked capture is recorded as unavailable, never inferred from a search snippet.
- Screenshots are first-screen evidence only. They do not establish full interactive parity, source-code rights, asset licenses, or visual approval for Motion Studio.

## Evidence limitations

This is a public-page content/interaction inspection record, not a complete device lab. Live motion and all interactive states still require human browser review. Mobile screenshot capture is automated evidence, not physical-device acceptance. A reference's current appearance may change; use the exact capture date and screenshot hashes from the R50/R56 artifact.
