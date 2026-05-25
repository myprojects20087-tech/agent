import json
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import declarative_base, sessionmaker
from typing import Dict, Any, List

Base = declarative_base()

class EpisodeModel(Base):
    __tablename__ = 'episodes'
    id = Column(Integer, primary_key=True)
    task = Column(String)
    trajectory = Column(Text)
    reward = Column(String)

class EpisodicMemory:
    def __init__(self, db_path="sqlite:///memory.db"):
        print(f"[Memory] Initializing SQLite DB for Episodic State Matching at {db_path}")
        self.engine = create_engine(db_path)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def store(self, episode: Dict[str, Any]):
        print(f"[Memory] Storing episode in SQLite DB. Reward: {episode.get('reward', 0)}")
        session = self.Session()
        new_ep = EpisodeModel(
            task=episode.get("task", ""),
            trajectory=json.dumps(episode.get("trajectory", [])),
            reward=str(episode.get("reward", 0))
        )
        session.add(new_ep)
        session.commit()
        session.close()

    def search_similar(self, current_state_vector: List[float], top_k: int = 3):
        print("[Memory] (Mock) Querying DB for similar historical trajectories...")
        return []

class KnowledgeGraph:
    def __init__(self):
        print("[Memory] Initializing Graph DB interface for Domain Ontologies...")
        self.graph = {}

    def map_ontology(self, domain: str, entity: str, relationships: Dict[str, str]):
        print(f"[Memory] Query: MERGE (n:Entity {{name: '{entity}'}}) in domain '{domain}'")
        if domain not in self.graph:
            self.graph[domain] = []
        self.graph[domain].append({"entity": entity, "relationships": relationships})

    def query_relationships(self, domain: str, entity: str):
        return [node for node in self.graph.get(domain, []) if node["entity"] == entity]