import asyncio
import subprocess
import pychrome
import time

class BrowserSession:
    def __init__(self, agent):
        self.agent = agent
        self.browser = None
        self.tab = None
        self.process = None

    async def __aenter__(self):
        print("[BrowserSession] Launching Google Chrome via subprocess for direct CDP control...")

        # Launch real chrome with debugging port, non-headless by default as per PRD
        command = [
            "google-chrome",
            "--remote-debugging-port=9222",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-infobars",
            "--disable-blink-features=AutomationControlled"
        ]

        # In this container environment, we'll try launching it, but fallback gracefully if missing
        try:
            self.process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            await asyncio.sleep(2) # Wait for Chrome to boot

            self.browser = pychrome.Browser(url="http://127.0.0.1:9222")
            self.tab = self.browser.new_tab()
            self.tab.start()

            # Setup network and page domains
            self.tab.call_method("Network.enable")
            self.tab.call_method("Page.enable")
            self.tab.call_method("DOM.enable")
            self.tab.call_method("Runtime.enable")

            print("[BrowserSession] Connected to real Chrome via pychrome (CDP)")
            self.agent.qpe.set_live_tab(self.tab)
            self.agent.tab = self.tab # Provide access to capabilities

        except FileNotFoundError:
            print("[BrowserSession] ERROR: google-chrome not found on system. Ensure it is installed.")
            # We don't crash, but pass a None tab to let the system mock gracefully if needed for tests

        return self

    async def __aexit__(self, exc_type, exc, tb):
        print("[BrowserSession] Shutting down CDP browser instance.")
        if self.tab:
            self.tab.stop()
            self.browser.close_tab(self.tab)
        if self.process:
            self.process.terminate()

    async def run(self, task: str):
        return await self.agent.run(task)