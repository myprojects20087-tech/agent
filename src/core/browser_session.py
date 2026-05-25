import asyncio
from playwright.async_api import async_playwright

class BrowserSession:
    def __init__(self, agent):
        self.agent = agent
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    async def __aenter__(self):
        print("[BrowserSession] Booting real Chromium instance via Playwright...")
        self.playwright = await async_playwright().start()

        # Apply anti-detection stealth flags natively available
        self.browser = await self.playwright.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-infobars"
            ]
        )
        self.context = await self.browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800}
        )
        self.page = await self.context.new_page()

        # Override navigator.webdriver
        await self.page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        # Link the live page back to the agent's perception engine
        self.agent.qpe.set_live_page(self.page)
        self.agent.page = self.page # direct access for capabilities

        return self

    async def __aexit__(self, exc_type, exc, tb):
        print("[BrowserSession] Shutting down browser instance.")
        if self.page:
            await self.page.close()
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def run(self, task: str):
        return await self.agent.run(task)