import AppKit
import WebKit
import Foundation

@main
final class MotionStudioApp: NSObject, NSApplicationDelegate, WKNavigationDelegate, WKDownloadDelegate, WKUIDelegate {
    private var window: NSWindow!
    private var webView: WKWebView!

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
