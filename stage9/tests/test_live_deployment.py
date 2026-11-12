"""P5 production URL smoke: GitHub Pages must serve a working editor, not a placeholder."""
import json, os, sys, traceback, hashlib
from pathlib import Path
from urllib.parse import urlparse, urljoin
from playwright.sync_api import sync_playwright

url=os.environ.get("MOTION_STUDIO_URL","").strip()
report={"url":url,"pass":False,"checks":{},"errors":[]}
screenshots=os.environ.get("MOTION_SCREENSHOT_DIR")
def capture(page,name):
    if screenshots:
        target=Path(screenshots)
        target.mkdir(parents=True,exist_ok=True)
        page.screenshot(path=str(target/(name+"-live.png")))
def verify(name,condition):
    report["checks"][name]=bool(condition)
    if not condition: raise AssertionError(name)
try:
    parsed=urlparse(url)
    verify("public_https_url",parsed.scheme=="https" and bool(parsed.netloc))
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True,args=["--no-sandbox","--use-gl=angle","--use-angle=swiftshader","--enable-webgl","--enable-unsafe-swiftshader"])
        page=browser.new_page(viewport={"width":1280,"height":800},accept_downloads=True)
        errors=[]
        page.on("pageerror",lambda e:errors.append(str(e)))
        response=page.goto(url,wait_until="domcontentloaded",timeout=45000)
        verify("served_successfully",response is not None and response.status==200)
        manifest_response=page.request.get(urljoin(url,"WEB_RELEASE.json"),timeout=45000)
        verify("release_manifest_served",manifest_response.status==200)
        manifest=manifest_response.json()
        html_bytes=response.body()
        observed_sha=hashlib.sha256(html_bytes).hexdigest()
        report["servedHtmlSha256"]=observed_sha
        report["manifestHtmlSha256"]=manifest.get("sha256")
        report["sourceCommit"]=manifest.get("sourceCommit")
        verify("served_html_matches_tested_release",observed_sha==manifest.get("sha256"))
        page.wait_for_timeout(300)
        verify("20_components",page.evaluate("typeof registry!=='undefined' && registry.length===20"))
        verify("template_discovery_default",page.locator("#discoveryView").is_visible())
        verify("eight_full_templates",page.locator("[data-template-card]").count()==8)
        capture(page,"template-library")
        page.locator("[data-template-card='editorial']").click()
        page.locator("#templatePreviewFrame").content_frame.locator("section.section").first.wait_for()
        capture(page,"immersive-preview")
        page.locator("#previewUse").click()
        page.locator("#editorView").wait_for(state="visible")
        verify("template_usable",page.evaluate("project.sections.length>0"))
        capture(page,"visual-editor")
        with page.expect_download() as download:
            page.locator("#saveProject").click()
        saved=Path("P5_LIVE_PROJECT.json")
        download.value.save_as(saved)
        value=json.loads(saved.read_text(encoding="utf8"))
        verify("downloaded_project_valid",value.get("schema")=="motion-studio-composition-v1" and len(value.get("sections",[]))>0)
        with page.expect_download() as download:
            page.locator("#exportPage").click()
        exported=Path("P5_LIVE_EXPORTED.html")
        download.value.save_as(exported)
        verify("html_export_nonempty",exported.stat().st_size>1000)
        verify("no_uncaught_page_errors",not errors)
        page.screenshot(path="P5_LIVE_EDITOR.png",full_page=True)
        browser.close()
    report["pass"]=all(report["checks"].values())
except Exception:
    report["errors"].append(traceback.format_exc(limit=5))
finally:
    Path("P5_LIVE_SMOKE.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf8")
    print(json.dumps(report,ensure_ascii=False,indent=2))
sys.exit(0 if report["pass"] else 1)
