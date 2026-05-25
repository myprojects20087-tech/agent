import asyncio
import json
import random

class CapabilityModules:
    @staticmethod
    async def execute_action(tab, action: str) -> dict:
        """
        Executes a raw CDP action (Input.dispatchMouseEvent, Page.navigate) based on the Brain's command string.
        """
        if not tab:
            print("[Capabilities] WARNING: No live tab. Skipping real CDP execution.")
            return {"status": "skipped_no_tab"}

        try:
            # Simple heuristic parsing if the Brain returns plain text
            if "navigate to" in action.lower():
                url = action.split("navigate to ")[-1].strip()
                if not url.startswith("http"): url = "https://" + url
                print(f"[Capabilities] Executing raw CDP Page.navigate to: {url}")
                await asyncio.to_thread(tab.call_method, "Page.navigate", url=url)
                return {"status": "success", "action": "navigate"}

            cmd = json.loads(action)
            action_type = cmd.get("type")

            if action_type == "navigate":
                url = cmd.get("url")
                print(f"[Capabilities] Executing raw CDP Page.navigate to: {url}")
                await asyncio.to_thread(tab.call_method, "Page.navigate", url=url)

            elif action_type == "click":
                # For a real click, we need x, y coordinates from QPE.
                # Here we simulate the raw CDP Input dispatch with biometric jitter
                x = cmd.get("x", 100) + random.uniform(-2, 2)
                y = cmd.get("y", 100) + random.uniform(-2, 2)

                print(f"[Capabilities] Executing raw CDP Input.dispatchMouseEvent at ({x}, {y})")
                await asyncio.to_thread(tab.call_method, "Input.dispatchMouseEvent", type="mouseMoved", x=x, y=y)
                await asyncio.to_thread(tab.call_method, "Input.dispatchMouseEvent", type="mousePressed", x=x, y=y, button="left", clickCount=1)
                await asyncio.to_thread(tab.call_method, "Input.dispatchMouseEvent", type="mouseReleased", x=x, y=y, button="left", clickCount=1)

            elif action_type == "type":
                text = cmd.get("text", "")
                print(f"[Capabilities] Executing raw CDP Input.dispatchKeyEvent for text: '{text}'")
                for char in text:
                    await asyncio.to_thread(tab.call_method, "Input.dispatchKeyEvent", type="char", text=char)
                    await asyncio.sleep(random.uniform(0.05, 0.15)) # Typing cadence

            else:
                return {"status": "error", "reason": f"Unknown action type: {action_type}"}

            await asyncio.sleep(0.5)
            return {"status": "success"}

        except json.JSONDecodeError:
            print(f"[Capabilities] Action was not JSON. Fallback text: {action}")
            return {"status": "error", "reason": "Failed to parse JSON action."}
        except Exception as e:
            print(f"[Capabilities] Real CDP execution failed: {e}")
            return {"status": "error", "reason": str(e)}