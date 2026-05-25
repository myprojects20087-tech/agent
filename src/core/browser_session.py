import asyncio
import subprocess
import pychrome
import os
import signal
from typing import Optional

class BrowserSession:
    def __init__(self, agent):
        self.agent = agent
        self.browser = None
        self.tab = None
        self.process: Optional[subprocess.Popen] = None

    async def __aenter__(self):
        print("[BrowserSession] Launching hardened Chrome instance via CDP...")

        # Production-grade flags for maximum evasion and stability
        command = [
            "google-chrome",
            "--remote-debugging-port=9222",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-infobars",
            "--disable-blink-features=AutomationControlled",
            "--disable-web-security", # Necessary for cross-origin iframe inspection
            "--window-size=1280,800",
            "--hide-scrollbars",
            "--mute-audio",
            "--disable-gpu", # Ensures stability in headless docker envs
            "--headless=new" # New headless mode behaves closer to real browser
        ]

        try:
            # Pre-exec fn ensures the child process dies if the parent dies
            self.process = subprocess.Popen(
                command,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                preexec_fn=os.setsid
            )

            # Smart polling for CDP port availability
            for _ in range(10):
                try:
                    self.browser = pychrome.Browser(url="http://127.0.0.1:9222")
                    self.tab = self.browser.new_tab()
                    break
                except Exception:
                    await asyncio.sleep(0.5)

            if not self.tab:
                raise ConnectionError("Failed to connect to Chrome CDP port 9222.")

            self.tab.start()

            # Setup domains natively
            self.tab.call_method("Network.enable")
            self.tab.call_method("Page.enable")
            self.tab.call_method("DOM.enable")
            self.tab.call_method("Runtime.enable")

            # Inject stealth JS early to mask CDP signatures
            stealth_js = """
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            window.chrome = { runtime: {} };
            """
            self.tab.call_method("Page.addScriptToEvaluateOnNewDocument", source=stealth_js)

            print("[BrowserSession] Hardened CDP connection established.")
            self.agent.qpe.set_live_tab(self.tab)
            self.agent.tab = self.tab

        except FileNotFoundError:
            print("[BrowserSession] ERROR: google-chrome executable missing. Running in mock/headless dev mode.")
            self.agent.tab = None

        except Exception as e:
            print(f"[BrowserSession] Critical launch failure: {e}")
            await self.__aexit__(None, None, None)
            raise

        return self

    async def __aexit__(self, exc_type, exc, tb):
        print("[BrowserSession] Executing clean teardown sequence.")
        try:
            if self.tab:
                self.tab.stop()
                self.browser.close_tab(self.tab)
        except Exception as e:
            print(f"[BrowserSession] Tab close error: {e}")

        if self.process:
            try:
                os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
                self.process.wait(timeout=2)
            except Exception:
                pass # Already dead

    async def run(self, task: str):
        return await self.agent.run(task)