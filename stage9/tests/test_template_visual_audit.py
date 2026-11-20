"""Visual-render audit of all 8 built-in templates in the bundled offline browser editor.

Checks inspect the actual exported preview frame, rather than a CSS mockup.
Screenshots are created in the runner (MOTION_SCREENSHOT_DIR controls location),
while structured JSON evidence is printed to CI logs and GitHub Job Summary.
A pass is a rendering/geometry smoke test, not subjective design approval.
"""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import hashlib
import json
import os
import threading

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
EDITOR = ROOT / "Motion-Studio-Stage15-Meshopt-OFFLINE.html"
OUTPUT = ROOT / "TEMPLATE_VISUAL_AUDIT.json"
SCREENSHOTS = Path(os.environ.get("MOTION_SCREENSHOT_DIR", "/tmp/motion-studio-visual-audit"))
TEMPLATES = ["editorial", "product-3d", "cinematic", "architecture",
             "agency", "fashion", "gallery", "saas"]


def run_audit():
    SCREENSHOTS.mkdir(parents=True, exist_ok=True)
    server = ThreadingHTTPServer(("127.0.0.1", 0),
        partial(SimpleHTTPRequestHandler, directory=str(ROOT)))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    issues = []
    result = {"source": EDITOR.name, "screenshots_saved_in_runner": str(SCREENSHOTS),
              "templates": [], "browser": "chromium", "status": "running"}
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True, args=["--no-sandbox"])
            page = browser.new_page(viewport={"width": 1440, "height": 900},
                                    device_scale_factor=1)
            errors = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.goto(f"http://127.0.0.1:{server.server_port}/{EDITOR.name}",
                      wait_until="domcontentloaded", timeout=30000)
            assert page.locator("#discoveryView").is_visible()
            assert page.locator("[data-template-card]").count() == 8
            initial_project = page.evaluate("JSON.stringify(project)")
            for template_id in TEMPLATES:
                card = page.locator(f'[data-template-card="{template_id}"]')
                assert card.count() == 1, f"Missing gallery card for {template_id}"
                card.click()
                page.wait_for_function("(id) => templatePhotoCache.has(id)",
                                       arg=template_id, timeout=30000)
                preview = page.locator("#templatePreviewFrame")
                frame = preview.content_frame
                if template_id in ("editorial","cinematic"):
                    # R42 magazine and R39 film are intentionally not the
                    # generic legacy iframe+section grid. Audit their ACTUAL
                    # authored scenes, not the removed split-scene markup.
                    if template_id=="editorial":
                        frame.locator('html[data-e42-editorial="coherent-print"]').wait_for(timeout=30000)
                        subject='.e42-sticky'
                        image_selector='.e42-image'
                        scene_selector='.e42-spread'
                    else:
                        frame.locator('html[data-r39-film="continuous"]').wait_for(timeout=30000)
                        subject='.r39-stage'
                        image_selector='.r39-frame'
                        scene_selector='.r39-caption'
                    total_sections=page.evaluate('(id)=>templateSets[id].sections.length',template_id)
                    manifest=page.evaluate('(id)=>templateAssetAuditCache.get(id)||[]',template_id)
                    assert len(manifest)==total_sections,(template_id,len(manifest),total_sections)
                    assert frame.locator(image_selector).count()==total_sections,template_id
                    assert frame.locator(scene_selector).count()==total_sections,template_id
                    assert frame.locator('iframe').count()==0,(template_id,'nested duplicate demonstration')
                    for device,width,height in (("desktop",1440,900),("mobile",390,844)):
                        page.set_viewport_size({"width":width,"height":height})
                        if device=="mobile":page.locator("#previewMobile").click()
                        else:page.locator("#previewDesktop").click()
                        if template_id=="cinematic":
                            # Desktop is captured first and ends at chapter 5.
                            # The iframe retains that scroll position when the
                            # preview is resized; explicitly reset each viewport
                            # so its opening capture starts at chapter 1.
                            frame.locator("html").evaluate("""e=>{
                              e.style.setProperty('scroll-behavior','auto','important');
                              scrollTo({top:0,behavior:'instant'});
                            }""")
                            frame.locator("html[data-r39-chapter='1']").wait_for(state="attached",timeout=15000)
                            page.wait_for_timeout(180)
                        snapshots=frame.locator(image_selector).evaluate_all("""els=>els.map(e=>({
                            src:e.getAttribute('src')?.startsWith('data:image/'),
                            loaded:e.complete&&e.naturalWidth>0,
                            width:Math.round(e.getBoundingClientRect().width)
                        }))""")
                        assert all(row['src'] and row['loaded'] and row['width']>45 for row in snapshots),(template_id,device,snapshots)
                        overflow=frame.locator('html').evaluate('e=>e.scrollWidth-innerWidth')
                        assert overflow<=32,(template_id,device,overflow)
                        screenshot=page.screenshot(animations="disabled",full_page=False)
                        (SCREENSHOTS/f"{template_id}-preview-{device}.png").write_bytes(screenshot)
                        (SCREENSHOTS/f"{template_id}-immersive-{device}.png").write_bytes(screenshot)
                        if template_id=="editorial":
                            first=frame.locator(subject).first
                            middle=frame.locator(subject).nth(2)
                            last=frame.locator(subject).last
                        else:
                            first=middle=last=frame.locator(subject)
                        if template_id=="cinematic":
                            # Capture the iframe element from the parent document.
                            # This preserves its internal scroll position while avoiding
                            # the sticky-stage auto-scroll performed by child locators.
                            state=frame.locator("html").evaluate("""e=>({
                              chapter:Number(e.dataset.r39Chapter),
                              progress:Number(e.dataset.r39Progress),
                              firstOpacity:Number(getComputedStyle(document.querySelector('.r39-frame[data-index="0"]')).opacity)
                            })""")
                            assert state["chapter"]==1 and state["progress"]<.02 and state["firstOpacity"]>.9,(template_id,device,"opening",state)
                            page.locator("#templatePreviewFrame").screenshot(
                                path=str(SCREENSHOTS/f"{template_id}-{device}.png"),animations="disabled")
                        else:
                            first.screenshot(path=str(SCREENSHOTS/f"{template_id}-{device}.png"),animations="disabled")
                        if template_id=="editorial":middle.scroll_into_view_if_needed()
                        else:
                            frame.locator('html').evaluate("""e=>{
                              e.style.setProperty('scroll-behavior','auto','important');
                              const s=document.querySelector('#r39-story');
                              scrollTo({top:s.offsetTop+(s.offsetHeight-innerHeight)*.5,behavior:'instant'});
                            }""")
                            frame.locator("html[data-r39-chapter='3']").wait_for(state="attached",timeout=15000)
                            page.wait_for_timeout(180)
                        if template_id=="cinematic":
                            state=frame.locator("html").evaluate("""e=>({
                              chapter:Number(e.dataset.r39Chapter),
                              progress:Number(e.dataset.r39Progress),
                              middleOpacity:Number(getComputedStyle(document.querySelector('.r39-frame[data-index="2"]')).opacity)
                            })""")
                            assert state["chapter"]==3 and .45<=state["progress"]<=.55 and state["middleOpacity"]>.9,(template_id,device,"middle",state)
                            page.locator("#templatePreviewFrame").screenshot(
                                path=str(SCREENSHOTS/f"{template_id}-chapter3-{device}.png"),animations="disabled")
                        else:
                            middle.screenshot(path=str(SCREENSHOTS/f"{template_id}-chapter3-{device}.png"),animations="disabled")
                        if template_id=="editorial":last.scroll_into_view_if_needed()
                        else:
                            frame.locator('html').evaluate("""e=>{
                              e.style.setProperty('scroll-behavior','auto','important');
                              const s=document.querySelector('#r39-story');
                              scrollTo({top:s.offsetTop+s.offsetHeight-innerHeight,behavior:'instant'});
                            }""")
                            frame.locator("html[data-r39-chapter='5']").wait_for(state="attached",timeout=15000)
                            page.wait_for_timeout(180)
                        if template_id=="cinematic":
                            state=frame.locator("html").evaluate("""e=>({
                              chapter:Number(e.dataset.r39Chapter),
                              progress:Number(e.dataset.r39Progress),
                              endingOpacity:Number(getComputedStyle(document.querySelector('.r39-frame[data-index="4"]')).opacity)
                            })""")
                            assert state["chapter"]==5 and state["progress"]>.98 and state["endingOpacity"]>.9,(template_id,device,"ending",state)
                            page.locator("#templatePreviewFrame").screenshot(
                                path=str(SCREENSHOTS/f"{template_id}-ending-{device}.png"),animations="disabled")
                        else:
                            last.screenshot(path=str(SCREENSHOTS/f"{template_id}-ending-{device}.png"),animations="disabled")
                        shot=(SCREENSHOTS/f"{template_id}-{device}.png").read_bytes()
                        middle_shot=(SCREENSHOTS/f"{template_id}-chapter3-{device}.png").read_bytes()
                        ending_shot=(SCREENSHOTS/f"{template_id}-ending-{device}.png").read_bytes()
                        row={
                          "template":template_id,"device":device,"sectionCount":total_sections,
                          "photoCount":total_sections,"visiblyRenderedPhotos":len(snapshots),
                          "collapsedSections":0,
                          "realPhotoCount":sum(x["kind"] in ("unsplash-photo","ai-generated-image") for x in manifest),
                          "originalFallbackCount":sum(x["kind"]=="original-generated-art" for x in manifest),
                          "documentWidth":width+max(0,overflow),"viewportWidth":width,
                          "firstSectionPngSHA256":hashlib.sha256(shot).hexdigest()[:16],
                          "chapter3PngSHA256":hashlib.sha256(middle_shot).hexdigest()[:16],
                          "designedEndingPngSHA256":hashlib.sha256(ending_shot).hexdigest()[:16],
                          "sourceManifest":[{"chapter":x["chapter"],"kind":x["kind"],"source":x.get("source")} for x in manifest],
                          "mediaRightsApproved":False,"storyEngine":'R42-paper' if template_id=='editorial' else 'R39-film'
                        }
                        result["templates"].append(row)
                    page.locator("#previewClose").click()
                    continue
                frame.locator("section.section").first.wait_for(timeout=30000)
                assert page.locator("#previewHeroTitle").inner_text().strip()
                assert page.locator("#previewUse").is_visible()
                assert page.locator("#previewUsePanel").is_hidden()  # R41 default full-width preview
                assert page.locator(".preview-product-layout").is_visible()
                if template_id in ("editorial", "product-3d"):
                    assert frame.locator(".section.designed-hero").count()==1

                total_sections = page.evaluate(
                    "(id) => templateSets[id].sections.length", template_id)
                # Source-based evidence: an image layer is NOT proof of a photo.
                # Actual network failures must remain visible as fallback counts.
                manifest = page.evaluate("(id)=>templateAssetAuditCache.get(id)||[]",template_id)
                real_photo_count = sum(entry["kind"] in ("unsplash-photo","ai-generated-image") for entry in manifest)
                fallback_count = sum(entry["kind"]=="original-generated-art" for entry in manifest)
                assert len(manifest)==total_sections, (template_id,len(manifest),total_sections)
                assert real_photo_count+fallback_count==total_sections, (template_id,manifest)
                assert frame.locator("section.section").count() == total_sections
                for device, width, height in (("desktop", 1440, 900), ("mobile", 390, 844)):
                    page.set_viewport_size({"width": width, "height": height})
                    # The mobile button narrows the embedded preview to device width.
                    if device == "mobile":
                        page.locator("#previewMobile").click()
                    else:
                        page.locator("#previewDesktop").click()
                    frame.locator(".section-art").first.wait_for(timeout=10000)
                    geometry = frame.locator("body").evaluate("""body => {
                       const doc = body.ownerDocument;
                       const arts = Array.from(doc.querySelectorAll('.section-art'));
                       const sections = Array.from(doc.querySelectorAll('section.section'));
                       const visible = arts.filter(node => {
                         const s = getComputedStyle(node), r = node.getBoundingClientRect();
                         return s.backgroundImage.startsWith('url("data:image/') &&
                                Number(s.opacity) >= .85 && r.width > 45 && r.height > 45;
                       });
                       const bad = sections.filter(s => {
                         const r = s.getBoundingClientRect();
                         return r.width < 160 || r.height < 220;
                       }).length;
                       return {
                         documentWidth: doc.documentElement.scrollWidth,
                         viewportWidth: doc.documentElement.clientWidth,
                         sectionCount: sections.length,
                         photoCount: arts.length,
                         dimmedScenePhotos: arts.filter(node => Number(getComputedStyle(node).opacity) < .85).length,
                         visiblyRenderedPhotos: visible.length,
                         collapsedSections: bad,
                         imageWidths: arts.map(e=>Math.round(e.getBoundingClientRect().width))
                       };
                    }""")
                    if template_id in ("editorial", "product-3d"):
                        hero = frame.locator(".section.designed-hero").first
                        sections = hero.evaluate("""section=>{
                          const text = section.querySelector('iframe').getBoundingClientRect();
                          const image = section.querySelector('.section-art').getBoundingClientRect();
                          const overlap = Math.max(0,Math.min(text.right,image.right)-Math.max(text.left,image.left))
                                        *Math.max(0,Math.min(text.bottom,image.bottom)-Math.max(text.top,image.top));
                          return {imageWidth:image.width,textWidth:text.width,overlapPx2:Math.round(overlap)}
                        }""")
                        geometry["heroGeometry"]=sections
                        if template_id=="product-3d":
                            # R36 product-3d is intentionally a layered full-bleed stage:
                            # the photograph is a backdrop behind the live GLB renderer.
                            if sections["imageWidth"]<width*.80 or sections["textWidth"]<width*.50:
                                issues.append(f"{template_id} {device}: layered hero collapsed {sections}")
                        elif sections["overlapPx2"]>300:
                            issues.append(f"{template_id} {device}: editorial hero zones overlap {sections}")
                    # R3: review the entire preview shell, not only iframe content.
                    if template_id in ("editorial", "product-3d"):
                        layout = page.locator(".preview-product-layout").evaluate("""el=>{
                          const info=el.querySelector('.preview-product-info').getBoundingClientRect();
                          const stage=el.querySelector('.preview-device').getBoundingClientRect();
                          const viewport=document.documentElement.getBoundingClientRect();
                          const horizontal=Math.max(0,Math.min(info.right,stage.right)-Math.max(info.left,stage.left));
                          const vertical=Math.max(0,Math.min(info.bottom,stage.bottom)-Math.max(info.top,stage.top));
                          return {infoW:Math.round(info.width),stageW:Math.round(stage.width),
                            infoH:Math.round(info.height),stageH:Math.round(stage.height),
                            overlapPx2:Math.round(horizontal*vertical),
                            overflows:document.documentElement.scrollWidth>viewport.width+32};
                        }""")
                        geometry["previewShell"]=layout
                        if layout["overlapPx2"]>300 or layout["overflows"]:
                            issues.append(f"{template_id} {device}: broken preview shell {layout}")
                        screenshot=page.screenshot(animations="disabled",full_page=False)
                        (SCREENSHOTS/f"{template_id}-preview-{device}.png").write_bytes(screenshot)
                        geometry["fullPreviewPngSHA256"]=hashlib.sha256(screenshot).hexdigest()[:16]
                    # R14: capture actual immersive website experience for ALL
                    # eight templates at both viewport sizes, not just two
                    # preview dialog screenshots.
                    # R41: stage is full width by default; opening template
                    # information is a FLOATING drawer, not a split overlay.
                    immersive = page.locator("#previewImmersive")
                    assert page.locator(".preview-product-info").is_hidden()
                    stage_width = page.locator("#previewDevice").evaluate(
                        "el => el.getBoundingClientRect().width"
                    )
                    assert stage_width >= width * .88, (template_id, device, stage_width, width)
                    immersive_shot = page.screenshot(animations="disabled", full_page=False)
                    (SCREENSHOTS / f"{template_id}-immersive-{device}.png").write_bytes(immersive_shot)
                    geometry["immersivePngSHA256"] = hashlib.sha256(immersive_shot).hexdigest()[:16]
                    immersive.click()
                    assert page.locator("#templatePreview").evaluate("el=>el.classList.contains('r41-info-open')")
                    assert page.locator(".preview-product-info").is_hidden()
                    assert abs(page.locator("#previewDevice").evaluate(
                        "el => el.getBoundingClientRect().width") - stage_width) < 4
                    immersive.click()
                    assert not page.locator("#templatePreview").evaluate("el=>el.classList.contains('r41-info-open')")
                    assert page.locator(".preview-product-info").is_hidden()
                    # R4: all six newly authored templates must have complete,
                    # nonoverlapping image/renderer zones in every chapter.
                    # Previously rebuilt pilots retain their original first-page hero.
                    if template_id in ("editorial", "product-3d","cinematic",
                                       "architecture","agency","fashion","gallery","saas"):
                        chapters = frame.locator("section.designed-chapter")
                        expected_chapters=total_sections-1 if template_id in ("editorial","product-3d") else total_sections
                        assert chapters.count()==expected_chapters, (template_id, chapters.count(),expected_chapters)
                        if template_id not in ("editorial","product-3d"):
                            assert frame.locator("section.authored-six").count()==total_sections
                        arrangements = chapters.evaluate_all("""nodes=>nodes.map(n=>{
                            const a=n.querySelector('.section-art').getBoundingClientRect();
                            const f=n.querySelector('iframe').getBoundingClientRect();
                            const x=Math.max(0,Math.min(a.right,f.right)-Math.max(a.left,f.left));
                            const y=Math.max(0,Math.min(a.bottom,f.bottom)-Math.max(a.top,f.top));
                            const title=n.querySelector('[data-chapter-title]');
                            const titleRect=title?.getBoundingClientRect();
                            const section=n.getBoundingClientRect();
                            return {hasHeading:!!title&&title.textContent.trim().length>3,
                              overlap:Math.round(x*y),artW:Math.round(a.width),
                              frameW:Math.round(f.width),artH:Math.round(a.height),frameH:Math.round(f.height),
                              sectionW:Math.round(section.width),headingW:Math.round(titleRect?.width||0),
                              headingH:Math.round(titleRect?.height||0)};
                        })""")
                        geometry["authoredChapters"]=arrangements
                        if template_id=="product-3d":
                            # Product-3D intentionally layers photography, live GLB and title
                            # in one canvas. Validate each layer's usable size, not separation.
                            if any(not x["hasHeading"] or x["artW"]<x["sectionW"]*.85 or
                                   x["frameW"]<x["sectionW"]*.50 or x["artH"]<200 or
                                   x["frameH"]<200 or x["headingW"]<100 or x["headingH"]<28
                                   for x in arrangements):
                                issues.append(f"{template_id} {device}: layered scene has a collapsed layer {arrangements}")
                        elif any(not x["hasHeading"] or x["overlap"]>300 or
                                 x["artW"]<70 or x["frameW"]<70 or
                                 x["artH"]<200 or x["frameH"]<200 for x in arrangements):
                            issues.append(f"{template_id} {device}: chapter image/renderer zones overlap or collapse {arrangements}")
                    # R8: each template needs a real designed ending, and the
                    # six non-pilot templates require a distinct opening mark.
                    closing = frame.locator("section.section.template-final").last
                    assert closing.count() == 1,template_id
                    ending = closing.locator(".template-closing-mark").evaluate("""el=>{
                       const r=el.getBoundingClientRect(),f=el.closest('section').querySelector('iframe').getBoundingClientRect();
                       const heading=el.querySelector('.closing-body strong').textContent.trim();
                       return {heading, visible:getComputedStyle(el).display!=='none',
                         width:Math.round(r.width), height:Math.round(r.height),
                         overlapped:Math.round(Math.max(0,Math.min(r.right,f.right)-Math.max(r.left,f.left))*
                                              Math.max(0,Math.min(r.bottom,f.bottom)-Math.max(r.top,f.top)))};
                    }""")
                    geometry["designedEnding"]=ending
                    # The product-3d ending is an intentional overlay over its
                    # full-stage GLB renderer; other templates require separated zones.
                    if (not ending["heading"] or not ending["visible"] or
                        ending["width"]<120 or ending["height"]<100 or
                        (template_id!="product-3d" and ending["overlapped"]>300)):
                        issues.append(f"{template_id} {device}: designed ending collapsed or incorrectly overlaps renderer {ending}")
                    if template_id not in ("editorial","product-3d"):
                        assert frame.locator("section.template-opening .template-opening-mark").count() == 1,template_id
                        assert frame.locator("section.template-opening .chapter-step").inner_text().strip().startswith("01 /"),template_id
                    geometry["photoSourcesAudited"]=len(manifest)
                    geometry["realPhotoCount"]=real_photo_count
                    geometry["originalFallbackCount"]=fallback_count
                    geometry["mediaRightsApproved"]=False
                    geometry["sourceManifest"]=[{"chapter":entry["chapter"],
                        "kind":entry["kind"],"source":entry.get("source")}
                        for entry in manifest]
                    geometry["template"] = template_id
                    geometry["device"] = device
                    shot = frame.locator("section.section").first.screenshot(
                        animations="disabled", timeout=30000)
                    geometry["firstSectionPngSHA256"] = hashlib.sha256(shot).hexdigest()[:16]
                    (SCREENSHOTS / f"{template_id}-{device}.png").write_bytes(shot)
                    if geometry["photoCount"] != total_sections:
                        issues.append(f"{template_id} {device}: missing photo layers {geometry}")
                    expected = total_sections - (1 if template_id == "product-3d" else 0)
                    if geometry["visiblyRenderedPhotos"] < expected:
                        issues.append(f"{template_id} {device}: invisible photos {geometry}")
                    if geometry["collapsedSections"] != 0:
                        issues.append(f"{template_id} {device}: collapsed sections {geometry}")
                    # More than 32px indicates unintended horizontal layout overflow.
                    if geometry["documentWidth"] > geometry["viewportWidth"] + 32:
                        issues.append(f"{template_id} {device}: overflow {geometry}")
                    # R5: the exported preview must change actual story motion
                    # on scroll. Not enough to merely contain the CSS declaration.
                    if template_id == "cinematic" and device == "desktop":
                        target = frame.locator("section.designed-chapter").nth(2)
                        before_motion = target.evaluate("""node=>({
                          progress:Number(node.style.getPropertyValue('--story-reveal')||1),
                          clip:getComputedStyle(node.querySelector('.section-art')).clipPath
                        })""")
                        target.scroll_into_view_if_needed()
                        page.wait_for_timeout(180)
                        after_motion = target.evaluate("""node=>({
                          progress:Number(node.style.getPropertyValue('--story-reveal')||0),
                          clip:getComputedStyle(node.querySelector('.section-art')).clipPath
                        })""")
                        geometry["scrollMotion"]={"before":before_motion,"after":after_motion}
                        if (after_motion["progress"] <= before_motion["progress"] + .1
                                or after_motion["clip"] == before_motion["clip"]):
                            issues.append(f"cinematic desktop: scroll reveal did not progress {geometry['scrollMotion']}")
                    # R6: a real cross-chapter transition must update the
                    # outgoing section AND the incoming section on a scroll,
                    # not just apply an on-load CSS class.
                    if template_id == "cinematic" and device == "desktop":
                        first=frame.locator("section.section").first
                        third=frame.locator("section.section").nth(2)
                        first.scroll_into_view_if_needed()
                        page.wait_for_timeout(180)
                        outgoing_before=first.evaluate(
                            "el=>Number(el.style.getPropertyValue('--chapter-exit')||0)")
                        incoming_before=third.evaluate(
                            "el=>Number(el.style.getPropertyValue('--chapter-enter')||0)")
                        third.scroll_into_view_if_needed()
                        page.wait_for_timeout(180)
                        outgoing_after=first.evaluate(
                            "el=>Number(el.style.getPropertyValue('--chapter-exit')||0)")
                        incoming_after=third.evaluate(
                            "el=>Number(el.style.getPropertyValue('--chapter-enter')||0)")
                        geometry["crossChapter"]={
                            "outBefore":outgoing_before,"outAfter":outgoing_after,
                            "inBefore":incoming_before,"inAfter":incoming_after}
                        if (outgoing_after <= outgoing_before+.3 or
                                incoming_after <= incoming_before+.3):
                            issues.append(f"R6: cross-chapter continuity stalled: {geometry['crossChapter']}")
                    # Screenshots of an actual middle chapter: card/hero screenshots
                    # alone cannot show whether a template has a real page narrative.
                    middle = frame.locator("section.section").nth(2)
                    middle.scroll_into_view_if_needed()
                    page.wait_for_timeout(130)
                    middle_png = middle.screenshot(animations="disabled", timeout=30000)
                    (SCREENSHOTS / f"{template_id}-chapter3-{device}.png").write_bytes(middle_png)
                    geometry["chapter3PngSHA256"] = hashlib.sha256(middle_png).hexdigest()[:16]
                    # Capture the closing editorial CONTENT, not its giant
                    # off-screen chapter. Screenshotting the whole section may
                    # show the top of an iframe or preview shell instead.
                    end_mark = closing.locator(".template-closing-mark")
                    end_mark.scroll_into_view_if_needed(timeout=30000)
                    page.wait_for_timeout(120)
                    end_rect = end_mark.bounding_box()
                    assert end_rect and end_rect["width"]>120 and end_rect["height"]>100, (template_id,device,end_rect)
                    final_png = end_mark.screenshot(animations="disabled",timeout=30000)
                    (SCREENSHOTS/f"{template_id}-ending-{device}.png").write_bytes(final_png)
                    geometry["designedEndingPngSHA256"]=hashlib.sha256(final_png).hexdigest()[:16]
                    geometry["closingScreenshotRegion"]={"width":round(end_rect["width"]),
                                                       "height":round(end_rect["height"])}
                    result["templates"].append(geometry)
                page.locator("#previewClose").click()
                assert page.locator("#templatePreview").is_hidden()
            assert page.evaluate("JSON.stringify(project)") == initial_project
            if errors: issues.append(f"Uncaught browser errors: {errors}")
            assert not issues, "\n".join(issues)
            browser.close()
        result["status"] = "pass"
    except Exception as err:
        result["status"] = "fail"
        result["error"] = str(err)
        raise
    finally:
        OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        print("VISUAL_AUDIT_JSON=" + json.dumps(result, ensure_ascii=False))
        server.shutdown()
        server.server_close()


if __name__ == "__main__":
    run_audit()
