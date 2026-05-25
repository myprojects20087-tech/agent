import re

with open("src/api/server.py", "r") as f:
    code = f.read()

# Replace the fast-but-unsafe fire-and-forget startup with a proper managed startup
old_startup = """@app.on_event("startup")
async def startup_event():
    global global_agent
    global_agent = NexusAgent(mode="distributed")
    # Boot the real background browser session to persist across requests
    # In production, this should handle concurrent sessions per user.
    asyncio.create_task(keep_browser_alive())

async def keep_browser_alive():
    global global_agent
    async with global_agent.session() as _:
        while True:
            await asyncio.sleep(3600) # Keep alive loop"""

new_startup = """global_session_manager = None

@app.on_event("startup")
async def startup_event():
    global global_agent, global_session_manager
    global_agent = NexusAgent(mode="distributed")
    print("[API] Global Nexus Agent initialized securely. Booting Browser Enclave...")

    # Properly await the browser boot sequence before accepting traffic
    global_session_manager = global_agent.session()
    await global_session_manager.__aenter__()

@app.on_event("shutdown")
async def shutdown_event():
    global global_session_manager
    if global_session_manager:
        await global_session_manager.__aexit__(None, None, None)"""

code = code.replace(old_startup, new_startup)

with open("src/api/server.py", "w") as f:
    f.write(code)
