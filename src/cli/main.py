import asyncio
import typer
from rich.console import Console
from rich.progress import track
from src.core.nexus_agent import NexusAgent

app = typer.Typer(help="NEXUS-PRIME CLI interface")
console = Console()

@app.command()
def run(goal: str, mode: str = "distributed", brain: str = "local"):
    """
    Run a specific task goal through NEXUS-PRIME.
    """
    console.print(f"[bold green]Starting NEXUS-PRIME in {mode} mode with {brain} brain...[/bold green]")

    agent = NexusAgent(mode=mode, brain_config={"type": brain})

    async def execute():
        for _ in track(range(10), description=f"Executing: {goal}..."):
            await asyncio.sleep(0.1) # Simulate progress
        result = await agent.run(goal)
        console.print(f"[bold cyan]Result:[/bold cyan] {result}")

    asyncio.run(execute())

@app.command()
def trace(task_id: str):
    """
    View execution trace for a given task ID.
    """
    console.print(f"Viewing trace for {task_id}")

if __name__ == "__main__":
    app()