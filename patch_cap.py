with open("src/agent/capabilities_base.py", "r") as f:
    code = f.read()

import re

# Replace synchronous tab.call_method with await asyncio.to_thread
code = re.sub(
    r'tab\.call_method\((.*)\)',
    r'await asyncio.to_thread(tab.call_method, \1)',
    code
)

with open("src/agent/capabilities_base.py", "w") as f:
    f.write(code)
