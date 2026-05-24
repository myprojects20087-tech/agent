class CapabilityModules:
    @staticmethod
    async def navigate(url):
        print(f"Navigating to {url}")

    @staticmethod
    async def click(nexus_id):
        print(f"Clicking element {nexus_id}")

    @staticmethod
    async def type_text(nexus_id, text):
        print(f"Typing '{text}' into {nexus_id}")