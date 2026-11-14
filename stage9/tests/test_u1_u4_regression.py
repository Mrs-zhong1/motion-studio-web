"""U1-U4 regression: template-first discovery, inlined demo photos, blank project, 20 components."""
from pathlib import Path
from functools import partial
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright
import threading

ROOT = Path(__file__).resolve().parents[1]
EDITOR = ROOT / "Motion-Studio-Unified-Editor.html"
DEMO_JPEG = (ROOT / 'template-thumbnails' / 'editorial.jpg').read_bytes()

def test_u1_u4_regression():
    server = ThreadingHTTPServer(("127.0.0.1",0),partial(SimpleHTTPRequestHandler,directory=str(ROOT)))
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True,args=["--no-sandbox"])
            page = browser.new_page(viewport={"width":1440,"height":900})
            errors = []
            page.on("pageerror",lambda e:errors.append(str(e)))
            page.route("https://images.unsplash.com/**",lambda route: route.fulfill(status=200,body=DEMO_JPEG,content_type="image/jpeg",headers={"access-control-allow-origin":"*"}))
            page.goto(f"http://127.0.0.1:{server.server_port}/{EDITOR.name}",wait_until="domcontentloaded")
            assert page.locator("#discoveryView").is_visible()
            assert page.locator("[data-template-card]").count()==8
            assert page.locator('[data-template-card="editorial"] .designed-card-copy').is_visible()
            assert page.locator('[data-template-card="product-3d"] .designed-card-photo').is_visible()

            page.locator("[data-template-card='editorial']").click()
            page.wait_for_function("() => templatePhotoCache.has('editorial')")
            page.locator("#templatePreviewFrame").wait_for(state="attached")
            page.locator("#previewUse").click()
            page.wait_for_function("() => project.templateId==='editorial'")
            assert page.evaluate("project.sections[0].image.startsWith('data:image/jpeg;base64,')"), page.evaluate("({has:templatePhotoCache.has('editorial'),sizes:templatePhotoCache.get('editorial')?.map(x=>x.length)})")
            assert page.evaluate("project.sections.length")>=3
            assert page.locator(".section.selected [data-canvas-image]").count()==1
            page.locator(".section.selected [data-canvas-image]").click()
            page.locator("#propImage").set_input_files({"name":"replacement.jpg","mimeType":"image/jpeg","buffer":DEMO_JPEG})
            page.wait_for_function("() => project.sections[0].image.startsWith('data:image/jpeg;base64,')")
            page.locator("#imageFocusX").evaluate("(el)=>{el.value='72';el.dispatchEvent(new Event('input',{bubbles:true}))}")
            assert page.locator("#page").get_attribute("data-template")=="editorial"
            assert page.locator(".section .section-art").count()>=1
            assert page.locator(".section .section-art").first.evaluate(
                "(el) => getComputedStyle(el).backgroundSize"
            )=="cover"
            assert page.locator(".section .section-art").first.evaluate(
                "(el) => getComputedStyle(el).opacity"
            )=="1"
            assert "CREATIVE PRACTICE  /  SELECTED WORK" in page.locator(".section").first.evaluate(
                "(el)=>getComputedStyle(el,'::before').content"
            )
            assert page.evaluate("project.sections[0].imageFocusX")==72
            assert page.locator(".section.selected .section-art").evaluate("(el)=>el.style.backgroundPosition.includes('72%')")
            page.locator('[data-asset-tier-button="l4"]').click()
            assert page.locator('[data-asset-tier="l4"]').is_visible()
            assert page.locator("#projectAssetList .asset-entry").count()>=1
            page.locator("#projectAssetList [data-asset-replace]").first.click()
            page.locator("#propImage").set_input_files({"name":"from-asset-list.jpg","mimeType":"image/jpeg","buffer":DEMO_JPEG})
            page.wait_for_function("() => document.querySelector('#projectAssetList .asset-entry img')?.getAttribute('src')===project.sections[0].image")
            assert page.evaluate("project.sections[0].imageFocusX")==72

            # Each preconfigured template must have image content for every section;
            # do not mutate the user's active project while checking other templates.
            completeness = page.evaluate("""async () => {
                const before = JSON.stringify(project);
                const checks = [];
                for (const t of templateCatalog) {
                    await ensureTemplatePhoto(t.id);
                    const doc = createProjectFromTemplate(t.id);
                    checks.push({
                        id: t.id,
                        total: doc.sections.length,
                        images: doc.sections.filter(s=>s.image.startsWith('data:image/jpeg;base64,')).length
                    });
                }
                return {checks,unchanged:before===JSON.stringify(project)};
            }""")
            assert completeness["unchanged"], completeness
            assert len(completeness["checks"])==8
            assert all(t["total"]>=3 and t["images"]==t["total"] for t in completeness["checks"]), completeness
            exported = page.evaluate("exportDocument()")
            assert exported.count("data:image/jpeg;base64,")>=3

            # R4: a newly created Product template must contain a real binary glTF
            # model, not merely the fallback cube or an empty iframe.
            binary_model = page.evaluate("""() => {
                const doc = createProjectFromTemplate('product-3d');
                const scene = doc.sections.find(s=>s.id==='offline-glb-scene');
                const b = atob(scene.glb || '');
                const header = Array.from(b.slice(0,12),x=>x.charCodeAt(0));
                return {bytes:b.length,magic:header.slice(0,4),version:header.slice(4,8),
                    embedded:exportDocument().includes('data:image/jpeg;base64,')};
            }""")
            assert binary_model["bytes"] > 600
            assert binary_model["magic"] == [103,108,84,70], binary_model
            assert binary_model["version"] == [2,0,0,0], binary_model
            page.locator("#backToLibrary").click()
            page.locator("[data-template-card='product-3d']").click()
            page.wait_for_function("() => templatePhotoCache.has('product-3d')")
            scene_frame = page.frame_locator("#templatePreviewFrame").frame_locator('section[data-index="1"] iframe')
            scene_frame.locator("#view").wait_for(timeout=30000)
            scene_frame.locator("#status").wait_for(state="attached",timeout=30000)
            scene_frame.locator("#stats").wait_for(state="attached",timeout=30000)
            for attempt in range(50):
                scene_status = scene_frame.locator("#view").evaluate(
                    "el => window.MotionStudio3DLab?.getStatus() || null")
                if scene_status and scene_status.get("vertices",0) >= 100:
                    break
                page.wait_for_timeout(300)
            else:
                raise AssertionError(f"GLB scene did not load: {scene_status}")
            # Reveal the real GLB chapter before checking requestAnimationFrame:
            # background/offscreen iframes are intentionally throttled by browsers.
            page.frame_locator("#templatePreviewFrame").locator(
                'section[data-index="1"]').scroll_into_view_if_needed()
            before_drag = scene_frame.locator("#view").evaluate(
                "el => window.MotionStudio3DLab.getStatus()")
            assert before_drag["triangles"] >= 50, before_drag
            assert before_drag["vertices"] >= 100, before_drag
            assert before_drag["engine"]=="webgl2", before_drag
            for frame_attempt in range(30):
                before_drag = scene_frame.locator("#view").evaluate(
                    "el => window.MotionStudio3DLab.getStatus()")
                if before_drag["frames"] > 0:break
                page.wait_for_timeout(250)
            else:
                raise AssertionError(f"GLB renderer did not paint after scrolling into view: {before_drag}")
            scene_frame.locator("#view").dispatch_event("pointerdown",{
                "pointerId":1,"pointerType":"mouse","clientX":150,"clientY":160,
                "buttons":1,"bubbles":True
            })
            scene_frame.locator("#view").dispatch_event("pointermove",{
                "pointerId":1,"pointerType":"mouse","clientX":260,"clientY":190,
                "buttons":1,"bubbles":True
            })
            scene_frame.locator("#view").dispatch_event("pointerup",{
                "pointerId":1,"pointerType":"mouse","clientX":260,"clientY":190,
                "buttons":0,"bubbles":True
            })
            # A running renderer is required; software canvas2d fallback is disclosed
            # separately from WebGL2 and is not counted as hardware GPU validation.
            after_drag = scene_frame.locator("#view").evaluate("el => window.MotionStudio3DLab.getStatus()")
            assert after_drag["frames"] >= before_drag["frames"]
            assert abs(after_drag["angY"]-before_drag["angY"])>0.2, (before_drag,after_drag)
            assert abs(after_drag["angX"]-before_drag["angX"])>0.05, (before_drag,after_drag)
            assert after_drag["engine"] in ("WebGL2","Canvas2D","webgl2","canvas2d"), after_drag
            page.locator("#previewClose").click()
            # Return from product gallery preview to a real editor before
            # executing the existing back-to-library + blank-project journey.
            page.locator("[data-template-card='editorial']").click()
            page.locator("#previewUse").click()
            page.wait_for_function("() => project.templateId==='editorial'")
            assert page.locator("#editorView").is_visible()

            assert page.evaluate("registry.length")==20
            assert page.locator("#editorTimeline").evaluate("(e)=>e.classList.contains('collapsed')")
            page.locator("#backToLibrary").click()
            page.locator("#discoveryBlank").click()
            page.wait_for_function("() => project.sections.length===0")
            assert page.locator("#emptyStartAdd").is_visible()
            page.locator("#emptyStartAdd").click()
            assert page.locator('[data-asset-tier="l2"]').is_visible()
            page.locator("[data-section-preset]").first.click()
            page.wait_for_function("() => project.sections.length===1")
            # U3: preview is not an add action; it boots the actual component renderer.
            page.locator('[data-asset-tier-button="l3"]').click()
            count_before = page.evaluate("project.sections.length")
            page.locator("#componentList .comp .component-preview-trigger").first.click()
            assert page.locator("#componentPreview").is_visible()
            assert page.evaluate("project.sections.length")==count_before
            assert page.locator("#componentPreviewFrame").get_attribute("srcdoc")
            page.locator("#componentPreviewReplay").click()
            assert page.locator("#componentPreviewFrame").get_attribute("srcdoc")
            page.locator("#componentPreviewClose").click()
            assert page.locator("#componentPreview").is_hidden()
            page.locator("#componentList .comp .component-preview-trigger").first.click()
            page.locator("#componentPreviewAdd").click()
            page.wait_for_function("(before) => project.sections.length===before+1",arg=count_before)
            assert page.locator("#componentPreview").is_hidden()
            assert not errors,errors
            browser.close()
    finally:
        server.shutdown()
        server.server_close()

if __name__=="__main__":
    test_u1_u4_regression()
    print("U1-U4 visual flow regression passed")
