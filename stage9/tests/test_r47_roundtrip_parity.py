"""R47: round-trip and exported composition parity for all eight templates."""
from pathlib import Path
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from functools import partial
import threading, json, os, traceback
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
EDITOR=ROOT/"Motion-Studio-Stage15-Meshopt-OFFLINE.html"
TEMPLATES=["editorial","product-3d","cinematic","architecture","agency","fashion","gallery","saas"]
report={"pass":False,"suite":"R47 eight-template save/reopen/export parity","templates":{},"errors":[],"browserDiagnostics":{"pageErrors":[],"consoleErrors":[]}}
server=None
try:
 server=ThreadingHTTPServer(("127.0.0.1",0),partial(SimpleHTTPRequestHandler,directory=str(ROOT)))
 threading.Thread(target=server.serve_forever,daemon=True).start()
 with sync_playwright() as pw:
  browser=pw.chromium.launch(headless=True,args=["--no-sandbox","--use-gl=angle","--use-angle=swiftshader","--enable-webgl","--enable-unsafe-swiftshader"])
  for template_id in TEMPLATES:
   page=browser.new_page(viewport={"width":1280,"height":800},accept_downloads=True)
   errors=[]
   console_errors=[]
   page.on("pageerror",lambda e:errors.append(str(e)))
   page.on("console",lambda msg:console_errors.append(msg.text) if msg.type=="error" else None)
   page.goto(f"http://127.0.0.1:{server.server_port}/{EDITOR.name}",wait_until="domcontentloaded")
   page.locator("#discoveryView").wait_for(state="visible",timeout=20000)
   page.locator("[data-template-card]").first.wait_for(state="visible",timeout=20000)
   assert page.locator("[data-template-card]").count()==8, f"{template_id}: template gallery did not initialize"
   page.locator(f"[data-template-card='{template_id}']").wait_for(state="visible",timeout=20000)
   page.locator(f"[data-template-card='{template_id}']").click()
   page.locator("#previewUse").click()
   page.locator("#editorView").wait_for(state="visible")
   assert page.evaluate("project.templateId") == template_id, f"{template_id}: wrong template loaded"
   assert page.evaluate("project.sections.length") > 0, f"{template_id}: no sections"
   with page.expect_download() as saved:
    page.locator("#saveProject").click()
   project_file=ROOT/f"R47_{template_id}.json"
   saved.value.save_as(project_file)
   project=json.loads(project_file.read_text(encoding="utf8"))
   assert project.get("templateId")==template_id and project.get("sections"), f"{template_id}: save payload mismatch"
   page.once("dialog",lambda dialog:dialog.accept())
   page.locator("#newProject").click()
   page.locator("#resumeProject").click()
   page.locator("#openFile").set_input_files(str(project_file))
   page.wait_for_function("(id)=>project.templateId===id && project.sections.length>0",arg=template_id)
   assert page.evaluate("project.templateId")==template_id, f"{template_id}: reopen mismatch"
   with page.expect_download() as exported:
    page.locator("#exportPage").click()
   html_file=ROOT/f"R47_{template_id}.html"
   exported.value.save_as(html_file)
   html=html_file.read_text(encoding="utf8")
   assert 'id="r45-export-composition"' in html, f"{template_id}: R45 composition CSS missing from export"
   assert 'id="r46-export-accessibility"' in html, f"{template_id}: R46 accessibility CSS missing from export"
   exported_page=browser.new_page(viewport={"width":1280,"height":800})
   export_errors=[]
   exported_page.on("pageerror",lambda e:export_errors.append(str(e)))
   exported_page.set_content(html,wait_until="domcontentloaded")
   exported_page.wait_for_timeout(350)
   section_count=exported_page.locator("section.section,section.e42-spread").count()
   assert section_count==len(project["sections"]), f"{template_id}: exported section count {section_count} != saved {len(project['sections'])}"
   geometry=exported_page.evaluate("({width:document.documentElement.scrollWidth,viewport:innerWidth,height:document.documentElement.scrollHeight})")
   assert geometry["width"]<=geometry["viewport"]+2, f"{template_id}: horizontal overflow {geometry}"
   assert not export_errors, f"{template_id}: exported page errors {export_errors}"
   assert not errors, f"{template_id}: editor page errors {errors}"
   report["templates"][template_id]={"sections":section_count,"exportBytes":len(html),"horizontalOverflow":max(0,geometry["width"]-geometry["viewport"]),"editorErrors":len(errors),"exportErrors":len(export_errors),"saveReopen":"pass","exportParity":"pass"}
   exported_page.close();page.close()
  browser.close()
 report["pass"]=len(report["templates"])==8
except Exception:
 report["errors"].append(traceback.format_exc(limit=8))
finally:
 if server:
  server.shutdown();server.server_close()
 report["browserDiagnostics"]={"pageErrors":errors if "errors" in locals() else [],"consoleErrors":console_errors if "console_errors" in locals() else []}
 (ROOT/"R47_ROUNDTRIP_PARITY.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf8")
 print(json.dumps(report,ensure_ascii=False,indent=2))
assert report["pass"],"R47 eight-template roundtrip/export parity failed"
