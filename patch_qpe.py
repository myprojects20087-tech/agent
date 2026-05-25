with open("src/perception/qpe.py", "r") as f:
    code = f.read()

# Replace synchronous self.tab.call_method with await asyncio.to_thread(self.tab.call_method, ...)
import re

# We need to make sure we don't double replace if we run it multiple times, but this is a one-off
code = re.sub(
    r'self\.tab\.call_method\("Runtime\.evaluate", expression=script, returnByValue=True\)',
    'await asyncio.to_thread(self.tab.call_method, "Runtime.evaluate", expression=script, returnByValue=True)',
    code
)

code = re.sub(
    r'self\.tab\.call_method\("Page\.captureScreenshot", format="jpeg", quality=80\)',
    'await asyncio.to_thread(self.tab.call_method, "Page.captureScreenshot", format="jpeg", quality=80)',
    code
)

code = re.sub(
    r'self\.tab\.call_method\("Runtime\.evaluate", expression=cleanup_script\)',
    'await asyncio.to_thread(self.tab.call_method, "Runtime.evaluate", expression=cleanup_script)',
    code
)

code = re.sub(
    r'self\.tab\.call_method\("Accessibility\.getFullAXTree"\)',
    'await asyncio.to_thread(self.tab.call_method, "Accessibility.getFullAXTree")',
    code
)

code = re.sub(
    r'self\.live_tab\.call_method\("Page\.getNavigationHistory"\)',
    'await asyncio.to_thread(self.live_tab.call_method, "Page.getNavigationHistory")',
    code
)

with open("src/perception/qpe.py", "w") as f:
    f.write(code)
