"""Capture catalog thumbnails from the same exported documents users preview."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import threading

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parent
EDITOR = ROOT / "Motion-Studio-Stage15-Meshopt-OFFLINE.html"
DESTINATION = ROOT / "template-thumbnails"


def main():
    DESTINATION.mkdir(exist_ok=True)
    server = ThreadingHTTPServer(
        ("127.0.0.1", 0), partial(SimpleHTTPRequestHandler, directory=str(ROOT))
    )
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True, args=["--no-sandbox"])
            editor = browser.new_page(viewport={"width": 1280, "height": 720})
            editor.goto(
                f"http://127.0.0.1:{server.server_port}/{EDITOR.name}",
                wait_until="domcontentloaded",
            )
            template_ids = editor.evaluate(
                "MotionStudioUnified.templates.map(template => template.id)"
            )
            for template_id in template_ids:
                html = editor.evaluate(
                    "id => buildTemplatePreviewDocument(id)", template_id
                )
                preview = browser.new_page(viewport={"width": 1280, "height": 720})
                preview.set_content(html, wait_until="domcontentloaded")
                preview.locator("section.section iframe").first.wait_for()
                preview.wait_for_timeout(1400)
                preview.screenshot(
                    path=str(DESTINATION / f"{template_id}.jpg"),
                    type="jpeg",
                    quality=76,
                )
                preview.close()
            browser.close()
    finally:
        server.shutdown()
        server.server_close()


if __name__ == "__main__":
    main()
