"""P0/P1/P3: real browser end-to-end user journey, not only renderer unit tests."""
from pathlib import Path
import json, traceback, os
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
EDITOR=ROOT/"Motion-Studio-Stage15-Meshopt-OFFLINE.html"
REPORT=ROOT/("WEB_PRODUCT_E2E_RESULT_"+os.environ.get("MOTION_BROWSER","chromium").lower()+".json")
browser_name=os.environ.get("MOTION_BROWSER","chromium").strip().lower()
if browser_name not in ("chromium","firefox","webkit"):
    raise ValueError("MOTION_BROWSER must be chromium, firefox, or webkit")
result={"pass":False,"suite":"Motion Studio Web product E2E","checks":{},"errors":[],"browser":browser_name,
        "webkitIsSafari":False,"scope":"Desktop automated engine smoke, not native Safari/mobile device acceptance"}
def check(name,condition):
    result["checks"][name]=bool(condition)
    assert condition,name

try:
    check("built_editor_exists",EDITOR.exists())
    with sync_playwright() as pw:
        engine=getattr(pw,browser_name)
        launch_args={"headless":True}
        if browser_name=="chromium":
            launch_args["args"]=["--no-sandbox","--use-gl=angle","--use-angle=swiftshader","--enable-webgl","--enable-unsafe-swiftshader"]
        browser=engine.launch(**launch_args)
        page=browser.new_page(viewport={"width":1280,"height":800},accept_downloads=True)
        page_errors=[]
        page.on("pageerror",lambda e:page_errors.append(str(e)))
        page.set_content(EDITOR.read_text(encoding="utf8"),wait_until="domcontentloaded")
        check("20_components",page.evaluate("registry.length")==20)
        page.locator("#loadTemplate").click()
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
        page.locator("#openFile").set_input_files(str(saved_path))
        check("roundtrip_restored",page.evaluate("project.title")=="Web Product Acceptance" and page.evaluate("project.sections.length")==len(data["sections"]))
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
        check("exported_sections",exported_page.locator("section.section").count()==len(data["sections"]))
        check("offline_no_remote_requests",not remote)
        check("export_no_page_errors",not exported_errors)
        check("editor_no_page_errors",not page_errors)
        exported_page.close();page.close();browser.close()
    result["pass"]=all(result["checks"].values())
except Exception:
    result["errors"].append(traceback.format_exc(limit=6))
finally:
    REPORT.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf8")
    print(json.dumps(result,ensure_ascii=False,indent=2))
assert result["pass"],"Web product E2E failed; inspect WEB_PRODUCT_E2E_RESULT.json"
