"""P0/P1/P3: real browser end-to-end user journey, not only renderer unit tests."""
from pathlib import Path
import json, traceback, os, threading
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from functools import partial
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
EDITOR=ROOT/"Motion-Studio-Stage15-Meshopt-OFFLINE.html"
REPORT=ROOT/("WEB_PRODUCT_E2E_RESULT_"+os.environ.get("MOTION_BROWSER","chromium").lower()+".json")
browser_name=os.environ.get("MOTION_BROWSER","chromium").strip().lower()
if browser_name not in ("chromium","firefox","webkit"):
    raise ValueError("MOTION_BROWSER must be chromium, firefox, or webkit")
result={"pass":False,"suite":"Motion Studio Web product E2E","checks":{},"errors":[],"browser":browser_name,
        "webkitIsSafari":False,"scope":"Desktop automated engine smoke, not native Safari/mobile device acceptance","browserDiagnostics":{"pageErrors":[],"consoleErrors":[],"failedRequests":[],"frames":[],"inlineScripts":[]}}
def check(name,condition):
    result["checks"][name]=bool(condition)
    assert condition,name

try:
    check("built_editor_exists",EDITOR.exists())
    # A real HTTP origin gives stable localStorage semantics across browser engines.
    server=ThreadingHTTPServer(("127.0.0.1",0),partial(SimpleHTTPRequestHandler,directory=str(ROOT)))
    server_thread=threading.Thread(target=server.serve_forever,daemon=True)
    server_thread.start()
    result["origin"]="http://127.0.0.1:<ephemeral>"
    with sync_playwright() as pw:
        engine=getattr(pw,browser_name)
        launch_args={"headless":True}
        if browser_name=="chromium":
            launch_args["args"]=["--no-sandbox","--use-gl=angle","--use-angle=swiftshader","--enable-webgl","--enable-unsafe-swiftshader"]
        browser=engine.launch(**launch_args)
        page=browser.new_page(viewport={"width":1280,"height":800},accept_downloads=True)
        page_errors=[]
        console_errors=[]
        failed_requests=[]
        page.on("pageerror",lambda e:page_errors.append({"message":str(e),"stack":getattr(e,"stack",None)}))
        page.on("console",lambda msg:console_errors.append({"text":msg.text,"location":msg.location}) if msg.type=="error" else None)
        page.on("requestfailed",lambda req:failed_requests.append({"url":req.url,"failure":req.failure}))
        page.goto(f"http://127.0.0.1:{server.server_port}/{EDITOR.name}",wait_until="domcontentloaded")
        page.wait_for_function("() => !!window.MotionStudioUnified && Array.isArray(window.MotionStudioUnified.registry)",timeout=15000)
        check("20_components",page.evaluate("window.MotionStudioUnified.registry.length")==20)
        check("template_discovery_default",page.locator("#discoveryView").is_visible())
        check("eight_full_templates",page.locator("[data-template-card]").count()==8)
        page.locator("[data-template-card='editorial']").click()
        page.locator("#previewUse").click()
        page.locator("#editorView").wait_for(state="visible")
        check("template_loaded",page.evaluate("project.sections.length")>0)
        page.locator("#projectName").fill("Web Product Acceptance")
        check("title_edited",page.evaluate("project.title")=="Web Product Acceptance")
        with page.expect_download() as saved:
            page.locator("#saveProject").click()
        saved_path=ROOT/("WEB_PRODUCT_E2E_PROJECT_"+browser_name+".json")
        saved.value.save_as(saved_path)
        data=json.loads(saved_path.read_text(encoding="utf8"))
        check("valid_saved_project",data.get("schema")=="motion-studio-composition-v1" and len(data["sections"])>0)
        page.once("dialog",lambda dlg:dlg.accept())
        page.locator("#newProject").click()
        check("new_project_empty",page.evaluate("project.sections.length")==0)
        check("new_project_draft_persisted",page.evaluate("JSON.parse(localStorage.getItem('motion-studio-draft-v1')).sections.length===0"))
        page.reload(wait_until="domcontentloaded")
        check("new_project_survives_reload",page.evaluate("project.sections.length===0"))
        page.locator("#resumeProject").click()
        page.locator("[data-asset-tier-button='l3']").click()
        check("all_components_in_library",page.locator("#componentList .comp").count()==20)
        # E6-02: exercise every real component preview, not merely registry presence.
        if browser_name=="chromium":
            effect_ids=page.evaluate("window.MotionStudioUnified.registry.slice(1).map(c=>c.id)")
            check("19_effects_discovered",len(effect_ids)==19)
            effect_results=[]
            for effect_id in effect_ids:
                page.locator(f'#componentList .comp[data-id="{effect_id}"] .component-preview-trigger').click()
                preview_frame=page.frame_locator("#componentPreviewFrame")
                preview_frame.locator("body").wait_for(state="visible",timeout=10000)
                page.wait_for_timeout(220)
                metrics=preview_frame.locator("body").evaluate("""body=>({
                    text:body.innerText.trim().length,
                    children:body.children.length,
                    height:Math.max(body.scrollHeight,document.documentElement.scrollHeight),
                    width:document.documentElement.scrollWidth,
                    viewport:innerWidth,
                    canvases:body.querySelectorAll('canvas').length,
                    animations:document.getAnimations({subtree:true}).length,
                    scripts:document.scripts.length
                })""")
                effect_results.append({"id":effect_id,**metrics})
                check("effect_"+effect_id+"_renders",metrics["text"]>0 and metrics["children"]>0 and metrics["height"]>0)
                check("effect_"+effect_id+"_no_horizontal_overflow",metrics["width"]<=metrics["viewport"]+48)
                page.locator("#componentPreviewClose").click()
            result["effectRegression"]={"count":len(effect_results),"items":effect_results}
        first_id=page.evaluate("window.MotionStudioUnified.registry[0].id")
        page.locator("#componentList .comp").first.locator(".component-add-trigger").click()
        check("component_add_via_ui",page.evaluate("(id)=>project.sections.length===1 && project.sections[0].id===id",first_id))
        # A newly added section initially has no .section-art node. Image upload must create it.
        import base64
        png_path=ROOT/("WEB_PRODUCT_E2E_IMAGE_"+browser_name+".png")
        png_path.write_bytes(base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVQIHWP4z8DwHwAFgAI/ScL/nwAAAABJRU5ErkJggg=="))
        page.locator("#propImage").set_input_files(str(png_path))
        page.wait_for_function("() => project.sections[0]?.image?.startsWith('data:image/png;base64,')")
        check("new_section_image_upload",page.locator(".section.selected .section-art").count()==1)
        page.locator("#clearImage").click()
        check("section_image_clear",page.evaluate("project.sections[0].image")=="" and page.locator(".section.selected .section-art").count()==0)

        check("component_add_persisted",page.evaluate("(id)=>JSON.parse(localStorage.getItem('motion-studio-draft-v1')).sections[0].id===id",first_id))
        page.reload(wait_until="domcontentloaded")
        check("component_add_survives_reload",page.evaluate("(id)=>project.sections.length===1 && project.sections[0].id===id",first_id))
        page.locator("#resumeProject").click()
        page.locator("#openFile").set_input_files(str(saved_path))
        page.wait_for_function("() => project.title === 'Web Product Acceptance' && project.sections.length > 0")
        check("import_resets_undo_history",page.locator("#undoBtn").is_disabled() and page.locator("#redoBtn").is_disabled())
        check("roundtrip_restored",page.evaluate("project.title")=="Web Product Acceptance" and page.evaluate("project.sections.length")==len(data["sections"]))
        page.reload(wait_until="domcontentloaded")
        check("imported_project_survives_reload",page.evaluate("project.title")=="Web Product Acceptance" and page.evaluate("project.sections.length")==len(data["sections"]))
        page.locator("#resumeProject").click()
        # Invalid project must be rejected without replacing the active project.
        invalid_path=ROOT/("WEB_PRODUCT_E2E_INVALID_"+browser_name+".json")
        invalid_path.write_text('{"schema":"unsupported","sections":[]}',encoding="utf8")
        before=page.evaluate("JSON.stringify(project)")
        page.locator("#openFile").set_input_files(str(invalid_path))
        page.wait_for_function("() => document.querySelector('#toast')?.textContent?.includes('打开失败') === true")
        check("invalid_import_preserves_project",page.evaluate("JSON.stringify(project)")==before)
        check("invalid_import_shows_error",page.locator("#toast").inner_text().find("打开失败")>=0)
        page.locator("#mobileView").click()
        check("mobile_preview",page.locator("#canvasWrap").evaluate("(el)=>el.classList.contains('mobile')"))
        page.locator("#desktopView").click()
        check("desktop_preview",not page.locator("#canvasWrap").evaluate("(el)=>el.classList.contains('mobile')"))
        with page.expect_download() as exported:
            page.locator("#exportPage").click()
        exported_path=ROOT/("WEB_PRODUCT_E2E_EXPORTED_"+browser_name+".html")
        exported.value.save_as(exported_path)
        html=exported_path.read_text(encoding="utf8")
        check("html_export",len(html)>1000 and "<!doctype html>" in html.lower() and "Web Product Acceptance" in html)
        exported_page=browser.new_page(viewport={"width":1200,"height":800})
        remote=[]
        exported_errors=[]
        exported_page.on("request",lambda r:remote.append(r.url) if r.url.startswith(("https://","http://")) else None)
        exported_page.on("pageerror",lambda e:exported_errors.append(str(e)))
        exported_page.set_content(html,wait_until="domcontentloaded")
        exported_page.wait_for_timeout(750)
        # R42 editorial intentionally exports one magazine spread per chapter,
        # not obsolete two-pane section.section + iframe wrappers.
        if data.get("templateId")=="editorial":
            check("exported_sections",exported_page.locator("section.e42-spread").count()==len(data["sections"]))
            check("editorial_has_no_nested_duplicated_demo",exported_page.locator("iframe").count()==0)
        else:
            check("exported_sections",exported_page.locator("section.section").count()==len(data["sections"]))
        check("offline_no_remote_requests",not remote)
        check("export_no_page_errors",not exported_errors)
        check("editor_no_page_errors",not page_errors)
        exported_page.close();page.close();browser.close()
    result["pass"]=all(result["checks"].values())
except Exception:
    result["errors"].append(traceback.format_exc(limit=6))
finally:
    if "server" in locals():
        server.shutdown()
        server.server_close()
    result["browserDiagnostics"]={"pageErrors":page_errors if "page_errors" in locals() else [],
        "consoleErrors":console_errors if "console_errors" in locals() else [],
        "failedRequests":failed_requests if "failed_requests" in locals() else [],
        "frames":[{"url":frame.url,"name":frame.name} for frame in page.frames] if "page" in locals() else [],
        "inlineScripts":page.locator("script").evaluate_all("""nodes=>nodes.map((s,i)=>({index:i,id:s.id||null,type:s.type||'text/javascript',src:s.src||null,length:(s.textContent||'').length,head:(s.textContent||'').slice(0,100)}))""") if "page" in locals() and not page.is_closed() else []}
    REPORT.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf8")
    print(json.dumps(result,ensure_ascii=False,indent=2))
assert result["pass"],"Web product E2E failed; inspect WEB_PRODUCT_E2E_RESULT.json"
