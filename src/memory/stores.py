class EpisodicMemory:
    def __init__(self):
        self.vector_db = []

    def store(self, episode):
        print(f"Storing episode in vector db: {episode}")
        self.vector_db.append(episode)

class KnowledgeGraph:
    def __init__(self):
        self.graph = {}

    def map_ontology(self, domain, entity):
        print(f"Mapping {entity} for domain {domain}")
        if domain not in self.graph:
            self.graph[domain] = []
        self.graph[domain].append(entity)