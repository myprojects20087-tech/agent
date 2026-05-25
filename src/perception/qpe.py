import asyncio
import hashlib
from playwright.async_api import Page
import base64

class DOMParser:
    def __init__(self):
        self.page: Page = None

    def set_page(self, page: Page):
        self.page = page

    async def parse(self):
        if not self.page:
            return {"nodes": [], "error": "No live page attached"}

        print("[QPE-L1] Executing real JS to extract live DOM semantic tree...")
        script = """
        () => {
            const interactables = Array.from(document.querySelectorAll('button, a, input, select, textarea, [role="button"]'));
            return interactables.filter(el => {
                const rect = el.getBoundingClientRect();
                return rect.width > 0 && rect.height > 0 && window.getComputedStyle(el).visibility !== 'hidden';
            }).map(el => {
                const rect = el.getBoundingClientRect();
                return {
                    tag: el.tagName.toLowerCase(),
                    text: el.innerText || el.value || el.placeholder || '',
                    x: Math.round(rect.x),
                    y: Math.round(rect.y),
                    width: Math.round(rect.width),
                    height: Math.round(rect.height)
                };
            });
        }
        """
        try:
            raw_nodes = await self.page.evaluate(script)
            nodes = []
            for n in raw_nodes:
                nid = self._hash_node(n['tag'], n['text'], f"{n['x']},{n['y']}")
                n["nexus_id"] = nid
                nodes.append(n)
            return {"nodes": nodes, "count": len(nodes)}
        except Exception as e:
            return {"nodes": [], "error": str(e)}

    def _hash_node(self, tag, text, position):
        return hashlib.sha256(f"{tag}-{text}-{position}".encode()).hexdigest()[:12]

class VLMGrounding:
    def __init__(self):
        self.page: Page = None

    def set_page(self, page: Page):
        self.page = page

    async def ground(self):
        if not self.page:
            return {"visual_elements": [], "error": "No live page attached"}

        print("[QPE-L2] Capturing real viewport screenshot for VLM Grounding...")
        try:
            screenshot_bytes = await self.page.screenshot(type="jpeg", quality=75)
            b64_img = base64.b64encode(screenshot_bytes).decode('utf-8')
            return {"screenshot_b64": b64_img[:50] + "...(truncated)", "ready": True}
        except Exception as e:
            return {"error": str(e)}

class AccessibilityFusion:
    def __init__(self):
        self.page: Page = None

    def set_page(self, page: Page):
        self.page = page

    async def extract(self):
        if not self.page:
             return {"a11y_tree": {}}
        print("[QPE-L3] Extracting native A11y tree snapshot...")
        try:
            snapshot = await self.page.accessibility.snapshot()
            return {"a11y_tree": snapshot}
        except Exception:
            return {"a11y_tree": {}}

class TemporalBehavioralEngine:
    def __init__(self):
        self.page: Page = None

    def set_page(self, page: Page):
        self.page = page

    async def analyze(self):
        if not self.page:
            return {"is_stable": True}
        print("[QPE-L4] Waiting for network idle state...")
        try:
            await self.page.wait_for_load_state("networkidle", timeout=2000)
            return {"is_stable": True, "network_idle": True}
        except:
            return {"is_stable": False, "network_idle": False}

class QuadLayerPerceptionEngine:
    def __init__(self):
        self.dom_parser = DOMParser()
        self.vlm_grounding = VLMGrounding()
        self.a11y_fusion = AccessibilityFusion()
        self.temporal_engine = TemporalBehavioralEngine()
        self.live_page = None

    def set_live_page(self, page: Page):
        self.live_page = page
        self.dom_parser.set_page(page)
        self.vlm_grounding.set_page(page)
        self.a11y_fusion.set_page(page)
        self.temporal_engine.set_page(page)

    async def perceive(self):
        print("\n[QPE] Initiating Live Perception Cycle on Page...")
        if not self.live_page:
             print("[QPE] Error: No page bound to perception engine.")
             return {}

        dom, vis, a11y, temp = await asyncio.gather(
            self.dom_parser.parse(),
            self.vlm_grounding.ground(),
            self.a11y_fusion.extract(),
            self.temporal_engine.analyze()
        )

        return {
            "url": self.live_page.url,
            "title": await self.live_page.title(),
            "dom": dom,
            "visual": vis,
            "a11y": a11y,
            "temporal": temp,
        }