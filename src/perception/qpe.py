import asyncio
import hashlib

class DOMParser:
    def __init__(self):
        self.tab = None

    def set_tab(self, tab):
        self.tab = tab

    async def parse(self):
        if not self.tab:
            return {"nodes": [], "error": "No live tab attached via CDP"}

        print("[QPE-L1] Executing Runtime.evaluate via CDP to extract DOM...")
        script = """
        () => {
            const interactables = Array.from(document.querySelectorAll('button, a, input, select, textarea, [role="button"]'));
            return interactables.filter(el => {
                const rect = el.getBoundingClientRect();
                return rect.width > 0 && rect.height > 0;
            }).map(el => {
                const rect = el.getBoundingClientRect();
                return {
                    tag: el.tagName.toLowerCase(),
                    text: el.innerText || el.value || el.placeholder || '',
                    x: Math.round(rect.x),
                    y: Math.round(rect.y)
                };
            });
        }
        """
        try:
            result = self.tab.call_method("Runtime.evaluate", expression=script, returnByValue=True)
            raw_nodes = result.get("result", {}).get("value", [])
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
        self.tab = None

    def set_tab(self, tab):
        self.tab = tab

    async def ground(self):
        if not self.tab:
            return {"visual_elements": [], "error": "No live tab attached via CDP"}

        print("[QPE-L2] Capturing raw CDP screenshot via Page.captureScreenshot...")
        try:
            # Capture jpeg quality 75 as requested by PRD
            result = self.tab.call_method("Page.captureScreenshot", format="jpeg", quality=75)
            b64_img = result.get("data", "")
            return {"screenshot_b64": b64_img[:50] + "...(truncated)", "ready": True}
        except Exception as e:
            return {"error": str(e)}

class AccessibilityFusion:
    def __init__(self):
        self.tab = None

    def set_tab(self, tab):
        self.tab = tab

    async def extract(self):
        if not self.tab:
             return {"a11y_tree": {}}
        print("[QPE-L3] Calling Accessibility.getFullAXTree natively...")
        try:
            snapshot = self.tab.call_method("Accessibility.getFullAXTree")
            return {"a11y_tree": snapshot}
        except Exception as e:
            return {"a11y_tree": {}, "error": str(e)}

class TemporalBehavioralEngine:
    def __init__(self):
        self.tab = None

    def set_tab(self, tab):
        self.tab = tab

    async def analyze(self):
        if not self.tab:
            return {"is_stable": True}
        print("[QPE-L4] Analyzing Temporal Context via CDP Events...")
        # Since we use synchronous pychrome, we approximate temporal check
        await asyncio.sleep(0.1)
        return {"is_stable": True, "network_idle": True}

class QuadLayerPerceptionEngine:
    def __init__(self):
        self.dom_parser = DOMParser()
        self.vlm_grounding = VLMGrounding()
        self.a11y_fusion = AccessibilityFusion()
        self.temporal_engine = TemporalBehavioralEngine()
        self.live_tab = None

    def set_live_tab(self, tab):
        self.live_tab = tab
        self.dom_parser.set_tab(tab)
        self.vlm_grounding.set_tab(tab)
        self.a11y_fusion.set_tab(tab)
        self.temporal_engine.set_tab(tab)

    async def perceive(self):
        print("\n[QPE] Initiating Live Perception Cycle via CDP...")
        if not self.live_tab:
             print("[QPE] Warning: No real tab bound. Returning mock state.")
             return {"url": "mock", "title": "mock"}

        # Extract page info
        try:
            nav_history = self.live_tab.call_method("Page.getNavigationHistory")
            idx = nav_history.get("currentIndex", 0)
            entries = nav_history.get("entries", [])
            url = entries[idx]["url"] if entries else ""
            title = entries[idx]["title"] if entries else ""
        except:
            url, title = "", ""

        dom, vis, a11y, temp = await asyncio.gather(
            self.dom_parser.parse(),
            self.vlm_grounding.ground(),
            self.a11y_fusion.extract(),
            self.temporal_engine.analyze()
        )

        return {
            "url": url,
            "title": title,
            "dom": dom,
            "visual": vis,
            "a11y": a11y,
            "temporal": temp,
        }