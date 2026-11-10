import AppKit
import WebKit
import Foundation

@main
final class MotionStudioApp: NSObject, NSApplicationDelegate, WKNavigationDelegate, WKDownloadDelegate, WKUIDelegate {
    private var window: NSWindow!
    private var webView: WKWebView!
    private let selfTest = CommandLine.arguments.contains("--self-test")

    static func main() {
        let app = NSApplication.shared
        let delegate = MotionStudioApp()
        app.delegate = delegate
        app.setActivationPolicy(.regular)
        app.run()
    }

    func applicationDidFinishLaunching(_ notification: Notification) {
        guard let file = Bundle.main.url(forResource: "Motion-Studio-Stage14-Stability-OFFLINE", withExtension: "html") else {
            NSAlert(error: NSError(domain: "MotionStudio", code: 1,
                userInfo: [NSLocalizedDescriptionKey: "Offline editor resource is missing from the application bundle."])).runModal()
            NSApp.terminate(nil)
            return
        }
        let config = WKWebViewConfiguration()
        config.defaultWebpagePreferences.allowsContentJavaScript = true
        config.websiteDataStore = .default()
        webView = WKWebView(frame: NSRect(x: 0, y: 0, width: 1420, height: 920), configuration: config)
        webView.navigationDelegate = self
        webView.uiDelegate = self
        webView.allowsBackForwardNavigationGestures = true
        window = NSWindow(contentRect: NSRect(x: 0, y: 0, width: 1420, height: 920),
                          styleMask: [.titled, .closable, .miniaturizable, .resizable],
                          backing: .buffered, defer: false)
        window.title = "Motion Studio"
        window.minSize = NSSize(width: 970, height: 650)
        window.center()
        window.contentView = webView
        window.makeKeyAndOrderFront(nil)
        NSApp.activate(ignoringOtherApps: true)
        // Explicit read access to the bundled document only; does not start a server.
        webView.loadFileURL(file, allowingReadAccessTo: file.deletingLastPathComponent())
    }

    func webView(_ webView: WKWebView, didFinish navigation: WKNavigation!) {
        guard selfTest else { return }
        let script = """
        (() => {
          try {
            const count = typeof registry === 'undefined' ? -1 : registry.length;
            const exportReady = typeof exportDocument === 'function';
            const hasThree = typeof stage9ThreeEngineURL === 'string'
                          && stage9ThreeEngineURL.startsWith('data:text/javascript;base64,');
            const hasShared = typeof stage9SharedEngineURL === 'string'
                           && stage9SharedEngineURL.startsWith('data:text/javascript;base64,');
            const gl = document.createElement('canvas').getContext('webgl2', {preserveDrawingBuffer:true});
            let drawnPixel = false;
            if (gl) {
              const vs = gl.createShader(gl.VERTEX_SHADER);
              gl.shaderSource(vs, '#version 300 es\\nvoid main(){vec2 p[3]=vec2[3](vec2(-1.,-1.),vec2(3.,-1.),vec2(-1.,3.));gl_Position=vec4(p[gl_VertexID],0.,1.);}');
              gl.compileShader(vs);
              const fs = gl.createShader(gl.FRAGMENT_SHADER);
              gl.shaderSource(fs, '#version 300 es\\nprecision highp float;out vec4 color;void main(){color=vec4(0.9,0.2,0.15,1.);}');
              gl.compileShader(fs);
              const program = gl.createProgram();
              gl.attachShader(program, vs);gl.attachShader(program, fs);
              gl.linkProgram(program);gl.useProgram(program);
              gl.viewport(0,0,300,150);
              gl.clearColor(0,0,0,1);gl.clear(gl.COLOR_BUFFER_BIT);
              gl.drawArrays(gl.TRIANGLES,0,3);
              const pixel = new Uint8Array(4);
              gl.readPixels(150,75,1,1,gl.RGBA,gl.UNSIGNED_BYTE,pixel);
              drawnPixel = gl.getError()===0 && pixel[0]>180 && pixel[1]>25 && pixel[2]<100;
            }
            const exported = exportReady ? exportDocument() : '';
            const exportPassed = exported.includes('motion-studio') && exported.length>15000;
            return { components: count, exportReady, exportPassed, hasThree, hasShared,
                     location: location.protocol, webgl2: !!gl, drawnPixel };
          } catch (error) { return { error: String(error) }; }
        })()
        """
        webView.evaluateJavaScript(script) { value, error in
            if let result = value as? [String: Any], error == nil,
               (result["components"] as? Int) == 20,
               (result["exportReady"] as? Bool) == true,
               (result["hasThree"] as? Bool) == true,
               (result["hasShared"] as? Bool) == true,
               (result["exportPassed"] as? Bool) == true,
               (result["drawnPixel"] as? Bool) == true,
               (result["location"] as? String) == "file:" {
                NSLog("MOTION_MAC_SELFTEST_PASS: %@", String(describing: result))
                fflush(stdout)
                exit(0)
            }
            NSLog("MOTION_MAC_SELFTEST_FAIL: %@ %@", String(describing: value), String(describing: error))
            fflush(stderr)
            exit(2)
        }
    }

