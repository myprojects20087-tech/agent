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

        print("[QPE-L1] Executing Set-of-Marks (SoM) Injection & DOM Extraction...")
        script = """
        () => {
            // Remove previous SoM overlays if they exist
            document.querySelectorAll('.nexus-som-overlay').forEach(e => e.remove());

            const interactables = Array.from(document.querySelectorAll('button, a, input, select, textarea, [role="button"], [role="link"], [role="menuitem"]'));

            let nodes = [];
            let counter = 1;

            interactables.forEach(el => {
                const rect = el.getBoundingClientRect();
                const style = window.getComputedStyle(el);

                // Visibility checks
                if (rect.width > 0 && rect.height > 0 && style.visibility !== 'hidden' && style.display !== 'none' && style.opacity > 0) {

                    // Draw SoM label for VLM grounding
                    const label = document.createElement('div');
                    label.className = 'nexus-som-overlay';
                    label.textContent = counter;
                    Object.assign(label.style, {
                        position: 'absolute',
                        left: (rect.left + window.scrollX) + 'px',
                        top: (rect.top + window.scrollY - 10) + 'px',
                        backgroundColor: '#ff0000',
                        color: '#ffffff',
                        border: '1px solid white',
                        fontSize: '10px',
                        fontWeight: 'bold',
                        padding: '1px 3px',
                        zIndex: 2147483647,
                        pointerEvents: 'none'
                    });
                    document.body.appendChild(label);

                    // Draw Bounding Box
                    const box = document.createElement('div');
                    box.className = 'nexus-som-overlay';
                    Object.assign(box.style, {
                        position: 'absolute',
                        left: (rect.left + window.scrollX) + 'px',
                        top: (rect.top + window.scrollY) + 'px',
                        width: rect.width + 'px',
                        height: rect.height + 'px',
                        border: '2px solid rgba(255, 0, 0, 0.5)',
                        zIndex: 2147483646,
                        pointerEvents: 'none'
                    });
                    document.body.appendChild(box);

                    nodes.push({
                        som_id: counter.toString(),
                        tag: el.tagName.toLowerCase(),
                        text: el.innerText || el.value || el.placeholder || el.getAttribute('aria-label') || '',
                        x: Math.round(rect.left + (rect.width / 2)),
                        y: Math.round(rect.top + (rect.height / 2))
                    });
                    counter++;
                }
            });
            return nodes;
        }
        """
        try:
            result = await asyncio.wait_for(asyncio.to_thread(self.tab.call_method, "Runtime.evaluate", expression=script, returnByValue=True), timeout=10.0)
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

        print("[QPE-L2] Capturing Annotated SoM Screenshot via Page.captureScreenshot...")
        try:
            result = await asyncio.wait_for(asyncio.to_thread(self.tab.call_method, "Page.captureScreenshot", format="jpeg", quality=80), timeout=10.0)
            b64_img = result.get("data", "")

            # Clean up SoM overlays after screenshot
            cleanup_script = "document.querySelectorAll('.nexus-som-overlay').forEach(e => e.remove());"
            await asyncio.wait_for(asyncio.to_thread(self.tab.call_method, "Runtime.evaluate", expression=cleanup_script), timeout=10.0)

            return {"screenshot_b64": b64_img, "ready": True}
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
            snapshot = await asyncio.wait_for(asyncio.to_thread(self.tab.call_method, "Accessibility.getFullAXTree"), timeout=10.0)
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

    async def perceive(self, skip_vision=False):
        print("\n[QPE] Initiating Live Perception Cycle via CDP...")
        if not self.live_tab:
             print("[QPE] Warning: No real tab bound. Returning mock state.")
             return {"url": "mock", "title": "mock"}

        try:
            nav_history = await asyncio.wait_for(asyncio.to_thread(self.live_tab.call_method, "Page.getNavigationHistory"), timeout=10.0)
            idx = nav_history.get("currentIndex", 0)
            entries = nav_history.get("entries", [])
            url = entries[idx]["url"] if entries else ""
            title = entries[idx]["title"] if entries else ""
        except:
            url, title = "", ""

        # Sequence matters for SoM: DOM parsing draws the boxes, Grounding takes the shot, then cleans up.
        dom = await self.dom_parser.parse()
        vis = await self.vlm_grounding.ground() if not skip_vision else {}
        a11y = await self.a11y_fusion.extract()
        temp = await self.temporal_engine.analyze()

        return {
            "url": url,
            "title": title,
            "dom": dom,
            "visual": vis,
            "a11y": a11y,
            "temporal": temp,
        }