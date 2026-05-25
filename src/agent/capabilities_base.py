import asyncio
import json
import random

def clean_json(text: str) -> str:
    if "```json" in text:
        return text.split("```json")[1].split("```")[0].strip()
    elif "```" in text:
        return text.split("```")[1].split("```")[0].strip()
    return text.strip()

class CapabilityModules:
    @staticmethod
    async def execute_action(tab, action: str) -> dict:
        if not tab:
            print("[Capabilities] WARNING: No live tab. Skipping real CDP execution.")
            return {"status": "skipped_no_tab"}

        try:
            if "navigate to" in action.lower():
                url = action.split("navigate to ")[-1].strip()
                if not url.startswith("http"): url = "https://" + url
                print(f"[Capabilities] Executing raw CDP Page.navigate to: {url}")
                await asyncio.wait_for(asyncio.to_thread(tab.call_method, "Page.navigate", url=url), timeout=10.0)
                return {"status": "success", "action": "navigate"}

            action = clean_json(action)
            cmd = json.loads(action)
            action_type = cmd.get("type")

            if action_type == "navigate":
                url = cmd.get("url")
                print(f"[Capabilities] Executing raw CDP Page.navigate to: {url}")
                await asyncio.wait_for(asyncio.to_thread(tab.call_method, "Page.navigate", url=url), timeout=10.0)

            elif action_type == "click":
                x = cmd.get("x", 100) + random.uniform(-2, 2)
                y = cmd.get("y", 100) + random.uniform(-2, 2)

                print(f"[Capabilities] Executing raw CDP Input.dispatchMouseEvent at ({x}, {y})")
                await asyncio.wait_for(asyncio.to_thread(tab.call_method, "Input.dispatchMouseEvent", type="mouseMoved", x=x, y=y), timeout=10.0)
                await asyncio.wait_for(asyncio.to_thread(tab.call_method, "Input.dispatchMouseEvent", type="mousePressed", x=x, y=y, button="left", clickCount=1), timeout=10.0)
                await asyncio.wait_for(asyncio.to_thread(tab.call_method, "Input.dispatchMouseEvent", type="mouseReleased", x=x, y=y, button="left", clickCount=1), timeout=10.0)

            elif action_type == "type":
                text = cmd.get("text", "")
                print(f"[Capabilities] Executing raw CDP Input.dispatchKeyEvent for text: '{text}'")
                for char in text:
                    await asyncio.wait_for(asyncio.to_thread(tab.call_method, "Input.dispatchKeyEvent", type="char", text=char), timeout=10.0)
                    await asyncio.sleep(random.uniform(0.05, 0.15))

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
