# NEXUS-PRIME Architecture

This document describes the high-level architecture of NEXUS-PRIME.

## Core Components
- **Quad-Layer Perception Engine (QPE)**: Fuses DOM, Visual, A11y, and Temporal states.
- **Neuro-Symbolic Planner**: Uses Monte Carlo Tree Search (MCTS) and external Brains to form execution graphs.
- **Stealth Core**: Bypasses WAFs via TLS spoofing and CDP protocol manipulation.
- **Swarm Orchestrator**: Distributes tasks across Firecracker MicroVMs.
- **Memory Stores**: Utilizes Vector DBs (Episodic) and Graph DBs (Ontologies).
- **Brain Abstraction**: Easily swap between Local Models, API endpoints, or CLI tools (Gemini, Anigravity).
