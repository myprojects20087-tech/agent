.PHONY: setup test run_rest run_grpc run_graphql

setup:
	pip install -r requirements.txt

test:
	pytest

run_rest:
	uvicorn src.api.server:app --reload --port 8000

run_graphql:
	uvicorn src.api.graphql_server:app --reload --port 8001

run_cli:
	python -m src.cli.main --help

run_mcp:
	python -c "import asyncio; from src.api.mcp_server import MCPServer; server = MCPServer(); asyncio.run(server.start())"

run_grpc:
	python -c "import asyncio; from src.api.grpc_server import MockGrpcServer; server = MockGrpcServer(); asyncio.get_event_loop().run_forever()"