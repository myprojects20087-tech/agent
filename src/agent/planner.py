import asyncio
import random
import math
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from src.brain import BrainProvider

class StateNode(BaseModel):
    state_vector: List[float]
    visits: int = 0
    value: float = 0.0
    children: Dict[str, 'StateNode'] = {}
    parent: Optional['StateNode'] = None
    action_taken: Optional[str] = None

class NeuroSymbolicPlanner:
    def __init__(self, brain: Optional[BrainProvider] = None, exploration_weight: float = 1.414):
        self.brain = brain
        self.exploration_weight = exploration_weight
        self.root = None

    async def generate_plan(self, goal: str, current_state: Dict[str, Any]) -> List[str]:
        print(f"[NeuroSymbolicPlanner] Decomposing goal via Brain: {goal}")

        if self.brain:
            brain_response = await self.brain.reason(f"Decompose goal into symbolic AST: {goal}", context=current_state)
            print(f"[NeuroSymbolicPlanner] Brain responded: {brain_response}")
        else:
            await asyncio.sleep(0.1) # Simulate

        # Build symbolic AST task graph
        task_graph = self._build_symbolic_ast(goal)
        print(f"[NeuroSymbolicPlanner] Task Graph AST Generated: {task_graph}")

        # Run MCTS for the next sequence of optimal actions
        initial_vector = self._encode_state(current_state)
        self.root = StateNode(state_vector=initial_vector)

        optimal_trajectory = await self._run_mcts(self.root, iterations=50)
        return optimal_trajectory

    def _build_symbolic_ast(self, goal: str) -> Dict[str, Any]:
        return {
            "node_type": "SEQUENCE",
            "children": [
                {"node_type": "PERCEIVE", "target": "DOM_STATE"},
                {"node_type": "EVALUATE", "condition": "ELEMENT_FOUND"},
                {"node_type": "ACT", "target": "ELEMENT"}
            ]
        }

    def _encode_state(self, state_dict: Dict[str, Any]) -> List[float]:
        # Dummy vectorization of current QPE state
        return [random.random() for _ in range(128)]

    async def _run_mcts(self, root: StateNode, iterations: int) -> List[str]:
        print("[NeuroSymbolicPlanner] Running Monte Carlo Tree Search...")
        for _ in range(iterations):
            node = self._select(root)
            if not self._is_terminal(node):
                node = self._expand(node)
            reward = await self._simulate(node)
            self._backpropagate(node, reward)

        # Extract best trajectory
        trajectory = []
        curr = root
        while curr.children:
            best_action = max(curr.children.items(), key=lambda item: item[1].visits)[0]
            trajectory.append(best_action)
            curr = curr.children[best_action]
        return trajectory

    def _is_terminal(self, node: StateNode) -> bool:
        # Dummy terminal check
        return node.visits > 10

    def _select(self, node: StateNode) -> StateNode:
        while node.children:
            node = max(node.children.values(), key=self._uct_score)
        return node

    def _uct_score(self, node: StateNode) -> float:
        if node.visits == 0:
            return float('inf')
        parent_visits = node.parent.visits if node.parent else 1
        exploitation = node.value / node.visits
        exploration = self.exploration_weight * math.sqrt(math.log(parent_visits) / node.visits)
        return exploitation + exploration

    def _expand(self, node: StateNode) -> StateNode:
        possible_actions = ["click_nexus_id", "type_input", "scroll_viewport", "solve_captcha"]
        for action in possible_actions:
            if action not in node.children:
                new_state = [v + random.uniform(-0.1, 0.1) for v in node.state_vector]
                child = StateNode(state_vector=new_state, parent=node, action_taken=action)
                node.children[action] = child
                return child # Expand one at a time
        return node

    async def _simulate(self, node: StateNode) -> float:
        # Simulate value network predicting success probability
        if self.brain:
            # Optionally use Brain to evaluate node value
            pass
        await asyncio.sleep(0.01)
        return random.random()

    def _backpropagate(self, node: StateNode, reward: float):
        while node is not None:
            node.visits += 1
            node.value += reward
            node = node.parent