class BrowserSession:
    def __init__(self, agent):
        self.agent = agent

    async def __aenter__(self):
        print("Starting browser session")
        # Initialize CDP connection
        return self

    async def __aexit__(self, exc_type, exc, tb):
        print("Closing browser session")
        # Close CDP connection
        pass

    async def run(self, task):
        print(f"Running task in session: {task}")
        # Execute task using agent logic
        return {"status": "success"}