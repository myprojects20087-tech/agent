import asyncio
import json

class CapabilityModules:
    @staticmethod
    async def execute_action(page, action: str) -> dict:
        """
        Executes a real Playwright action based on the Brain's command string.
        Action format expected: JSON string like {"type": "click", "selector": "button.submit"}
        or {"type": "type", "selector": "input#search", "text": "hello"}
        or {"type": "navigate", "url": "https://google.com"}
        """
        try:
            # Simple heuristic parsing if the Brain returns plain text instead of JSON
            if "navigate to" in action.lower():
                url = action.split("navigate to ")[-1].strip()
                if not url.startswith("http"): url = "https://" + url
                print(f"[Capabilities] Executing REAL Navigation to: {url}")
                await page.goto(url)
                return {"status": "success", "action": "navigate"}

            cmd = json.loads(action)
            action_type = cmd.get("type")
            selector = cmd.get("selector")

            if action_type == "navigate":
                url = cmd.get("url")
                print(f"[Capabilities] Executing REAL Navigation to: {url}")
                await page.goto(url)

            elif action_type == "click":
                print(f"[Capabilities] Executing REAL Click on: {selector}")
                # Use strict locator to click the exact element
                element = page.locator(selector).first
                await element.scroll_into_view_if_needed()
                await element.click()

            elif action_type == "type":
                text = cmd.get("text", "")
                print(f"[Capabilities] Executing REAL Type '{text}' into: {selector}")
                element = page.locator(selector).first
                await element.scroll_into_view_if_needed()
                await element.fill(text)

            elif action_type == "extract":
                print("[Capabilities] Executing REAL text extraction")
                element = page.locator(selector).first
                text = await element.inner_text()
                return {"status": "success", "extracted_text": text}

            else:
                return {"status": "error", "reason": f"Unknown action type: {action_type}"}

            # Wait a beat for UI to settle
            await asyncio.sleep(0.5)
            return {"status": "success"}

        except json.JSONDecodeError:
            print(f"[Capabilities] Action was not JSON. Attempting fallback text interpretation: {action}")
            # Fallback logic if LLM doesn't output strict JSON
            return {"status": "error", "reason": "Failed to parse JSON action."}
        except Exception as e:
            print(f"[Capabilities] Real execution failed: {e}")
            return {"status": "error", "reason": str(e)}