    func applicationShouldTerminateAfterLastWindowClosed(_ sender: NSApplication) -> Bool { true }

    // Blob/file downloads from the exported editor remain local.
    @available(macOS 11.3, *)
    func webView(_ webView: WKWebView, navigationAction: WKNavigationAction, didBecome download: WKDownload) {
        download.delegate = self
    }

    @available(macOS 11.3, *)
    func webView(_ webView: WKWebView, navigationResponse: WKNavigationResponse, didBecome download: WKDownload) {
        download.delegate = self
    }

    @available(macOS 11.3, *)
    func download(_ download: WKDownload, decideDestinationUsing response: URLResponse,
                  suggestedFilename: String, completionHandler: @escaping (URL?) -> Void) {
        let downloads = FileManager.default.urls(for: .downloadsDirectory, in: .userDomainMask).first
            ?? FileManager.default.homeDirectoryForCurrentUser
        let cleanName = (suggestedFilename as NSString).lastPathComponent
        var destination = downloads.appendingPathComponent(cleanName.isEmpty ? "Motion-Studio-Export.html" : cleanName)
        if FileManager.default.fileExists(atPath: destination.path) {
            let stem = destination.deletingPathExtension().lastPathComponent
            let ext = destination.pathExtension
            let suffix = ISO8601DateFormatter().string(from: Date()).replacingOccurrences(of: ":", with: "-")
            destination = downloads.appendingPathComponent(stem + "-" + suffix + (ext.isEmpty ? "" : "." + ext))
        }
        completionHandler(destination)
    }

    @available(macOS 11.3, *)
    func download(_ download: WKDownload, didFailWithError error: Error, resumeData: Data?) {
        NSLog("Motion Studio download failed: %@", String(describing: error))
    }

    // Permits existing editor confirm()/prompt()/alert() actions.
    func webView(_ webView: WKWebView, runJavaScriptAlertPanelWithMessage message: String,
                 initiatedByFrame frame: WKFrameInfo, completionHandler: @escaping () -> Void) {
        let alert = NSAlert()
        alert.messageText = "Motion Studio"
        alert.informativeText = message
        alert.runModal()
        completionHandler()
    }

    func webView(_ webView: WKWebView, runJavaScriptConfirmPanelWithMessage message: String,
                 initiatedByFrame frame: WKFrameInfo, completionHandler: @escaping (Bool) -> Void) {
        let alert = NSAlert()
        alert.messageText = "Motion Studio"
        alert.informativeText = message
        alert.addButton(withTitle: "继续")
        alert.addButton(withTitle: "取消")
        completionHandler(alert.runModal() == .alertFirstButtonReturn)
    }

    func webView(_ webView: WKWebView, runOpenPanelWith parameters: WKOpenPanelParameters,
                 initiatedByFrame frame: WKFrameInfo, completionHandler: @escaping ([URL]?) -> Void) {
        let panel = NSOpenPanel()
        panel.allowsMultipleSelection = parameters.allowsMultipleSelection
        panel.canChooseDirectories = parameters.allowsDirectories
        panel.canChooseFiles = true
        panel.begin { result in completionHandler(result == .OK ? panel.urls : nil) }
    }
}
